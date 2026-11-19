.PHONY: install up down reset test lint

install:
	python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -e ".[dev]"

up:
	docker compose up -d

down:
	docker compose down

reset:  ## wipe the database and re-run init.sql
	docker compose down -v && docker compose up -d

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/ruff check . && .venv/bin/ruff format --check .
