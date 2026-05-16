from fastapi import APIRouter, Depends

from app.schemas.auth import ChangePasswordRequest, ChangePasswordResponse, CurrentUserResponse, LoginRequest, RefreshRequest, RevokeTokensResponse, TokenResponse
from app.services.auth_service import ROLE_ADMIN, change_password, get_current_user_info, login, refresh, require_roles, revoke_all_refresh_tokens

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login_endpoint(request: LoginRequest) -> TokenResponse:
    return login(request)


@router.post("/refresh", response_model=TokenResponse)
def refresh_endpoint(request: RefreshRequest) -> TokenResponse:
    return refresh(request)


@router.post("/change-password", response_model=ChangePasswordResponse)
def change_password_endpoint(request: ChangePasswordRequest) -> ChangePasswordResponse:
    return change_password(request)


@router.get("/me", response_model=CurrentUserResponse)
def me_endpoint(current_user: CurrentUserResponse = Depends(get_current_user_info)) -> CurrentUserResponse:
    return current_user


@router.post("/revoke-all-refresh", response_model=RevokeTokensResponse)
def revoke_all_refresh_endpoint(_: object = Depends(require_roles(ROLE_ADMIN))) -> RevokeTokensResponse:
    revoked_count = revoke_all_refresh_tokens()
    return RevokeTokensResponse(revoked_count=revoked_count)
