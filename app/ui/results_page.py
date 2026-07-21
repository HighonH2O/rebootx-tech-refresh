"""Results page for Streamlit assessment output."""

from __future__ import annotations

import json
from html import escape

import plotly.graph_objects as go
import streamlit as st

from app.ui.components import render_header, render_panel, render_status_banner


def _risk_color(level: str | None) -> str:
    mapping = {
        "Low": "#10b981",
        "Medium": "#f59e0b",
        "High": "#ef4444",
        "Critical": "#b91c1c",
    }
    return mapping.get(level or "", "#6366f1")


def render_results_content() -> None:
    render_header("Results", "Inspect the latest assessment output with charts, risks, and export actions.")
    assessment = st.session_state.get("latest_assessment")

    if not assessment:
        render_panel("No assessment yet", "Run a new assessment to populate this report view.")
        render_status_banner("No assessment data available yet. Submit a new assessment from the Assessment page.", "info")
        return

    render_panel(
        "Assessment results",
        "Review the generated risk report, supporting recommendations, and exportable report content.",
    )

    overall_risk = str(assessment.get("overall_risk", "Medium")).capitalize()
    risk_level = overall_risk if overall_risk in {"Low", "Medium", "High", "Critical"} else "Medium"
    summary_text = assessment.get("summary", "No executive summary was returned by the backend.")
    recommendations = assessment.get("recommended_actions", []) or ["No specific recommended actions were returned by the backend."]
    knowledge_sources = assessment.get("knowledge_sources") or [
        "RebootX knowledge documents",
        "ChromaDB retrieval context",
        "Optional Ollama reasoning",
    ]

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Overall risk score")
    risk_badge = f"<span class='risk-badge {risk_level.lower()}'>{risk_level}</span>"
    st.markdown(f"<p><strong>Risk badge:</strong> {risk_badge}</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([0.8, 1.2])
    with col1:
        gauge_value = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(risk_level, 2)
        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=gauge_value,
                number={"suffix": ""},
                gauge={
                    "axis": {"range": [0, 4], "tickvals": [1, 2, 3, 4], "ticktext": ["Low", "Medium", "High", "Critical"]},
                    "bar": {"color": _risk_color(risk_level)},
                    "steps": [
                        {"range": [0, 1], "color": "#1f2937"},
                        {"range": [1, 2], "color": "#374151"},
                        {"range": [2, 3], "color": "#4b5563"},
                        {"range": [3, 4], "color": "#6b7280"},
                    ],
                },
            )
        )
        gauge.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(gauge, use_container_width=True)
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Executive summary</div>
                <div class="metric-value">{risk_level}</div>
                <div class="metric-helper">{escape(summary_text)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("**Technology:**", assessment.get("technology_type", "n/a"))
        st.write("**Version range:**", f"{assessment.get('current_version', 'n/a')} → {assessment.get('target_version', 'n/a')}")
        st.write("**Confidence:**", assessment.get("confidence", "Medium"))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Severity distribution")
    risk_levels = [str(risk.get("risk_level", "Medium")).capitalize() for risk in assessment.get("risks", [])]
    counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for level in risk_levels:
        counts[level] = counts.get(level, 0) + 1
    donut = go.Figure(
        go.Pie(
            labels=list(counts.keys()),
            values=list(counts.values()),
            hole=0.48,
            marker_colors=["#10b981", "#f59e0b", "#ef4444", "#b91c1c"],
            textinfo="label+value",
        )
    )
    donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
        showlegend=True,
    )
    st.plotly_chart(donut, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Risk cards")
    for risk in assessment.get("risks", []):
        with st.expander(risk.get("title", "Risk detail")):
            st.write(f"**Category:** {risk.get('category', 'n/a')}")
            st.write(f"**Level:** {risk.get('risk_level', 'Medium')}")
            st.write(risk.get("explanation", ""))
            st.write(f"**Recommendation:** {risk.get('recommendation', '')}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Recommendations")
    for item in recommendations:
        st.write(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Validation checklist")
    checklist = [
        "Review dependency compatibility",
        "Run regression and integration tests",
        "Confirm rollback readiness",
        "Validate environment-specific configurations",
    ]
    for item in checklist:
        st.checkbox(item, value=True, disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Retrieved knowledge sources")
    for source in knowledge_sources:
        st.write(f"- {source}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Download report")
    col_actions1, col_actions2, col_actions3 = st.columns(3)
    with col_actions1:
        st.download_button(
            "Download HTML",
            data=f"<html><body><pre>{escape(json.dumps(assessment, indent=2, default=str))}</pre></body></html>",
            file_name="rebootx-assessment.html",
            mime="text/html",
        )
    with col_actions2:
        st.download_button(
            "Download PDF",
            data="PDF export is prepared for the next iteration of the reporting workflow.",
            file_name="rebootx-assessment.pdf",
            mime="application/pdf",
        )
    with col_actions3:
        st.download_button(
            "Download JSON",
            data=json.dumps(assessment, indent=2, default=str),
            file_name="rebootx-assessment.json",
            mime="application/json",
        )
    st.markdown("</div>", unsafe_allow_html=True)
