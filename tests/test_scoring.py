import datetime
import math

import pytest
from freezegun import freeze_time

from app.scoring import repo_scoring_algo


class TestRepoScoringAlgo:

    @freeze_time("2026-04-05T12:00:00Z")
    def test_returns_float(self):
        result = repo_scoring_algo(1000, 500, "2025-01-01T00:00:00Z")
        assert isinstance(result, float)

    @freeze_time("2026-04-05T12:00:00Z")
    def test_more_stars_higher_score(self):
        score_high = repo_scoring_algo(10000, 500, "2025-01-01T00:00:00Z")
        score_low = repo_scoring_algo(1000, 500, "2025-01-01T00:00:00Z")
        assert score_high > score_low

    @freeze_time("2026-04-05T12:00:00Z")
    def test_more_forks_higher_score(self):
        score_high = repo_scoring_algo(1000, 5000, "2025-01-01T00:00:00Z")
        score_low = repo_scoring_algo(1000, 500, "2025-01-01T00:00:00Z")
        assert score_high > score_low

    @freeze_time("2026-04-05T12:00:00Z")
    def test_zero_stars_and_forks_does_not_crash(self):
        result = repo_scoring_algo(0, 0, "2025-01-01T00:00:00Z")
        assert isinstance(result, float)
        assert result >= 0

    @freeze_time("2026-04-05T12:00:00Z")
    def test_recently_pushed_higher_score_than_old(self):
        score_recent = repo_scoring_algo(1000, 500, "2026-04-04T00:00:00Z")
        score_old = repo_scoring_algo(1000, 500, "2020-01-01T00:00:00Z")
        assert score_recent > score_old

    @freeze_time("2026-04-05T12:00:00Z")
    def test_score_calculation(self):
        pushed_at = "2025-01-01T00:00:00+00:00"
        now = datetime.datetime(
            2026, 4, 5, 12, 0, 0, tzinfo=datetime.timezone.utc
        )
        pushed = datetime.datetime.fromisoformat(pushed_at)
        days_since_push = (now - pushed).days
        expected_recency = 1 / (1 + days_since_push)
        expected_score = (
            math.log1p(1000) * 0.5
            + math.log1p(500) * 0.3
            + expected_recency * 0.2
        )
        result = repo_scoring_algo(1000, 500, pushed_at)
        assert result == pytest.approx(expected_score)
