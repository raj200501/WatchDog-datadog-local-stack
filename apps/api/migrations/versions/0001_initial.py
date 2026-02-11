"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-02-09 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("env", sa.String(), nullable=False),
    )
    op.create_table(
        "metricpoint",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("service", sa.String(), nullable=False),
    )
    op.create_table(
        "logevent",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("service", sa.String(), nullable=False),
        sa.Column("level", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("attrs", sa.JSON(), nullable=False),
    )
    op.create_table(
        "span",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trace_id", sa.String(), nullable=False),
        sa.Column("span_id", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), nullable=True),
        sa.Column("service", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("start_ts", sa.DateTime(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
    )
    op.create_table(
        "monitor",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("query", sa.String(), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("window", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
    )
    op.create_table(
        "alert",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("monitor_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("fired_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_table(
        "slo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("monitor_id", sa.Integer(), nullable=True),
        sa.Column("query", sa.String(), nullable=True),
        sa.Column("target", sa.Float(), nullable=False),
        sa.Column("window_days", sa.Integer(), nullable=False),
    )
    op.create_table(
        "incident",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "incidentevent",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=False),
    )
    op.create_table(
        "syntheticcheck",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("interval_sec", sa.Integer(), nullable=False),
        sa.Column("timeout_ms", sa.Integer(), nullable=False),
    )
    op.create_table(
        "syntheticresult",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("check_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("ok", sa.Boolean(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("error", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("syntheticresult")
    op.drop_table("syntheticcheck")
    op.drop_table("incidentevent")
    op.drop_table("incident")
    op.drop_table("slo")
    op.drop_table("alert")
    op.drop_table("monitor")
    op.drop_table("span")
    op.drop_table("logevent")
    op.drop_table("metricpoint")
    op.drop_table("service")
