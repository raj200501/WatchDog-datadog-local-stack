from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):
    name: str
    env: str = "prod"


class MetricPointIn(BaseModel):
    name: str
    ts: datetime
    value: float
    tags: dict[str, Any] = Field(default_factory=dict)
    service: str


class LogEventIn(BaseModel):
    ts: datetime
    service: str
    level: str
    message: str
    attrs: dict[str, Any] = Field(default_factory=dict)


class SpanIn(BaseModel):
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None
    service: str
    name: str
    start_ts: datetime
    duration_ms: int
    status: str
    tags: dict[str, Any] = Field(default_factory=dict)


class MonitorIn(BaseModel):
    name: str
    type: str
    query: str
    threshold: float
    window: str
    severity: str


class MonitorOut(MonitorIn):
    id: int


class AlertOut(BaseModel):
    id: int
    monitor_id: int
    status: str
    fired_at: datetime
    resolved_at: Optional[datetime] = None
    payload: dict[str, Any]


class SLOIn(BaseModel):
    name: str
    monitor_id: Optional[int] = None
    query: Optional[str] = None
    target: float
    window_days: int


class IncidentIn(BaseModel):
    title: str
    severity: str
    status: str


class IncidentEventIn(BaseModel):
    kind: str
    message: str
    meta: dict[str, Any] = Field(default_factory=dict)


class SyntheticCheckIn(BaseModel):
    name: str
    type: str
    url: str
    interval_sec: int
    timeout_ms: int


class SyntheticResultOut(BaseModel):
    id: int
    check_id: int
    ts: datetime
    ok: bool
    latency_ms: int
    status_code: Optional[int]
    error: Optional[str]
