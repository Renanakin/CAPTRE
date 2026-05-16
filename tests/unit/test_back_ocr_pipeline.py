import importlib.util
from pathlib import Path


def _load_module():
    module_path = Path("g:/PROYECTOS/capturador_datos_v2/apps/back/app/ocr_pipeline.py")
    spec = importlib.util.spec_from_file_location("ocr_pipeline", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_document_text_returns_default_for_missing_file():
    pipeline = _load_module()
    result = pipeline.extract_document_text(
        storage_path="g:/no/existe/archivo.pdf",
        mime_type="application/pdf",
        file_name="archivo.pdf",
    )

    assert "text" in result
    assert "confidence" in result
    assert "metrics" in result
    assert result["text"] == ""
    assert result["confidence"] == 0.0


def test_extract_document_text_image_without_path_is_safe():
    pipeline = _load_module()
    result = pipeline.extract_document_text(
        storage_path=None,
        mime_type="image/png",
        file_name="imagen.png",
    )

    assert result["confidence"] == 0.0
    assert isinstance(result["metrics"], dict)
