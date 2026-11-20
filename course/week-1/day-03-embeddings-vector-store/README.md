# Day 3: Embeddings and vector store

**Goal:** embed every chunk and store it in Postgres so it can be searched by meaning, and make reloading safe.

## What you'll study

- Choosing an embedding model
- Storing vectors in **pgvector**
- **Exact vs. approximate** search, and the **HNSW** index
- **Idempotent** loads
- Batching for speed

## Explained simply

### Tokenization vs. embedding: ingredient codes vs. flavor profile
Both turn text into numbers, but the numbers mean very different things.

- **Tokenization** is like writing a recipe's **ingredient list with product codes**: flour = #1032, sugar = #2210. It just names the pieces; the codes say nothing about taste.
- **Embedding** is like the dish's **flavor profile**: sweet 0.8, salty 0.1, spicy 0.0… A chocolate cake and a brownie have different ingredient codes but similar flavor profiles.

![Two sentences with almost no tokens in common get close embeddings](fig-tokens-vs-embedding.png)

*"The cat sat on the mat" and "A kitten rested on a rug" share only one token ("on"), yet their embeddings score 0.63 (Day 1).*

| | Tokenization | Embedding |
| --- | --- | --- |
| Output | a **list of IDs**, one per piece | **one list of 384 numbers** for the whole text |
| Output size | grows with the text | always **384** |
| What a number means | a label: "this is piece #6681" | part of the **meaning**; only useful when compared |
| Can compare meanings? | ❌ "cat" and "kitten" are unrelated IDs | ✅ similar meanings → similar numbers |
| Where you use it | Day 2: cutting chunks to 200 tokens | Day 3: making chunks searchable |

Tokenization is the **first step inside** embedding: `text → tokenize → model → embedding`. You never call the tokenizer yourself when embedding; `embed_texts()` does it for you.

### Normalizing: keep the direction, drop the length
An embedding is an **arrow**. Its **direction** is the meaning. Its **length** isn't useful for search, and could make an arrow score higher just for being long. `normalize_embeddings=True` stretches or shrinks every arrow to **length 1** without changing its direction.

![Normalizing keeps the direction and removes the length](fig-normalize.png)

*Like a compass bearing: "walk north-east 5 km" and "walk north-east 50 m" point the same way. Normalizing keeps only the bearing.*

Two bonuses: for length-1 vectors, cosine similarity is just the **dot product** (`a @ b` in Python), and cosine and Euclidean distance **rank chunks in the same order**.

### Similarity vs. distance: score vs. points lost
Two readings of the same angle between two arrows, counted from opposite ends, like a test score of 95 vs. 5 points lost.

- **Cosine similarity** (Day 1, `util.cos_sim`): how alike. **Bigger = more alike.**
- **Cosine distance** (pgvector `<=>`): how different. **Smaller = more alike.**
- **distance = 1 − similarity**

![Similarity and distance for three pairs of arrows](fig-similarity-vs-distance.png)

| Pair | Similarity | Distance |
| --- | --- | --- |
| `[1,2,3]` vs `[1,2,4]` | 0.9915 | **0.0085** |
| cat ↔ kitten sentence | 0.63 | 0.37 |
| LoRA abstract ↔ "fine-tune cheaply" | 0.54 | 0.46 |
| cat ↔ stock market | 0.03 | 0.97 |

That's why vector search in SQL is `ORDER BY embedding <=> question LIMIT 5`: **smallest distance first**. To show a score to a person, convert back: `1 - (embedding <=> question) AS similarity`.

Don't confuse **length** (one arrow: how long, which we normalize away) with **distance** (two arrows: how different their directions, meaning how different their meanings are).

### pgvector: Postgres learns a new column type
pgvector adds a `vector(384)` column type and distance operators to Postgres. You keep using SQL, joins and transactions, so it fits naturally with your data engineering background.

| Operator | Meaning |
| --- | --- |
| `<=>` | cosine **distance** (0 = identical). Similarity = `1 - distance` |
| `<->` | Euclidean distance |
| `<#>` | negative inner product |

### Exact vs. approximate search: checking every house vs. using highways
**Exact search** compares the query with every chunk. That's perfect, but slow with millions of rows, like visiting every house in a city to find your friend.

**HNSW** (Hierarchical Navigable Small World) builds a layered map: highways at the top, then main roads, then local streets. Search starts on the highway, gets close quickly, then drops down to the streets for the last stretch. It's **much faster and almost always finds the right answer** (≈95–99% of the true nearest neighbors).

With only a few thousand chunks, exact search would be fine. You add HNSW because a production system needs it and interviewers will ask about it.

![HNSW's layers: the search starts where points are sparse and drops down layer by layer.](fig-hnsw.png)

*HNSW's layers: the search starts where points are sparse and drops down layer by layer.*

### Idempotent loads: pressing the elevator button twice
Pressing an elevator button twice doesn't call two elevators. Running ingestion twice shouldn't create duplicate chunks either. The fix: give each chunk a **content hash** (a fingerprint of its text + source) with a `UNIQUE` constraint, and insert with `ON CONFLICT DO NOTHING`.

![Running ingestion twice: the second insert of the same chunk is skipped, so nothing is duplicated.](fig-idempotent.png)

*Running ingestion twice: the second insert of the same chunk is skipped, so nothing is duplicated.*

### Same model for documents and questions
Embeddings from different models live in different "maps". Embedding documents with model A and questions with model B is like using GPS coordinates from Earth on a map of Mars. Always use **one model for both**.

![What vector search does: return the chunks nearest to the question.](fig-meaning-map.png)

*What vector search does: return the chunks nearest to the question.*

## Diagram

![Diagram](diagram-1.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
flowchart LR
    C[Chunks from Day 2] --> E["embedder.py<br/>batch of 64 → 384-dim vectors<br/>(normalized)"]
    E --> S["store.py<br/>INSERT ... ON CONFLICT DO NOTHING"]
    S --> T[(document_chunks)]
    T --> I["HNSW index<br/>vector_cosine_ops"]
```

</details>

![Diagram](diagram-2.png)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
erDiagram
    document_chunks {
        bigserial id PK
        text content_hash UK "sha256(source + text)"
        text source "file name"
        int page
        int chunk_index
        text text
        int token_count
        vector embedding "vector(384)"
        timestamptz created_at
    }
```

</details>

## Tools and services

| Tool | Use today |
| --- | --- |
| Postgres 16 + pgvector (Docker) | Store and search vectors |
| `psycopg` 3 + `pgvector` Python package | Talk to Postgres, send vectors |
| `sentence-transformers` | Embed chunks |
| `hashlib` | Content hashes |
| `psql` or a GUI like TablePlus/DBeaver | Inspect the table |

## What to implement

- [ ] Add the table and index to `db/init.sql`, then `make reset`:
  ```sql
  CREATE TABLE IF NOT EXISTS document_chunks (
      id            BIGSERIAL PRIMARY KEY,
      content_hash  TEXT UNIQUE NOT NULL,
      source        TEXT NOT NULL,
      page          INT  NOT NULL,
      chunk_index   INT  NOT NULL,
      text          TEXT NOT NULL,
      token_count   INT  NOT NULL,
      embedding     vector(384) NOT NULL,
      created_at    TIMESTAMPTZ DEFAULT now()
  );
  CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw
      ON document_chunks USING hnsw (embedding vector_cosine_ops);
  ```
- [ ] `src/research_rag/embeddings/embedder.py`: load the model once, `embed(texts) -> np.ndarray`, batch size 64, `normalize_embeddings=True`
- [ ] `src/research_rag/embeddings/store.py`: open a connection, `register_vector(conn)`, bulk insert with `ON CONFLICT (content_hash) DO NOTHING`
- [ ] Extend `ingestion/run.py`: load → clean → chunk → embed → store
- [ ] Sanity query in `psql`: the 3 chunks closest to the first chunk's embedding should be from the same paper
- [ ] `tests/test_store.py`: inserting the same chunks twice leaves the row count unchanged

## Done when

`make up` plus one ingestion command fills the table, and running it again doesn't change `SELECT count(*) FROM document_chunks`.
