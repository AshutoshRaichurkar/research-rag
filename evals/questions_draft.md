# Golden questions: draft

Write questions from the PDFs only. Don't run any searches yet.
For each question, note the paper and page where you found the answer.

| arXiv file | Paper |
| --- | --- |
| 1706.03762.pdf | Attention Is All You Need (Transformer) |
| 1908.10084.pdf | Sentence-BERT |
| 2004.04906.pdf | Dense Passage Retrieval (DPR) |
| 2005.11401.pdf | Retrieval-Augmented Generation (RAG) |
| 2106.09685.pdf | LoRA |
| 2201.11903.pdf | Chain-of-Thought prompting |
| 2210.03629.pdf | ReAct |
| 2212.10496.pdf | HyDE |
| 2305.14314.pdf | QLoRA |
| 2307.03172.pdf | Lost in the Middle |
| 2309.15217.pdf | RAGAS |
| 2310.11511.pdf | Self-RAG |

## Questions

### q001
- **type:** conceptual
- **question:** What happens to a language model's accuracy when the relevant document is placed in the middle of a long context?
- **expected answer:** Accuracy drops. Performance follows a U-shaped curve: it is highest when the relevant information is at the beginning (primacy bias) or the end (recency bias), and lowest in the middle.
- **paper and page:** 2307.03172.pdf (Lost in the Middle), p.1–2

### q002
- **type:** factual
- **question:** Which two tasks does the Lost in the Middle paper use to study how models use long contexts?
- **expected answer:** Multi-document question answering and a synthetic key-value retrieval task.
- **paper and page:** 2307.03172.pdf, p.1

### q003
- **type:** multi_chunk
- **question:** In Lost in the Middle, does giving the model more retrieved documents keep improving accuracy?
- **expected answer:** No. Model performance saturates long before retriever recall does: using 50 documents instead of 20 improves accuracy only about 1.5% for GPT-3.5-Turbo and about 1% for Claude-1.3.
- **paper and page:** 2307.03172.pdf, p.2–3

### q004
- **type:** exact_term
- **question:** What does RAGAS stand for, and what is it for?
- **expected answer:** Retrieval Augmented Generation Assessment: a framework for evaluating RAG pipelines without needing human-annotated ground-truth answers (reference-free).
- **paper and page:** 2309.15217.pdf (RAGAS), p.1

### q005
- **type:** conceptual
- **question:** How does RAGAS calculate the faithfulness score?
- **expected answer:** An LLM splits the answer into short statements, then checks whether each statement can be inferred from the retrieved context. Faithfulness = supported statements / total statements.
- **paper and page:** 2309.15217.pdf, p.3

### q006
- **type:** factual
- **question:** Which three quality aspects does RAGAS measure?
- **expected answer:** Faithfulness, answer relevance and context relevance.
- **paper and page:** 2309.15217.pdf, p.2–3

### q007
- **type:** factual
- **question:** How much better is DPR than BM25 in top-5 retrieval accuracy on Natural Questions?
- **expected answer:** 65.2% for DPR vs 42.9% for BM25.
- **paper and page:** 2004.04906.pdf (Dense Passage Retrieval), p.2

### q008
- **type:** conceptual
- **question:** Why can dense retrieval find passages that keyword search like BM25 misses?
- **expected answer:** Dense embeddings map synonyms and paraphrases with different words to nearby vectors, so a question about the "bad guy" can match a passage about the "villain". Keyword methods only match the same terms.
- **paper and page:** 2004.04906.pdf, p.1

### q009
- **type:** exact_term
- **question:** What is HyDE and how does it retrieve documents?
- **expected answer:** Hypothetical Document Embeddings. An instruction-following LLM writes a fake answer document for the query; an encoder (Contriever) embeds it, and the most similar real documents are retrieved. The embedding filters out the fake details.
- **paper and page:** 2212.10496.pdf (HyDE), p.1–2

### q010
- **type:** multi_chunk
- **question:** What two kinds of memory does the RAG model combine, and what is used for each?
- **expected answer:** Parametric memory, a pre-trained seq2seq generator (BART), and non-parametric memory, a dense vector index of Wikipedia accessed with a pre-trained retriever (DPR).
- **paper and page:** 2005.11401.pdf (RAG), p.1–2
