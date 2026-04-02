from fastapi import FastAPI
from api import repos

app = FastAPI()


app.include_router(repos.router)

@app.get("/health")
async def read_root():
    return {"Hello": "World"}


