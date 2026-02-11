import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import typer
import yaml

app = typer.Typer(add_completion=False)


DEFAULT_CONFIG = {
    "api_url": "http://localhost:8000",
    "api_key": "dev-watchdog-key",
    "services": ["web", "api", "worker"],
}


def load_config(path: str) -> dict[str, Any]:
    if not Path(path).exists():
        return DEFAULT_CONFIG
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def send_payload(api_url: str, api_key: str, endpoint: str, payload: list[dict]) -> None:
    with httpx.Client() as client:
        response = client.post(
            f"{api_url}{endpoint}",
            json=payload,
            headers={"X-API-Key": api_key},
            timeout=10,
        )
        response.raise_for_status()


def generate_metrics(service: str) -> list[dict]:
    return [
        {
            "name": "cpu.util",
            "ts": datetime.utcnow().isoformat(),
            "value": random.random(),
            "tags": {"service": service},
            "service": service,
        }
    ]


def generate_logs(service: str) -> list[dict]:
    level = random.choice(["info", "info", "warn", "error"])
    return [
        {
            "ts": datetime.utcnow().isoformat(),
            "service": service,
            "level": level,
            "message": f"{service} handled request",
            "attrs": {"request_id": str(random.randint(1000, 9999))},
        }
    ]


def generate_traces(service: str) -> list[dict]:
    trace_id = str(random.randint(100000, 999999))
    span_id = str(random.randint(1000, 9999))
    return [
        {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_id": None,
            "service": service,
            "name": "request",
            "start_ts": datetime.utcnow().isoformat(),
            "duration_ms": random.randint(20, 300),
            "status": random.choice(["ok", "ok", "error"]),
            "tags": {"service": service},
        }
    ]


@app.command()
def run(config: str = "configs/agent.yaml", duration: int = 60) -> None:
    settings = load_config(config)
    end_time = time.time() + duration
    while time.time() < end_time:
        for service in settings["services"]:
            send_payload(settings["api_url"], settings["api_key"], "/api/v1/ingest/metrics", generate_metrics(service))
            send_payload(settings["api_url"], settings["api_key"], "/api/v1/ingest/logs", generate_logs(service))
            send_payload(settings["api_url"], settings["api_key"], "/api/v1/ingest/traces", generate_traces(service))
        time.sleep(2)


@app.command("synthetics")
def run_synthetics_once(config: str = "configs/agent.yaml") -> None:
    settings = load_config(config)
    with httpx.Client() as client:
        response = client.get(
            f"{settings['api_url']}/api/v1/synthetics",
            headers={"X-API-Key": settings["api_key"]},
            timeout=10,
        )
        response.raise_for_status()
        checks = response.json()
    for check in checks:
        with httpx.Client() as client:
            client.get(check["url"], timeout=check["timeout_ms"] / 1000)


@app.command("seed-demo")
def seed_demo(config: str = "configs/agent.yaml") -> None:
    settings = load_config(config)
    with httpx.Client() as client:
        client.post(
            f"{settings['api_url']}/api/v1/monitors",
            headers={"X-API-Key": settings["api_key"]},
            json={
                "name": "High CPU",
                "type": "threshold",
                "query": "metric:avg(last_5m):cpu.util{service:web}",
                "threshold": 0.8,
                "window": "5m",
                "severity": "high",
            },
            timeout=10,
        )
        client.post(
            f"{settings['api_url']}/api/v1/slo",
            headers={"X-API-Key": settings["api_key"]},
            json={
                "name": "Web Availability",
                "monitor_id": 1,
                "target": 0.99,
                "window_days": 7,
            },
            timeout=10,
        )
        client.post(
            f"{settings['api_url']}/api/v1/synthetics",
            headers={"X-API-Key": settings["api_key"]},
            json={
                "name": "Homepage",
                "type": "http",
                "url": "https://example.com",
                "interval_sec": 60,
                "timeout_ms": 1000,
            },
            timeout=10,
        )
    run(config=config, duration=120)


if __name__ == "__main__":
    app()
