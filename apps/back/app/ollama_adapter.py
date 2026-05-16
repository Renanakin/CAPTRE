from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.parse import urlparse

import requests

OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434/api")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
OLLAMA_RETRY_COUNT = int(os.getenv("OLLAMA_RETRY_COUNT", "2"))
OLLAMA_BACKOFF_SECONDS = float(os.getenv("OLLAMA_BACKOFF_SECONDS", "0.5"))
OLLAMA_REQUIRE_MODEL_AVAILABLE = os.getenv("OLLAMA_REQUIRE_MODEL_AVAILABLE", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
OLLAMA_ALLOWED_HOSTS = {
    value.strip().lower()
    for value in os.getenv("OLLAMA_ALLOWED_HOSTS", "localhost,127.0.0.1,kernelia-ollama,ollama").split(",")
    if value.strip()
}


def _is_ollama_endpoint_allowed() -> bool:
    parsed = urlparse(OLLAMA_API)
    host = (parsed.hostname or "").strip().lower()
    if not host:
        return False
    return host in OLLAMA_ALLOWED_HOSTS


def _extract_json_block(raw_text: str) -> dict[str, Any] | None:
    raw_text = raw_text.strip()
    if not raw_text:
        return None

    if raw_text.startswith("{") and raw_text.endswith("}"):
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(raw_text[start : end + 1])
        except json.JSONDecodeError:
            return None

    return None


def _build_prompt(*, content: str, file_name: str, mime_type: str) -> str:
    return (
        "Eres un extractor de documentos contables. "
        "Debes responder SOLO JSON valido, sin texto adicional.\n"
        "Schema esperado:\n"
        "{\n"
        '  "classification": {"document_type": "invoice|receipt|credit_note|unknown", "country_code": "CL|INTL|unknown", "confidence": 0.0},\n'
        '  "extraction": {"supplier_name": "", "supplier_tax_id": "", "document_number": "", "issue_date": "YYYY-MM-DD", "currency": "CLP|USD|EUR", "total": 0.0, "amount_due": 0.0}\n'
        "}\n"
        "Reglas:\n"
        "- confidence entre 0.0 y 1.0\n"
        "- Si no hay dato, usar null\n"
        "- No inventes campos fuera del schema\n"
        f"Archivo: {file_name}\n"
        f"Mime: {mime_type}\n"
        "Contenido OCR/PDF:\n"
        f"{content[:12000]}"
    )


def _is_model_available() -> bool:
    if not OLLAMA_REQUIRE_MODEL_AVAILABLE:
        return True

    try:
        response = requests.get(
            f"{OLLAMA_API}/tags",
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        return False

    if response.status_code != 200:
        return False

    try:
        payload = response.json()
    except ValueError:
        return False

    models = payload.get("models") or []
    for model in models:
        if not isinstance(model, dict):
            continue
        if str(model.get("name") or "") == OLLAMA_MODEL:
            return True
    return False


def fetch_ai_candidate(*, content: str, file_name: str, mime_type: str) -> dict[str, Any] | None:
    if not OLLAMA_ENABLED:
        return None

    if not _is_ollama_endpoint_allowed():
        return None

    if not _is_model_available():
        return None

    prompt = _build_prompt(content=content, file_name=file_name, mime_type=mime_type)

    response = None
    last_error: requests.RequestException | None = None
    attempts = max(1, OLLAMA_RETRY_COUNT + 1)
    for attempt in range(attempts):
        try:
            response = requests.post(
                f"{OLLAMA_API}/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=OLLAMA_TIMEOUT_SECONDS,
            )
            if response.status_code == 200:
                break
        except requests.RequestException as exc:
            last_error = exc

        if attempt < attempts - 1:
            time.sleep(OLLAMA_BACKOFF_SECONDS * (attempt + 1))

    if response is None or response.status_code != 200:
        if last_error:
            return None
        return None

    try:
        payload = response.json()
    except ValueError:
        return None

    raw = str(payload.get("response") or "")
    parsed = _extract_json_block(raw)
    if not parsed:
        return None

    if not isinstance(parsed.get("classification"), dict):
        return None
    if not isinstance(parsed.get("extraction"), dict):
        return None

    return {
        "classification": parsed.get("classification") or {},
        "extraction": parsed.get("extraction") or {},
        "meta": {
            "provider": "ollama",
            "model": OLLAMA_MODEL,
            "api": OLLAMA_API,
        },
    }
