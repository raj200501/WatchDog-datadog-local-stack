from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from ..db import get_session
from ..deps import require_api_key
from ..models import Incident, IncidentEvent
from ..schemas import IncidentIn, IncidentEventIn

incidents_router = APIRouter(prefix="/api/v1/incidents", dependencies=[Depends(require_api_key)])


@incidents_router.get("")
async def list_incidents() -> list[dict]:
    with get_session() as session:
        incidents = session.exec(select(Incident)).all()
        return [incident.model_dump() for incident in incidents]


@incidents_router.post("")
async def create_incident(payload: IncidentIn) -> dict:
    with get_session() as session:
        incident = Incident(
            title=payload.title,
            severity=payload.severity,
            status=payload.status,
            created_at=datetime.utcnow(),
        )
        session.add(incident)
        session.commit()
        session.refresh(incident)
        return incident.model_dump()


@incidents_router.get("/{incident_id}")
async def get_incident(incident_id: int) -> dict:
    with get_session() as session:
        incident = session.get(Incident, incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="incident not found")
        events = session.exec(
            select(IncidentEvent).where(IncidentEvent.incident_id == incident_id)
        ).all()
        return {
            **incident.model_dump(),
            "events": [event.model_dump() for event in events],
        }


@incidents_router.post("/{incident_id}/events")
async def add_incident_event(incident_id: int, payload: IncidentEventIn) -> dict:
    with get_session() as session:
        incident = session.get(Incident, incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="incident not found")
        event = IncidentEvent(
            incident_id=incident_id,
            ts=datetime.utcnow(),
            kind=payload.kind,
            message=payload.message,
            meta=payload.meta,
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        return event.model_dump()
