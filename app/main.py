from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import repos

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(repos.router, prefix="/api/v1")


@app.get("/health")
async def get_health():
    return {"healthy": True}
