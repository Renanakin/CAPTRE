from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.repositories.document_repository import get_db_connection
from app.schemas.auth import ChangePasswordRequest, ChangePasswordResponse, CurrentUserResponse, LoginRequest, RefreshRequest, TokenResponse

JWT_SECRET = os.getenv("SECURITY_JWT_SECRET", "change_me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "capturador-v2")

bearer_scheme = HTTPBearer(auto_error=False)


def _auth_enabled() -> bool:
    return os.getenv("AUTH_ENABLED", "false").lower() in {"1", "true", "yes", "on"}


@dataclass
class AuthUser:
    user_id: str
    username: str
    role: str
    company_id: str


ROLE_ADMIN = "admin"
ROLE_CONTADOR = "contador"
ROLE_EJECUTIVO = "ejecutivo"
ROLE_AUDITOR = "auditor"

INSECURE_SECRETS = {"", "change_me", "changeme", "default", "dev", "test"}
INSECURE_PASSWORDS = {"", "change_me_123", "changeme", "password", "admin", "123456"}
LEGACY_HASH_RE = re.compile(r"^[a-f0-9]{64}$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _audit_security_event(event_type: str, payload: dict[str, object]) -> None:
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO audit_events (id, entity_type, entity_id, event_type, payload_json, actor_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                "security",
                "security",
                event_type,
                json.dumps(payload, ensure_ascii=True),
                str(payload.get("actor_id")) if payload.get("actor_id") else None,
                _utc_now_iso(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _is_production_like_runtime() -> bool:
    env = (os.getenv("ENV", "dev") or "dev").strip().lower()
    return env in {"prod", "production", "staging"}


def validate_security_runtime_config() -> None:
    if not _is_production_like_runtime():
        return

    if not _auth_enabled():
        raise RuntimeError("AUTH_ENABLED must be true in production-like runtime")

    jwt_secret_normalized = JWT_SECRET.strip().lower()
    if jwt_secret_normalized in INSECURE_SECRETS or len(JWT_SECRET.strip()) < 32:
        raise RuntimeError("SECURITY_JWT_SECRET is weak or uses an insecure default")

    rotated_at = (os.getenv("SECURITY_JWT_ROTATED_AT", "") or "").strip()
    if not rotated_at:
        raise RuntimeError("SECURITY_JWT_ROTATED_AT is required in production-like runtime")
    try:
        rotated_dt = datetime.fromisoformat(rotated_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("SECURITY_JWT_ROTATED_AT must be ISO-8601") from exc

    max_age_days = int(os.getenv("SECURITY_JWT_MAX_AGE_DAYS", "90"))
    if (_utc_now() - rotated_dt).days > max_age_days:
        raise RuntimeError("SECURITY_JWT_SECRET rotation age exceeded policy")

    seed_password = (os.getenv("DEFAULT_SEED_PASSWORD", "") or "").strip().lower()
    if seed_password in INSECURE_PASSWORDS:
        raise RuntimeError("DEFAULT_SEED_PASSWORD uses an insecure default in production-like runtime")


def _hash_password_legacy(password: str) -> str:
    return hashlib.sha256(f"{PASSWORD_SALT}:{password}".encode("utf-8")).hexdigest()


def _hash_password_strong(password: str) -> str:
    encoded = password.encode("utf-8")
    hashed = bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=12)).decode("utf-8")
    return f"bcrypt${hashed}"


def _verify_password(password: str, stored_hash: str) -> tuple[bool, bool]:
    # returns (is_valid, needs_upgrade)
    candidate = password.encode("utf-8")
    normalized = (stored_hash or "").strip()

    if normalized.startswith("bcrypt$"):
        return bcrypt.checkpw(candidate, normalized.split("$", 1)[1].encode("utf-8")), False

    if normalized.startswith("$2"):
        return bcrypt.checkpw(candidate, normalized.encode("utf-8")), False

    if LEGACY_HASH_RE.match(normalized):
        return normalized == _hash_password_legacy(password), True

    return False, False


def _validate_password_strength(password: str) -> None:
    if len(password) < 12:
        raise HTTPException(status_code=400, detail="Password must have at least 12 characters")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must include an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must include a lowercase letter")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must include a number")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise HTTPException(status_code=400, detail="Password must include a symbol")


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def _create_access_token(user: AuthUser) -> tuple[str, int]:
    expires = _utc_now() + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role,
        "company_id": user.company_id,
        "type": "access",
        "exp": int(expires.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, ACCESS_TOKEN_MINUTES * 60


def _create_refresh_token(user: AuthUser) -> str:
    token_id = str(uuid.uuid4())
    expires = _utc_now() + timedelta(days=REFRESH_TOKEN_DAYS)
    payload = {
        "sub": user.user_id,
        "username": user.username,
        "role": user.role,
        "company_id": user.company_id,
        "jti": token_id,
        "type": "refresh",
        "exp": int(expires.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO refresh_tokens (
                id, user_id, token_id, revoked, expires_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), user.user_id, token_id, 0, expires.isoformat(), _utc_now_iso()),
        )
        conn.commit()
    finally:
        conn.close()

    return token


def _get_user_by_username(username: str) -> AuthUser | None:
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT id, username, role, company_id
            FROM user_accounts
            WHERE username = ?
            """,
            (username,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return None
    return AuthUser(user_id=row["id"], username=row["username"], role=row["role"], company_id=row["company_id"])


def _validate_credentials(username: str, password: str) -> tuple[AuthUser | None, bool]:
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT id, username, role, company_id, password_hash, COALESCE(must_change_password, 0) AS must_change_password
            FROM user_accounts
            WHERE username = ?
            """,
            (username,),
        ).fetchone()
        if not row:
            return None, False

        valid, needs_upgrade = _verify_password(password, str(row["password_hash"] or ""))
        if not valid:
            return None, False

        if needs_upgrade:
            conn.execute(
                "UPDATE user_accounts SET password_hash = ?, password_changed_at = ? WHERE id = ?",
                (_hash_password_strong(password), _utc_now_iso(), row["id"]),
            )
            conn.commit()

        must_change = bool(int(row["must_change_password"] or 0))
        user = AuthUser(user_id=row["id"], username=row["username"], role=row["role"], company_id=row["company_id"])
        return user, must_change
    finally:
        conn.close()


def login(request: LoginRequest) -> TokenResponse:
    user, must_change_password = _validate_credentials(request.username, request.password)
    if not user:
        _audit_security_event("AUTH_LOGIN_FAILED", {"username": request.username})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if must_change_password:
        _audit_security_event("AUTH_PASSWORD_CHANGE_REQUIRED", {"username": request.username})
        raise HTTPException(status_code=403, detail="Password change required")

    access_token, expires_in = _create_access_token(user)
    refresh_token = _create_refresh_token(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)


def refresh(request: RefreshRequest) -> TokenResponse:
    payload = _decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        _audit_security_event("AUTH_REFRESH_FAILED", {"reason": "invalid_token_type"})
        raise HTTPException(status_code=401, detail="Invalid token type")

    token_id = payload.get("jti")
    user_id = payload.get("sub")
    if not token_id or not user_id:
        _audit_security_event("AUTH_REFRESH_FAILED", {"reason": "invalid_payload"})
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")

    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT revoked, expires_at
            FROM refresh_tokens
            WHERE token_id = ? AND user_id = ?
            """,
            (token_id, user_id),
        ).fetchone()
        if not row:
            _audit_security_event("AUTH_REFRESH_FAILED", {"reason": "token_not_found", "user_id": user_id})
            raise HTTPException(status_code=401, detail="Refresh token not found")
        if int(row["revoked"] or 0) == 1:
            _audit_security_event("AUTH_REFRESH_FAILED", {"reason": "token_revoked", "user_id": user_id})
            raise HTTPException(status_code=401, detail="Refresh token revoked")
        expires_at = datetime.fromisoformat(str(row["expires_at"]))
        if expires_at < _utc_now():
            _audit_security_event("AUTH_REFRESH_FAILED", {"reason": "token_expired", "user_id": user_id})
            raise HTTPException(status_code=401, detail="Refresh token expired")

        conn.execute(
            "UPDATE refresh_tokens SET revoked = 1 WHERE token_id = ?",
            (token_id,),
        )
        conn.commit()
    finally:
        conn.close()

    user = _get_user_by_username(str(payload.get("username") or ""))
    if not user:
        user = _get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token, expires_in = _create_access_token(user)
    refresh_token = _create_refresh_token(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)


def revoke_all_refresh_tokens() -> int:
    conn = get_db_connection()
    try:
        pending_row = conn.execute("SELECT COUNT(*) AS total FROM refresh_tokens WHERE revoked = 0").fetchone()
        pending = int(pending_row["total"] if pending_row else 0)
        conn.execute("UPDATE refresh_tokens SET revoked = 1 WHERE revoked = 0")
        conn.commit()
        _audit_security_event("AUTH_REFRESH_REVOKE_ALL", {"revoked_count": pending})
        return pending
    finally:
        conn.close()


def change_password(request: ChangePasswordRequest) -> ChangePasswordResponse:
    _validate_password_strength(request.new_password)
    if request.new_password == request.current_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")

    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT id, password_hash
            FROM user_accounts
            WHERE username = ?
            """,
            (request.username,),
        ).fetchone()
        if not row:
            _audit_security_event("AUTH_PASSWORD_CHANGE_FAILED", {"username": request.username, "reason": "invalid_credentials"})
            raise HTTPException(status_code=401, detail="Invalid credentials")

        valid, _ = _verify_password(request.current_password, str(row["password_hash"] or ""))
        if not valid:
            _audit_security_event("AUTH_PASSWORD_CHANGE_FAILED", {"username": request.username, "reason": "invalid_credentials"})
            raise HTTPException(status_code=401, detail="Invalid credentials")

        conn.execute(
            """
            UPDATE user_accounts
            SET password_hash = ?, must_change_password = 0, is_bootstrap = 0, password_changed_at = ?
            WHERE id = ?
            """,
            (_hash_password_strong(request.new_password), _utc_now_iso(), row["id"]),
        )
        conn.execute(
            "UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ?",
            (row["id"],),
        )
        conn.commit()
        _audit_security_event("AUTH_PASSWORD_CHANGED", {"username": request.username, "actor_id": row["id"]})
        return ChangePasswordResponse(password_changed=True)
    finally:
        conn.close()


def _get_user_by_id(user_id: str) -> AuthUser | None:
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT id, username, role, company_id
            FROM user_accounts
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return None
    return AuthUser(user_id=row["id"], username=row["username"], role=row["role"], company_id=row["company_id"])


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> AuthUser:
    if not _auth_enabled():
        return AuthUser(user_id="system", username="system", role=ROLE_ADMIN, company_id="*")

    if credentials is None:
        _audit_security_event("AUTH_BEARER_MISSING", {})
        raise HTTPException(status_code=401, detail="Missing bearer token")

    payload = _decode_token(credentials.credentials)
    if payload.get("type") != "access":
        _audit_security_event("AUTH_TOKEN_INVALID", {"reason": "invalid_token_type"})
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = str(payload.get("sub") or "")
    username = str(payload.get("username") or "")
    role = str(payload.get("role") or "")
    company_id = str(payload.get("company_id") or "")

    if not user_id or not username or not role or not company_id:
        _audit_security_event("AUTH_TOKEN_INVALID", {"reason": "invalid_token_payload"})
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return AuthUser(user_id=user_id, username=username, role=role, company_id=company_id)


def require_roles(*allowed_roles: str) -> Callable[[AuthUser], AuthUser]:
    def _dependency(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if current_user.role == ROLE_ADMIN:
            return current_user
        if current_user.role not in allowed_roles:
            _audit_security_event(
                "AUTH_ACCESS_DENIED",
                {
                    "actor_id": current_user.user_id,
                    "username": current_user.username,
                    "role": current_user.role,
                    "allowed_roles": list(allowed_roles),
                },
            )
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _dependency


def enforce_company_access(current_user: AuthUser, company_id: str) -> None:
    if current_user.role == ROLE_ADMIN:
        return
    if current_user.company_id != company_id:
        raise HTTPException(status_code=403, detail="Cross-company access denied")


def _document_tenant(document_id: str) -> str | None:
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT tenant_id FROM documents WHERE id = ?", (document_id,)).fetchone()
    finally:
        conn.close()
    return str(row["tenant_id"]) if row else None


def _rendition_tenant(rendition_id: str) -> str | None:
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT tenant_id FROM renditions WHERE id = ?", (rendition_id,)).fetchone()
    finally:
        conn.close()
    return str(row["tenant_id"]) if row else None


def enforce_document_access(current_user: AuthUser, document_id: str) -> None:
    tenant = _document_tenant(document_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Document not found")
    enforce_company_access(current_user, tenant)


def enforce_rendition_access(current_user: AuthUser, rendition_id: str) -> None:
    tenant = _rendition_tenant(rendition_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Rendition not found")
    enforce_company_access(current_user, tenant)


def list_pending_reviews_scoped(current_user: AuthUser) -> dict[str, object]:
    from app.services.document_service import list_pending_reviews

    data = list_pending_reviews()
    if current_user.role == ROLE_ADMIN:
        return data

    items = [item for item in data.get("items", []) if item.get("tenant_id") == current_user.company_id]
    return {"total": len(items), "items": items}


def get_current_user_info(current_user: AuthUser = Depends(get_current_user)) -> CurrentUserResponse:
    return CurrentUserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role,
        company_id=current_user.company_id,
    )


def hash_password_for_seed(password: str) -> str:
    return _hash_password_strong(password)


def get_security_dashboard(hours: int = 24) -> dict[str, object]:
    window_hours = max(1, min(hours, 24 * 30))
    cutoff = (_utc_now() - timedelta(hours=window_hours)).isoformat()

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT event_type, COUNT(*) AS total
            FROM audit_events
            WHERE entity_type = 'security' AND created_at >= ?
            GROUP BY event_type
            ORDER BY total DESC
            """,
            (cutoff,),
        ).fetchall()
    finally:
        conn.close()

    counts = {str(row["event_type"]): int(row["total"]) for row in rows}
    return {
        "window_hours": window_hours,
        "total_events": sum(counts.values()),
        "events": counts,
    }
