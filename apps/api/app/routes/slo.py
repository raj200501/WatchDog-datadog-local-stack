from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import select

from ..db import get_session
from ..deps import require_api_key
from ..models import Monitor, SLO, Alert
from ..schemas import SLOIn

slo_router = APIRouter(prefix="/api/v1/slo", dependencies=[Depends(require_api_key)])


@slo_router.get("")
async def list_slos() -> list[dict]:
    with get_session() as session:
        slos = session.exec(select(SLO)).all()
        return [slo.model_dump() for slo in slos]


@slo_router.post("")
async def create_slo(payload: SLOIn) -> dict:
    with get_session() as session:
        slo = SLO(**payload.model_dump())
        session.add(slo)
        session.commit()
        session.refresh(slo)
        return slo.model_dump()


@slo_router.get("/{slo_id}/status")
async def slo_status(slo_id: int) -> dict:
    with get_session() as session:
        slo = session.get(SLO, slo_id)
        if not slo:
            return {"error": "slo not found"}
        target = slo.target
        window_start = datetime.utcnow() - timedelta(days=slo.window_days)
        if slo.monitor_id:
            alerts = session.exec(
                select(Alert).where(
                    Alert.monitor_id == slo.monitor_id,
                    Alert.fired_at >= window_start,
                )
            ).all()
            total = len(alerts)
            burn_rate = len([alert for alert in alerts if alert.status == "firing"]) / (total or 1)
        else:
            burn_rate = 0.0
        return {
            "slo_id": slo_id,
            "target": target,
            "burn_rate": burn_rate,
            "status": "ok" if burn_rate < (1 - target) else "breach",
        }
