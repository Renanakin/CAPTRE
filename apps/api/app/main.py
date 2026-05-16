import uuid
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.documents import router as documents_router
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.renditions import router as renditions_router
from app.api.v1.routes.reviews import router as reviews_router
from app.api.v1.routes.security import router as security_router
from app.core.correlation import correlation_id_ctx
from app.repositories.document_repository import init_database
from app.services.auth_service import validate_security_runtime_config

app = FastAPI(title="capturador-datos-v2", version="0.1.0")


def _env_name() -> str:
    return (os.getenv("ENV", "dev") or "dev").strip().lower()


def _is_production_like() -> bool:
    return _env_name() in {"prod", "production", "staging"}


def _split_csv_env(name: str, default_csv: str) -> list[str]:
    return [value.strip() for value in os.getenv(name, default_csv).split(",") if value.strip()]


def _validate_cors_runtime(origins: list[str], methods: list[str], headers: list[str]) -> None:
    if not _is_production_like():
        return
    if "*" in origins:
        raise RuntimeError("CORS_ALLOW_ORIGINS must not contain wildcard in production-like runtime")
    if "*" in methods:
        raise RuntimeError("CORS_ALLOW_METHODS must not contain wildcard in production-like runtime")
    if "*" in headers:
        raise RuntimeError("CORS_ALLOW_HEADERS must not contain wildcard in production-like runtime")

default_origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
configured_origins = [
    value.strip()
    for value in os.getenv("CORS_ALLOW_ORIGINS", ",".join(default_origins)).split(",")
    if value.strip()
]
cors_allow_methods = _split_csv_env("CORS_ALLOW_METHODS", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
cors_allow_headers = _split_csv_env("CORS_ALLOW_HEADERS", "Authorization,Content-Type,X-Correlation-Id")

_validate_cors_runtime(configured_origins, cors_allow_methods, cors_allow_headers)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=cors_allow_methods,
    allow_headers=cors_allow_headers,
)


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
    token = correlation_id_ctx.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = correlation_id
        return response
    finally:
        correlation_id_ctx.reset(token)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if _is_production_like():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    if _is_production_like():
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    raise exc


validate_security_runtime_config()
init_database()
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(reviews_router)
app.include_router(renditions_router)
app.include_router(security_router)
