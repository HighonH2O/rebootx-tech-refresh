"""Reusable UI components for the Streamlit interface."""

from __future__ import annotations

import streamlit as st


def render_header(title: str, subtitle: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <h1 style="margin:0 0 0.35rem 0; font-size: 1.8rem;">🛠️ {title}</h1>
            <p style="margin:0; color:#cbd5e1;">{subtitle or 'RebootX frontend foundation with reusable layout components.'}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, helper: str = "") -> None:
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


def render_status_banner(message: str, kind: str = "info") -> None:
    st.markdown(
        f"""
        <div class="status-box {kind}">{message}</div>
        """,
        unsafe_allow_html=True,
    )


def render_risk_badge(risk: str | None) -> str:
    risk_value = (risk or "unknown").lower()
    return f"<span class='risk-badge {risk_value}'>{risk_value.capitalize()}</span>"


def render_dashboard_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <h1 style="margin:0 0 0.35rem 0; font-size: 1.8rem;">{title}</h1>
            <p style="margin:0; color:#cbd5e1;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_grid(metrics: list[dict]) -> None:
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{metric['label']}</div>
                    <div class="metric-value">{metric['value']}</div>
                    <div class="metric-helper">{metric['helper']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_panel(title: str, subtitle: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <h2 style="margin:0 0 0.25rem 0;">{title}</h2>
            <p style="margin:0; color:#cbd5e1;">{subtitle or ''}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_assessment_result(assessment: dict) -> None:
    if not assessment:
        return

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Assessment outcome")
    st.markdown(
        f"<p><strong>Overall risk:</strong> {render_risk_badge(assessment.get('overall_risk'))}</p>",
        unsafe_allow_html=True,
    )
    st.write(assessment.get("summary", "No summary returned."))
    if assessment.get("risks"):
        st.write("### Risks")
        for risk in assessment["risks"]:
            with st.expander(risk.get("title", "Risk detail")):
                st.write(f"**Level:** {risk.get('risk_level')}")
                st.write(risk.get("explanation", ""))
                st.write(f"**Recommendation:** {risk.get('recommendation', '')}")
    st.write("### Recommended actions")
    for action in assessment.get("recommended_actions", []):
        st.write(f"- {action}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_capture_result(captured: dict) -> None:
    if not captured:
        return

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Captured input")
    st.write(f"**Technology:** {captured.get('technology_type')}")
    st.write(f"**Current version:** {captured.get('current_version')}")
    st.write(f"**Target version:** {captured.get('target_version')}")
    if captured.get("dependencies"):
        st.write("**Dependencies:**")
        for dep in captured["dependencies"]:
            st.write(f"- {dep}")
    if captured.get("integrations"):
        st.write("**Integrations:**")
        for integration in captured["integrations"]:
            st.write(f"- {integration}")
    if captured.get("warnings"):
        st.write("**Warnings:**")
        for warning in captured["warnings"]:
            st.write(f"- {warning}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_knowledge_stats(stats: dict) -> None:
    if not stats:
        return

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Knowledge base")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Documents", str(stats.get("total_documents", 0)), "Loaded knowledge units")
    with col2:
        render_metric_card("Source files", str(stats.get("source_files", 0)), "JSON files indexed")
    with col3:
        render_metric_card("Chromadb entries", str(stats.get("chroma_documents", 0)), "Persistent vector store")
    st.write("**By technology:**")
    for key, value in stats.get("by_technology_type", {}).items():
        st.write(f"- {key}: {value}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown("""
    <div class="section-card" style="margin-top: 1rem; text-align:center; color:#94a3b8;">
        RebootX frontend foundation • modular UI • backend untouched
    </div>
    """, unsafe_allow_html=True)
