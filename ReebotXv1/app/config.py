"""Application configuration — reads from .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the RebootX application.

    All values can be overridden via environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "RebootX"
    app_version: str = "0.1.0"

    # Ollama LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    use_ollama: bool = True

    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"

    # Knowledge Base
    knowledge_dir: str = "./knowledge"


settings = Settings()
