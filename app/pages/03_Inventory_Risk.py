import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(APP_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import PROCESSED_DATA_DIR
from src.utils import format_inr
from ui_theme import apply_custom_css, render_sidebar, render_page_header, render_kpi_card, render_risk_badge, get_plotly_layout

st.set_page_config(page_title="Inventory Risk - FORESIGHT", layout="wide")
apply_custom_css()
render_sidebar()

render_page_header(
    title="Inventory Risk & Decisioning Matrix",
    subtitle="Stockout & Overstock Risk scoring combined with actionable operational recommendations",
    status_text="Risk Scoring Engine Active"
)

@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'risk_impact_matrix.csv'))

df_risk = load_data()

# Top Risk Cards
counts = df_risk['recommended_action'].value_counts()
reorder_c = counts.get('REORDER NOW', 0)
markdown_c = counts.get('MARKDOWN / CLEAR', 0)
healthy_c = counts.get('HEALTHY', 0)
investigate_c = counts.get('INVESTIGATE', 0)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card(
        title="Stockout Risk",
        value=f"{reorder_c} SKUs",
        subtext="Stock covers < lead time demand",
        icon="🚨",
        border_color="#DC2626",
        badge_text="REORDER NOW",
        badge_class="badge-reorder-now"
    )

with c2:
    render_kpi_card(
        title="Overstock Risk",
        value=f"{markdown_c} SKUs",
        subtext="Stock > 2.5x 8-week forecast",
        icon="📦",
        border_color="#D97706",
        badge_text="MARKDOWN / CLEAR",
        badge_class="badge-markdown-clear"
    )

with c3:
    render_kpi_card(
        title="Healthy Inventory",
        value=f"{healthy_c} SKUs",
        subtext="Coverage matches forecast",
        icon="✅",
        border_color="#059669",
        badge_text="BALANCED",
        badge_class="badge-healthy"
    )

with c4:
    render_kpi_card(
        title="Items Requiring Review",
        value=f"{investigate_c} SKUs",
        subtext="Erratic demand or batching",
        icon="🔍",
        border_color="#7C3AED",
        badge_text="INVESTIGATE",
        badge_class="badge-investigate"
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# 2D Interactive Decisioning Grid Section
st.markdown("""
<div class="content-card">
    <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem;">
        📊 2D Interactive Inventory Decisioning Grid
    </div>
    <div style="font-size: 0.88rem; color: #64748B; margin-bottom: 1rem;">
        Maps SKU position across Stockout Risk (y-axis) vs Overstock Risk (x-axis). Bubble size reflects Rupee Revenue at Risk.
    </div>
</div>
""", unsafe_allow_html=True)

# Build 2D Scatter Chart
fig_grid = px.scatter(
    df_risk,
    x='overstock_risk_score',
    y='stockout_risk_score',
    size='revenue_at_risk',
    color='recommended_action',
    hover_name='sku_id',
    hover_data={
        'category': True,
        'on_hand_units': True,
        'lead_time_demand': ':.1f',
        'revenue_at_risk': ':.2f',
        'business_reason': True
    },
    color_discrete_map={
        'REORDER NOW': '#DC2626',
        'MARKDOWN / CLEAR': '#D97706',
        'INVESTIGATE': '#7C3AED',
        'HEALTHY': '#059669'
    },
    size_max=38
)

# Add Quadrant Reference Lines & Labels
fig_grid.add_hline(y=0.5, line_dash="dash", line_color="#94A3B8")
fig_grid.add_vline(x=0.5, line_dash="dash", line_color="#94A3B8")

fig_grid.add_annotation(x=0.15, y=0.9, text="REORDER NOW", showarrow=False, font=dict(color="#DC2626", size=13, family="Inter, sans-serif"))
fig_grid.add_annotation(x=0.85, y=0.1, text="MARKDOWN / CLEAR", showarrow=False, font=dict(color="#D97706", size=13, family="Inter, sans-serif"))
fig_grid.add_annotation(x=0.85, y=0.9, text="INVESTIGATE", showarrow=False, font=dict(color="#7C3AED", size=13, family="Inter, sans-serif"))
fig_grid.add_annotation(x=0.15, y=0.1, text="HEALTHY", showarrow=False, font=dict(color="#059669", size=13, family="Inter, sans-serif"))

layout = get_plotly_layout("SKU Inventory Decisioning Grid (Stockout vs Overstock Risk)")
layout['height'] = 520
layout['xaxis']['title'] = "Overstock Risk Score →"
layout['yaxis']['title'] = "Stockout Risk Score →"
fig_grid.update_layout(**layout)

st.plotly_chart(fig_grid, use_container_width=True)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Risk Action Filter Table
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>📋 Actionable Inventory Risk Register</h4>", unsafe_allow_html=True)

selected_action = st.radio(
    "Filter Action Category",
    ["ALL", "REORDER NOW", "MARKDOWN / CLEAR", "INVESTIGATE", "HEALTHY"],
    horizontal=True
)

filtered_df = df_risk.copy()
if selected_action != "ALL":
    filtered_df = filtered_df[filtered_df['recommended_action'] == selected_action]

st.dataframe(
    filtered_df[[
        'sku_id', 'category', 'subcategory', 'on_hand_units', 'on_order_units',
        'lead_time_days', 'forecast_8w_demand', 'lead_time_demand',
        'stockout_risk_level', 'recommended_action', 'revenue_at_risk', 'capital_locked', 'business_reason'
    ]],
    column_config={
        'sku_id': "SKU Identifier",
        'category': "Category",
        'subcategory': "Subcategory",
        'on_hand_units': st.column_config.NumberColumn("On Hand Stock", format="%d units"),
        'on_order_units': st.column_config.NumberColumn("On Order Stock", format="%d units"),
        'lead_time_days': st.column_config.NumberColumn("Lead Time", format="%d days"),
        'forecast_8w_demand': st.column_config.NumberColumn("8-Wk Forecast", format="%.0f units"),
        'lead_time_demand': st.column_config.NumberColumn("Lead Time Demand", format="%.1f units"),
        'stockout_risk_level': "Stockout Risk",
        'recommended_action': "Action Badge",
        'revenue_at_risk': st.column_config.NumberColumn("Revenue at Risk (₹)", format="₹%.2f"),
        'capital_locked': st.column_config.NumberColumn("Capital Locked (₹)", format="₹%.2f"),
        'business_reason': "Operational Explanation"
    },
    use_container_width=True
)
