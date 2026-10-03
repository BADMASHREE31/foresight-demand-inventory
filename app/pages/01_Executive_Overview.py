import os
import sys
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(APP_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import PROCESSED_DATA_DIR, MODEL_ARTIFACTS_DIR
from src.utils import format_inr
from ui_theme import apply_custom_css, render_sidebar, render_page_header, render_hero_banner, render_kpi_card, render_risk_badge, get_plotly_layout

st.set_page_config(page_title="Executive Overview - FORESIGHT", layout="wide")
apply_custom_css()
render_sidebar()

render_page_header(
    title="Executive Overview",
    subtitle="NorthBay Living Operations Briefing — Key Inventory & Demand KPIs",
    status_text="Data Pipeline Connected"
)

render_hero_banner(
    title="FORESIGHT — Inventory decisions powered by demand intelligence",
    subtitle="Understand future demand, identify inventory risk, and prioritize business action."
)

@st.cache_data
def load_data():
    impact_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'risk_impact_matrix.csv'))
    forecast_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'forecast_outputs.csv'))
    
    summary_path = os.path.join(MODEL_ARTIFACTS_DIR, 'business_summary.json')
    meta_path = os.path.join(MODEL_ARTIFACTS_DIR, 'selection_metadata.json')
    
    summary = {}
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            summary = json.load(f)
            
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
            
    return impact_df, forecast_df, summary, meta

try:
    df_impact, df_forecast, summary, meta = load_data()
except Exception as e:
    st.error(f"Please run the pipeline first using `python run_pipeline.py`. Details: {e}")
    st.stop()

# Top KPI Cards (6 columns layout)
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    tot_skus = summary.get('total_skus', 'Data unavailable')
    render_kpi_card(
        title="Total Active SKUs",
        value=str(tot_skus),
        subtext="Tracked product catalog",
        icon="📦",
        border_color="#2563EB",
        badge_text="CATALOG",
        badge_class="badge-healthy"
    )

with c2:
    render_kpi_card(
        title="Forecast Horizon",
        value="8 Weeks",
        subtext="Weekly rolling forecast",
        icon="📅",
        border_color="#4F46E5",
        badge_text="PROJECTION",
        badge_class="badge-healthy"
    )

with c3:
    reorder_count = summary.get('reorder_skus_count', 'Data unavailable')
    render_kpi_card(
        title="Stockout Risk SKUs",
        value=f"{reorder_count} SKUs",
        subtext="Immediate reorder needed",
        icon="🚨",
        border_color="#DC2626",
        badge_text="CRITICAL",
        badge_class="badge-reorder-now"
    )

with c4:
    markdown_count = summary.get('markdown_skus_count', 'Data unavailable')
    render_kpi_card(
        title="Overstock Risk SKUs",
        value=f"{markdown_count} SKUs",
        subtext="Excess inventory capital",
        icon="⚠️",
        border_color="#D97706",
        badge_text="EXCESS",
        badge_class="badge-markdown-clear"
    )

with c5:
    rev_risk = summary.get('total_revenue_at_risk', 0)
    cap_lock = summary.get('total_capital_locked', 0)
    tot_impact = rev_risk + cap_lock
    render_kpi_card(
        title="Est. Business Impact",
        value=format_inr(tot_impact) if tot_impact else "Data unavailable",
        subtext="Combined financial exposure",
        icon="💰",
        border_color="#7C3AED",
        badge_text="FINANCIAL RISK",
        badge_class="badge-investigate"
    )

with c6:
    wape_val = f"{meta.get('final_wape', 0) * 100:.1f}%" if 'final_wape' in meta else "Data unavailable"
    render_kpi_card(
        title="Model WAPE",
        value=wape_val,
        subtext="Weighted forecast error",
        icon="🎯",
        border_color="#0D9488",
        badge_text=meta.get('status', 'BEATS BASELINE'),
        badge_class="badge-healthy"
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# 1. Inventory Health Summary Grid
st.markdown("""
<div class="content-card">
    <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 0.8rem;">
        🩺 Inventory Health Breakdown
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
        <div style="background-color: #D1FAE5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 0.9rem; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #059669; text-transform: uppercase;">HEALTHY INVENTORY</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #065F46; margin-top: 0.2rem;">{} SKUs</div>
        </div>
        <div style="background-color: #FEE2E2; border: 1px solid #FCA5A5; border-radius: 8px; padding: 0.9rem; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #DC2626; text-transform: uppercase;">REORDER NOW</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #991B1B; margin-top: 0.2rem;">{} SKUs</div>
        </div>
        <div style="background-color: #FEF9C3; border: 1px solid #FEF08A; border-radius: 8px; padding: 0.9rem; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #CA8A04; text-transform: uppercase;">MONITOR</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #854D0E; margin-top: 0.2rem;">0 SKUs</div>
        </div>
        <div style="background-color: #FEF3C7; border: 1px solid #FDE68A; border-radius: 8px; padding: 0.9rem; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #D97706; text-transform: uppercase;">MARKDOWN / CLEAR</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #92400E; margin-top: 0.2rem;">{} SKUs</div>
        </div>
        <div style="background-color: #F3E8FF; border: 1px solid #DDD6FE; border-radius: 8px; padding: 0.9rem; text-align: center;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #7C3AED; text-transform: uppercase;">INVESTIGATE</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #5B21B6; margin-top: 0.2rem;">{} SKUs</div>
        </div>
    </div>
</div>
""".format(
    summary.get('healthy_skus_count', 0),
    summary.get('reorder_skus_count', 0),
    summary.get('markdown_skus_count', 0),
    summary.get('investigate_skus_count', 0)
), unsafe_allow_html=True)

# 2. Demand Trend & Action Quadrant Charts
col_left, col_right = st.columns([6, 4])

with col_left:
    st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.5rem;'>📈 8-Week Projected Demand Trend by Category</h4>", unsafe_allow_html=True)
    df_merged = df_forecast.merge(df_impact[['sku_id', 'category']], on='sku_id', how='left')
    df_cat_trend = df_merged.groupby(['forecast_week', 'category'])['forecast'].sum().reset_index()
    
    fig_trend = px.line(
        df_cat_trend,
        x='forecast_week',
        y='forecast',
        color='category',
        markers=True,
        color_discrete_sequence=['#2563EB', '#0D9488', '#D97706', '#7C3AED']
    )
    
    layout = get_plotly_layout("Weekly Demand Units per Category")
    layout['height'] = 380
    layout['hovermode'] = "x unified"
    fig_trend.update_layout(**layout)
    st.plotly_chart(fig_trend, use_container_width=True)

with col_right:
    st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.5rem;'>🎯 Inventory Decision Distribution</h4>", unsafe_allow_html=True)
    action_counts = df_impact['recommended_action'].value_counts().reset_index()
    action_counts.columns = ['Recommended Action', 'SKU Count']

    fig_pie = px.pie(
        action_counts,
        names='Recommended Action',
        values='SKU Count',
        color='Recommended Action',
        color_discrete_map={
            'REORDER NOW': '#DC2626',
            'MARKDOWN / CLEAR': '#D97706',
            'INVESTIGATE': '#7C3AED',
            'HEALTHY': '#059669'
        },
        hole=0.55
    )
    
    layout_pie = get_plotly_layout("SKUs by Recommended Action Quadrant")
    layout_pie['height'] = 380
    fig_pie.update_layout(**layout_pie)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# 3. Priority Operational Actions
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>⚡ Immediate Operations Priority Action List</h4>", unsafe_allow_html=True)

tab_reorder, tab_markdown = st.tabs([
    "🔥 Top Stockout Risk Candidates (Reorder Now)",
    "📦 Top Overstock Candidates (Capital Tied Up)"
])

with tab_reorder:
    top_reorder = df_impact[df_impact['recommended_action'] == 'REORDER NOW'].sort_values('revenue_at_risk', ascending=False).head(5)
    if len(top_reorder) > 0:
        st.dataframe(
            top_reorder[['sku_id', 'category', 'on_hand_units', 'on_order_units', 'lead_time_days', 'lead_time_demand', 'revenue_at_risk', 'business_reason']],
            column_config={
                'sku_id': "SKU Identifier",
                'category': "Category",
                'on_hand_units': st.column_config.NumberColumn("On-Hand Stock", format="%d units"),
                'on_order_units': st.column_config.NumberColumn("On-Order Stock", format="%d units"),
                'lead_time_days': st.column_config.NumberColumn("Lead Time", format="%d days"),
                'lead_time_demand': st.column_config.NumberColumn("Lead Time Demand", format="%.0f units"),
                'revenue_at_risk': st.column_config.NumberColumn("Revenue at Risk (₹)", format="₹%.2f"),
                'business_reason': "Operational Rationale"
            },
            use_container_width=True
        )
    else:
        st.success("✅ Data verified: No SKUs currently require urgent reordering.")

with tab_markdown:
    top_markdown = df_impact[df_impact['recommended_action'] == 'MARKDOWN / CLEAR'].sort_values('capital_locked', ascending=False).head(5)
    if len(top_markdown) > 0:
        st.dataframe(
            top_markdown[['sku_id', 'category', 'on_hand_units', 'forecast_8w_demand', 'overstock_ratio', 'capital_locked', 'business_reason']],
            column_config={
                'sku_id': "SKU Identifier",
                'category': "Category",
                'on_hand_units': st.column_config.NumberColumn("On-Hand Stock", format="%d units"),
                'forecast_8w_demand': st.column_config.NumberColumn("8-Wk Demand", format="%.0f units"),
                'overstock_ratio': st.column_config.NumberColumn("Overstock Coverage", format="%.1fx"),
                'capital_locked': st.column_config.NumberColumn("Capital Tied Up (₹)", format="₹%.2f"),
                'business_reason': "Operational Rationale"
            },
            use_container_width=True
        )
    else:
        st.info("ℹ️ No SKUs currently require markdown clearing.")
