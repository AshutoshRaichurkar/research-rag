# Week 1: Build it, then learn to measure it

By the end of this week you have a working RAG pipeline that answers questions with citations, and a set of evals that tell you how good it is.

![Diagram](diagram-1.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    D0[Day 0<br/>Setup] --> D1[Day 1<br/>Fundamentals]
    D1 --> D2[Day 2<br/>Ingestion]
    D2 --> D3[Day 3<br/>Vector store]
    D3 --> D4[Day 4<br/>Baseline RAG]
    D4 --> D5[Day 5<br/>Golden set]
    D5 --> D6[Day 6<br/>Retrieval evals]
    D6 --> D7[Day 7<br/>Generation evals]
```

</details>

| Day | You'll be able to say |
| --- | --- |
| 1 | "I can explain tokens, embeddings and why RAG exists." |
| 2 | "My PDFs become clean, overlapping chunks with page numbers." |
| 3 | "Every chunk is embedded and searchable in pgvector." |
| 4 | "I ask a question and get a cited answer, or 'I don't know'." |
| 5 | "I have 30+ hand-checked questions with known answers." |
| 6 | "Baseline recall@5 is X and MRR is Y." |
| 7 | "Faithfulness is Z, and I know which chunking strategy wins." |

**End-of-week checkpoint:** the README results table has a real baseline row.

## What you'll have built by Sunday

Each box shows the day you build it. Read it left to right: papers go in at the top, questions come in at the bottom, and the evals on the right grade both.

![What you'll have built by Sunday](diagram-2.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    subgraph Ingest["1 · Ingestion pipeline (Days 2–3)"]
        direction LR
        PDF["PDFs<br/>(Day 0)"] --> LOAD["Load + clean<br/>(Day 2)"] --> CHUNK["Chunk 200/40<br/>(Day 2)"] --> EMB["Embed<br/>(Day 3)"] --> DB[("pgvector<br/>(Day 3)")]
    end
    subgraph Ask["2 · Question answering (Day 4)"]
        direction LR
        Q[Question] --> SEARCH["Vector search<br/>top-5"] --> PROMPT["Prompt<br/>+ rules"] --> LLM["Llama 3.1<br/>via Ollama"] --> ANS["Answer +<br/>citations"]
    end
    subgraph Measure["3 · Evals (Days 5–7)"]
        direction LR
        GOLD[("Golden set<br/>(Day 5)")] --> RE["Retrieval score<br/>recall@k, MRR (Day 6)"]
        GOLD --> GE["Answer score<br/>faithfulness, relevance (Day 7)"]
    end
    Ingest -->|chunks are searched| Ask
    Ask -->|results are graded| Measure
```

</details>

## How the ideas build on each other

Each day's concept is what the next day needs. If something later feels confusing, go back one box.

![How the ideas build on each other](diagram-3.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    T["Tokens<br/>text is read in pieces"] --> CW["Context window<br/>the prompt has a size limit"]
    CW --> WHY["So we can't paste every paper:<br/>we must pick the right parts"]
    E["Embeddings<br/>meaning as numbers"] --> SIM["Cosine similarity<br/>find text with close meaning"]
    WHY --> RAG["RAG = retrieve the right chunks,<br/>then answer from them"]
    SIM --> RAG
    RAG --> Q1{"Is it any good?"}
    Q1 --> EV["Evals: an answer key<br/>+ metrics for each part"]
```

</details>
