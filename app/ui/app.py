"""Streamlit multipage frontend foundation for RebootX."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import streamlit as st

from app.ui.api_client import APIClient, get_api_base_url
from app.ui.components import render_footer, render_status_banner
from app.ui.pages import (
    render_about_page,
    render_assessment_page,
    render_dashboard_page,
    render_reports_page,
    render_results_page,
)
from app.ui.styles import load_css


def main() -> None:
    st.set_page_config(page_title="RebootX", page_icon="🛠️", layout="wide")
    load_css()

    api_base_url = st.sidebar.text_input("Backend URL", value=get_api_base_url(), key="backend_url")
    api_client = APIClient(api_base_url)

    st.sidebar.markdown("### 🧭 Navigation")
    st.sidebar.caption("RebootX control center")
    pages = {
        "Dashboard": lambda: render_dashboard_page(),
        "New Assessment": lambda: render_assessment_page(api_client),
        "Results": lambda: render_results_page(),
        "Reports": lambda: render_reports_page(),
        "About": lambda: render_about_page(),
    }

    page_names = list(pages.keys())
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Dashboard"

    selected_page = st.sidebar.radio(
        "",
        page_names,
        index=page_names.index(st.session_state["active_page"]),
        label_visibility="collapsed",
        key="page_selector",
    )
    st.session_state["active_page"] = selected_page

    st.sidebar.divider()
    st.sidebar.header("Controls")
    if st.sidebar.button("🟢 Check backend health", use_container_width=True):
        try:
            health = api_client.get_health()
            render_status_banner(f"Backend healthy: {health.get('app_name', 'RebootX')}", "success")
        except Exception as exc:  # pragma: no cover - UI feedback path
            render_status_banner(f"Backend unavailable: {exc}", "error")

    pages[selected_page]()
    render_footer()


if __name__ == "__main__":
    main()
