from research_rag.evals import judge
from research_rag.evals.judge import Claim, FaithfulnessVerdict


def test_faithfulness_score_is_share_of_supported_claims():
    verdict = FaithfulnessVerdict(
        claims=[Claim(claim="a", supported=True), Claim(claim="b", supported=False)]
    )
    assert verdict.score() == 0.5


def test_no_claims_gives_no_score():
    assert FaithfulnessVerdict(claims=[]).score() is None


def test_judge_parses_valid_json(monkeypatch):
    def fake_generate(prompt, temperature, json_format):
        return '{"score": 4, "reason": "mostly answers it"}'

    monkeypatch.setattr(judge, "generate", fake_generate)
    verdict = judge.judge_relevance("Q?", "A.")
    assert verdict.score == 4


def test_judge_retries_then_gives_up(monkeypatch):
    calls = []

    def fake_generate(prompt, temperature, json_format):
        calls.append(temperature)
        return '{"score": 9}'  # out of range and missing "reason" → invalid every time

    monkeypatch.setattr(judge, "generate", fake_generate)
    assert judge.judge_relevance("Q?", "A.") is None  # judge_error, not a crash
    assert calls == [0, 0.3]  # tried twice, and the retry used a higher temperature


def test_judge_recovers_on_retry(monkeypatch):
    replies = ["not json at all", '{"score": 2, "reason": "partly"}']

    def fake_generate(prompt, temperature, json_format):
        return replies.pop(0)

    monkeypatch.setattr(judge, "generate", fake_generate)
    assert judge.judge_relevance("Q?", "A.").score == 2


def test_refusal_is_not_sent_to_the_judge(monkeypatch):
    def fake_generate(prompt, temperature, json_format):
        raise AssertionError("the judge should not be called for a refusal")

    monkeypatch.setattr(judge, "generate", fake_generate)
    verdict = judge.judge_faithfulness("I don't know based on the provided papers.", [])
    assert verdict.score() is None
