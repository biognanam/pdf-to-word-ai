"""PDF ingestion, parsing, and layout preparation service."""

from __future__ import annotations

import io
import re
from typing import List

from PIL import Image, ImageDraw, ImageFont

from utils.model_types import DocumentPage, ParsedDocument


_DEMO_TEXTS = [
    """
    PRODUCT OPERATIONS MANUAL
    1. Verify source document integrity and approvals before conversion.
    2. Extract document metadata, headings, tables, and lists.
    3. Validate compliance statements for regulatory workflow alignment.
    4. Package approved output for multilingual publishing and audit.
    """,
    """
    INSTALLATION GUIDELINES
    1. Confirm prerequisites and responsible stakeholders.
    2. Configure environment baseline and perform safety checks.
    3. Execute installation sequence and record outcomes.
    4. Submit final validation evidence and release package.
    """,
]


class PDFService:
    """Handles PDF parsing with graceful fallbacks and preview generation."""

    def __init__(self, logger) -> None:
        self.logger = logger

    def load_demo_document(self) -> ParsedDocument:
        """Return a demo parsed document for quick exploration."""
        pages = [
            self._build_page(index + 1, text.strip(), confidence=95.0)
            for index, text in enumerate(_DEMO_TEXTS)
        ]
        previews = [self._placeholder_preview(page) for page in pages]

        metadata = self._build_metadata(pages, source_name="demo_operations_manual.pdf", engine="Demo")
        return ParsedDocument(
            source_name="demo_operations_manual.pdf",
            pages=pages,
            metadata=metadata,
            preview_images=previews,
        )

    def parse_pdf_bytes(self, source_name: str, pdf_bytes: bytes) -> ParsedDocument:
        """Parse PDF bytes to normalized pages, metadata, and previews."""
        if not pdf_bytes:
            raise ValueError("Uploaded PDF is empty.")

        extracted_texts = self._extract_text_pages(pdf_bytes)
        if not extracted_texts:
            self.logger.warning("No text extracted from %s, using demo fallback text.", source_name)
            extracted_texts = [segment.strip() for segment in _DEMO_TEXTS]

        pages = [
            self._build_page(index + 1, text, confidence=self._estimate_confidence(text))
            for index, text in enumerate(extracted_texts)
        ]

        previews = self._render_pdf_previews(pdf_bytes)
        rendered_pdf_preview = bool(previews)
        if not previews:
            previews = [self._placeholder_preview(page) for page in pages]

        metadata = self._build_metadata(
            pages,
            source_name=source_name,
            engine="PyMuPDF" if rendered_pdf_preview else "Text + Placeholder Preview",
        )

        return ParsedDocument(
            source_name=source_name,
            pages=pages,
            metadata=metadata,
            preview_images=previews,
        )

    def _extract_text_pages(self, pdf_bytes: bytes) -> List[str]:
        """Extract text using pypdf, page by page."""
        pages: List[str] = []
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in reader.pages:
                text = (page.extract_text() or "").strip()
                pages.append(text)
            self.logger.info("Text extraction complete. Pages=%s", len(pages))
        except Exception as exc:
            self.logger.exception("Text extraction failed: %s", exc)
            return []

        return pages

    def _render_pdf_previews(self, pdf_bytes: bytes) -> List[Image.Image]:
        """Render page previews from PDF using PyMuPDF when available."""
        previews: List[Image.Image] = []
        try:
            import fitz

            document = fitz.open(stream=pdf_bytes, filetype="pdf")
            matrix = fitz.Matrix(1.4, 1.4)
            for page in document:
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                previews.append(image)
            document.close()
        except Exception as exc:
            self.logger.warning("Preview rendering unavailable, fallback enabled: %s", exc)
            return []

        return previews

    def _build_page(self, page_number: int, text: str, confidence: float) -> DocumentPage:
        elements = self._detect_elements(text)
        return DocumentPage(
            page_number=page_number,
            text=text,
            elements=elements,
            confidence=confidence,
        )

    @staticmethod
    def _estimate_confidence(text: str) -> float:
        if not text:
            return 70.0
        length = len(text.split())
        return min(98.0, 80.0 + (length / 25.0))

    def _detect_elements(self, text: str) -> List[dict]:
        elements: List[dict] = []
        for line in text.splitlines():
            cleaned = line.strip()
            if not cleaned:
                continue
            if cleaned.isupper() and len(cleaned) > 7:
                elements.append({"type": "heading", "level": 1, "text": cleaned})
            elif re.match(r"^\d+[.)]\s+", cleaned):
                elements.append({"type": "list_item", "text": cleaned})
            elif re.match(r"^\d+\.\d+", cleaned):
                elements.append({"type": "heading", "level": 2, "text": cleaned})
            elif len(re.split(r"\s{2,}", cleaned)) >= 3:
                elements.append({"type": "table_row", "text": cleaned})
            else:
                elements.append({"type": "paragraph", "text": cleaned})

        if not elements:
            elements.append({"type": "paragraph", "text": text.strip() or "No text detected."})
        return elements

    def _build_metadata(self, pages: List[DocumentPage], source_name: str, engine: str) -> dict:
        word_count = sum(len(page.text.split()) for page in pages)
        table_count = sum(
            1
            for page in pages
            for element in page.elements
            if element.get("type") == "table_row"
        )
        avg_conf = sum(page.confidence for page in pages) / max(1, len(pages))
        return {
            "source_name": source_name,
            "pages": len(pages),
            "words": word_count,
            "tables": table_count,
            "average_confidence": round(avg_conf, 2),
            "engine": engine,
        }

    @staticmethod
    def _placeholder_preview(page: DocumentPage) -> Image.Image:
        image = Image.new("RGB", (900, 1150), color=(248, 251, 255))
        draw = ImageDraw.Draw(image)

        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except Exception:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()

        draw.rectangle((0, 0, 900, 70), fill=(30, 58, 138))
        draw.text((30, 24), f"Page {page.page_number} Preview", fill=(230, 245, 255), font=title_font)

        y_cursor = 100
        for line in page.text.splitlines()[:18]:
            line = line.strip()
            if not line:
                continue
            draw.text((40, y_cursor), line[:100], fill=(15, 37, 77), font=body_font)
            y_cursor += 38

        draw.rectangle((0, 1110, 900, 1150), fill=(14, 116, 144))
        draw.text((30, 1120), "Canberbyte Technologies - AI Preview", fill=(224, 242, 254), font=body_font)
        return image
