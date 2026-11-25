"""Score retrieval on the golden dataset. No LLM is involved."""

from datetime import datetime

from pydantic import BaseModel

from research_rag.config import get_settings
from research_rag.evals.dataset import load_golden
from research_rag.evals.metrics import recall_at_k, reciprocal_rank
from research_rag.paths import EVALS_DIR
from research_rag.retrieval.search import search

RESULTS_DIR = EVALS_DIR / "results"
K_VALUES = [1, 3, 5, 10]
MAX_K = 10


class QuestionResult(BaseModel):
    id: str
    type: str
    question: str
    relevant_chunk_ids: list[str]
    retrieved_chunk_ids: list[str]
    first_relevant_position: int | None
    recall: dict[int, float]
    reciprocal_rank: float


class RetrievalReport(BaseModel):
    run_at: str
    config: dict[str, str | int]
    question_count: int
    recall: dict[int, float]
    mrr: float
    questions: list[QuestionResult]


def find_first_position(retrieved: list[str], relevant: list[str]) -> int | None:
    for position, chunk_id in enumerate(retrieved, start=1):
        if chunk_id in relevant:
            return position
    return None


def score_question(item) -> QuestionResult:
    results = search(item.question, k=MAX_K)
    retrieved = []
    for result in results:
        retrieved.append(result.id)

    recall = {}
    for k in K_VALUES:
        recall[k] = recall_at_k(retrieved, item.relevant_chunk_ids, k)

    return QuestionResult(
        id=item.id,
        type=item.type,
        question=item.question,
        relevant_chunk_ids=item.relevant_chunk_ids,
        retrieved_chunk_ids=retrieved,
        first_relevant_position=find_first_position(retrieved, item.relevant_chunk_ids),
        recall=recall,
        reciprocal_rank=reciprocal_rank(retrieved, item.relevant_chunk_ids),
    )


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 3)


def run() -> RetrievalReport:
    settings = get_settings()
    answerable = []
    for item in load_golden():
        if item.relevant_chunk_ids:
            answerable.append(item)

    question_results = []
    for item in answerable:
        question_results.append(score_question(item))

    recall = {}
    for k in K_VALUES:
        scores = []
        for result in question_results:
            scores.append(result.recall[k])
        recall[k] = average(scores)

    rr_scores = []
    for result in question_results:
        rr_scores.append(result.reciprocal_rank)

    return RetrievalReport(
        run_at=datetime.now().isoformat(timespec="seconds"),
        config={
            "embedding_model": settings.embedding_model,
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "max_k": MAX_K,
            "search": "vector",
        },
        question_count=len(question_results),
        recall=recall,
        mrr=average(rr_scores),
        questions=question_results,
    )


def save(report: RetrievalReport) -> str:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{report.run_at[:10]}_retrieval.json"
    path.write_text(report.model_dump_json(indent=2) + "\n")
    return str(path)


def print_summary(report: RetrievalReport) -> None:
    print(f"{'id':<6} {'type':<12} {'first hit':>9}  question")
    for result in report.questions:
        position = result.first_relevant_position
        hit = f"#{position}" if position else "miss"
        print(f"{result.id:<6} {result.type:<12} {hit:>9}  {result.question[:60]}")
    print()
    for k, value in report.recall.items():
        print(f"recall@{k:<3} {value:.2f}")
    print(f"MRR        {report.mrr:.2f}")


def main() -> None:
    report = run()
    print_summary(report)
    print(f"\nSaved to {save(report)}")


if __name__ == "__main__":
    main()
