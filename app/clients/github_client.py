import datetime

import httpx
from async_lru import alru_cache

from app.core.config import settings
from app.core.logger import get_logger
from app.schemas.repos_schema import GithubClientReposAPIResponse

logger = get_logger(__name__)


@alru_cache(maxsize=100)
async def fetch(
    language: str, created_date: datetime.datetime, page: int, per_page: int
) -> GithubClientReposAPIResponse:
    logger.info(
        "Fetching repos from GitHub: language=%s "
        "created_after=%s page=%d per_page=%d",
        language,
        created_date.date().isoformat(),
        page,
        per_page,
    )
    async with httpx.AsyncClient(timeout=10) as client:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": settings.GITHUB_API_VERSION,
        }
        if settings.GITHUB_PAT:
            headers["Authorization"] = settings.GITHUB_PAT
        try:
            response = await client.get(
                settings.GITHUB_REPO_SEARCH_URL,
                headers=headers,
                params={
                    "q": f"language:{language} "
                    f"created:>{created_date.date().isoformat()}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": per_page,
                    "page": page,
                },
            )
        except httpx.RequestError as e:
            logger.error("Network error contacting GitHub API: %s", str(e))
            raise

        response.raise_for_status()
        result = GithubClientReposAPIResponse(**response.json())
        logger.info("GitHub API returned %d total results", result.total_count)
        return result
