import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.clients.github_client import fetch
from app.schemas.examples import EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE


@pytest.mark.asyncio
class TestGithubClient:

    async def test_fetch_returns_valid_response(self):
        mock_response = MagicMock()
        mock_response.json.return_value = EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            result = await fetch(
                "python", datetime.datetime.fromisoformat("2022-03-01"), 1, 10
            )

        assert result is not None
        assert len(result.items) > 0
        mock_client.assert_called_once()

    async def test_fetch_raises_on_http_error(self):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401", request=MagicMock(), response=MagicMock()
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            with pytest.raises(httpx.HTTPStatusError):
                await fetch(
                    "python",
                    datetime.datetime.fromisoformat("2022-03-01"),
                    1,
                    10,
                )

    async def test_fetch_raises_on_network_error(self):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.RequestError("network error")
            )
            with pytest.raises(httpx.RequestError):
                await fetch(
                    "python",
                    datetime.datetime.fromisoformat("2022-03-01"),
                    1,
                    10,
                )

    async def test_includes_auth_header_when_pat_set(self):
        mock_response = MagicMock()
        mock_response.json.return_value = EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch("app.clients.github_client.settings") as mock_settings:
            mock_settings.GITHUB_PAT = "Bearer test-token"
            mock_settings.GITHUB_API_VERSION = "2022-11-28"
            mock_settings.GITHUB_REPO_SEARCH_URL = (
                "https://api.github.com/search/repositories"
            )
            with patch("httpx.AsyncClient") as mock_client:
                mock_get = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.get = mock_get
                await fetch(
                    "python",
                    datetime.datetime.fromisoformat("2022-03-01"),
                    1,
                    10,
                )
            headers_sent = mock_get.call_args[1]["headers"]
            assert "Authorization" in headers_sent
            assert headers_sent["Authorization"] == "Bearer test-token"

    async def test_excludes_auth_header_when_pat_empty(self):
        mock_response = MagicMock()
        mock_response.json.return_value = EXAMPLE_FOR_GITHUB_CLIENT_RESPONSE
        mock_response.raise_for_status = MagicMock()

        with patch("app.clients.github_client.settings") as mock_settings:
            mock_settings.GITHUB_PAT = ""
            mock_settings.GITHUB_API_VERSION = "2022-11-28"
            mock_settings.GITHUB_REPO_SEARCH_URL = (
                "https://api.github.com/search/repositories"
            )
            with patch("httpx.AsyncClient") as mock_client:
                mock_get = AsyncMock(return_value=mock_response)
                mock_client.return_value.__aenter__.return_value.get = mock_get
                await fetch(
                    "python",
                    datetime.datetime.fromisoformat("2022-03-01"),
                    1,
                    10,
                )
            headers_sent = mock_get.call_args[1]["headers"]
            assert "Authorization" not in headers_sent
