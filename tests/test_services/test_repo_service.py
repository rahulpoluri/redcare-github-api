import datetime
from unittest.mock import AsyncMock, patch

from app.schemas.examples import EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
from app.schemas.repos_schema import (
    GithubClientReposAPIResponse,
    ReposAPIResponseSchema,
)
from app.services.repo_service import get_popular_repos


class TestRepoService:

    async def test_returns_correct_schema(self):
        with patch(
            "app.services.repo_service.fetch",
            new_callable=AsyncMock,
            return_value=GithubClientReposAPIResponse(
                **EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
            ),
        ):
            with patch(
                "app.services.repo_service.repo_scoring_algo",
                return_value=10.0,
            ):
                result = await get_popular_repos(
                    "python",
                    datetime.datetime.fromisoformat("2022-03-01"),
                    1,
                    10,
                )
        assert isinstance(result, ReposAPIResponseSchema)

    async def test_fetch_called_with_correct_params(self):
        language = "python"
        created_date = datetime.datetime.fromisoformat("2022-03-01")
        page = 1
        per_page = 10
        with patch(
            "app.services.repo_service.fetch",
            new_callable=AsyncMock,
            return_value=GithubClientReposAPIResponse(
                **EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
            ),
        ) as mock_fetch:
            with patch(
                "app.services.repo_service.repo_scoring_algo",
                return_value=10.0,
            ):
                await get_popular_repos(language, created_date, page, per_page)
        mock_fetch.assert_called_once_with(
            language, created_date, page, per_page
        )

    async def test_scoring_applied_to_each_repo(self):
        language = "python"
        created_date = datetime.datetime.fromisoformat("2022-03-01")
        page = 1
        per_page = 10
        with patch(
            "app.services.repo_service.fetch",
            new_callable=AsyncMock,
            return_value=GithubClientReposAPIResponse(
                **EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
            ),
        ):
            with patch(
                "app.services.repo_service.repo_scoring_algo",
                return_value=10.0,
            ) as mock_scoring:
                await get_popular_repos(language, created_date, page, per_page)
        expected_calls = len(
            GithubClientReposAPIResponse(
                **EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
            ).items
        )
        assert mock_scoring.call_count == expected_calls

    async def test_empty_github_results_returns_empty_list(self):
        with patch(
            "app.services.repo_service.fetch",
            new_callable=AsyncMock,
            return_value=GithubClientReposAPIResponse(total_count=0, items=[]),
        ):
            result = await get_popular_repos(
                "python",
                datetime.datetime.fromisoformat("2022-03-01"),
                1,
                10,
            )
        assert result.results == []
        assert result.total_count == 0

    async def test_results_sorted_by_score_descending(self):
        language = "python"
        created_date = datetime.datetime.fromisoformat("2022-03-01")
        page = 1
        per_page = 10
        scores = [5.0, 15.0, 10.0]
        with patch(
            "app.services.repo_service.fetch",
            new_callable=AsyncMock,
            return_value=GithubClientReposAPIResponse(
                **EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
            ),
        ):
            with patch(
                "app.services.repo_service.repo_scoring_algo",
                side_effect=scores,
            ):
                result = await get_popular_repos(
                    language, created_date, page, per_page
                )
        repo_scores = [r.repo_score for r in result.results]
        assert repo_scores == sorted(repo_scores, reverse=True)
