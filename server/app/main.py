from fastapi import FastAPI

from app.config import load_db_config

load_db_config()

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
