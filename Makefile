VENV := .venv
VENV_BIN := $(VENV)/bin
PYTHON := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip
UVICORN := $(VENV_BIN)/uvicorn
AGENT := $(VENV_BIN)/python

WEB_DIR := apps/web
API_DIR := apps/api
AGENT_DIR := apps/agent

.PHONY: bootstrap dev demo verify test clean

bootstrap:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(API_DIR)/requirements.txt -r $(AGENT_DIR)/requirements.txt -r $(API_DIR)/requirements-dev.txt
	cd $(WEB_DIR) && npm install

verify:
	scripts/verify.sh

test:
	python3 -m unittest discover -s tests_stdlib

clean:
	rm -rf $(VENV) .pytest_cache


dev:
	scripts/dev.sh

demo:
	$(AGENT) $(AGENT_DIR)/main.py seed-demo --config configs/agent.yaml
