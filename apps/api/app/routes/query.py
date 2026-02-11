from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import select

from ..db import get_session
from ..deps import require_api_key
from ..models import LogEvent, MetricPoint, Span, Service
from ..sse import LogBroadcaster
from ..state import get_broadcaster

query_router = APIRouter(prefix="/api/v1", dependencies=[Depends(require_api_key)])


@query_router.get("/services")
async def list_services() -> list[dict]:
    with get_session() as session:
        services = session.exec(select(Service)).all()
        return [service.model_dump() for service in services]


@query_router.get("/metrics/timeseries")
async def metrics_timeseries(
    name: str,
    service: str | None = None,
    from_ts: datetime | None = Query(default=None, alias="from"),
    to_ts: datetime | None = Query(default=None, alias="to"),
    rollup: str | None = None,
) -> dict:
    with get_session() as session:
        stmt = select(MetricPoint).where(MetricPoint.name == name)
        if service:
            stmt = stmt.where(MetricPoint.service == service)
        if from_ts:
            stmt = stmt.where(MetricPoint.ts >= from_ts)
        if to_ts:
            stmt = stmt.where(MetricPoint.ts <= to_ts)
        points = session.exec(stmt).all()
    values = [point.value for point in points]
    rollups = {}
    if values:
        rollups = {
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }
    return {
        "points": [point.model_dump() for point in points],
        "rollups": rollups,
    }


@query_router.get("/logs/search")
async def search_logs(
    q: str | None = None,
    service: str | None = None,
    level: str | None = None,
    from_ts: datetime | None = Query(default=None, alias="from"),
    to_ts: datetime | None = Query(default=None, alias="to"),
    limit: int = 100,
) -> list[dict]:
    with get_session() as session:
        stmt = select(LogEvent)
        if service:
            stmt = stmt.where(LogEvent.service == service)
        if level:
            stmt = stmt.where(LogEvent.level == level)
        if from_ts:
            stmt = stmt.where(LogEvent.ts >= from_ts)
        if to_ts:
            stmt = stmt.where(LogEvent.ts <= to_ts)
        logs = session.exec(stmt).all()
    if q:
        logs = [log for log in logs if q.lower() in log.message.lower()]
    logs = sorted(logs, key=lambda item: item.ts, reverse=True)[:limit]
    return [log.model_dump() for log in logs]


@query_router.get("/traces/search")
async def search_traces(
    service: str | None = None,
    from_ts: datetime | None = Query(default=None, alias="from"),
    to_ts: datetime | None = Query(default=None, alias="to"),
    min_duration_ms: int | None = None,
    status: str | None = None,
) -> list[dict]:
    with get_session() as session:
        stmt = select(Span)
        if service:
            stmt = stmt.where(Span.service == service)
        if from_ts:
            stmt = stmt.where(Span.start_ts >= from_ts)
        if to_ts:
            stmt = stmt.where(Span.start_ts <= to_ts)
        if min_duration_ms:
            stmt = stmt.where(Span.duration_ms >= min_duration_ms)
        if status:
            stmt = stmt.where(Span.status == status)
        spans = session.exec(stmt).all()
    return [span.model_dump() for span in spans]


@query_router.get("/traces/{trace_id}")
async def trace_detail(trace_id: str) -> dict:
    with get_session() as session:
        stmt = select(Span).where(Span.trace_id == trace_id)
        spans = sorted(session.exec(stmt).all(), key=lambda item: item.start_ts)
    return {
        "trace_id": trace_id,
        "spans": [span.model_dump() for span in spans],
    }


@query_router.get("/logs/tail")
async def tail_logs(
    service: str,
    broadcaster: LogBroadcaster = Depends(get_broadcaster),
):
    async def event_stream():
        async for payload in broadcaster.subscribe(service):
            yield f"data: {payload}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
