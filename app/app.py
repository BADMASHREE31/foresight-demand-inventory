import os
import sys
import streamlit as st

# Setup path: add parent directory and app directory to sys.path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(APP_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui_theme import apply_custom_css, render_sidebar, render_hero_banner, render_kpi_card

st.set_page_config(
    page_title="FORESIGHT - Demand & Inventory Intelligence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Corporate UI Theme
apply_custom_css()
render_sidebar()

# Landing Page Content
render_hero_banner(
    "FORESIGHT — Demand & Inventory Intelligence Platform",
    "NorthBay Living Operations Briefing & Executive Decision Suite"
)

st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.8rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
    <h3 style="color: #0F172A; font-weight: 700; margin-top: 0; margin-bottom: 0.5rem; font-size: 1.2rem;">
        Welcome to FORESIGHT
    </h3>
    <p style="color: #475569; font-size: 0.95rem; margin-bottom: 0;">
        FORESIGHT integrates historical D2C sales telemetry, machine learning demand forecasting (HistGradientBoosting), and automated stockout/overstock risk algorithms to guide supply chain decision-making for NorthBay Living.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 1rem;'>🚀 Available Intelligence Modules</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    render_kpi_card(
        title="Executive Overview",
        value="Briefing Dashboard",
        subtext="High-level demand trends, priority actions, and aggregated financial exposure.",
        icon="📊",
        border_color="#2563EB",
        badge_text="MANAGEMENT",
        badge_class="badge-healthy"
    )

with col2:
    render_kpi_card(
        title="Demand Forecast",
        value="8-Week Horizon",
        subtext="SKU-level weekly projections with 80% confidence bounds and baseline checks.",
        icon="📈",
        border_color="#4F46E5",
        badge_text="OPERATIONS",
        badge_class="badge-healthy"
    )

with col3:
    render_kpi_card(
        title="Inventory Risk",
        value="Decision Matrix",
        subtext="2D Stockout vs Overstock risk scoring quadrant and actionable risk register.",
        icon="🎯",
        border_color="#DC2626",
        badge_text="RISK SCORING",
        badge_class="badge-reorder-now"
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

col4, col5, col6, col7 = st.columns(4)

with col4:
    render_kpi_card(
        title="SKU Explorer",
        value="Product Deep-Dive",
        subtext="Individual SKU profiles, stock telemetry, dynamic risk explanations.",
        icon="🔍",
        border_color="#7C3AED",
        badge_text="SKU LEVEL",
        badge_class="badge-investigate"
    )

with col5:
    render_kpi_card(
        title="Business Impact",
        value="Financial Exposure",
        subtext="Quantified Rupee revenue at risk and capital locked in excess stock.",
        icon="💰",
        border_color="#D97706",
        badge_text="FINANCE",
        badge_class="badge-markdown-clear"
    )

with col6:
    render_kpi_card(
        title="Data Quality",
        value="Audit & Hygiene",
        subtext="Schema validation, deduplication logs, and dataset completeness tracking.",
        icon="🛡️",
        border_color="#0D9488",
        badge_text="PIPELINE",
        badge_class="badge-healthy"
    )

with col7:
    render_kpi_card(
        title="Model Evaluation",
        value="ML Performance",
        subtext="Rolling-origin cross-validation, WAPE metrics, and baseline comparisons.",
        icon="🎯",
        border_color="#2563EB",
        badge_text="DATA SCIENCE",
        badge_class="badge-healthy"
    )

st.info("👈 Select any module from the sidebar navigation to view details.")
