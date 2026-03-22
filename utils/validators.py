"""Input and domain validation helpers."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from utils.model_types import ParsedDocument


_ALLOWED_EXTENSIONS = {".pdf"}


def sanitize_filename(filename: str) -> str:
    """Return a filesystem-safe filename while preserving readability."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._")
    return cleaned or "document"


def validate_pdf_upload(uploaded_file: Any, max_upload_mb: int) -> Tuple[bool, str]:
    """Validate uploaded PDF file for type and size."""
    if uploaded_file is None:
        return False, "Please upload a PDF file to continue."

    name = getattr(uploaded_file, "name", "")
    size = int(getattr(uploaded_file, "size", 0) or 0)

    if not name:
        return False, "Uploaded file is missing a valid name."

    if not any(name.lower().endswith(ext) for ext in _ALLOWED_EXTENSIONS):
        return False, "Only PDF files are supported."

    if size <= 0:
        return False, "Uploaded file is empty."

    max_bytes = max_upload_mb * 1024 * 1024
    if size > max_bytes:
        return False, f"File exceeds {max_upload_mb} MB upload limit."

    return True, "PDF validation passed."


def validate_document_structure(document: ParsedDocument) -> List[Dict[str, str]]:
    """Run simple quality checks before AI processing."""
    validations: List[Dict[str, str]] = []

    page_count = len(document.pages)
    total_words = sum(len(page.text.split()) for page in document.pages)
    has_headings = any(
        element.get("type") == "heading"
        for page in document.pages
        for element in page.elements
    )

    validations.append(
        {
            "name": "Page Count",
            "status": "pass" if page_count > 0 else "fail",
            "detail": f"Detected {page_count} page(s).",
        }
    )
    validations.append(
        {
            "name": "Minimum Text Coverage",
            "status": "pass" if total_words >= 50 else "warn",
            "detail": f"Detected {total_words} words.",
        }
    )
    validations.append(
        {
            "name": "Section Detection",
            "status": "pass" if has_headings else "warn",
            "detail": "Heading structure found." if has_headings else "No heading markers detected.",
        }
    )

    return validations
