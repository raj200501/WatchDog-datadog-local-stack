VENV := .venv
VENV_BIN := $(VENV)/bin
PYTHON := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip
UVICORN := $(VENV_BIN)/uvicorn
AGENT := $(VENV_BIN)/python

WEB_DIR := apps/web
API_DIR := apps/api
AGENT_DIR := apps/agent

.PHONY: bootstrap dev seed demo

bootstrap:
	python3.11 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(API_DIR)/requirements.txt -r $(AGENT_DIR)/requirements.txt
	cd $(WEB_DIR) && npm install

dev:
	$(UVICORN) apps.api.main:app --host 0.0.0.0 --port 8000 --reload & \
	cd $(WEB_DIR) && npm run dev -- --host 0.0.0.0 --port 3000

seed:
	$(AGENT) $(AGENT_DIR)/main.py --duration 30

demo: bootstrap seed dev
