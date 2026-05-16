from __future__ import annotations

import os

from app.repositories.document_repository import get_db_connection


def get_health_status() -> dict[str, str]:
    return {"status": "ok"}


def get_liveness_status() -> dict[str, str]:
    return {"status": "alive"}


def get_readiness_status() -> dict[str, object]:
    checks: dict[str, str] = {
        "database": "down",
        "redis": "down",
    }

    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        checks["database"] = "up"
    except Exception:
        checks["database"] = "down"
    finally:
        try:
            conn.close()
        except Exception:
            pass

    redis_url = os.getenv("REDIS_URL", "")
    if redis_url:
        try:
            import redis

            client = redis.from_url(redis_url)
            client.ping()
            checks["redis"] = "up"
        except Exception:
            checks["redis"] = "down"
    else:
        checks["redis"] = "not_configured"

    overall = "ready" if checks["database"] == "up" and checks["redis"] in {"up", "not_configured"} else "not_ready"
    return {
        "status": overall,
        "checks": checks,
    }
