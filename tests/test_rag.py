from research_rag import rag
from research_rag.generation.prompts import NO_ANSWER
from research_rag.retrieval.search import RetrievedChunk

FAKE_CHUNK = RetrievedChunk(
    id="lora.pdf::0021",
    source="lora.pdf",
    page_number=4,
    text="LoRA adds no latency.",
    similarity=0.6,
)


def fake_search(question, k):
    return [FAKE_CHUNK]


def test_answer_with_citation(monkeypatch):
    def fake_generate(prompt):
        return "No, it adds no latency [1]."

    monkeypatch.setattr(rag, "search", fake_search)
    monkeypatch.setattr(rag, "generate", fake_generate)

    result = rag.answer("Does LoRA add latency?")
    assert result.answered is True
    assert result.citations[0].page_number == 4


def test_answer_detects_i_dont_know(monkeypatch):
    def fake_generate(prompt):
        return NO_ANSWER

    monkeypatch.setattr(rag, "search", fake_search)
    monkeypatch.setattr(rag, "generate", fake_generate)

    result = rag.answer("Banana bread?")
    assert result.answered is False
    assert result.citations == []
