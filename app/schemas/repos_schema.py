import json
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.examples import (
    EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE,
    EXAMPLE_FOR_REPO_API_RESPONSE,
)


class ReposAPIResponseSchemaItems(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": json.dumps(EXAMPLE_FOR_REPO_API_RESPONSE)
        },
    )
    full_name: str
    html_url: str
    description: str | None
    language: str | None
    created_at: str
    open_issues_count: int
    archived: bool

    repo_score: float


class ReposAPIResponseSchema(BaseModel):
    total_count: int
    page: int
    per_page: int
    results: List[ReposAPIResponseSchemaItems]


# Github Client Schemas
class GithubClientReposAPIResponseItems(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": json.dumps(EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE)
        },
    )
    full_name: str
    html_url: str
    description: str | None
    language: str | None
    created_at: str
    open_issues_count: int
    archived: bool

    stargazers_count: int
    forks_count: int
    pushed_at: str


class GithubClientReposAPIResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    total_count: int
    items: List[GithubClientReposAPIResponseItems]
