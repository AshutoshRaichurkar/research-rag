from research_rag.config import Settings


def test_defaults_are_sane():
    s = Settings(_env_file=None)
    assert s.chunk_overlap < s.chunk_size
    assert s.embedding_dim == 384


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("CHUNK_SIZE", "256")
    assert Settings(_env_file=None).chunk_size == 256
