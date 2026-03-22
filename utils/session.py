"""Streamlit session state initialization and helpers."""

from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULT_STATE: dict[str, Any] = {
    "authenticated": False,
    "username": None,
    "user_role": None,
    "workflow_step": "Upload PDF",
    "uploaded_name": None,
    "uploaded_bytes": None,
    "parsed_document": None,
    "processing_result": None,
    "editable_sop": "",
    "editable_json": "",
    "export_word_path": None,
    "export_json_path": None,
    "export_markdown_path": None,
    "qa_approved": False,
    "dark_mode": False,
    "last_error": None,
}


def initialize_session_state() -> None:
    """Seed missing session keys with defaults."""
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_processing_state() -> None:
    """Reset workflow state when a new file is uploaded."""
    st.session_state["parsed_document"] = None
    st.session_state["processing_result"] = None
    st.session_state["editable_sop"] = ""
    st.session_state["editable_json"] = ""
    st.session_state["export_word_path"] = None
    st.session_state["export_json_path"] = None
    st.session_state["export_markdown_path"] = None
    st.session_state["qa_approved"] = False


def logout_user() -> None:
    """Clear auth/session values."""
    for key in [
        "authenticated",
        "username",
        "user_role",
        "workflow_step",
        "uploaded_name",
        "uploaded_bytes",
        "parsed_document",
        "processing_result",
        "editable_sop",
        "editable_json",
        "export_word_path",
        "export_json_path",
        "export_markdown_path",
        "qa_approved",
        "last_error",
    ]:
        if key in st.session_state:
            st.session_state[key] = DEFAULT_STATE.get(key)
