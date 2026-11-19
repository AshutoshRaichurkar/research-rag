# Learning log

Three lines per day: what I built, what surprised me, which number changed.

## Day 1: LLM and embedding fundamentals (2026-11-18)
- **Built:** `notebooks/01_fundamentals.ipynb`: token counting, an `ask()` helper for Ollama, a temperature experiment, an embedding similarity grid, and a tiny RAG loop over 4 paragraphs.
- **Surprised me:** without context, llama3.1:8b confidently invented what LoRA stands for, twice, with two *different* fake answers and fake authors. With the abstract in the prompt it got it right and admitted the authors weren't given. Also: "LoRA" vs. "Low-rank adaptation" scored only 0.40 in embeddings, because the model doesn't know the acronym.
- **Numbers:** about 0.73 words/token on a physics abstract · about 46 tokens/s on my Mac · paraphrases about 0.6 cosine, unrelated about 0.05 · the right paragraph scored 0.54 vs. 0.23 for the runner-up.
