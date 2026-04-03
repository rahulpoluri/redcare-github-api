from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    GITHUB_REPO_SEARCH_URL: str = "https://api.github.com/search/repositories"
    GITHUB_PAT: str = ""  # from .env
    GITHUB_API_VERSION: str = "2026-03-10"


@lru_cache(maxsize=1)
def get_settings():
    return Settings()


settings = get_settings()
