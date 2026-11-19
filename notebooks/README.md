# Notebooks

Experiments and learning notebooks, organized like the course: one folder per week and per day.
Product code lives in `src/research_rag/`; notebooks import from it.

```
notebooks/
  LEARNINGS.md                    learning log (3 lines per day)
  week-1/
    day-01-llm-fundamentals/      01_fundamentals.ipynb
    day-02-ingestion-chunking/    02_ingestion.ipynb
    ...
  week-2/
    ...
```

**Finding project files from a notebook:** don't use relative paths like `../data/papers`, which break at different folder depths. Use:

```python
from research_rag.paths import PAPERS_DIR, PROJECT_ROOT
```

Each notebook uses the `.venv` kernel.
