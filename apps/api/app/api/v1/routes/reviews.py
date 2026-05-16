from fastapi import APIRouter, Depends

from app.schemas.documents import ReviewActionRequest, ReviewOverridesRequest, ReviewResolveRequest
from app.services.auth_service import (
    ROLE_AUDITOR,
    ROLE_CONTADOR,
    AuthUser,
    enforce_document_access,
    list_pending_reviews_scoped,
    require_roles,
)
from app.services.document_service import (
    approve_review,
    apply_review_overrides,
    get_review_detail,
    list_pending_reviews,
    reject_review,
    resolve_review,
)

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.get("/pending")
def list_pending_reviews_endpoint(
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_AUDITOR)),
) -> dict[str, object]:
    return list_pending_reviews_scoped(current_user)


@router.get("/{document_id}")
def get_review_detail_endpoint(
    document_id: str,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_AUDITOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return get_review_detail(document_id)


@router.post("/{document_id}/overrides")
def apply_review_overrides_endpoint(
    document_id: str,
    request: ReviewOverridesRequest,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_AUDITOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return apply_review_overrides(document_id, request)


@router.post("/{document_id}/approve")
def approve_review_endpoint(
    document_id: str,
    request: ReviewActionRequest,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_AUDITOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return approve_review(document_id, request)


@router.post("/{document_id}/reject")
def reject_review_endpoint(
    document_id: str,
    request: ReviewActionRequest,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_AUDITOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return reject_review(document_id, request)


@router.post("/{document_id}/resolve")
def resolve_review_endpoint(
    document_id: str,
    request: ReviewResolveRequest,
    current_user: AuthUser = Depends(require_roles(ROLE_CONTADOR, ROLE_AUDITOR)),
) -> dict[str, object]:
    enforce_document_access(current_user, document_id)
    return resolve_review(document_id, request)
