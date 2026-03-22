"""Simplified end-user guided workflow UI."""

from __future__ import annotations

import json
import re
from pathlib import Path

import streamlit as st

from services.ai_pipeline import AIWorkflowService
from services.export_service import ExportService
from services.pdf_service import PDFService
from utils.config import AppConfig
from utils.session import clear_processing_state
from utils.validators import sanitize_filename, validate_document_structure, validate_pdf_upload


def _render_section(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="cb-section">
            <div class="cb-section-title">{title}</div>
            <div class="cb-step-status">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_converted_page_text(page, result) -> str:
    """Create a readable converted-view text for side-by-side QA."""
    lines: list[str] = []
    for element in page.elements:
        element_type = element.get("type", "paragraph")
        text = element.get("text", "").strip()
        if not text:
            continue
        if element_type == "heading":
            lines.append(f"[Section] {text}")
        elif element_type == "list_item":
            lines.append(f"- {text.lstrip('0123456789.) ').strip()}")
        elif element_type == "table_row":
            lines.append(f"| {text}")
        else:
            lines.append(text)

    lines.append("")
    lines.append("Workflow Summary:")
    for step in result.workflow_steps[:8]:
        lines.append(f"{step.step_id}. {step.title}")

    return "\n".join(lines).strip()


def _calculate_qa_confidence(page, converted_text: str) -> tuple[float, float]:
    """Compute QA confidence based on extraction confidence and content coverage."""
    source_tokens = set(re.findall(r"[A-Za-z0-9]+", page.text.lower()))
    converted_tokens = set(re.findall(r"[A-Za-z0-9]+", converted_text.lower()))
    if not source_tokens:
        coverage = 0.0
    else:
        coverage = len(source_tokens & converted_tokens) / len(source_tokens)

    extraction_confidence = float(page.confidence or 0.0)
    score = (0.7 * extraction_confidence) + (0.3 * (coverage * 100))
    return round(score, 1), round(coverage * 100, 1)


def _render_agentic_orchestration(result) -> None:
    """Render multi-agent orchestration summary for transparency."""
    agentic_data = result.structured_json.get("agentic_ai", {})
    agents = agentic_data.get("agents", {})
    if not agents:
        st.info("Agentic AI trace is not available for this run.")
        return

    overall_score = float(agentic_data.get("overall_score", 0.0))
    st.metric("Agentic Overall Score", f"{overall_score:.1f}%")

    for key in [
        "extractor_agent",
        "structure_agent",
        "compliance_agent",
        "qa_reviewer_agent",
        "optimization_agent",
    ]:
        agent = agents.get(key, {})
        if not agent:
            continue
        st.markdown(
            f"""
            <div class="agentic-card">
                <div class="agentic-title">{agent.get('name', key)}</div>
                <div class="agentic-meta">Purpose: {agent.get('purpose', '-')}</div>
                <div class="agentic-meta">Score: {agent.get('score', 0)}% | Status: {agent.get('status', 'done')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_simplified_flow(
    config: AppConfig,
    pdf_service: PDFService,
    ai_service: AIWorkflowService,
    export_service: ExportService,
    logger,
) -> None:
    """Render streamlined user flow with minimal interactions."""
    _render_section(
        "1) Upload PDF",
        "Upload once and continue with guided processing.",
    )

    uploaded = st.file_uploader("Upload PDF document", type=["pdf"], accept_multiple_files=False)
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        upload_clicked = st.button(
            "Load Uploaded PDF",
            use_container_width=True,
            type="primary",
        )
    with col_u2:
        demo_clicked = st.button(
            "Use Demo Document",
            use_container_width=True,
            type="primary",
        )

    if upload_clicked:
        is_valid, message = validate_pdf_upload(uploaded, max_upload_mb=config.max_upload_mb)
        if not is_valid:
            st.error(message)
        else:
            try:
                uploaded.seek(0)
                clear_processing_state()
                pdf_bytes = uploaded.read()
                source_name = sanitize_filename(uploaded.name)
                parsed = pdf_service.parse_pdf_bytes(source_name=source_name, pdf_bytes=pdf_bytes)
                st.session_state["parsed_document"] = parsed
                st.session_state["uploaded_name"] = parsed.source_name
                st.session_state["qa_approved"] = False
                st.success("PDF loaded successfully.")
            except Exception as exc:
                logger.exception("Failed to load uploaded PDF: %s", exc)
                st.error("Unable to parse uploaded PDF. Please try another file.")

    if demo_clicked:
        try:
            clear_processing_state()
            parsed = pdf_service.load_demo_document()
            st.session_state["parsed_document"] = parsed
            st.session_state["uploaded_name"] = parsed.source_name
            st.session_state["qa_approved"] = False
            st.success("Demo document loaded.")
        except Exception as exc:
            logger.exception("Failed to load demo document: %s", exc)
            st.error("Unable to load demo document.")

    document = st.session_state.get("parsed_document")
    if not document:
        st.info("Upload a PDF or choose demo to continue.")
        return

    _render_section(
        "2) Preview & Validate",
        "Quickly verify extraction quality before AI conversion.",
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Pages", document.metadata.get("pages", 0))
    m2.metric("Words", document.metadata.get("words", 0))
    m3.metric("Confidence", f"{document.metadata.get('average_confidence', 0)}%")
    m4.metric("Tables", document.metadata.get("tables", 0))

    validations = validate_document_structure(document)
    for item in validations:
        if item["status"] == "pass":
            st.success(f"{item['name']}: {item['detail']}")
        elif item["status"] == "fail":
            st.error(f"{item['name']}: {item['detail']}")
        else:
            st.warning(f"{item['name']}: {item['detail']}")

    preview_index = st.selectbox(
        "Preview Page",
        options=list(range(len(document.pages))),
        format_func=lambda idx: f"Page {idx + 1}",
        key="preview_page_index",
    )
    left, right = st.columns([1.3, 1.0])
    with left:
        if preview_index < len(document.preview_images):
            st.image(document.preview_images[preview_index], use_container_width=True)
    with right:
        st.text_area(
            "Extracted Text",
            value=document.pages[preview_index].text,
            height=300,
            disabled=True,
        )

    _render_section(
        "3) AI Conversion",
        "Generate SOP and structured workflow in one click.",
    )

    if st.button("Generate Workflow Output", use_container_width=True, type="primary"):
        with st.spinner("Processing with AI pipeline..."):
            try:
                result = ai_service.process_document(document)
                st.session_state["processing_result"] = result
                st.session_state["qa_approved"] = False
                st.success("Workflow output generated.")
            except Exception as exc:
                logger.exception("AI conversion failed: %s", exc)
                st.error("AI conversion failed. Please retry.")

    result = st.session_state.get("processing_result")
    if not result:
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Workflow Steps", result.metrics.get("workflow_steps", 0))
    m2.metric("LLM Mode", result.metrics.get("llm_mode", "stub"))
    m3.metric("Embeddings", result.metrics.get("embedding_chunks", 0))
    m4.metric("JSON Size", f"{result.metrics.get('json_size_bytes', 0)} B")

    _render_section(
        "3A) Agentic AI Orchestration",
        "Specialized AI agents collaborate to improve workflow quality.",
    )
    _render_agentic_orchestration(result)

    with st.expander("Review Output", expanded=False):
        st.markdown("### SOP")
        st.text_area("SOP", value=result.sop_markdown, height=220, disabled=True)
        st.markdown("### Structured JSON")
        st.code(json.dumps(result.structured_json, indent=2), language="json")

    _render_section(
        "4) QA Comparison",
        "Review source vs converted view and approve for export.",
    )

    qa_index = st.selectbox(
        "QA Review Page",
        options=list(range(len(document.pages))),
        format_func=lambda idx: f"Page {idx + 1}",
        key="qa_page_index",
    )

    page = document.pages[qa_index]
    converted_text = _build_converted_page_text(page, result)
    confidence_score, coverage_score = _calculate_qa_confidence(page, converted_text)

    qa_left, qa_right = st.columns([1.0, 1.0])
    with qa_left:
        st.markdown('<div class="qa-panel"><div class="qa-panel-title">Source Document</div></div>', unsafe_allow_html=True)
        if qa_index < len(document.preview_images):
            st.image(document.preview_images[qa_index], use_container_width=True)
        st.text_area("Source Text", value=page.text, height=220, disabled=True, key="qa_source_text")

    with qa_right:
        st.markdown('<div class="qa-panel"><div class="qa-panel-title">Converted Document</div></div>', unsafe_allow_html=True)
        st.text_area(
            "Converted Text",
            value=converted_text,
            height=420,
            disabled=True,
            key="qa_converted_text",
        )

    q1, q2, q3 = st.columns(3)
    q1.metric("QA Confidence Score", f"{confidence_score}%")
    q2.metric("Coverage Match", f"{coverage_score}%")
    q3.metric("Extraction Confidence", f"{page.confidence:.1f}%")
    st.progress(confidence_score / 100.0)

    approved = st.checkbox(
        "QA review completed and approved for export",
        value=st.session_state.get("qa_approved", False),
    )
    st.session_state["qa_approved"] = approved

    _render_section(
        "5) Export",
        "Download Word, JSON, and Markdown outputs.",
    )

    if not st.session_state.get("qa_approved", False):
        st.warning("Complete QA approval to enable export.")

    if st.button(
        "Generate Download Files",
        use_container_width=True,
        type="primary",
        disabled=not st.session_state.get("qa_approved", False),
    ):
        try:
            source_name = document.source_name
            word_path = export_service.export_word(result, source_name)
            json_path = export_service.export_json(result, source_name)
            markdown_path = export_service.export_markdown(result, source_name)

            st.session_state["export_word_path"] = str(word_path)
            st.session_state["export_json_path"] = str(json_path)
            st.session_state["export_markdown_path"] = str(markdown_path)
            st.success("Files generated. Download below.")
        except Exception as exc:
            logger.exception("Export generation failed: %s", exc)
            st.error("Export failed. Please retry.")

    word_path = st.session_state.get("export_word_path")
    json_path = st.session_state.get("export_json_path")
    markdown_path = st.session_state.get("export_markdown_path")

    col_d1, col_d2, col_d3 = st.columns(3)

    if word_path and Path(word_path).exists():
        with col_d1:
            mime = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if word_path.endswith(".docx")
                else "text/plain"
            )
            with Path(word_path).open("rb") as handle:
                st.download_button("Download Word", handle.read(), file_name=Path(word_path).name, mime=mime)

    if json_path and Path(json_path).exists():
        with col_d2:
            with Path(json_path).open("rb") as handle:
                st.download_button(
                    "Download JSON",
                    handle.read(),
                    file_name=Path(json_path).name,
                    mime="application/json",
                )

    if markdown_path and Path(markdown_path).exists():
        with col_d3:
            with Path(markdown_path).open("rb") as handle:
                st.download_button(
                    "Download Markdown",
                    handle.read(),
                    file_name=Path(markdown_path).name,
                    mime="text/markdown",
                )
