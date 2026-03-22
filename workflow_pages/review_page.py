"""Review and editing stage page module."""

from __future__ import annotations

import json

import streamlit as st

from utils.model_types import WorkflowStep


def render_review_page(logger) -> None:
    """Render editable SOP and workflow output."""
    st.subheader("Edit / Review Output")

    result = st.session_state.get("processing_result")
    if not result:
        st.warning("Run AI processing before reviewing outputs.")
        return

    st.markdown("### Edit SOP")
    edited_sop = st.text_area(
        "SOP Markdown",
        value=st.session_state.get("editable_sop", result.sop_markdown),
        height=320,
    )

    st.markdown("### Review Workflow Steps")
    edited_steps: list[WorkflowStep] = []
    for step in result.workflow_steps:
        with st.expander(f"{step.step_id} - {step.title}"):
            title = st.text_input("Title", value=step.title, key=f"title_{step.step_id}")
            description = st.text_area(
                "Description",
                value=step.description,
                key=f"desc_{step.step_id}",
            )
            role = st.text_input("Owner Role", value=step.role, key=f"role_{step.step_id}")
            edited_steps.append(
                WorkflowStep(
                    step_id=step.step_id,
                    title=title,
                    description=description,
                    role=role,
                    inputs=step.inputs,
                    outputs=step.outputs,
                )
            )

    st.markdown("### Edit Structured JSON")
    edited_json = st.text_area(
        "Workflow JSON",
        value=st.session_state.get("editable_json", json.dumps(result.structured_json, indent=2)),
        height=280,
    )

    if st.button("Save Review Changes", use_container_width=True):
        try:
            parsed_json = json.loads(edited_json)
            result.workflow_steps = edited_steps
            result.sop_markdown = edited_sop
            result.structured_json = parsed_json

            st.session_state["processing_result"] = result
            st.session_state["editable_sop"] = edited_sop
            st.session_state["editable_json"] = json.dumps(parsed_json, indent=2)
            st.session_state["workflow_step"] = "Export Results"
            st.success("Review changes saved successfully.")
        except json.JSONDecodeError as exc:
            logger.warning("Invalid JSON during review save: %s", exc)
            st.error("Structured JSON is invalid. Fix formatting before saving.")
