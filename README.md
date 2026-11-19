# arXiv Paper Curator

Ask questions about a collection of research papers and get answers that cite the exact paper and page.
Built as a production-shaped RAG system: local LLM, Postgres/pgvector, an evaluation suite, and a FastAPI service.

> Status: in progress. Building in public over 14 days. Daily study guides are in [`course/`](course/).

## Results

Retrieval and answer quality on a hand-labeled golden set (filled in from Day 5 on).

| Config | Recall@5 | MRR | Faithfulness | Latency (p50) |
| --- | --- | --- | --- | --- |
| Baseline (vector only) | – | – | – | – |
| Hybrid (vector + BM25) | – | – | – | – |
| Hybrid + rerank | – | – | – | – |

## Architecture

```
PDFs → ingestion (parse, clean, chunk) → embeddings → Postgres/pgvector
                                                          │
question → embed → retrieve top-k → (rerank) → prompt → Llama 3.1 → cited answer
```

## Stack

| Layer | Tool |
| --- | --- |
| LLM | Ollama, llama3.1:8b (local) |
| Embeddings | sentence-transformers, all-MiniLM-L6-v2 |
| Vector store | Postgres 16 + pgvector |
| API | FastAPI |
| Evals | Golden set, recall@k, MRR, Ragas |
| Infra | Docker Compose |

## Quickstart

Prerequisites: Python 3.11+, Docker Desktop (running), [Ollama](https://ollama.com).

```bash
cp .env.example .env
ollama pull llama3.1:8b
make install   # creates .venv and installs dependencies
make up        # starts Postgres + pgvector
make test
```

Put PDFs in `data/papers/` (they are git-ignored).

## Project layout

```
research_rag/
  ingestion/    PDF parsing, cleaning, chunking
  embeddings/   embedding model + vector store writes
  retrieval/    vector, keyword and hybrid search, reranking
  generation/   prompts, LLM client, guardrails
  evals/        retrieval and answer-quality evaluation
  api/          FastAPI service
  config.py     settings from .env
db/init.sql     database setup
evals/          golden dataset and results
notebooks/      experiments
tests/
```

## Roadmap

- [x] Day 0: project skeleton
- [x] Day 1: LLM and embedding fundamentals
- [ ] Day 2: ingestion and chunking
- [ ] Day 3: embeddings and vector store
- [ ] Day 4: baseline RAG with citations
- [ ] Days 5–7: evaluation suite
- [ ] Days 8–9: hybrid search and reranking
- [ ] Days 10–11: API, guardrails, tracing
- [ ] Days 12–14: deploy, CI, demo
