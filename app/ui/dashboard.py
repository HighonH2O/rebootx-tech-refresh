"""Dashboard page for the Streamlit UI."""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go

from .components import render_dashboard_hero, render_kpi_grid, render_status_banner


RECENT_ASSESSMENTS = [
    {
        "timestamp": "2026-07-20 09:30",
        "technology": "Python",
        "risk": "High",
        "summary": "Python 3.9 → 3.12 with pandas and Airflow dependencies",
    },
    {
        "timestamp": "2026-07-19 14:15",
        "technology": "PostgreSQL",
        "risk": "Medium",
        "summary": "PostgreSQL 13 → 15 compatibility review for BI reporting layer",
    },
    {
        "timestamp": "2026-07-18 11:00",
        "technology": "MWAA",
        "risk": "High",
        "summary": "Airflow provider drift and DAG migration review",
    },
]


def render_dashboard(api_client) -> None:
    render_dashboard_hero(
        "Upgrade intelligence at a glance",
        "Monitor health, review recent assessments, and explore the knowledge landscape behind every recommendation.",
    )

    try:
        health = api_client.get_health()
        knowledge_stats = api_client.get_knowledge_stats()
    except Exception as exc:  # pragma: no cover - UI feedback path
        health = None
        knowledge_stats = {}
        render_status_banner(f"Connectivity check failed: {exc}", "error")

    metrics = [
        {
            "label": "Backend",
            "value": "Healthy" if health else "Offline",
            "helper": health.get("app_name", "RebootX") if health else "Unable to reach API",
        },
        {
            "label": "Knowledge docs",
            "value": str(knowledge_stats.get("total_documents", 0)),
            "helper": "Indexed compatibility documents",
        },
        {
            "label": "Ollama",
            "value": "Available" if health and health.get("ollama_available") else "Fallback",
            "helper": "AI reasoning or rules fallback",
        },
        {
            "label": "Source files",
            "value": str(knowledge_stats.get("source_files", 0)),
            "helper": "JSON knowledge sources",
        },
    ]
    render_kpi_grid(metrics)

    col_left, col_right = st.columns([1.2, 0.8])
    with col_left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("System health")
        health_values = [100, 88, 92]
        labels = ["API", "Ollama", "Knowledge"]
        fig = go.Figure(
            data=[go.Bar(x=labels, y=health_values, marker_color=["#6366f1", "#38bdf8", "#10b981"])]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            showlegend=False,
            xaxis=dict(showgrid=False, color="#cbd5e1"),
            yaxis=dict(showgrid=False, color="#cbd5e1"),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Status snapshot")
        if health:
            render_status_banner("Backend is reachable and serving the assessment API.", "success")
        else:
            render_status_banner("Backend is unavailable; the UI is showing offline state.", "error")
        st.write("- FastAPI assessment endpoint available")
        st.write("- ChromaDB knowledge retrieval enabled")
        st.write("- Ollama integration is optional and falls back gracefully")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Recent assessments")
    st.dataframe(
        st.session_state.get("recent_assessments", RECENT_ASSESSMENTS),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col_supported, col_architecture = st.columns(2)
    with col_supported:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Supported technologies")
        tech_labels = ["Python", "Database", "EMR", "MWAA"]
        tech_values = [
            knowledge_stats.get("by_technology_type", {}).get("python", 0),
            knowledge_stats.get("by_technology_type", {}).get("database", 0),
            knowledge_stats.get("by_technology_type", {}).get("emr", 0),
            knowledge_stats.get("by_technology_type", {}).get("mwaa", 0),
        ]
        tech_fig = go.Figure(data=[go.Pie(labels=tech_labels, values=tech_values, hole=0.38, marker_colors=["#6366f1", "#38bdf8", "#10b981", "#f59e0b"])])
        tech_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            showlegend=True,
        )
        st.plotly_chart(tech_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_architecture:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Architecture overview")
        st.write("The platform follows a layered design with a FastAPI backend, a ChromaDB knowledge layer, and optional local LLM reasoning through Ollama.")
        st.markdown(
            """
            <ul>
                <li><strong>UI:</strong> Streamlit control center</li>
                <li><strong>API:</strong> FastAPI assessment and capture endpoints</li>
                <li><strong>Knowledge:</strong> JSON docs + ChromaDB retrieval</li>
                <li><strong>Reasoning:</strong> Ollama AI or rules fallback</li>
            </ul>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
