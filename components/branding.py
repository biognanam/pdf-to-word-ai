"""Branding and header components."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from utils.config import AppConfig


LOGO_RELATIVE_PATH = "assets/caberbyte_logo.png"


def get_logo_path(config: AppConfig) -> Path:
    """Return absolute path of the configured logo asset."""
    return config.output_dir.parent / LOGO_RELATIVE_PATH


def render_app_header(config: AppConfig) -> None:
    """Render no top header content on main app screen."""
    _ = config
    return


def render_sidebar_brand(config: AppConfig) -> None:
    """Render brand logo at top of sidebar."""
    logo_path = get_logo_path(config)
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown(
            """
            <div style="padding:0.25rem 0 0.75rem 0; text-align:center;">
                <div style="font-size:1.3rem;font-weight:800;color:#1E3A8A;">CABER<span style='color:#34BEBF;'>BYTE</span></div>
                <div style="font-size:0.72rem;color:#47679C;">TECHNOLOGIES PVT LTD</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
