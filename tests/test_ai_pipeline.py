"""Unit tests for AI workflow generation service."""

import logging
import unittest

from services.ai_pipeline import AIWorkflowService
from utils.config import AppConfig
from utils.model_types import DocumentPage, ParsedDocument


class AIPipelineTestCase(unittest.TestCase):
    """AI pipeline output tests."""

    def setUp(self) -> None:
        self.logger = logging.getLogger("tests.ai")
        self.config = AppConfig()
        self.service = AIWorkflowService(config=self.config, logger=self.logger)

    def test_process_document_generates_workflow(self) -> None:
        document = ParsedDocument(
            source_name="ops_manual.pdf",
            pages=[
                DocumentPage(
                    page_number=1,
                    text="Verify document integrity. Extract metadata. Export workflow.",
                    elements=[
                        {"type": "paragraph", "text": "Verify document integrity."},
                        {"type": "paragraph", "text": "Extract metadata."},
                        {"type": "paragraph", "text": "Export workflow."},
                    ],
                    confidence=92.0,
                )
            ],
            metadata={"average_confidence": 92.0},
        )

        result = self.service.process_document(document)

        self.assertGreaterEqual(len(result.workflow_steps), 1)
        self.assertIn("workflow", result.structured_json)
        self.assertIn("future_integrations", result.structured_json)
        self.assertGreaterEqual(len(result.embedding_payload), 1)
        self.assertEqual(
            result.metrics["embedding_chunks"],
            len(result.embedding_payload),
        )


if __name__ == "__main__":
    unittest.main()
