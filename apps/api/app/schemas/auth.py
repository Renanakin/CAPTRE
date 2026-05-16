from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ChangePasswordRequest(BaseModel):
    username: str
    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    password_changed: bool


class CurrentUserResponse(BaseModel):
    user_id: str
    username: str
    role: str
    company_id: str


class RevokeTokensResponse(BaseModel):
    revoked_count: int
