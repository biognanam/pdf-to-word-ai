"""Preview and validation stage page module."""

from __future__ import annotations

import streamlit as st

from components.status import render_validation_summary
from utils.validators import validate_document_structure


def render_preview_page() -> None:
    """Render parsed document preview and validation checks."""
    st.subheader("Preview & Validate")

    document = st.session_state.get("parsed_document")
    if not document:
        st.warning("Upload a PDF first to preview parsed content.")
        return

    metrics = document.metadata
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pages", metrics.get("pages", 0))
    c2.metric("Words", metrics.get("words", 0))
    c3.metric("Avg Confidence", f"{metrics.get('average_confidence', 0)}%")
    c4.metric("Detected Tables", metrics.get("tables", 0))

    st.markdown("### Validation Checks")
    validations = validate_document_structure(document)
    render_validation_summary(validations)

    page_labels = [f"Page {page.page_number}" for page in document.pages]
    selected = st.selectbox("Preview Page", page_labels)
    page_index = int(selected.split()[-1]) - 1

    left_col, right_col = st.columns([1.3, 1.0])

    with left_col:
        st.markdown("### Source Preview")
        if page_index < len(document.preview_images):
            st.image(document.preview_images[page_index], use_container_width=True)
        else:
            st.info("Preview image not available for this page.")

    with right_col:
        page = document.pages[page_index]
        st.markdown("### Extracted Content")
        st.text_area(
            "Raw Extracted Text",
            value=page.text,
            height=340,
            disabled=True,
            label_visibility="collapsed",
        )
        st.caption(f"Page Confidence: {page.confidence:.1f}%")

    st.markdown("### Detected Elements")
    for element in document.pages[page_index].elements[:30]:
        st.markdown(f"- `{element.get('type', 'paragraph')}`: {element.get('text', '')[:140]}")
