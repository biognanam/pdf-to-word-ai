"""AI processing stage page module."""

from __future__ import annotations

import json
import time

import streamlit as st

from services.ai_pipeline import AIWorkflowService


def render_processing_page(ai_service: AIWorkflowService, logger) -> None:
    """Run AI workflow generation pipeline with status indicators."""
    st.subheader("AI Processing")

    document = st.session_state.get("parsed_document")
    if not document:
        st.warning("Upload and validate a document before AI processing.")
        return

    st.write("Convert parsed PDF content into SOP and structured workflow outputs.")

    run_clicked = st.button("Run AI Pipeline", use_container_width=False)

    if run_clicked:
        steps = [
            "Reading validated document structure",
            "Normalizing layout elements",
            "Generating workflow steps",
            "Drafting SOP and structured JSON",
            "Preparing embedding payload",
        ]

        progress = st.progress(0)
        status_box = st.empty()
        result = None

        try:
            for index, step in enumerate(steps, start=1):
                progress.progress(int((index - 1) / len(steps) * 100))
                status_box.info(f"{step}...")
                time.sleep(0.18)
                if "Generating workflow steps" in step:
                    result = ai_service.process_document(document)

            progress.progress(100)
            status_box.success("AI processing complete.")

            if result is None:
                result = ai_service.process_document(document)

            st.session_state["processing_result"] = result
            st.session_state["editable_sop"] = result.sop_markdown
            st.session_state["editable_json"] = json.dumps(result.structured_json, indent=2)
            st.session_state["workflow_step"] = "Edit / Review Output"
            st.success("Structured output generated. Continue to Edit / Review Output.")

        except Exception as exc:
            logger.exception("AI processing failed: %s", exc)
            st.error("AI processing failed. Review logs and retry.")

    result = st.session_state.get("processing_result")
    if result:
        st.markdown("### Processing Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Workflow Steps", result.metrics.get("workflow_steps", 0))
        m2.metric("LLM Mode", result.metrics.get("llm_mode", "stub"))
        m3.metric("Avg Confidence", f"{result.metrics.get('average_confidence', 0)}%")
        m4.metric("JSON Size", f"{result.metrics.get('json_size_bytes', 0)} B")
