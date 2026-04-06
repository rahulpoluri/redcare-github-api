from unittest.mock import MagicMock, patch

import httpx

from app.schemas.examples import (
    EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE,
    EXAMPLE_FOR_REPO_API_RESPONSE,
)
from app.schemas.repos_schema import GithubClientReposAPIResponse


class TestReposEndpoint:
    Endpoint = "get_popular_github_repos"

    def test_get_popular_github_repos_return_200(self, client, app_main):
        language = "python"
        created_date = "2022-05-06"
        page = 1
        per_page = 10
        with patch(
            "app.services.repo_service.fetch",
            return_value=GithubClientReposAPIResponse(
                **EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
            ),
        ) as fetch_call:
            with patch(
                "app.services.repo_service.repo_scoring_algo",
                side_effect=[9.09, 8],
            ) as scoring_call:
                response = client.get(
                    f"{app_main.url_path_for(self.Endpoint)}?"
                    f"language={language}&"
                    f"created_date={created_date}&"
                    f"page={page}&"
                    f"per_page={per_page}"
                )
                assert response.status_code == 200
                assert response.json() == EXAMPLE_FOR_REPO_API_RESPONSE
                fetch_call.assert_called_once()
                scoring_call.assert_called()

    def test_invalid_date_format_returns_422(self, client, app_main):
        response = client.get(
            f"{app_main.url_path_for(self.Endpoint)}?"
            "language=python&created_date=not-a-date"
        )
        assert response.status_code == 422

    def test_future_date_returns_422(self, client, app_main):
        response = client.get(
            f"{app_main.url_path_for(self.Endpoint)}?"
            "language=python&created_date=2099-01-01"
        )
        assert response.status_code == 422

    def test_page_below_min_returns_422(self, client, app_main):
        response = client.get(
            f"{app_main.url_path_for(self.Endpoint)}?"
            "language=python&created_date=2022-05-06&page=0"
        )
        assert response.status_code == 422

    def test_per_page_above_max_returns_422(self, client, app_main):
        response = client.get(
            f"{app_main.url_path_for(self.Endpoint)}?"
            "language=python&created_date=2022-05-06&per_page=101"
        )
        assert response.status_code == 422

    def test_language_empty_returns_422(self, client, app_main):
        response = client.get(
            f"{app_main.url_path_for(self.Endpoint)}?"
            "language=&created_date=2022-05-06"
        )
        assert response.status_code == 422

    def test_rate_limit_returns_429(self, client, app_main):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "30"}
        with patch(
            "app.services.repo_service.fetch",
            side_effect=httpx.HTTPStatusError(
                "rate limit", request=MagicMock(), response=mock_response
            ),
        ):
            response = client.get(
                f"{app_main.url_path_for(self.Endpoint)}?"
                "language=python&created_date=2022-05-06"
            )
        assert response.status_code == 429

    def test_network_error_returns_503(self, client, app_main):
        with patch(
            "app.services.repo_service.fetch",
            side_effect=httpx.RequestError("connection failed"),
        ):
            response = client.get(
                f"{app_main.url_path_for(self.Endpoint)}?"
                "language=python&created_date=2022-05-06"
            )
        assert response.status_code == 503
