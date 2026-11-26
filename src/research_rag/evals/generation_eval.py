"""Score the full RAG answers on the golden dataset, using the LLM judge."""

import statistics
from datetime import datetime

from pydantic import BaseModel

from research_rag.config import get_settings
from research_rag.evals.dataset import load_golden
from research_rag.evals.judge import JUDGE_VERSION, judge_faithfulness, judge_relevance
from research_rag.evals.retrieval_eval import RESULTS_DIR
from research_rag.generation.prompts import PROMPT_VERSION
from research_rag.rag import answer

K = 5
NO_ANSWER_TYPES = {"unanswerable", "adversarial"}


class AnswerResult(BaseModel):
    id: str
    type: str
    question: str
    answer: str
    answered: bool
    should_answer: bool
    faithfulness: float | None = None  # None: refused, no claims, or judge error
    claims: list[str] = []  # each claim with ✅/❌, for reading by hand
    relevance: int | None = None
    relevance_reason: str | None = None
    judge_error: bool = False
    latency_ms: int


class GenerationReport(BaseModel):
    run_at: str
    config: dict[str, str | int]
    faithfulness: float | None
    relevance: float | None
    abstention_accuracy: float
    false_refusal_rate: float
    judge_errors: int
    latency_p50_ms: int
    answers: list[AnswerResult]


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def score_item(item) -> AnswerResult:
    result = answer(item.question, k=K)
    should_answer = item.type not in NO_ANSWER_TYPES
    scored = AnswerResult(
        id=item.id,
        type=item.type,
        question=item.question,
        answer=result.text,
        answered=result.answered,
        should_answer=should_answer,
        latency_ms=result.latency_ms,
    )
    if not (should_answer and result.answered):
        return scored  # nothing to fact-check or grade for relevance

    faithfulness = judge_faithfulness(result.text, result.chunks)
    relevance = judge_relevance(item.question, result.text)
    if faithfulness is None or relevance is None:
        scored.judge_error = True
    if faithfulness is not None:
        scored.faithfulness = faithfulness.score()
        for claim in faithfulness.claims:
            mark = "✅" if claim.supported else "❌"
            scored.claims.append(f"{mark} {claim.claim}")
    if relevance is not None:
        scored.relevance = relevance.score
        scored.relevance_reason = relevance.reason
    return scored


def run() -> GenerationReport:
    settings = get_settings()
    answers = []
    for item in load_golden():
        print(f"  {item.id} ...", flush=True)  # progress: this takes a few minutes
        answers.append(score_item(item))

    faithfulness_scores = []
    relevance_scores = []
    correct_abstentions = 0
    no_answer_count = 0
    false_refusals = 0
    answerable_count = 0
    judge_errors = 0
    latencies = []
    for result in answers:
        latencies.append(result.latency_ms)
        if result.judge_error:
            judge_errors += 1
        if result.should_answer:
            answerable_count += 1
            if not result.answered:
                false_refusals += 1
            if result.faithfulness is not None:
                faithfulness_scores.append(result.faithfulness)
            if result.relevance is not None:
                relevance_scores.append(result.relevance)
        else:
            no_answer_count += 1
            if not result.answered:
                correct_abstentions += 1

    return GenerationReport(
        run_at=datetime.now().isoformat(timespec="seconds"),
        config={
            "llm_model": settings.llm_model,
            "embedding_model": settings.embedding_model,
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "k": K,
            "prompt_version": PROMPT_VERSION,
            "judge_version": JUDGE_VERSION,
        },
        faithfulness=mean_or_none(faithfulness_scores),
        relevance=mean_or_none(relevance_scores),
        abstention_accuracy=round(correct_abstentions / no_answer_count, 3),
        false_refusal_rate=round(false_refusals / answerable_count, 3),
        judge_errors=judge_errors,
        latency_p50_ms=int(statistics.median(latencies)),
        answers=answers,
    )


def save(report: GenerationReport) -> str:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{report.run_at[:10]}_generation.json"
    path.write_text(report.model_dump_json(indent=2) + "\n")
    return str(path)


def print_summary(report: GenerationReport) -> None:
    print(f"\n{'id':<6} {'type':<12} {'answered':<9} {'faith':>5} {'rel':>4}  question")
    for result in report.answers:
        faith = "-" if result.faithfulness is None else f"{result.faithfulness:.2f}"
        rel = "-" if result.relevance is None else str(result.relevance)
        answered = "yes" if result.answered else "refused"
        print(
            f"{result.id:<6} {result.type:<12} {answered:<9} {faith:>5} {rel:>4}"
            f"  {result.question[:50]}"
        )
    print()
    print(f"faithfulness         {report.faithfulness}")
    print(f"relevance (1-5)      {report.relevance}")
    print(f"abstention accuracy  {report.abstention_accuracy}")
    print(f"false refusal rate   {report.false_refusal_rate}")
    print(f"judge errors         {report.judge_errors}")
    print(f"latency p50          {report.latency_p50_ms} ms")


def main() -> None:
    report = run()
    print_summary(report)
    print(f"\nSaved to {save(report)}")


if __name__ == "__main__":
    main()
