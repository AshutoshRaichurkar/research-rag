.PHONY: install up down reset logs ingest test lint

install:
	python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -e ".[dev]"

up:
	docker compose up -d

down:
	docker compose down

reset:  ## wipe the database and re-run init.sql
	docker compose down -v && docker compose up -d

logs:
	docker compose logs -f

ingest:  ## load, clean and chunk every PDF in data/papers
	.venv/bin/python -m research_rag.ingestion.run

test:
	.venv/bin/pytest -q

lint:
	.venv/bin/ruff check . && .venv/bin/ruff format --check .
