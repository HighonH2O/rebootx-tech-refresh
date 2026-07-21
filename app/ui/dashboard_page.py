"""Dashboard page implementation for the multipage Streamlit frontend."""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go

from app.ui.components import render_metric_card, render_panel, render_status_banner


RECENT_ASSESSMENTS = [
    {"timestamp": "2026-07-20 09:30", "technology": "Python", "risk": "High", "summary": "Python 3.9 -> 3.12 with pandas and Airflow dependencies"},
    {"timestamp": "2026-07-19 14:15", "technology": "Database", "risk": "Medium", "summary": "PostgreSQL 13 -> 15 compatibility review"},
    {"timestamp": "2026-07-18 11:00", "technology": "MWAA", "risk": "High", "summary": "Airflow provider drift and DAG migration review"},
]


def render_dashboard_content() -> None:
    render_header("Dashboard", "Enterprise readiness, health, and recent activity at a glance.")
    render_panel("Operational overview", "Monitor system health, recent assessments, and supported upgrade domains.")

    metrics = [
        ("Assessments", "24", "Completed this month"),
        ("Knowledge Docs", "21", "Indexed compatibility references"),
        ("Health", "99%", "API + retrieval availability"),
        ("Coverage", "4", "Supported technology domains"),
    ]

    cols = st.columns(4)
    for col, (label, value, helper) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-helper">{helper}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    col_left, col_right = st.columns([1.25, 0.75])
    with col_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("System health")
        health_data = [100, 88, 92]
        health_labels = ["API", "Knowledge", "Ollama"]
        fig = go.Figure(data=[go.Bar(x=health_labels, y=health_data, marker_color=["#6366f1", "#38bdf8", "#10b981"])])
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            showlegend=False,
            xaxis=dict(color="#cbd5e1"),
            yaxis=dict(color="#cbd5e1"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Live status")
        render_status_banner("Backend API connected and ready for assessments.", "success")
        render_status_banner("Knowledge base available for retrieval and reasoning.", "info")
        st.write("- FastAPI assessment endpoints")
        st.write("- ChromaDB knowledge retrieval")
        st.write("- Optional Ollama reasoning")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Recent assessments")
    st.dataframe(
        RECENT_ASSESSMENTS,
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Supported technologies")
        tech_labels = ["Python", "Database", "EMR", "MWAA"]
        tech_values = [8, 6, 4, 3]
        tech_fig = go.Figure(data=[go.Pie(labels=tech_labels, values=tech_values, hole=0.42, marker_colors=["#6366f1", "#38bdf8", "#10b981", "#f59e0b"])])
        tech_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=250,
            showlegend=True,
        )
        st.plotly_chart(tech_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with bottom_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Architecture snapshot")
        st.write("RebootX combines a FastAPI backend, a retrieval layer backed by ChromaDB, and a modular Streamlit frontend for enterprise workflows.")
        st.write("- UI shell and multipage navigation")
        st.write("- Reusable layout components")
        st.write("- Backend integration point remains untouched")
        st.markdown("</div>", unsafe_allow_html=True)
