"""Upload stage page module."""

from __future__ import annotations

import streamlit as st

from services.pdf_service import PDFService
from utils.config import AppConfig
from utils.session import clear_processing_state
from utils.validators import sanitize_filename, validate_pdf_upload


def render_upload_page(config: AppConfig, pdf_service: PDFService, logger) -> None:
    """Render PDF upload and ingestion stage."""
    st.subheader("Upload PDF")
    st.write("Upload a source PDF to begin AI conversion into structured workflows.")

    uploaded = st.file_uploader(
        "Select PDF",
        type=["pdf"],
        accept_multiple_files=False,
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        validate_clicked = st.button("Validate & Load PDF", use_container_width=True)
    with action_col2:
        demo_clicked = st.button("Load Demo Document", use_container_width=True)

    if validate_clicked:
        is_valid, message = validate_pdf_upload(uploaded, max_upload_mb=config.max_upload_mb)
        if not is_valid:
            st.error(message)
            return

        try:
            uploaded.seek(0)
            pdf_bytes = uploaded.read()
            safe_name = sanitize_filename(uploaded.name)

            clear_processing_state()
            parsed_document = pdf_service.parse_pdf_bytes(source_name=safe_name, pdf_bytes=pdf_bytes)

            st.session_state["uploaded_name"] = safe_name
            st.session_state["uploaded_bytes"] = pdf_bytes
            st.session_state["parsed_document"] = parsed_document
            st.session_state["workflow_step"] = "Preview & Validate"
            st.success("PDF loaded successfully. Continue to Preview & Validate.")
        except Exception as exc:
            logger.exception("Upload processing failed: %s", exc)
            st.error("Failed to parse PDF. Please check the file and try again.")

    if demo_clicked:
        try:
            clear_processing_state()
            parsed_document = pdf_service.load_demo_document()
            st.session_state["uploaded_name"] = parsed_document.source_name
            st.session_state["uploaded_bytes"] = b""
            st.session_state["parsed_document"] = parsed_document
            st.session_state["workflow_step"] = "Preview & Validate"
            st.success("Demo document loaded successfully.")
        except Exception as exc:
            logger.exception("Demo load failed: %s", exc)
            st.error("Unable to load demo data.")

    current_doc = st.session_state.get("parsed_document")
    if current_doc:
        st.markdown("### Current Upload Summary")
        metrics = current_doc.metadata
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pages", metrics.get("pages", 0))
        c2.metric("Words", metrics.get("words", 0))
        c3.metric("Tables", metrics.get("tables", 0))
        c4.metric("Engine", metrics.get("engine", "-"))
