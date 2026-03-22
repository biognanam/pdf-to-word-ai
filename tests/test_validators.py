"""Unit tests for validators module."""

import unittest

from utils.model_types import DocumentPage, ParsedDocument
from utils.validators import sanitize_filename, validate_document_structure, validate_pdf_upload


class DummyUpload:
    """Minimal upload object for testing."""

    def __init__(self, name: str, size: int) -> None:
        self.name = name
        self.size = size


class ValidatorsTestCase(unittest.TestCase):
    """Validation helper tests."""

    def test_validate_pdf_upload_success(self) -> None:
        upload = DummyUpload(name="manual.pdf", size=2048)
        is_valid, message = validate_pdf_upload(upload, max_upload_mb=5)
        self.assertTrue(is_valid)
        self.assertIn("passed", message.lower())

    def test_validate_pdf_upload_rejects_wrong_extension(self) -> None:
        upload = DummyUpload(name="manual.docx", size=1024)
        is_valid, message = validate_pdf_upload(upload, max_upload_mb=5)
        self.assertFalse(is_valid)
        self.assertIn("pdf", message.lower())

    def test_sanitize_filename(self) -> None:
        self.assertEqual(sanitize_filename("Quarterly Report (v2).pdf"), "Quarterly_Report_v2_.pdf")

    def test_validate_document_structure(self) -> None:
        document = ParsedDocument(
            source_name="sample.pdf",
            pages=[
                DocumentPage(
                    page_number=1,
                    text="TITLE\n1. Validate input\n2. Export output",
                    elements=[
                        {"type": "heading", "text": "TITLE", "level": 1},
                        {"type": "list_item", "text": "1. Validate input"},
                    ],
                    confidence=96.0,
                )
            ],
        )

        validations = validate_document_structure(document)
        statuses = {item["name"]: item["status"] for item in validations}
        self.assertEqual(statuses.get("Page Count"), "pass")
        self.assertEqual(statuses.get("Section Detection"), "pass")


if __name__ == "__main__":
    unittest.main()
