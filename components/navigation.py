"""Sidebar navigation and workflow state controls."""

from __future__ import annotations

from typing import Tuple

import streamlit as st

from components.branding import render_sidebar_brand

WORKFLOW_STEPS = [
    "Upload PDF",
    "Preview & Validate",
    "AI Processing",
    "Edit / Review Output",
    "Export Results",
]


def render_sidebar_navigation(
    company_name: str,
    current_step: str,
    has_document: bool,
    has_result: bool,
    dark_mode: bool,
    dark_mode_toggle_enabled: bool,
) -> Tuple[str, bool, bool]:
    """Render app navigation and return selected step + logout + dark mode."""
    with st.sidebar:
        render_sidebar_brand(company_name)

        st.markdown("### Workflow")
        default_index = WORKFLOW_STEPS.index(current_step) if current_step in WORKFLOW_STEPS else 0
        selected = st.radio(
            "Process Stage",
            WORKFLOW_STEPS,
            index=default_index,
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("### Status")
        st.caption("1. Login / Landing")
        st.caption("2. Upload PDF" + ("  [Done]" if has_document else ""))
        st.caption("3. Preview & Validate" + ("  [Done]" if has_document else ""))
        st.caption("4. AI Processing" + ("  [Done]" if has_result else ""))
        st.caption("5. Edit / Review Output" + ("  [Done]" if has_result else ""))
        st.caption("6. Export Results" + ("  [Done]" if has_result else ""))

        if dark_mode_toggle_enabled:
            st.markdown("---")
            dark_mode = st.toggle("Dark mode", value=dark_mode)

        st.markdown("---")
        logout_clicked = st.button("Logout", use_container_width=True)

    return selected, logout_clicked, dark_mode
