from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class ExtractionPayload(BaseModel):
    supplier_name: str | None = None
    supplier_tax_id: str | None = None
    document_number: str | None = None
    issue_date: str | None = None
    currency: str | None = None
    total: float | None = None
    amount_due: float | None = None
    subtotal: float | None = None
    tax: float | None = None
    description: str | None = None
    extra_fields: dict[str, Any] | None = None


class ClassificationPayload(BaseModel):
    document_type: str = "unknown"
    country_code: str = "unknown"
    confidence: float = 0.0


class CandidateResult(BaseModel):
    provider: str
    classification: ClassificationPayload
    extraction: ExtractionPayload


class CompanyRules(BaseModel):
    min_confidence_auto_approve: float = Field(default=0.75, ge=0.0, le=1.0)
    prefer_ai_for_international: bool = True
    force_review_document_types: list[str] = Field(default_factory=list)
    required_fields_by_country: dict[str, list[str]] = Field(default_factory=dict)
    allowed_currencies_by_country: dict[str, list[str]] = Field(default_factory=dict)


CandidateResult.model_rebuild()


def _load_rules_raw() -> dict[str, Any]:
    path_value = os.getenv("COMPANY_RULES_PATH")
    if not path_value:
        return {}

    path = Path(path_value)
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_company_rules(tenant_id: str) -> CompanyRules:
    data = _load_rules_raw()
    default_rules = data.get("default") or {}
    tenant_rules = (data.get("tenants") or {}).get(tenant_id) or {}

    merged = dict(default_rules)
    merged.update(tenant_rules)

    try:
        return CompanyRules.model_validate(merged)
    except ValidationError:
        return CompanyRules()


def _to_candidate(provider: str, classification: dict[str, Any], extraction: dict[str, Any]) -> CandidateResult:
    return CandidateResult(
        provider=provider,
        classification=ClassificationPayload.model_validate(classification),
        extraction=ExtractionPayload.model_validate(extraction),
    )


def route_extraction(
    *,
    tenant_id: str,
    regex_classification: dict[str, Any],
    regex_extraction: dict[str, Any],
    ocr_confidence: float,
    ai_candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rules = load_company_rules(tenant_id)

    regex_candidate = _to_candidate("regex", regex_classification, regex_extraction)
    selected = regex_candidate
    compared: list[dict[str, Any]] = [
        {
            "provider": "regex",
            "confidence": float(regex_candidate.classification.confidence),
            "document_type": regex_candidate.classification.document_type,
            "country_code": regex_candidate.classification.country_code,
        }
    ]

    if ai_candidate is not None:
        try:
            ai = _to_candidate(
                "ai",
                ai_candidate.get("classification") or {},
                ai_candidate.get("extraction") or {},
            )
            compared.append(
                {
                    "provider": "ai",
                    "confidence": float(ai.classification.confidence),
                    "document_type": ai.classification.document_type,
                    "country_code": ai.classification.country_code,
                }
            )

            regex_is_intl = (regex_candidate.classification.country_code or "").upper() not in {"CL", "UNKNOWN"}
            ai_better = ai.classification.confidence >= (regex_candidate.classification.confidence + 0.05)
            if ai_better or (rules.prefer_ai_for_international and regex_is_intl):
                selected = ai
        except ValidationError:
            pass

    unified_confidence = float(selected.classification.confidence)
    if ocr_confidence > 0:
        unified_confidence = min(0.99, (unified_confidence * 0.8) + (float(ocr_confidence) * 0.2))

    doc_type = selected.classification.document_type or "unknown"
    requires_review = unified_confidence < rules.min_confidence_auto_approve or doc_type == "unknown"
    if doc_type in rules.force_review_document_types:
        requires_review = True

    final_classification = selected.classification.model_dump()
    final_classification["confidence"] = round(unified_confidence, 4)

    regex_extraction_base = dict(regex_extraction)
    selected_extraction = selected.extraction.model_dump()
    final_extraction = dict(regex_extraction_base)
    for key, value in selected_extraction.items():
        if value is not None:
            final_extraction[key] = value

    final_extraction["amount_due"] = final_extraction.get("amount_due") or final_extraction.get("total")

    country_code = str(final_classification.get("country_code") or "unknown").upper()
    validation_flags: list[str] = []

    required_fields = list((rules.required_fields_by_country or {}).get(country_code, []))
    for field_name in required_fields:
        value = final_extraction.get(field_name)
        if value is None or (isinstance(value, str) and not value.strip()):
            requires_review = True
            validation_flags.append(f"MISSING_REQUIRED_FIELD:{field_name}")

    allowed_currencies = list((rules.allowed_currencies_by_country or {}).get(country_code, []))
    currency_value = str(final_extraction.get("currency") or "").upper()
    if allowed_currencies and currency_value and currency_value not in {c.upper() for c in allowed_currencies}:
        requires_review = True
        validation_flags.append(f"INVALID_CURRENCY:{currency_value}")

    candidate_meta: dict[str, Any] = {}
    if ai_candidate and isinstance(ai_candidate, dict):
        candidate_meta = dict(ai_candidate.get("meta") or {})

    return {
        "classification": final_classification,
        "extraction": final_extraction,
        "requires_review": requires_review,
        "routing": {
            "selected_provider": selected.provider,
            "compared_candidates": compared,
            "ocr_confidence": round(float(ocr_confidence), 4),
            "min_confidence_auto_approve": rules.min_confidence_auto_approve,
            "validation_flags": validation_flags,
            "selected_candidate_meta": candidate_meta,
        },
    }
