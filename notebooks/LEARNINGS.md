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

## Day 4: Baseline RAG (2026-11-23)
- **Built:** the full question → answer loop: `retrieval/search.py` (top-k by cosine in pgvector), `generation/prompts.py` (prompt v1 with numbered context, a citation rule and an exact "I don't know" reply), `generation/llm.py` (Ollama, temperature 0, `num_ctx` 8192, one retry), `generation/citations.py` (maps `[n]` to source and page), `rag.py` returning an `Answer` with latency, `make ask Q="..."`, and 7 mocked tests that need neither Postgres nor Ollama.
- **Surprised me:** two wrong answers had two different causes. "Lost in the middle" retrieved five Chain-of-Thought golf-ball maths chunks because MiniLM matched the word "lost" (a **retrieval** failure, so refusing was correct). "ReAct" retrieved the right chunk ("combined reasoning and action"), but the chunk began mid-word with "Act is…", and the model refused (a **generation and chunking** miss). Rule: when an answer is wrong, first check whether the answer was in the retrieved chunks.
- **Numbers:** 9 questions by eye · 1 fully correct with citations (LoRA latency) · 2 correct refusals (banana bread, World Cup) · 3 partial or vague (QLoRA memory, HyDE, NF4) · 2 false refusals (lost in the middle, ReAct) · 3.6–9 s per answer · 28 tests.

## Day 5: Golden dataset (2026-11-23)
- **Built:** `evals/golden.jsonl` with 18 hand-checked questions (3 factual, 3 conceptual, 2 exact_term, 2 multi_chunk, 5 unanswerable, 3 adversarial) from the RAG-focused papers (Lost in the Middle, RAGAS, DPR, HyDE, RAG); `evals/dataset.py` (a `GoldenItem` Pydantic model with a `Literal` type, and `load_golden()`, which fails with the line number); `evals/find.py` (`find_chunks()`, an exact-text `ILIKE` search used for labelling); and 5 tests, including one that every labelled chunk ID exists in the database.
- **Surprised me:** labelling chunks is judgement, not lookup: "U-shaped" appears in 13 chunks, but only 4 actually explain it. And "unanswerable" questions can still match words in the corpus: *banana* is in ReAct (banana chips in a shopping task) and *World Cup* is in the RAG paper (a Jeopardy example), so search will return those chunks and the LLM must still refuse.
- **Numbers:** 18 questions · 10 answerable with 1–4 relevant chunks each (23 labels) · 8 with no relevant chunks · 33 tests.

## Day 6: Retrieval evals (2026-11-25)
- **Built:** `evals/metrics.py` (`recall_at_k`, `reciprocal_rank`) with tests that reproduce the course's worked example; `evals/retrieval_eval.py` + `make eval-retrieval`, which searches once with k=10 per answerable golden question, scores recall@1/3/5/10 and MRR, and saves a dated JSON file with the config and per-question detail (now committed, so git shows the history); a recall@k curve from the saved IDs.
- **Surprised me:** the first score (recall@5 0.20, MRR 0.08) was mostly **my labels' fault**: 4 "misses" were chunks that did answer the question, in the results and conclusion sections I hadn't labelled. Fixing labels (system unchanged) took it to 0.50 / 0.39. The real misses are mainly **junk chunks** (tables, reference lists, formulas) beating real text, plus acronyms (RAGAS, HyDE) and exact numbers (65.2%). The right *paper* was #1 for 9/10 questions; the right *chunk* wasn't.
- **Numbers:** baseline recall@1 0.30 · @3 0.50 · @5 **0.50** · @10 0.60 · MRR **0.39** · curve flat from k=3 to k=8 → keep k=5 · 40% of answers not in the top 10 · 37 tests.
