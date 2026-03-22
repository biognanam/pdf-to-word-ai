"""Design system and visual cleanup styles."""

from __future__ import annotations

import streamlit as st


def apply_global_styles() -> None:
    """Inject high-contrast, simplified style system."""
    st.markdown(
        """
        <style>
        :root {
            --cb-primary: #2A3C8B;
            --cb-secondary: #34BEBF;
            --cb-bg: #F4F7FC;
            --cb-surface: #FFFFFF;
            --cb-text: #102A63;
            --cb-muted: #4A6797;
            --cb-border: #D7E1F2;
            --cb-success: #15803D;
            --cb-warn: #B45309;
            --cb-danger: #B91C1C;
        }

        html, body, [class*="css"] {
            font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif !important;
        }

        [data-testid="stAppViewContainer"], .stApp {
            background: var(--cb-bg) !important;
            color: var(--cb-text) !important;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.98) !important;
            border-bottom: 1px solid var(--cb-border) !important;
        }

        [data-testid="stSidebarContent"] {
            background: linear-gradient(180deg, #EAF0FB 0%, #F7FAFF 100%) !important;
            border-right: 1px solid var(--cb-border) !important;
        }

        [data-testid="stSidebarContent"] * {
            color: #183875 !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .workflow-landing {
            background: var(--cb-surface);
            border: 1px solid var(--cb-border);
            border-radius: 10px;
            padding: 0.7rem 0.85rem;
            margin-bottom: 0.8rem;
        }

        .workflow-landing-title {
            font-size: 1.02rem;
            font-weight: 800;
            color: #1E3A8A;
            margin-bottom: 0.15rem;
        }

        .workflow-landing-sub {
            font-size: 0.8rem;
            color: #4A6797;
        }

        .workflow-landing-meta {
            font-size: 0.74rem;
            color: #6A84B1;
            margin-top: 0.25rem;
        }

        .cb-section {
            background: var(--cb-surface);
            border: 1px solid var(--cb-border);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.8rem;
        }

        .cb-section-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: var(--cb-primary);
            margin-bottom: 0.3rem;
        }

        .cb-step-status {
            font-size: 0.78rem;
            color: var(--cb-muted);
            margin-bottom: 0.4rem;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 8px !important;
            border: 0 !important;
            font-weight: 600 !important;
            color: #FFFFFF !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #2A3C8B, #3D59B3) !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #23337A, #2F4CA3) !important;
        }

        [data-testid="stSidebarContent"] .stButton > button {
            background: linear-gradient(135deg, #2A3C8B, #3D59B3) !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }

        [data-testid="stSidebarContent"] .stButton > button * {
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }

        .stDownloadButton > button {
            background: linear-gradient(135deg, #0E7490, #34BEBF) !important;
        }

        .stProgress > div > div {
            background: linear-gradient(90deg, #2A3C8B, #34BEBF) !important;
        }

        .stAlert {
            border-radius: 8px !important;
        }

        [data-testid="stSidebarContent"] details summary {
            background: linear-gradient(135deg, #2A3C8B, #3D59B3) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            padding: 0.35rem 0.55rem !important;
        }

        [data-testid="stSidebarContent"] details summary * {
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }

        .qa-panel {
            background: #FFFFFF;
            border: 1px solid var(--cb-border);
            border-radius: 10px;
            padding: 0.65rem 0.75rem;
            margin-bottom: 0.55rem;
        }

        .qa-panel-title {
            font-size: 0.82rem;
            color: var(--cb-primary);
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .agentic-card {
            background: #FFFFFF;
            border: 1px solid var(--cb-border);
            border-left: 4px solid #34BEBF;
            border-radius: 10px;
            padding: 0.65rem 0.75rem;
            margin-bottom: 0.55rem;
        }

        .agentic-title {
            color: #1B397B;
            font-weight: 700;
            font-size: 0.82rem;
            margin-bottom: 0.25rem;
        }

        .agentic-meta {
            color: #55739F;
            font-size: 0.75rem;
            margin-bottom: 0.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
