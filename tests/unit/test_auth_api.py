import importlib
import io
import os
import sqlite3
import hashlib

from fastapi.testclient import TestClient


def _new_client_auth_enabled(tmp_path):
    db_path = tmp_path / "auth_test.db"
    os.environ["APP_DB_PATH"] = str(db_path)
    os.environ["EXPORT_DIR"] = str(tmp_path / "exports")
    os.environ["ENV"] = "dev"
    os.environ["AUTH_ENABLED"] = "true"
    os.environ["DEFAULT_SEED_PASSWORD"] = "change_me_123"

    from app import main as app_main

    importlib.reload(app_main)
    return TestClient(app_main.app)


def _rotated_password_for(username: str) -> str:
    return f"{username}-StrongP@ss1"


def _new_client_with_env(tmp_path, *, env: str, auth_enabled: str, jwt_secret: str, seed_password: str):
    db_path = tmp_path / "auth_env_test.db"
    os.environ["APP_DB_PATH"] = str(db_path)
    os.environ["EXPORT_DIR"] = str(tmp_path / "exports")
    os.environ["ENV"] = env
    os.environ["AUTH_ENABLED"] = auth_enabled
    os.environ["SECURITY_JWT_SECRET"] = jwt_secret
    os.environ["DEFAULT_SEED_PASSWORD"] = seed_password

    from app import main as app_main

    importlib.reload(app_main)
    return TestClient(app_main.app)


def _login(client: TestClient, username: str) -> dict[str, str]:
    password = "change_me_123"
    response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    if response.status_code == 403 and response.json().get("detail") == "Password change required":
        change = client.post(
            "/api/v1/auth/change-password",
            json={
                "username": username,
                "current_password": password,
                "new_password": _rotated_password_for(username),
            },
        )
        assert change.status_code == 200
        password = _rotated_password_for(username)
        response = client.post("/api/v1/auth/login", json={"username": username, "password": password})

    assert response.status_code == 200
    payload = response.json()
    return {
        "Authorization": f"Bearer {payload['access_token']}",
    }


def test_auth_login_and_me(tmp_path):
    client = _new_client_auth_enabled(tmp_path)

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "change_me_123",
        },
    )
    assert login_response.status_code == 403
    assert login_response.json()["detail"] == "Password change required"

    change_response = client.post(
        "/api/v1/auth/change-password",
        json={
            "username": "admin",
            "current_password": "change_me_123",
            "new_password": _rotated_password_for("admin"),
        },
    )
    assert change_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": _rotated_password_for("admin"),
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_auth_refresh_rotates_token(tmp_path):
    client = _new_client_auth_enabled(tmp_path)

    change_response = client.post(
        "/api/v1/auth/change-password",
        json={
            "username": "contador",
            "current_password": "change_me_123",
            "new_password": _rotated_password_for("contador"),
        },
    )
    assert change_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "contador",
            "password": _rotated_password_for("contador"),
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    rotated = refresh_response.json()
    assert rotated["refresh_token"] != tokens["refresh_token"]

    reused_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reused_response.status_code == 401


def test_documents_upload_forbidden_for_auditor_role(tmp_path):
    client = _new_client_auth_enabled(tmp_path)
    auditor_headers = _login(client, "auditor")

    files = {"file": ("boleta.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    data = {"tenant_id": "real-go-nogo"}
    response = client.post("/api/v1/documents/upload", files=files, data=data, headers=auditor_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_cross_company_upload_denied_and_admin_bypass(tmp_path):
    client = _new_client_auth_enabled(tmp_path)
    contador_headers = _login(client, "contador")
    admin_headers = _login(client, "admin")

    files = {"file": ("cross-company.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    denied = client.post(
        "/api/v1/documents/upload",
        files=files,
        data={"tenant_id": "tenant-otro"},
        headers=contador_headers,
    )
    assert denied.status_code == 403
    assert denied.json()["detail"] == "Cross-company access denied"

    files_admin = {"file": ("admin-cross-company.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    allowed = client.post(
        "/api/v1/documents/upload",
        files=files_admin,
        data={"tenant_id": "tenant-otro"},
        headers=admin_headers,
    )
    assert allowed.status_code == 202


def test_cross_company_document_read_denied(tmp_path):
    client = _new_client_auth_enabled(tmp_path)
    admin_headers = _login(client, "admin")
    contador_headers = _login(client, "contador")

    files = {"file": ("tenant-other.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    upload_response = client.post(
        "/api/v1/documents/upload",
        files=files,
        data={"tenant_id": "tenant-otro"},
        headers=admin_headers,
    )
    assert upload_response.status_code == 202
    document_id = upload_response.json()["document_id"]

    get_response = client.get(f"/api/v1/documents/{document_id}", headers=contador_headers)
    assert get_response.status_code == 403
    assert get_response.json()["detail"] == "Cross-company access denied"


def test_revoke_all_refresh_requires_admin(tmp_path):
    client = _new_client_auth_enabled(tmp_path)
    contador_headers = _login(client, "contador")

    response = client.post("/api/v1/auth/revoke-all-refresh", headers=contador_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_revoke_all_refresh_revokes_active_tokens(tmp_path):
    client = _new_client_auth_enabled(tmp_path)
    admin_headers = _login(client, "admin")

    # Create at least one active refresh token
    _login(client, "contador")

    revoke_response = client.post("/api/v1/auth/revoke-all-refresh", headers=admin_headers)
    assert revoke_response.status_code == 200
    payload = revoke_response.json()
    assert payload["revoked_count"] >= 1


def test_prod_runtime_rejects_auth_disabled(tmp_path):
    try:
        _new_client_with_env(
            tmp_path,
            env="prod",
            auth_enabled="false",
            jwt_secret="this_is_a_very_long_secret_for_testing_123",
            seed_password="safe_password_value",
        )
    except RuntimeError as exc:
        assert "AUTH_ENABLED" in str(exc)
    else:
        assert False, "Expected runtime validation to reject AUTH_ENABLED=false in prod"


def test_prod_runtime_rejects_weak_jwt_secret(tmp_path):
    try:
        _new_client_with_env(
            tmp_path,
            env="prod",
            auth_enabled="true",
            jwt_secret="change_me",
            seed_password="safe_password_value",
        )
    except RuntimeError as exc:
        assert "SECURITY_JWT_SECRET" in str(exc)
    else:
        assert False, "Expected runtime validation to reject weak jwt secret in prod"


def test_prod_runtime_rejects_cors_wildcard(tmp_path):
    db_path = tmp_path / "auth_cors_test.db"
    os.environ["APP_DB_PATH"] = str(db_path)
    os.environ["EXPORT_DIR"] = str(tmp_path / "exports")
    os.environ["ENV"] = "prod"
    os.environ["AUTH_ENABLED"] = "true"
    os.environ["SECURITY_JWT_SECRET"] = "this_is_a_very_long_secret_for_testing_123"
    os.environ["SECURITY_JWT_ROTATED_AT"] = "2026-05-16T00:00:00Z"
    os.environ["DEFAULT_SEED_PASSWORD"] = "safe_password_value"
    os.environ["CORS_ALLOW_ORIGINS"] = "*"

    from app import main as app_main

    try:
        importlib.reload(app_main)
    except RuntimeError as exc:
        assert "CORS_ALLOW_ORIGINS" in str(exc)
    else:
        assert False, "Expected runtime validation to reject CORS wildcard in prod"


def test_change_password_rejects_weak_new_password(tmp_path):
    client = _new_client_auth_enabled(tmp_path)

    response = client.post(
        "/api/v1/auth/change-password",
        json={
            "username": "admin",
            "current_password": "change_me_123",
            "new_password": "weakpass",
        },
    )
    assert response.status_code == 400


def test_legacy_hash_is_upgraded_to_bcrypt_on_login(tmp_path):
    client = _new_client_auth_enabled(tmp_path)

    db_path = str(tmp_path / "auth_test.db")
    legacy_hash = hashlib.sha256("capturador-v2:change_me_123".encode("utf-8")).hexdigest()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "UPDATE user_accounts SET password_hash = ?, must_change_password = 0 WHERE username = ?",
            (legacy_hash, "admin"),
        )
        conn.commit()
    finally:
        conn.close()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "change_me_123"},
    )
    assert login_response.status_code == 200

    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("SELECT password_hash FROM user_accounts WHERE username = ?", ("admin",)).fetchone()
    finally:
        conn.close()
    assert row is not None
    assert str(row[0]).startswith("bcrypt$")


def test_security_dashboard_requires_admin(tmp_path):
    client = _new_client_auth_enabled(tmp_path)
    contador_headers = _login(client, "contador")

    response = client.get("/api/v1/security/dashboard", headers=contador_headers)
    assert response.status_code == 403


def test_security_dashboard_collects_security_events(tmp_path):
    client = _new_client_auth_enabled(tmp_path)
    admin_headers = _login(client, "admin")

    # Trigger at least one denied event.
    contador_headers = _login(client, "contador")
    denied = client.post("/api/v1/auth/revoke-all-refresh", headers=contador_headers)
    assert denied.status_code == 403

    dashboard = client.get("/api/v1/security/dashboard?hours=24", headers=admin_headers)
    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["window_hours"] == 24
    assert payload["total_events"] >= 1
    assert isinstance(payload["events"], dict)
