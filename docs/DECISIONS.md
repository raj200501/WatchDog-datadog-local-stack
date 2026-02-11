# Decision Log

## Stack
- **FastAPI + SQLModel** for predictable SQLite/Postgres support.
- **SQLite default** for a local-first experience; Postgres optional via env var.
- **React + Vite + Tailwind** for a lightweight yet polished UI.

## Background Tasks
- Use FastAPI lifespan and asyncio tasks for monitor evaluation and synthetic checks.
- Avoid Celery/Redis to keep the stack self-contained.

## Auth
- Simple API key via `X-API-Key` header with a dev default in `.env.example`.
