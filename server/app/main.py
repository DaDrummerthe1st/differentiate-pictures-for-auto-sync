from fastapi import FastAPI

from app.auth_routes import router as auth_router
from app.config import load_auth_config, load_db_config

load_db_config()
load_auth_config()

app = FastAPI()
app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
