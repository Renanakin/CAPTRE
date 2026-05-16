from fastapi import APIRouter, Depends, Query

from app.services.auth_service import ROLE_ADMIN, get_security_dashboard, require_roles

router = APIRouter(prefix="/api/v1/security", tags=["security"])


@router.get("/dashboard")
def security_dashboard_endpoint(
    hours: int = Query(default=24, ge=1, le=24 * 30),
    _: object = Depends(require_roles(ROLE_ADMIN)),
) -> dict[str, object]:
    return get_security_dashboard(hours=hours)
