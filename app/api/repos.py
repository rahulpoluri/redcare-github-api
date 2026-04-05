import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.logger import get_logger
from app.schemas.repos_schema import ReposAPIResponseSchema
from app.services.repo_service import get_popular_repos

logger = get_logger(__name__)

router = APIRouter(
    prefix="/github",
    tags=["Github"],
    responses={404: {"description": "Not found"}},
)


def parse_created_date(
    created_date: str = Query(
        default="2022-03-04", description="Format: YYYY-MM-DD"
    )
) -> datetime.datetime:
    try:
        parsed = datetime.datetime.strptime(created_date, "%Y-%m-%d")
    except ValueError as e:
        raise HTTPException(422, "Invalid date format. Use YYYY-MM-DD") from e
    if parsed > datetime.datetime.now():
        raise HTTPException(422, "Given date is greater than current datetime")
    return parsed


@router.get("/repos", response_model=ReposAPIResponseSchema)
async def get_popular_github_repos(
    language: str = Query(
        default="python",
        min_length=1,
        max_length=50,
        description="Programming language filter (e.g. python, javascript)",
    ),
    created_date: datetime.datetime = Depends(parse_created_date),
    page: int = Query(default=1, ge=1, le=10000, description="Page number"),
    per_page: int = Query(
        default=10, ge=1, le=100, description="Results per page"
    ),
):
    logger.info(
        "GET /repos request: language=%s created_date=%s page=%d per_page=%d",
        language,
        created_date.date().isoformat(),
        page,
        per_page,
    )
    try:
        return await get_popular_repos(
            language.lower(), created_date, page, per_page
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (429, 403):
            retry_after = e.response.headers.get("retry-after", "60")
            logger.warning(
                "Error (429, 403): GitHub rate limit hit. "
                "Retry after %s seconds",
                retry_after,
            )
            raise HTTPException(
                429, f"Rate limit exceeded. Retry after {retry_after} seconds"
            ) from e
        raise HTTPException(e.response.status_code, "GitHub API error") from e
    except httpx.RequestError as e:
        logger.warning("Error 503: Could not reach GitHub API")
        raise HTTPException(503, "Could not reach GitHub API") from e
