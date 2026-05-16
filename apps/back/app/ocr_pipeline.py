from __future__ import annotations

from pathlib import Path
from typing import Any


def _preprocess_image_bytes(image_bytes: bytes) -> tuple[bytes, list[str]]:
    steps: list[str] = []
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
        import io
    except ModuleNotFoundError:
        return image_bytes, steps

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = ImageOps.exif_transpose(img)
            steps.append("orientation_fix")

            img = img.convert("L")
            steps.append("grayscale")

            img = ImageEnhance.Contrast(img).enhance(1.8)
            steps.append("contrast_boost")

            img = img.filter(ImageFilter.MedianFilter(size=3))
            steps.append("noise_reduction")

            img = ImageOps.autocontrast(img)
            steps.append("autocontrast")

            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
                steps.append("crop_content")

            out = io.BytesIO()
            img.save(out, format="PNG")
            return out.getvalue(), steps
    except Exception:
        return image_bytes, steps


def _ocr_from_image_bytes(image_bytes: bytes) -> tuple[str, float, dict[str, Any]]:
    processed, steps = _preprocess_image_bytes(image_bytes)

    try:
        import pytesseract
        from PIL import Image
        import io
    except ModuleNotFoundError:
        return "", 0.0, {"engine": "none", "preprocess_steps": steps}

    try:
        img = Image.open(io.BytesIO(processed))
        text = pytesseract.image_to_string(img, lang="spa+eng") or ""
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        confs: list[float] = []
        for c in data.get("conf", []):
            try:
                value = float(c)
                if value >= 0:
                    confs.append(value)
            except (TypeError, ValueError):
                continue

        confidence = (sum(confs) / len(confs) / 100.0) if confs else 0.0
        metrics = {
            "engine": "tesseract",
            "preprocess_steps": steps,
            "word_count": len((text or "").split()),
            "char_count": len((text or "").strip()),
            "mean_word_confidence": round(confidence, 4),
        }
        return text, confidence, metrics
    except Exception:
        return "", 0.0, {"engine": "tesseract", "preprocess_steps": steps, "error": "ocr_failed"}


def _pdf_text(file_path: Path) -> tuple[str, float, dict[str, Any]]:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError:
        return "", 0.0, {"engine": "none", "source": "pdf"}

    try:
        reader = PdfReader(str(file_path))
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts)
        non_space = len([c for c in text if not c.isspace()])
        confidence = 0.9 if non_space > 300 else (0.75 if non_space > 80 else 0.45)
        metrics = {
            "engine": "pypdf",
            "source": "pdf",
            "page_count": len(reader.pages),
            "char_count": len(text.strip()),
            "mean_word_confidence": confidence,
        }
        return text, confidence, metrics
    except Exception:
        return "", 0.0, {"engine": "pypdf", "source": "pdf", "error": "pdf_parse_failed"}


def extract_document_text(storage_path: str | None, mime_type: str, file_name: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {
        "text": "",
        "confidence": 0.0,
        "metrics": {
            "engine": "none",
            "char_count": 0,
            "word_count": 0,
            "mean_word_confidence": 0.0,
        },
    }

    if not storage_path:
        return result

    file_path = Path(storage_path)
    if not file_path.exists():
        return result

    if mime_type == "application/pdf":
        text, confidence, metrics = _pdf_text(file_path)
        result["text"] = text
        result["confidence"] = confidence
        result["metrics"] = metrics
        return result

    if mime_type in {"image/png", "image/jpeg"}:
        try:
            image_bytes = file_path.read_bytes()
        except Exception:
            return result

        text, confidence, metrics = _ocr_from_image_bytes(image_bytes)
        result["text"] = text
        result["confidence"] = confidence
        result["metrics"] = metrics
        return result

    return result
