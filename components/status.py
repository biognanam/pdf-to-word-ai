"""UI helpers for status and validation rendering."""

from __future__ import annotations

from typing import Dict, List

import streamlit as st


def render_validation_summary(validations: List[Dict[str, str]]) -> None:
    """Render validation checks in a consistent format."""
    if not validations:
        st.info("No validation checks available.")
        return

    for item in validations:
        status = item.get("status", "warn")
        text = f"**{item.get('name', 'Check')}**: {item.get('detail', '')}"
        if status == "pass":
            st.success(text)
        elif status == "fail":
            st.error(text)
        else:
            st.warning(text)


def render_processing_status(step_name: str, detail: str) -> None:
    """Render an informational status line during pipeline execution."""
    st.info(f"{step_name}: {detail}")
