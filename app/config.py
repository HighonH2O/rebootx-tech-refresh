"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "RebootX"
    app_version: str = "0.1.0"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    chroma_persist_dir: str = "./data/chroma"
    use_ollama: bool = True
    knowledge_dir: str = "./knowledge"


settings = Settings()
