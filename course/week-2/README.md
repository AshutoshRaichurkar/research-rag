# Week 2: Make it better, then make it real

Week 1 gave you a working, measured system. Week 2 improves retrieval with techniques production teams use, turns the script into a service, and puts it online.

![Diagram](diagram-1.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    D8[Day 8<br/>Hybrid search] --> D9[Day 9<br/>Reranking]
    D9 --> D10[Day 10<br/>FastAPI]
    D10 --> D11[Day 11<br/>Guardrails + tracing]
    D11 --> D12[Day 12<br/>Cloud deploy]
    D12 --> D13[Day 13<br/>CI + provider swap]
    D13 --> D14[Day 14<br/>Capstone]
```

</details>

| Day | You'll be able to say |
| --- | --- |
| 8 | "Hybrid search fixed acronym questions; recall@5 went from X to Y." |
| 9 | "A cross-encoder reranker raised MRR, at a cost of N ms per query." |
| 10 | "It's a FastAPI service with streaming, running with one command." |
| 11 | "It refuses out-of-scope questions, resists prompt injection, and every request is traced." |
| 12 | "It's live on AWS." |
| 13 | "Every push runs tests and a quick eval in CI." |
| 14 | "Here's the README, the demo, and what I learned." |

**Rule for this week:** every retrieval change (Days 8–9) must show up as a new row in the README results table.

## What changes this week

Gray boxes were built in Week 1. Colored boxes are new this week.

![What changes this week](diagram-2.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart TB
    Q[Question] --> G1["Input guardrails<br/>(Day 11)"]
    G1 --> V[Vector search]
    G1 --> K["Keyword search<br/>(Day 8)"]
    V --> F["RRF merge<br/>(Day 8)"]
    K --> F
    F --> RR["Rerank top 20 → 5<br/>(Day 9)"]
    RR --> TH{"Relevant enough?<br/>(Day 11)"}
    TH -->|no| IDK["I don't know"]
    TH -->|yes| P[Prompt]
    P --> AD["LLM adapter<br/>(Day 13)"]
    AD --> L[Ollama or hosted LLM]
    L --> G3["Citation + PII checks<br/>(Day 11)"]
    G3 --> API["FastAPI + streaming<br/>(Day 10)"]
    API --> U[User]

    classDef old fill:#eeeeee,stroke:#999,color:#333
    classDef new fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    class Q,V,P,L,U old
    class G1,K,F,RR,TH,AD,G3,API,IDK new
```

</details>

## From laptop to live

![From laptop to live](diagram-3.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    subgraph Laptop["Your Mac (Days 10–11)"]
        DC["docker compose up<br/>api + db"]
        LF["Langfuse traces"]
    end
    subgraph GitHub["GitHub (Day 13)"]
        CI["Actions: lint, tests,<br/>smoke eval"]
    end
    subgraph AWS["AWS EC2 (Day 12)"]
        PROD["Caddy HTTPS → API → db"]
    end
    DC -->|git push| CI
    CI -->|green build| PROD
    PROD --> USER["Anyone with the link<br/>(Day 14 demo)"]
```

</details>
