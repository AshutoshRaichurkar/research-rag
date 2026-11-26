"""LLM-as-judge: grade one answer for faithfulness and relevance.

Every function returns None if the judge fails, so one bad grade never crashes an eval run.
"""

from pydantic import BaseModel, Field, ValidationError

from research_rag.generation.llm import LLMError, generate
from research_rag.generation.prompts import NO_ANSWER, format_context
from research_rag.retrieval.search import RetrievedChunk

JUDGE_VERSION = "v2"  # v1 took claims from the context instead of the answer

FAITHFULNESS_PROMPT = """You are a strict fact-checker.
Below are an ANSWER written by an assistant and the CONTEXT the assistant was given.
List the factual claims made in the ANSWER, and for each one decide whether the CONTEXT supports it.

Rules:
- Take claims ONLY from the text between <answer> and </answer>, never from the context.
- If the answer makes no factual claims (for example, it says it doesn't know),
  return {{"claims": []}}.
- Ignore citation markers like [1]. Do not use outside knowledge.

Return only JSON in this shape:
{{"claims": [{{"claim": "...", "supported": true}}]}}

<answer>
{answer}
</answer>

<context>
{context}
</context>
"""

RELEVANCE_PROMPT = """You are grading whether an ANSWER addresses a QUESTION.
Do not judge whether it is true, only whether it answers what was asked.
5 = fully answers the question
3 = partly answers it
1 = does not answer it (off-topic, or says it doesn't know)

Return only JSON in this shape:
{{"score": 3, "reason": "one short sentence"}}

QUESTION: {question}
ANSWER: {answer}
"""


class Claim(BaseModel):
    claim: str
    supported: bool


class FaithfulnessVerdict(BaseModel):
    claims: list[Claim]

    def score(self) -> float | None:
        """Share of claims the context supports. None if there were no claims."""
        if not self.claims:
            return None
        supported = 0
        for claim in self.claims:
            if claim.supported:
                supported += 1
        return supported / len(self.claims)


class RelevanceVerdict(BaseModel):
    score: int = Field(ge=1, le=5)
    reason: str


def ask_judge(prompt: str, verdict_class: type[BaseModel], retries: int = 1) -> BaseModel | None:
    """Ask the LLM, parse its JSON into verdict_class. Retry once, then give up (None)."""
    for attempt in range(retries + 1):
        temperature = 0 if attempt == 0 else 0.3  # a retry at temperature 0 would repeat itself
        try:
            raw = generate(prompt, temperature=temperature, json_format=True)
            return verdict_class.model_validate_json(raw)
        except (ValidationError, LLMError):
            continue
    return None


def judge_faithfulness(answer: str, chunks: list[RetrievedChunk]) -> FaithfulnessVerdict | None:
    if NO_ANSWER.lower() in answer.lower():
        # A refusal makes no claims. Decide this in code: the judge counted
        # "I don't know" itself as a supported claim.
        return FaithfulnessVerdict(claims=[])
    prompt = FAITHFULNESS_PROMPT.format(context=format_context(chunks), answer=answer)
    return ask_judge(prompt, FaithfulnessVerdict)


def judge_relevance(question: str, answer: str) -> RelevanceVerdict | None:
    prompt = RELEVANCE_PROMPT.format(question=question, answer=answer)
    return ask_judge(prompt, RelevanceVerdict)
