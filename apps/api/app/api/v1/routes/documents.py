from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.schemas.documents import OverrideRequest
from app.services.auth_service import (
    ROLE_CONTADOR,
    ROLE_EJECUTIVO,
    AuthUser,
    enforce_company_access,
    enforce_document_access,
    require_roles,
)
from app.services.document_service import (
    get_document,
    override_document_fields,
    process_document,
    upload_document,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", status_code=202)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    tenant_id: str = Form(...),
    responsible: str | None = Form(None),
    period: str | None = Form(None),
    center_cost: str | None = Form(None),
    current_user: AuthUser = Depends(require_roles(ROLE_EJECUTIVO, ROLE_CONTADOR)),
) -> dict[str, object]:
    enforce_company_access(current_user, tenant_id)
    return await upload_document(
        file=file,
        tenant_id=tenant_id,
        responsible=responsible,
        period=period,
        center_cost=center_cost,
    )


@router.get("/{document_id}")
def get_document_endpoint(
    document_id: str,
    current_user: AuthUser = Depends(require_roles(ROLE_EJECUTIVO, ROLE_CONTADOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return get_document(document_id)


@router.post("/{document_id}/process")
def process_document_endpoint(
    document_id: str,
    current_user: AuthUser = Depends(require_roles(ROLE_EJECUTIVO, ROLE_CONTADOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return process_document(document_id)


@router.post("/{document_id}/override")
def override_document_fields_endpoint(
    document_id: str,
    request: OverrideRequest,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return override_document_fields(document_id, request)
