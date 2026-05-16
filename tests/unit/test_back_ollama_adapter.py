import importlib.util
from pathlib import Path

import requests


def _load_module():
    module_path = Path("g:/PROYECTOS/capturador_datos_v2/apps/back/app/ollama_adapter.py")
    spec = importlib.util.spec_from_file_location("ollama_adapter", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_json_block_plain_json():
    mod = _load_module()
    payload = mod._extract_json_block('{"classification": {}, "extraction": {}}')
    assert isinstance(payload, dict)
    assert "classification" in payload


def test_extract_json_block_with_extra_text():
    mod = _load_module()
    payload = mod._extract_json_block('respuesta\n{"classification": {}, "extraction": {}}\nfin')
    assert isinstance(payload, dict)
    assert "extraction" in payload


def test_fetch_ai_candidate_disabled_returns_none(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "OLLAMA_ENABLED", False)
    candidate = mod.fetch_ai_candidate(content="hola", file_name="a.pdf", mime_type="application/pdf")
    assert candidate is None


def test_fetch_ai_candidate_returns_none_when_model_not_available(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "OLLAMA_ENABLED", True)
    monkeypatch.setattr(mod, "OLLAMA_REQUIRE_MODEL_AVAILABLE", True)
    monkeypatch.setattr(mod, "OLLAMA_MODEL", "llama3.1:8b")

    class _Resp:
        status_code = 200

        @staticmethod
        def json():
            return {"models": [{"name": "mistral:latest"}]}

    monkeypatch.setattr(mod.requests, "get", lambda *args, **kwargs: _Resp())
    candidate = mod.fetch_ai_candidate(content="hola", file_name="a.pdf", mime_type="application/pdf")
    assert candidate is None


def test_fetch_ai_candidate_returns_none_when_endpoint_not_allowed(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "OLLAMA_ENABLED", True)
    monkeypatch.setattr(mod, "OLLAMA_API", "http://malicious-host:11434/api")
    monkeypatch.setattr(mod, "OLLAMA_ALLOWED_HOSTS", {"localhost", "127.0.0.1"})

    candidate = mod.fetch_ai_candidate(content="hola", file_name="a.pdf", mime_type="application/pdf")
    assert candidate is None


def test_fetch_ai_candidate_retries_and_succeeds(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "OLLAMA_ENABLED", True)
    monkeypatch.setattr(mod, "OLLAMA_REQUIRE_MODEL_AVAILABLE", False)
    monkeypatch.setattr(mod, "OLLAMA_RETRY_COUNT", 2)
    monkeypatch.setattr(mod, "OLLAMA_BACKOFF_SECONDS", 0)

    calls = {"n": 0}

    class _RespOK:
        status_code = 200

        @staticmethod
        def json():
            return {
                "response": '{"classification":{"document_type":"invoice","country_code":"CL","confidence":0.9},"extraction":{"supplier_name":"X","supplier_tax_id":"76000000-0","document_number":"123","issue_date":"2026-05-01","currency":"CLP","total":100.0,"amount_due":100.0}}'
            }

    def _fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 2:
            raise requests.RequestException("temporary network error")
        return _RespOK()

    monkeypatch.setattr(mod.requests, "post", _fake_post)
    candidate = mod.fetch_ai_candidate(content="hola", file_name="a.pdf", mime_type="application/pdf")
    assert candidate is not None
    assert candidate["classification"]["document_type"] == "invoice"
    assert calls["n"] == 2
