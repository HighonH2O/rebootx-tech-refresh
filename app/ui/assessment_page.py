"""New assessment page for the Streamlit frontend."""

from __future__ import annotations

import time

import streamlit as st

from app.ui.components import render_assessment_result, render_panel, render_status_banner


def _render_progress_workflow() -> None:
    steps = [
        "Building Query",
        "Retrieving Knowledge",
        "Running AI Analysis",
        "Calculating Risk",
        "Generating Report",
    ]
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Assessment workflow")
    for index, step in enumerate(steps, start=1):
        progress = index / len(steps)
        st.markdown(
            f"""
            <div style="margin-bottom: 0.45rem;">
                <div style="display:flex; justify-content:space-between; color:#e2e8f0; font-size:0.95rem; margin-bottom:0.2rem;">
                    <span>{step}</span>
                    <span>{int(progress * 100)}%</span>
                </div>
                <div style="height: 8px; border-radius:999px; background: rgba(148,163,184,0.2); overflow:hidden;">
                    <div style="height:100%; width:{int(progress * 100)}%; background: linear-gradient(90deg, #4f46e5, #38bdf8); border-radius:999px;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_assessment_page(api_client) -> None:
    render_panel(
        "New assessment",
        "Capture the upgrade context below and submit it to the existing backend assessment API.",
    )

    with st.form("assessment_form"):
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Assessment details")

        technology_type = st.selectbox(
            "Technology",
            options=["database", "emr", "python", "mwaa"],
            index=2,
            help="The technology domain being assessed",
        )

        col1, col2 = st.columns(2)
        with col1:
            current_version = st.text_input("Current version", value="Python 3.9")
        with col2:
            target_version = st.text_input("Target version", value="Python 3.12")

        environment = st.selectbox(
            "Environment",
            options=["production", "staging", "development"],
            index=0,
        )

        st.markdown("### Dependency and integration context")
        dependencies_text = st.text_area(
            "Dependencies",
            value="numpy==1.21\npandas==1.3\nsqlalchemy==1.4",
            help="Enter one dependency per line",
        )
        integrations_text = st.text_area(
            "Integrations",
            value="Airflow DAGs\nREST microservices",
            help="Enter one integration per line",
        )

        notes = st.text_area(
            "Notes",
            value="Batch processing pipelines depend on legacy pandas APIs",
            help="Add any upgrade context or assumptions",
        )

        summary = st.empty()
        submitted = st.form_submit_button("Analyze Upgrade", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        payload = {
            "technology_type": technology_type,
            "current_version": current_version,
            "target_version": target_version,
            "dependencies": [item.strip() for item in dependencies_text.splitlines() if item.strip()],
            "integrations": [item.strip() for item in integrations_text.splitlines() if item.strip()],
            "environment": environment,
            "notes": notes,
        }

        summary.markdown(
            f"""
            <div class="section-card">
                <h4 style="margin:0 0 0.3rem 0;">Live summary</h4>
                <p style="margin:0; color:#cbd5e1;">{technology_type.title()} upgrade from {current_version} to {target_version} in {environment}.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            _render_progress_workflow()
            with st.spinner(""):
                for _ in range(2):
                    time.sleep(0.2)
                assessment = api_client.assess_upgrade(payload)
            st.session_state["latest_assessment"] = assessment
            render_assessment_result(assessment)
        except Exception as exc:  # pragma: no cover - UI feedback path
            render_status_banner(f"Assessment failed: {exc}", "error")
