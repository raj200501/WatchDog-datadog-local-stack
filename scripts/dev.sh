#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate

uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

cd apps/web
npm run dev -- --host 0.0.0.0 --port 3000

kill $API_PID
