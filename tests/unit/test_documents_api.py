import importlib
import io
import os
from pathlib import Path

from fastapi.testclient import TestClient


def _new_client(tmp_path):
    db_path = tmp_path / "api_test.db"
    os.environ["APP_DB_PATH"] = str(db_path)
    os.environ["EXPORT_DIR"] = str(tmp_path / "exports")
    os.environ["ENV"] = "dev"
    os.environ["AUTH_ENABLED"] = "false"
    os.environ["UPLOAD_QUARANTINE_ENABLED"] = "false"

    from app import main as app_main

    importlib.reload(app_main)
    return TestClient(app_main.app)


def test_upload_and_get_document(tmp_path):
    client = _new_client(tmp_path)

    files = {"file": ("boleta.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    data = {"tenant_id": "tenant-a"}
    upload_response = client.post("/api/v1/documents/upload", files=files, data=data)

    assert upload_response.status_code == 202
    payload = upload_response.json()
    assert payload["status"] == "RECEIVED"
    assert payload["duplicate"] is False

    document_id = payload["document_id"]
    get_response = client.get(f"/api/v1/documents/{document_id}")
    assert get_response.status_code == 200
    result = get_response.json()
    assert result["document_id"] == document_id
    assert result["status"] == "RECEIVED"


def test_upload_duplicate_returns_same_document_id(tmp_path):
    client = _new_client(tmp_path)

    data = {"tenant_id": "tenant-a"}
    files = {"file": ("same.pdf", io.BytesIO(b"%PDF-1.7 same file"), "application/pdf")}
    first = client.post("/api/v1/documents/upload", files=files, data=data)
    assert first.status_code == 202

    files_dup = {"file": ("same.pdf", io.BytesIO(b"%PDF-1.7 same file"), "application/pdf")}
    second = client.post("/api/v1/documents/upload", files=files_dup, data=data)
    assert second.status_code == 202

    p1 = first.json()
    p2 = second.json()
    assert p1["document_id"] == p2["document_id"]
    assert p2["duplicate"] is True


def test_upload_unsupported_mime_type(tmp_path):
    client = _new_client(tmp_path)

    files = {"file": ("bad.txt", io.BytesIO(b"hello"), "text/plain")}
    data = {"tenant_id": "tenant-a"}
    response = client.post("/api/v1/documents/upload", files=files, data=data)

    assert response.status_code == 415


def test_health_returns_correlation_id_header(tmp_path):
    client = _new_client(tmp_path)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Correlation-Id")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


def test_upload_rejects_mime_extension_mismatch(tmp_path):
    client = _new_client(tmp_path)

    files = {"file": ("mismatch.pdf", io.BytesIO(b"%PDF-1.7 fake"), "image/png")}
    data = {"tenant_id": "tenant-a"}
    response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 415


def test_upload_rejects_invalid_signature(tmp_path):
    client = _new_client(tmp_path)

    files = {"file": ("fake.pdf", io.BytesIO(b"not a real pdf header"), "application/pdf")}
    data = {"tenant_id": "tenant-a"}
    response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 422


def test_process_document_and_generate_rendition(tmp_path):
    client = _new_client(tmp_path)

    files = {"file": ("boleta_enero.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    data = {"tenant_id": "tenant-a", "responsible": "Ana", "period": "2026-05"}
    upload_response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert upload_response.status_code == 202
    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")
    assert process_response.status_code == 200
    process_payload = process_response.json()
    assert process_payload["status"] in {"COMPLETED", "REVIEW_REQUIRED"}
    assert isinstance(process_payload["missing_fields"], list)

    get_document_response = client.get(f"/api/v1/documents/{document_id}")
    assert get_document_response.status_code == 200
    document_payload = get_document_response.json()
    assert document_payload["classification"]["country_code"] == "CL"

    rendition_response = client.post(
        "/api/v1/renditions/generate",
        json={
            "tenant_id": "tenant-a",
            "period": "2026-05",
            "document_ids": [document_id],
            "template_version": "01-rendicion-gastos-2025",
        },
    )
    assert rendition_response.status_code == 200
    rendition_payload = rendition_response.json()
    assert rendition_payload["status"] == "GENERATED"
    assert Path(rendition_payload["file_url"]).exists()

    get_rendition_response = client.get(f"/api/v1/renditions/{rendition_payload['rendition_id']}")
    assert get_rendition_response.status_code == 200
    summary = get_rendition_response.json()["summary"]
    assert summary["rows"] == 1
    assert isinstance(summary["missing_fields"], list)

    items_response = client.get(f"/api/v1/renditions/{rendition_payload['rendition_id']}/items")
    assert items_response.status_code == 200
    items_payload = items_response.json()
    assert items_payload["total"] == 1

    download_response = client.get(f"/api/v1/renditions/{rendition_payload['rendition_id']}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def test_generate_rendition_by_filter(tmp_path):
    client = _new_client(tmp_path)

    files = {"file": ("boleta_filtro.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    data = {
        "tenant_id": "tenant-filter",
        "responsible": "Mario",
        "period": "2026-06",
        "center_cost": "VENTAS",
    }
    upload_response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert upload_response.status_code == 202
    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")
    assert process_response.status_code == 200

    rendition_response = client.post(
        "/api/v1/renditions/generate/by-filter",
        json={
            "tenant_id": "tenant-filter",
            "period": "2026-06",
            "responsible": "Mario",
            "center_cost": "VENTAS",
            "template_version": "01-rendicion-gastos-2025",
        },
    )
    assert rendition_response.status_code == 200
    payload = rendition_response.json()
    assert payload["status"] == "GENERATED"


def test_review_queue_and_resolve(tmp_path):
    client = _new_client(tmp_path)

    # Forzamos revisión: documento sin pistas fuertes (tipo unknown, baja confianza).
    files = {"file": ("documento_random.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    data = {"tenant_id": "tenant-review", "responsible": "QA", "period": "2026-05"}
    upload_response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert upload_response.status_code == 202
    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")
    assert process_response.status_code == 200
    assert process_response.json()["status"] == "REVIEW_REQUIRED"

    pending_response = client.get("/api/v1/reviews/pending")
    assert pending_response.status_code == 200
    pending_payload = pending_response.json()
    assert pending_payload["total"] >= 1
    assert any(item["document_id"] == document_id for item in pending_payload["items"])

    resolve_response = client.post(
        f"/api/v1/reviews/{document_id}/resolve",
        json={
            "decision": "approve",
            "reason": "Validado por QA",
            "overrides": {"RUT": "76850000-8"},
        },
    )
    assert resolve_response.status_code == 200
    resolve_payload = resolve_response.json()
    assert resolve_payload["status"] == "COMPLETED"

    get_document_response = client.get(f"/api/v1/documents/{document_id}")
    assert get_document_response.status_code == 200
    assert get_document_response.json()["status"] == "COMPLETED"


def test_review_detail_overrides_and_reject(tmp_path):
    client = _new_client(tmp_path)

    files = {"file": ("documento_review.pdf", io.BytesIO(b"%PDF-1.7 fake pdf bytes"), "application/pdf")}
    data = {"tenant_id": "tenant-review-2", "responsible": "QA2", "period": "2026-05"}
    upload_response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert upload_response.status_code == 202
    document_id = upload_response.json()["document_id"]

    process_response = client.post(f"/api/v1/documents/{document_id}/process")
    assert process_response.status_code == 200
    assert process_response.json()["status"] == "REVIEW_REQUIRED"

    detail_response = client.get(f"/api/v1/reviews/{document_id}")
    assert detail_response.status_code == 200
    detail_payload = detail_response.json()
    assert detail_payload["review"]["status"] == "PENDING"
    assert isinstance(detail_payload["review"]["warnings"], list)

    overrides_response = client.post(
        f"/api/v1/reviews/{document_id}/overrides",
        json={
            "reviewer_id": "reviewer-a",
            "reason": "Ajuste de campos",
            "overrides": {"RUT": "76111111-1", "Centro Costo": "FINANZAS"},
        },
    )
    assert overrides_response.status_code == 200
    assert overrides_response.json()["overrides_applied"] >= 1

    reject_response = client.post(
        f"/api/v1/reviews/{document_id}/reject",
        json={
            "reviewer_id": "reviewer-a",
            "reason": "Documento invalido",
            "overrides": {},
        },
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "REJECTED"

    detail_after_response = client.get(f"/api/v1/reviews/{document_id}")
    assert detail_after_response.status_code == 200
    detail_after = detail_after_response.json()
    assert detail_after["review"]["decision"] == "reject"
    assert detail_after["review"]["reviewer_id"] == "reviewer-a"
    assert detail_after["review"]["resolved_at"] is not None
    assert len(detail_after["manual_changes"]) >= 1
