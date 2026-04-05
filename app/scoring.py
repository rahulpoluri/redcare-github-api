import datetime
import math


def repo_scoring_algo(
    stargazers_count: int, forks_count: int, pushed_at: str
) -> float:
    now = datetime.datetime.now(datetime.timezone.utc)
    pushed = datetime.datetime.fromisoformat(pushed_at)
    days_since_push = (now - pushed).days

    recency_score = 1 / (
        1 + days_since_push
    )  # 1.0 = today, approaches 0 for old repos

    score = (
        math.log1p(stargazers_count) * 0.5
        + math.log1p(forks_count) * 0.3
        + recency_score * 0.2
    )
    return score
