import datetime

from app.clients.github_client import fetch
from app.core.logger import get_logger
from app.schemas.repos_schema import (
    ReposAPIResponseSchema,
    ReposAPIResponseSchemaItems,
)
from app.scoring import repo_scoring_algo

logger = get_logger(__name__)


async def get_popular_repos(
    language: str, created_date: datetime.datetime, page: int, per_page: int
) -> ReposAPIResponseSchema:
    repos = await fetch(language, created_date, page, per_page)
    response = []
    logger.info("Scoring %d repos for language=%s", len(repos.items), language)
    for repo in repos.items:
        repo_score = repo_scoring_algo(
            repo.stargazers_count, repo.forks_count, repo.pushed_at
        )
        response.append(
            ReposAPIResponseSchemaItems(
                **{**repo.model_dump(), **{"repo_score": repo_score}}
            )
        )
    sorted_items = sorted(response, key=lambda x: x.repo_score, reverse=True)
    logger.info("Returning %d scored and sorted repos", len(sorted_items))
    return ReposAPIResponseSchema(
        **{
            "total_count": repos.total_count,
            "page": page,
            "per_page": per_page,
            "results": sorted_items,
        }
    )
