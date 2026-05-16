from fastapi import APIRouter

from app.services.health_service import get_health_status, get_liveness_status, get_readiness_status

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return get_health_status()


@router.get("/liveness")
def liveness() -> dict[str, str]:
    return get_liveness_status()


@router.get("/readiness")
def readiness() -> dict[str, object]:
    return get_readiness_status()
