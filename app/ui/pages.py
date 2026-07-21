"""Page entry points for the Streamlit multipage frontend foundation."""

from __future__ import annotations

import streamlit as st

from app.ui.api_client import APIClient
from app.ui.assessment_page import render_assessment_page as render_assessment_content
from app.ui.components import render_footer, render_header, render_panel, render_status_banner
from app.ui.dashboard_page import render_dashboard_content
from app.ui.results_page import render_results_content


def render_dashboard_page() -> None:
    render_dashboard_content()


def render_assessment_page(api_client: APIClient | None = None) -> None:
    render_assessment_content(api_client)


def render_results_page() -> None:
    render_results_content()


def render_reports_page() -> None:
    render_header("Reports", "Review saved or generated reports for stakeholders.")
    render_panel("Reports list", "Report history and export actions will be added here in a later phase.")
    st.info("Reports placeholder")


def render_about_page() -> None:
    render_header("About", "Learn about the RebootX platform and its architecture.")
    render_panel("About RebootX", "This frontend foundation is designed to be modular and reusable.")
    render_status_banner("Phase 1 focuses on architecture, layout, and reusable components.", "info")


def render_footer_section() -> None:
    render_footer()
