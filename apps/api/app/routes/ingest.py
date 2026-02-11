from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import select

from ..db import get_session
from ..deps import require_api_key
from ..models import LogEvent, MetricPoint, Span, Service
from ..schemas import LogEventIn, MetricPointIn, SpanIn
from ..sse import LogBroadcaster
from ..state import get_broadcaster
from ..utils.dogstatsd import parse_line, DogstatsdParseError


ingest_router = APIRouter(prefix="/api/v1/ingest", dependencies=[Depends(require_api_key)])


@ingest_router.post("/metrics")
async def ingest_metrics(payload: list[MetricPointIn]) -> dict:
    with get_session() as session:
        for item in payload:
            existing = session.exec(select(Service).where(Service.name == item.service)).first()
            if not existing:
                session.add(Service(name=item.service, env="prod"))
            session.add(MetricPoint(**item.model_dump()))
        session.commit()
    return {"ingested": len(payload)}


@ingest_router.post("/logs")
async def ingest_logs(
    payload: list[LogEventIn],
    broadcaster: LogBroadcaster = Depends(get_broadcaster),
) -> dict:
    with get_session() as session:
        for item in payload:
            existing = session.exec(select(Service).where(Service.name == item.service)).first()
            if not existing:
                session.add(Service(name=item.service, env="prod"))
            log = LogEvent(**item.model_dump())
            session.add(log)
            await broadcaster.publish(log.service, log.model_dump())
        session.commit()
    return {"ingested": len(payload)}


@ingest_router.post("/traces")
async def ingest_traces(payload: list[SpanIn]) -> dict:
    with get_session() as session:
        for item in payload:
            existing = session.exec(select(Service).where(Service.name == item.service)).first()
            if not existing:
                session.add(Service(name=item.service, env="prod"))
            session.add(Span(**item.model_dump()))
        session.commit()
    return {"ingested": len(payload)}


@ingest_router.post("/dogstatsd")
async def ingest_dogstatsd(payload: str = Body(..., media_type="text/plain")) -> dict:
    lines = [line.strip() for line in payload.splitlines() if line.strip()]
    points = []
    for line in lines:
        try:
            points.append(parse_line(line))
        except DogstatsdParseError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    with get_session() as session:
        for point in points:
            existing = session.exec(select(Service).where(Service.name == point["service"])).first()
            if not existing:
                session.add(Service(name=point["service"], env="prod"))
            session.add(MetricPoint(**point))
        session.commit()
    return {"ingested": len(points)}
