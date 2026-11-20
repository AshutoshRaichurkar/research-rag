.PHONY: install up down reset logs ingest test lint format check

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

lint:  ## check style without changing anything (this is what CI runs)
	.venv/bin/ruff check . && .venv/bin/ruff format --check .

format:  ## fix import order and formatting automatically
	.venv/bin/ruff check . --fix && .venv/bin/ruff format .

check: lint test  ## run everything CI runs, before you push

load:  ## embed every chunk and store it in Postgres
	.venv/bin/python -m research_rag.embeddings.load
