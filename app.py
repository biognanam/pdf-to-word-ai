"""Main Streamlit entry point for the Canberbyte DocFlow AI platform."""

from __future__ import annotations

import streamlit as st

from components.branding import render_sidebar_brand
from components.styles import apply_global_styles
from services.ai_pipeline import AIWorkflowService
from services.auth_service import AuthService
from services.export_service import ExportService
from services.pdf_service import PDFService
from utils.config import get_config
from utils.logger import setup_logger
from utils.session import initialize_session_state, logout_user
from workflow_pages.login_page import render_login_page
from workflow_pages.simplified_flow import render_simplified_flow

st.set_page_config(
    page_title="Canberbyte DocFlow AI",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Run the Streamlit application."""
    config = get_config()
    logger = setup_logger(config)
    initialize_session_state()

    auth_service = AuthService(config.auth_users, logger)
    pdf_service = PDFService(logger)
    ai_service = AIWorkflowService(config, logger)
    export_service = ExportService(config, logger)

    apply_global_styles()

    if not st.session_state.get("authenticated", False):
        render_login_page(config, auth_service)
        return

    with st.sidebar:
        render_sidebar_brand(config)
        st.markdown("---")
        st.caption("Workflow")
        st.caption("1. Upload")
        st.caption("2. Validate")
        st.caption("3. Convert")
        st.caption("4. QA Compare")
        st.caption("5. Export")
        with st.expander("User & Settings", expanded=False):
            st.write(f"Username: {st.session_state.get('username', 'Unknown')}")
            st.write(f"Role: {st.session_state.get('user_role', 'User')}")
            st.write(f"Environment: {config.environment}")
            st.write(f"Max upload size: {config.max_upload_mb} MB")
            st.write(f"LLM Provider: {config.llm_provider}")

        st.markdown("---")
        if st.button("Logout", use_container_width=True, type="primary"):
            logout_user()
            st.rerun()

    try:
        render_simplified_flow(
            config=config,
            pdf_service=pdf_service,
            ai_service=ai_service,
            export_service=export_service,
            logger=logger,
        )
    except Exception as exc:
        logger.exception("Unhandled application error: %s", exc)
        st.error("Unexpected error occurred. Please retry or check logs/app.log.")


if __name__ == "__main__":
    main()
