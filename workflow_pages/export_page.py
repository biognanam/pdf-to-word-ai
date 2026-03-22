"""Export stage page module."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from services.export_service import ExportService


def _render_download(path: Path, label: str, mime: str) -> None:
    with path.open("rb") as handle:
        st.download_button(
            label=label,
            data=handle.read(),
            file_name=path.name,
            mime=mime,
            use_container_width=True,
        )


def render_export_page(export_service: ExportService, logger) -> None:
    """Render export controls and downloadable outputs."""
    st.subheader("Export Results")

    result = st.session_state.get("processing_result")
    document = st.session_state.get("parsed_document")
    if not result or not document:
        st.warning("Complete AI processing before exporting results.")
        return

    st.write("Generate final artifacts in Word, JSON, and structured Markdown formats.")

    if st.button("Generate Export Files", use_container_width=False):
        try:
            source_name = document.source_name
            word_path = export_service.export_word(result, source_name)
            json_path = export_service.export_json(result, source_name)
            markdown_path = export_service.export_markdown(result, source_name)

            st.session_state["export_word_path"] = str(word_path)
            st.session_state["export_json_path"] = str(json_path)
            st.session_state["export_markdown_path"] = str(markdown_path)
            st.success("Export files generated successfully.")
        except Exception as exc:
            logger.exception("Export generation failed: %s", exc)
            st.error("Failed to generate exports.")

    st.markdown("### Download Artifacts")
    word_path = st.session_state.get("export_word_path")
    json_path = st.session_state.get("export_json_path")
    markdown_path = st.session_state.get("export_markdown_path")

    if word_path and Path(word_path).exists():
        word_mime = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if word_path.endswith(".docx")
            else "text/plain"
        )
        _render_download(Path(word_path), "Download Word/TXT", word_mime)

    if json_path and Path(json_path).exists():
        _render_download(Path(json_path), "Download JSON", "application/json")

    if markdown_path and Path(markdown_path).exists():
        _render_download(Path(markdown_path), "Download Markdown", "text/markdown")

    st.markdown("### Export Preview")
    st.text_area(
        "SOP Output",
        value=result.sop_markdown,
        height=240,
        disabled=True,
    )
