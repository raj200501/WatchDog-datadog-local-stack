from datetime import datetime, timedelta
from sqlmodel import select

from ..db import get_session
from ..models import Alert, LogEvent, MetricPoint, Monitor
from ..utils.monitor_dsl import parse_query


def parse_window(window: str) -> timedelta:
    if window.endswith("m"):
        return timedelta(minutes=int(window[:-1]))
    if window.endswith("h"):
        return timedelta(hours=int(window[:-1]))
    raise ValueError("invalid window")


def evaluate_monitor(monitor: Monitor) -> dict:
    query = parse_query(monitor.query)
    window = parse_window(monitor.window)
    end = datetime.utcnow()
    start = end - window
    with get_session() as session:
        if query.source == "metric":
            stmt = select(MetricPoint).where(
                MetricPoint.name == query.metric,
                MetricPoint.ts >= start,
                MetricPoint.ts <= end,
            )
            if query.filter_service:
                stmt = stmt.where(MetricPoint.service == query.filter_service)
            points = session.exec(stmt).all()
            values = [p.value for p in points]
            avg = sum(values) / len(values) if values else 0.0
            current = avg
        else:
            stmt = select(LogEvent).where(
                LogEvent.ts >= start,
                LogEvent.ts <= end,
            )
            if query.filter_service:
                stmt = stmt.where(LogEvent.service == query.filter_service)
            logs = session.exec(stmt).all()
            total = len(logs)
            errors = len([log for log in logs if log.level.lower() == "error"])
            current = errors / total if total else 0.0
        triggered = current > monitor.threshold
        return {
            "value": current,
            "triggered": triggered,
        }


def upsert_alert(monitor: Monitor, evaluation: dict) -> Alert:
    now = datetime.utcnow()
    with get_session() as session:
        stmt = select(Alert).where(Alert.monitor_id == monitor.id)
        alert = session.exec(stmt).first()
        if evaluation["triggered"]:
            if not alert:
                alert = Alert(
                    monitor_id=monitor.id,
                    status="firing",
                    fired_at=now,
                    payload=evaluation,
                )
                session.add(alert)
            else:
                alert.status = "firing"
                alert.payload = evaluation
            session.commit()
            session.refresh(alert)
            return alert
        if alert and alert.status == "firing":
            alert.status = "resolved"
            alert.resolved_at = now
            alert.payload = evaluation
            session.commit()
            session.refresh(alert)
        return alert
