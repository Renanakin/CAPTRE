import importlib.util
from pathlib import Path


def _load_module():
    module_path = Path("g:/PROYECTOS/capturador_datos_v2/apps/back/app/intelligent_extraction.py")
    spec = importlib.util.spec_from_file_location("intelligent_extraction", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_route_extraction_uses_regex_by_default():
    mod = _load_module()
    routed = mod.route_extraction(
        tenant_id="tenant-a",
        regex_classification={"document_type": "invoice", "country_code": "CL", "confidence": 0.9},
        regex_extraction={
            "supplier_name": "Proveedor Demo",
            "supplier_tax_id": "76000000-0",
            "document_number": "12345",
            "issue_date": "2026-05-01",
            "currency": "CLP",
            "total": 10000.0,
            "amount_due": 10000.0,
        },
        ocr_confidence=0.8,
        ai_candidate=None,
    )

    assert routed["classification"]["document_type"] == "invoice"
    assert routed["routing"]["selected_provider"] == "regex"
    assert routed["requires_review"] is False


def test_route_extraction_can_select_ai_when_confidence_is_higher():
    mod = _load_module()
    routed = mod.route_extraction(
        tenant_id="tenant-a",
        regex_classification={"document_type": "unknown", "country_code": "INTL", "confidence": 0.7},
        regex_extraction={
            "supplier_name": "Proveedor Demo",
            "supplier_tax_id": "FOREIGN",
            "document_number": "12345",
            "issue_date": "2026-05-01",
            "currency": "USD",
            "total": 10.0,
            "amount_due": 10.0,
        },
        ocr_confidence=0.6,
        ai_candidate={
            "classification": {"document_type": "receipt", "country_code": "INTL", "confidence": 0.88},
            "extraction": {
                "supplier_name": "Google Play",
                "supplier_tax_id": "FOREIGN",
                "document_number": "INV-9",
                "issue_date": "2026-05-01",
                "currency": "USD",
                "total": 10.0,
                "amount_due": 10.0,
            },
        },
    )

    assert routed["routing"]["selected_provider"] == "ai"
    assert routed["classification"]["document_type"] == "receipt"
    assert routed["requires_review"] is False


def test_route_extraction_requires_review_when_required_field_missing(monkeypatch):
    mod = _load_module()

    class _Rules:
        min_confidence_auto_approve = 0.75
        prefer_ai_for_international = False
        force_review_document_types = []
        required_fields_by_country = {"CL": ["supplier_tax_id"]}
        allowed_currencies_by_country = {}

    monkeypatch.setattr(mod, "load_company_rules", lambda tenant_id: _Rules())

    routed = mod.route_extraction(
        tenant_id="tenant-a",
        regex_classification={"document_type": "invoice", "country_code": "CL", "confidence": 0.95},
        regex_extraction={
            "supplier_name": "Proveedor Demo",
            "supplier_tax_id": None,
            "document_number": "12345",
            "issue_date": "2026-05-01",
            "currency": "CLP",
            "total": 10000.0,
            "amount_due": 10000.0,
        },
        ocr_confidence=0.8,
        ai_candidate=None,
    )

    assert routed["requires_review"] is True
    assert any(flag.startswith("MISSING_REQUIRED_FIELD") for flag in routed["routing"]["validation_flags"])


def test_route_extraction_requires_review_when_currency_not_allowed(monkeypatch):
    mod = _load_module()

    class _Rules:
        min_confidence_auto_approve = 0.75
        prefer_ai_for_international = False
        force_review_document_types = []
        required_fields_by_country = {}
        allowed_currencies_by_country = {"CL": ["CLP"]}

    monkeypatch.setattr(mod, "load_company_rules", lambda tenant_id: _Rules())

    routed = mod.route_extraction(
        tenant_id="tenant-a",
        regex_classification={"document_type": "invoice", "country_code": "CL", "confidence": 0.95},
        regex_extraction={
            "supplier_name": "Proveedor Demo",
            "supplier_tax_id": "76000000-0",
            "document_number": "12345",
            "issue_date": "2026-05-01",
            "currency": "USD",
            "total": 10000.0,
            "amount_due": 10000.0,
        },
        ocr_confidence=0.8,
        ai_candidate=None,
    )

    assert routed["requires_review"] is True
    assert any(flag.startswith("INVALID_CURRENCY") for flag in routed["routing"]["validation_flags"])
