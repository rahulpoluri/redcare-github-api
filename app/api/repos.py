from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/github",
    tags=["Github"],
    responses={404: {"description": "Not found"}},
)

@router.get("/repos")
async def get_popular_github_repos():
    return "blablabla"