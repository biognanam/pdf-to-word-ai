"""Login and landing page module."""

from __future__ import annotations

import streamlit as st

from components.branding import get_logo_path
from services.auth_service import AuthService
from utils.config import AppConfig


def render_login_page(config: AppConfig, auth_service: AuthService) -> None:
    """Render clean login UI and authenticate users."""
    logo_path = get_logo_path(config)
    top_col, form_col = st.columns([1.4, 1.0])

    with top_col:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        st.markdown("## PDF to Work Agentics AI Platform")
        st.markdown(
            """
            Convert documents into structured workflows with a simple guided experience.
            """
        )
        st.caption(config.company_name)

    with form_col:
        st.markdown("### Sign In")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            identity = auth_service.authenticate(username=username, password=password)
            if identity:
                st.session_state["authenticated"] = True
                st.session_state["username"] = identity.username
                st.session_state["user_role"] = identity.role
                st.success("Login successful")
                st.rerun()
            st.error("Invalid username or password")

        st.caption("Demo credential: admin / Admin@123")
