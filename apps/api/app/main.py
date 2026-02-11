import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from .config import get_settings
from .db import init_db, get_session
from .models import Monitor, SyntheticCheck, SyntheticResult
from .routes.ingest import ingest_router
from .routes.query import query_router
from .routes.monitors import monitors_router
from .routes.incidents import incidents_router
from .routes.slo import slo_router
from .routes.synthetics import synthetics_router
from .services.monitor_eval import evaluate_monitor, upsert_alert

settings = get_settings()


async def monitor_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        with get_session() as session:
            monitors = session.exec(select(Monitor)).all()
        for monitor in monitors:
            evaluation = evaluate_monitor(monitor)
            upsert_alert(monitor, evaluation)
        await asyncio.sleep(settings.monitor_interval_sec)


async def synthetics_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        with get_session() as session:
            checks = session.exec(select(SyntheticCheck)).all()
        async with httpx.AsyncClient() as client:
            for check in checks:
                start = datetime.utcnow()
                try:
                    response = await client.get(check.url, timeout=check.timeout_ms / 1000)
                    ok = response.status_code < 500
                    latency_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
                    result = SyntheticResult(
                        check_id=check.id,
                        ts=datetime.utcnow(),
                        ok=ok,
                        latency_ms=latency_ms,
                        status_code=response.status_code,
                    )
                except Exception as exc:  # noqa: BLE001
                    latency_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
                    result = SyntheticResult(
                        check_id=check.id,
                        ts=datetime.utcnow(),
                        ok=False,
                        latency_ms=latency_ms,
                        error=str(exc),
                    )
                with get_session() as session:
                    session.add(result)
                    session.commit()
        await asyncio.sleep(settings.synthetics_interval_sec)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    stop_event = asyncio.Event()
    monitor_task = asyncio.create_task(monitor_loop(stop_event))
    synthetic_task = asyncio.create_task(synthetics_loop(stop_event))
    yield
    stop_event.set()
    monitor_task.cancel()
    synthetic_task.cancel()


app = FastAPI(title="WatchDog API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(monitors_router)
app.include_router(incidents_router)
app.include_router(slo_router)
app.include_router(synthetics_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
