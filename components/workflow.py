"""Workflow stepper UI component."""

from __future__ import annotations

import streamlit as st

from components.navigation import WORKFLOW_STEPS


def render_stepper(current_step: str) -> None:
    """Render a horizontal workflow stepper."""
    columns = st.columns(len(WORKFLOW_STEPS))
    for idx, step in enumerate(WORKFLOW_STEPS):
        css_class = "cb-card cb-step"
        if step == current_step:
            css_class += " current"
        elif WORKFLOW_STEPS.index(current_step) > idx:
            css_class += " done"

        with columns[idx]:
            st.markdown(
                f"""
                <div class="{css_class}">
                    <div style="font-size:0.72rem;font-weight:700;opacity:0.8;">Step {idx + 2}</div>
                    <div style="font-size:0.82rem;font-weight:650;line-height:1.3;">{step}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
