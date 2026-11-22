# Learning log

Three lines per day: what I built, what surprised me, which number changed.

## Day 1: LLM and embedding fundamentals (2026-11-18)
- **Built:** `notebooks/week-1/day-01-llm-fundamentals/01_fundamentals.ipynb`: token counting, an `ask()` helper for Ollama, a temperature experiment, an embedding similarity grid, and a tiny RAG loop over 4 paragraphs.
- **Surprised me:** without context, llama3.1:8b confidently invented what LoRA stands for, twice, with two *different* fake answers and fake authors. With the abstract in the prompt it got it right and admitted the authors weren't given. Also: "LoRA" vs. "Low-rank adaptation" scored only 0.40 in embeddings, because the model doesn't know the acronym.
- **Numbers:** about 0.73 words/token on a physics abstract · about 46 tokens/s on my Mac · paraphrases about 0.6 cosine, unrelated about 0.05 · the right paragraph scored 0.54 vs. 0.23 for the runner-up.

## Day 2: Ingestion and chunking (2026-11-19)
- **Built:** a PDF → chunks pipeline in `src/research_rag/ingestion/`: Pydantic models (`Page`, `Chunk`), a loader (PyMuPDF), a cleaner (ligatures, hyphenated line breaks, watermark, page numbers, whitespace), a sliding-window chunker (200 tokens, 40 overlap) with page tracking and stable IDs (`2106.09685.pdf::0003`), `make ingest` writing `data/processed/chunks.jsonl`, and 13 new tests.
- **Surprised me:** the `ﬁ` ligature hid 146 occurrences of "fine" from search; a page-number regex that looked fine on a sample deleted 1,300 lines across the corpus, mostly results-table numbers (fixed by only checking a page's first and last line). And 200 tiktoken tokens is not always 200 tokens for the embedding model: 3 chunks are over its limit.
- **Numbers:** 12 papers · 253 pages · 1,405 chunks · 205 noise lines removed · 3/1,405 chunks (0.2%) over the embedding model's 254-token limit (longest 313) · 16 tests passing.

## Day 3: Embeddings and vector store (2026-11-22)
- **Built:** a `document_chunks` table in Postgres with a `vector(384)` column and an HNSW index; `embedder.py` (MiniLM, loaded once, batches, normalized), `store.py` (upsert on the chunk id, plus deleting stale rows), `make load` (embeds and stores everything in 4.2 s), a first vector search in SQL, and tests that run in a throwaway database.
- **Surprised me:** the first load failed because equation brackets in PDFs come out as invisible NUL characters, which Postgres rejects; removing ~2,400 control characters took the corpus from 1,405 to 1,389 chunks. An off-topic question ("banana bread") scored 0.48, higher than a real acronym question ("What is NF4?", 0.43), so one similarity threshold can't separate good from bad results. And the query planner estimated a Seq Scan would be cheaper, but the HNSW index was actually 3× faster when measured.
- **Numbers:** 1,389 chunks · 384 dimensions · ~330 chunks/s to embed · neighbouring chunks ≈ 0.5 similarity · best search hits 0.57–0.67 · Seq Scan 22 ms vs HNSW 7.4 ms · 20 tests.
