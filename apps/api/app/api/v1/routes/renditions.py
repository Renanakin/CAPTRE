from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.schemas.documents import RenditionGenerateByFilterRequest, RenditionGenerateRequest
from app.services.auth_service import (
    ROLE_CONTADOR,
    ROLE_EJECUTIVO,
    AuthUser,
    enforce_company_access,
    enforce_rendition_access,
    require_roles,
)
from app.services.document_service import (
    download_rendition,
    generate_rendition,
    generate_rendition_by_filter,
    get_rendition,
    list_rendition_items,
)

router = APIRouter(prefix="/api/v1/renditions", tags=["renditions"])


@router.post("/generate")
def generate_rendition_endpoint(
    request: RenditionGenerateRequest,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_EJECUTIVO)),
) -> dict[str, object]:
    enforce_company_access(current_user, request.tenant_id)
    return generate_rendition(request)


@router.post("/generate/by-filter")
def generate_rendition_by_filter_endpoint(
    request: RenditionGenerateByFilterRequest,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_EJECUTIVO)),
) -> dict[str, object]:
    enforce_company_access(current_user, request.tenant_id)
    return generate_rendition_by_filter(request)


@router.get("/{rendition_id}")
def get_rendition_endpoint(
    rendition_id: str,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_EJECUTIVO)),
) -> dict[str, object]:
    enforce_rendition_access(current_user, rendition_id)
    return get_rendition(rendition_id)


@router.get("/{rendition_id}/items")
def list_rendition_items_endpoint(
    rendition_id: str,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_EJECUTIVO)),
) -> dict[str, object]:
    enforce_rendition_access(current_user, rendition_id)
    return list_rendition_items(rendition_id)


@router.get("/{rendition_id}/download")
def download_rendition_endpoint(
    rendition_id: str,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_EJECUTIVO)),
) -> FileResponse:
    enforce_rendition_access(current_user, rendition_id)
    file_path = download_rendition(rendition_id)
    return FileResponse(path=file_path, filename=f"rendition_{rendition_id}.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
