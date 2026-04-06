# redcare-github-api
 
A backend API for searching and scoring popular GitHub repositories by language and creation date.

## Getting Started
 
### Prerequisites
- Python 3.14
- A GitHub Personal Access Token (optional — unauthenticated requests are allowed but rate-limited to 10 req/min)
 
### Local Setup
 
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
 
Create a `.env` file (see `.env.example`):
```
GITHUB_PAT=your_token_here
```
 
Run the app:
```bash
uvicorn app.main:app --reload
```
 
### Docker
 
```bash
docker build -t redcare-github-api .
docker run -p 8000:8000 -e GITHUB_PAT="Bearer your_token_here" redcare-github-api
```
 
## API
 
Base URL: `/api/v1`
 
### `GET /api/v1/github/repos`
 
Returns GitHub repositories scored by popularity.
 
**Query Parameters:**
 
| Parameter | Type | Default | Description |
|---|---|---|---|
| `language` | string | `python` | Programming language filter |
| `created_date` | string | `2022-03-04` | Earliest creation date (YYYY-MM-DD) |
| `page` | int | `1` | Page number (min: 1) |
| `per_page` | int | `10` | Results per page (min: 1, max: 100) |
 
**Example Request:**
```
GET /api/v1/github/repos?language=python&created_date=2022-01-01&page=1&per_page=10
```
 
**Example Response:**
```json
{
  "total_count": 60647,
  "page": 1,
  "per_page": 10,
  "results": [
    {
      "full_name": "Comfy-Org/ComfyUI",
      "html_url": "https://github.com/Comfy-Org/ComfyUI",
      "description": "The most powerful and modular diffusion model GUI",
      "language": "Python",
      "created_at": "2023-01-17T03:15:56Z",
      "open_issues_count": 3928,
      "archived": false,
      "repo_score": 9.09
    }
  ]
}
```
 
### `GET /health`
 
Returns API health status.
 
## Design Decisions
 
### Scoring Algorithm
 
Each repository is scored using three signals:
 
```
score = log1p(stars) * 0.5  log1p(forks) * 0.3  recency_score * 0.2
```
 
- **Stars (50%)** - primary indicator of community interest
- **Forks (30%)** - indicates active usage and contribution
- **Recency (20%)** - `1 / (1  days_since_last_push)` - score of 1.0 for today, approaches 0 for old repos
 
**Why `log1p`?** Stars and forks span several orders of magnitude (10 to 500,000). Without normalisation, high-star repos dominate completely. `log1p` compresses the scale so recency and forks still meaningfully contribute to the final score.
 
**Why these weights?** Stars are the most universal signal of popularity. Forks indicate real usage. Recency prevents stale but historically popular repos from outranking actively maintained ones.
 
### Caching
 
Results are cached using `alru_cache` (async-compatible LRU cache) keyed on `(language, created_date, page, per_page)`. This avoids redundant GitHub API calls for identical queries.
 
**Known limitation:** `alru_cache` has no TTL — cached results never expire and can become stale. In production, Redis with a TTL (e.g. 5 minutes) would be the right choice, enabling shared cache across multiple instances and automatic expiry.
 
### Rate Limit Handling
 
The GitHub Search API allows 30 requests/minute (authenticated) or 10/minute (unauthenticated). The API handles GitHub's rate limit responses:
 
- **429 / 403** — returns a `429` with the `Retry-After` value from GitHub's response headers
- **Network errors** — returns `503 Service Unavailable`
 
In production, a retry mechanism with exponential backoff (e.g. `tenacity`) would be added.
 
### Authentication
 
The GitHub PAT is optional. If not set, requests are made unauthenticated (lower rate limit). The `Authorization` header is conditionally included only when `GITHUB_PAT` is configured.
 
### Pagination
 
GitHub's search API supports pagination via `page` and `per_page`. Both are exposed as query parameters with sensible defaults (`page=1`, `per_page=10`) and validation (`per_page` max 100 per GitHub's limit). The response includes `total_count` so callers know how many pages exist.
 
### API Versioning
 
All endpoints are prefixed with `/api/v1` to allow future breaking changes without affecting existing consumers.
 
### CORS
 
CORS is configured with `allow_origins=["*"]` to allow any frontend to consume the API. In production this should be restricted to known origins.
 
### Docker
 
The container runs as a non-root user (`appuser`) to follow security best practices. Dependencies are installed before copying application code to take advantage of Docker layer caching.
 
## Project Structure
 
```
app/
  api/          # FastAPI routers and endpoint definitions
  clients/      # External API clients (GitHub)
  core/         # Config, logger
  schemas/      # Pydantic request/response models and examples
  services/     # Business logic layer
  scoring.py    # Popularity scoring algorithm
  main.py       # FastAPI app entrypoint
tests/
  test_api/
  test_clients/
  test_services/
  test_scoring.py
  test_main.py
```
 
## Testing
 
```bash
pip install -r requirements-dev.txt
pytest
```
 
All tests are fully mocked — no real GitHub API calls are made during testing.
 
```bash
# Linting
ruff check app/
black --check app/
isort --check-only app/
 
# Type checking
mypy .
```
 
## Known Production Gaps
 
- **Cache TTL** — replace `alru_cache` with Redis  TTL for shared, expiring cache
- **Retry logic** — add exponential backoff for transient GitHub API failures
- **CORS** — restrict `allow_origins` to known domains
- **Structured logging** — replace basic logging with structured JSON logs for log aggregation
- **Request correlation IDs** — add per-request tracing IDs
- **Graceful shutdown** — add FastAPI lifespan events for clean resource cleanup