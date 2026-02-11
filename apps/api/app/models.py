from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    env: str = "prod"


class MetricPoint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ts: datetime
    value: float
    tags: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    service: str


class LogEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ts: datetime
    service: str
    level: str
    message: str
    attrs: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Span(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None
    service: str
    name: str
    start_ts: datetime
    duration_ms: int
    status: str
    tags: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Monitor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    query: str
    threshold: float
    window: str
    severity: str


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monitor_id: int = Field(foreign_key="monitor.id")
    status: str
    fired_at: datetime
    resolved_at: Optional[datetime] = None
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class SLO(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    monitor_id: Optional[int] = Field(default=None, foreign_key="monitor.id")
    query: Optional[str] = None
    target: float
    window_days: int


class Incident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    severity: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None


class IncidentEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    incident_id: int = Field(foreign_key="incident.id")
    ts: datetime
    kind: str
    message: str
    meta: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class SyntheticCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str
    url: str
    interval_sec: int
    timeout_ms: int


class SyntheticResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    check_id: int = Field(foreign_key="syntheticcheck.id")
    ts: datetime
    ok: bool
    latency_ms: int
    status_code: Optional[int] = None
    error: Optional[str] = None
