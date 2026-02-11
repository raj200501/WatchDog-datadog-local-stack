from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..db import get_session
from ..deps import require_api_key
from ..models import Monitor, Alert
from ..schemas import MonitorIn, MonitorOut, AlertOut
from ..utils.monitor_dsl import parse_query, MonitorQueryError

monitors_router = APIRouter(prefix="/api/v1/monitors", dependencies=[Depends(require_api_key)])


@monitors_router.get("")
async def list_monitors() -> list[MonitorOut]:
    with get_session() as session:
        monitors = session.exec(select(Monitor)).all()
        return [MonitorOut(**monitor.model_dump()) for monitor in monitors]


@monitors_router.post("")
async def create_monitor(payload: MonitorIn) -> MonitorOut:
    try:
        parse_query(payload.query)
    except MonitorQueryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    with get_session() as session:
        monitor = Monitor(**payload.model_dump())
        session.add(monitor)
        session.commit()
        session.refresh(monitor)
        return MonitorOut(**monitor.model_dump())


@monitors_router.put("/{monitor_id}")
async def update_monitor(monitor_id: int, payload: MonitorIn) -> MonitorOut:
    with get_session() as session:
        monitor = session.get(Monitor, monitor_id)
        if not monitor:
            raise HTTPException(status_code=404, detail="monitor not found")
        for key, value in payload.model_dump().items():
            setattr(monitor, key, value)
        session.add(monitor)
        session.commit()
        session.refresh(monitor)
        return MonitorOut(**monitor.model_dump())


@monitors_router.delete("/{monitor_id}")
async def delete_monitor(monitor_id: int) -> dict:
    with get_session() as session:
        monitor = session.get(Monitor, monitor_id)
        if not monitor:
            raise HTTPException(status_code=404, detail="monitor not found")
        session.delete(monitor)
        session.commit()
    return {"deleted": monitor_id}


@monitors_router.get("/alerts")
async def list_alerts() -> list[AlertOut]:
    with get_session() as session:
        alerts = session.exec(select(Alert)).all()
        return [AlertOut(**alert.model_dump()) for alert in alerts]


@monitors_router.post("/validate")
async def validate_monitor(payload: dict) -> dict:
    query = payload.get("query", "")
    try:
        parse_query(query)
    except MonitorQueryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"valid": True}
