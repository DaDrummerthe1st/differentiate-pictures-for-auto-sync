from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.auth_routes import router as auth_router
from app.config import load_auth_config, load_db_config
from app.db import ensure_schema, get_connection
from app.login_page import router as login_page_router
from app.rate_limit import limiter

load_db_config()
load_auth_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_connection()
    try:
        ensure_schema(conn)
        conn.commit()
    finally:
        conn.close()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(auth_router)
app.include_router(login_page_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
