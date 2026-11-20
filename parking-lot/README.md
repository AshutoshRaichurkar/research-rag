# Parking lot

Ideas and work we've deliberately put aside for later, so nothing gets forgotten.
When you pick one up, move it out of this list (and into a commit).

| Item | Why it's parked | When to pick it up | How |
| --- | --- | --- | --- |
| **CI: lint + tests on every push** | Not needed while building alone; adds a step to every push | Day 13 (or any time you want the green badge) | `ci.yml` in this folder is ready. Move it to `.github/workflows/ci.yml`, push, check the **Actions** tab, then add the README badge. |
| **CD: deploy automatically after CI passes** | Nothing to deploy until the API (Day 10) and AWS (Day 12) exist | Day 12 | Add a deploy job that runs only when CI is green. |
| **Chunk with the embedding model's own tokenizer** | 3 of 1,405 chunks (0.2%) go over MiniLM's 254-token limit and get truncated | Day 7 | Count tokens with the embedding model's tokenizer (or try `CHUNK_SIZE=180`) and compare retrieval metrics. |
| **Sentence-aware chunking** | Chunks start and end mid-sentence | Day 7 | Cut at sentence or section boundaries; compare against fixed-size chunks with evals. |
| **Drop references-section and title chunks** | Search for "lost in the middle" returned the title chunk and 2 bibliography chunks in its top 5 | Day 7 | Detect the "References" heading and stop chunking there; skip chunk 0 if it's mostly names and emails. Compare retrieval metrics before and after. |
| **Remove footnotes from page text** | Footnotes bleed into body text | Only if evals show it hurts | Detect footnote lines at the bottom of a page. |

## Already done for CI (kept even though CI is parked)

These run locally and cost nothing:
- `make lint`: style check without changing anything
- `make format`: fix import order and formatting automatically
- `make check`: lint + tests, the same as CI would run
- ruff skips `notebooks/` and `course/`, and its version is pinned in `pyproject.toml`
