from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "message/rfc822",
}


@dataclass
class DocResult:
    file_path: str
    mime_type: str
    supported: bool
    upload_ok: bool
    process_ok: bool
    document_id: str | None
    final_status: str | None
    review_required: bool
    duplicate: bool
    country_code: str | None
    document_type: str | None
    confidence: float
    critical_fields_present: int
    critical_fields_total: int
    warnings: int
    error: str | None


def _detect_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if path.suffix.lower() == ".pdf":
        return "application/pdf"
    return mime or "application/octet-stream"


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _compute_critical(extraction: dict[str, Any]) -> tuple[int, int]:
    critical = ["supplier_tax_id", "supplier_name", "document_number", "issue_date", "total"]
    present = sum(1 for key in critical if _non_empty(extraction.get(key)))
    return present, len(critical)


def run(base_url: str, dataset_dir: Path) -> dict[str, Any]:
    files = [p for p in dataset_dir.rglob("*") if p.is_file()]
    results: list[DocResult] = []

    session = requests.Session()
    correlation = {"X-Correlation-Id": f"real-docs-{datetime.now().strftime('%Y%m%d%H%M%S')}"}

    for file_path in files:
        mime_type = _detect_mime(file_path)
        supported = mime_type in SUPPORTED_MIME_TYPES

        if not supported:
            results.append(
                DocResult(
                    file_path=str(file_path),
                    mime_type=mime_type,
                    supported=False,
                    upload_ok=False,
                    process_ok=False,
                    document_id=None,
                    final_status=None,
                    review_required=False,
                    duplicate=False,
                    country_code=None,
                    document_type=None,
                    confidence=0.0,
                    critical_fields_present=0,
                    critical_fields_total=0,
                    warnings=0,
                    error="unsupported_mime",
                )
            )
            continue

        try:
            with file_path.open("rb") as fh:
                upload = session.post(
                    f"{base_url}/api/v1/documents/upload",
                    files={"file": (file_path.name, fh, mime_type)},
                    data={"tenant_id": "real-go-nogo", "responsible": "QA-REAL", "period": "2026-05"},
                    headers=correlation,
                    timeout=60,
                )

            if upload.status_code != 202:
                results.append(
                    DocResult(
                        file_path=str(file_path),
                        mime_type=mime_type,
                        supported=True,
                        upload_ok=False,
                        process_ok=False,
                        document_id=None,
                        final_status=None,
                        review_required=False,
                        duplicate=False,
                        country_code=None,
                        document_type=None,
                        confidence=0.0,
                        critical_fields_present=0,
                        critical_fields_total=0,
                        warnings=0,
                        error=f"upload_status_{upload.status_code}",
                    )
                )
                continue

            up = upload.json()
            document_id = up.get("document_id")
            duplicate = bool(up.get("duplicate", False))

            process = session.post(
                f"{base_url}/api/v1/documents/{document_id}/process",
                headers=correlation,
                timeout=90,
            )
            process_ok = process.status_code == 200

            detail = session.get(
                f"{base_url}/api/v1/documents/{document_id}",
                headers=correlation,
                timeout=30,
            )

            if detail.status_code != 200:
                results.append(
                    DocResult(
                        file_path=str(file_path),
                        mime_type=mime_type,
                        supported=True,
                        upload_ok=True,
                        process_ok=process_ok,
                        document_id=document_id,
                        final_status=None,
                        review_required=False,
                        duplicate=duplicate,
                        country_code=None,
                        document_type=None,
                        confidence=0.0,
                        critical_fields_present=0,
                        critical_fields_total=0,
                        warnings=0,
                        error=f"detail_status_{detail.status_code}",
                    )
                )
                continue

            payload = detail.json()
            classification = payload.get("classification") or {}
            extraction = payload.get("extraction") or {}
            present, total = _compute_critical(extraction)

            results.append(
                DocResult(
                    file_path=str(file_path),
                    mime_type=mime_type,
                    supported=True,
                    upload_ok=True,
                    process_ok=process_ok,
                    document_id=document_id,
                    final_status=payload.get("status"),
                    review_required=bool(payload.get("review_required", False)),
                    duplicate=duplicate,
                    country_code=classification.get("country_code"),
                    document_type=classification.get("document_type"),
                    confidence=float(classification.get("confidence") or 0.0),
                    critical_fields_present=present,
                    critical_fields_total=total,
                    warnings=len(payload.get("warnings") or []),
                    error=None,
                )
            )
        except Exception as exc:
            results.append(
                DocResult(
                    file_path=str(file_path),
                    mime_type=mime_type,
                    supported=True,
                    upload_ok=False,
                    process_ok=False,
                    document_id=None,
                    final_status=None,
                    review_required=False,
                    duplicate=False,
                    country_code=None,
                    document_type=None,
                    confidence=0.0,
                    critical_fields_present=0,
                    critical_fields_total=0,
                    warnings=0,
                    error=f"exception:{exc}",
                )
            )

    supported_results = [r for r in results if r.supported]
    processed = [r for r in supported_results if r.upload_ok and r.process_ok and r.error is None]

    cl_docs = [r for r in processed if (r.country_code or "").upper() == "CL"]
    intl_docs = [r for r in processed if (r.country_code or "").upper() != "CL"]

    def ratio(items: list[DocResult]) -> float:
        total_fields = sum(i.critical_fields_total for i in items)
        if total_fields == 0:
            return 0.0
        return sum(i.critical_fields_present for i in items) / total_fields

    output_generated_rate = (len(processed) / len(supported_results)) if supported_results else 0.0
    review_rate = (sum(1 for r in processed if r.review_required) / len(processed)) if processed else 0.0
    cl_precision_proxy = ratio(cl_docs)
    intl_precision_proxy = ratio(intl_docs)

    go = True
    reasons: list[str] = []

    if output_generated_rate < 1.0:
        go = False
        reasons.append("No se genero salida para 100% de documentos soportados")
    if review_rate > 0.15:
        go = False
        reasons.append("Derivacion a revision manual supera 15%")
    if cl_docs and cl_precision_proxy < 0.97:
        go = False
        reasons.append("Proxy precision campos criticos Chile bajo 97%")
    if intl_docs and intl_precision_proxy < 0.93:
        go = False
        reasons.append("Proxy precision campos criticos internacional bajo 93%")

    report = {
        "timestamp": datetime.now().isoformat(),
        "dataset_dir": str(dataset_dir),
        "totals": {
            "all_files": len(results),
            "supported_files": len(supported_results),
            "unsupported_files": len(results) - len(supported_results),
            "processed_ok": len(processed),
            "duplicates": sum(1 for r in processed if r.duplicate),
        },
        "metrics": {
            "output_generated_rate": round(output_generated_rate, 4),
            "review_rate": round(review_rate, 4),
            "chile_precision_proxy": round(cl_precision_proxy, 4),
            "international_precision_proxy": round(intl_precision_proxy, 4),
        },
        "decision": {
            "go": go,
            "no_go_reasons": reasons,
            "note": "Precision reportada como proxy de completitud por falta de ground truth etiquetado.",
        },
        "errors": [
            {
                "file": r.file_path,
                "error": r.error,
            }
            for r in results
            if r.error is not None
        ],
        "sample": [
            {
                "file": r.file_path,
                "status": r.final_status,
                "review_required": r.review_required,
                "country_code": r.country_code,
                "document_type": r.document_type,
                "confidence": r.confidence,
                "critical_fields": f"{r.critical_fields_present}/{r.critical_fields_total}",
                "warnings": r.warnings,
            }
            for r in processed[:20]
        ],
    }
    return report


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    dataset = project_root / "facturas pagos ia"
    result = run(base_url="http://127.0.0.1:8000", dataset_dir=dataset)

    out_json = project_root / "docs" / "REAL_GO_NOGO_REPORT_2026-05-15.json"
    out_md = project_root / "docs" / "REAL_GO_NOGO_REPORT_2026-05-15.md"

    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Real Documents Go/No-Go Report (2026-05-15)",
        "",
        f"- Dataset: {result['dataset_dir']}",
        f"- Files (all): {result['totals']['all_files']}",
        f"- Files supported: {result['totals']['supported_files']}",
        f"- Files unsupported: {result['totals']['unsupported_files']}",
        f"- Processed OK: {result['totals']['processed_ok']}",
        f"- Duplicates: {result['totals']['duplicates']}",
        "",
        "## Metrics",
        f"- output_generated_rate: {result['metrics']['output_generated_rate']}",
        f"- review_rate: {result['metrics']['review_rate']}",
        f"- chile_precision_proxy: {result['metrics']['chile_precision_proxy']}",
        f"- international_precision_proxy: {result['metrics']['international_precision_proxy']}",
        "",
        "## Decision",
        f"- GO: {result['decision']['go']}",
    ]

    if result["decision"]["no_go_reasons"]:
        lines.append("- NO_GO reasons:")
        for reason in result["decision"]["no_go_reasons"]:
            lines.append(f"  - {reason}")
    else:
        lines.append("- NO_GO reasons: none")

    lines.append("")
    lines.append(f"- Note: {result['decision']['note']}")

    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nReport written to: {out_json}")
    print(f"Report written to: {out_md}")
