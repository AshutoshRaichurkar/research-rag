"""Central settings, loaded from environment variables or a .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://rag:rag@localhost:5432/research_rag"

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.1:8b"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    chunk_size: int = 200  # all-MiniLM-L6-v2 reads at most 256 of its tokens
    chunk_overlap: int = 40

    papers_dir: str = "data/papers"


@lru_cache
def get_settings() -> Settings:
    return Settings()
