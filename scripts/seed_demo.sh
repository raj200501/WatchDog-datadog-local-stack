#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
python apps/agent/main.py seed-demo --config configs/agent.yaml
