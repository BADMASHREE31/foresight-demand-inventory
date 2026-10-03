import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import PROCESSED_DATA_DIR
from src.utils import format_inr
from app.ui_theme import apply_custom_css, render_sidebar, render_page_header, render_kpi_card, get_plotly_layout

st.set_page_config(page_title="Business Impact - FORESIGHT", layout="wide")
apply_custom_css()
render_sidebar()

render_page_header(
    title="Financial Business Impact",
    subtitle="Quantified Rupee Revenue at Risk from stockouts & capital locked in excess inventory",
    status_text="Financial Impact Engine Active"
)

@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'risk_impact_matrix.csv'))

df_impact = load_data()

tot_rev_risk = df_impact['revenue_at_risk'].sum()
tot_cap_locked = df_impact['capital_locked'].sum()
tot_inv_val = df_impact['inventory_value'].sum()

# Top Financial KPI Summary Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card(
        title="Total Warehouse Inventory Value",
        value=format_inr(tot_inv_val),
        subtext="Total capital tied in current stock",
        icon="🏛️",
        border_color="#2563EB",
        badge_text="WAREHOUSE",
        badge_class="badge-healthy"
    )

with c2:
    render_kpi_card(
        title="Estimated Revenue at Risk",
        value=format_inr(tot_rev_risk),
        subtext="Potential unfulfilled sales loss",
        icon="🚨",
        border_color="#DC2626",
        badge_text="STOCKOUT RISK",
        badge_class="badge-reorder-now"
    )

with c3:
    render_kpi_card(
        title="Estimated Capital Tied Up",
        value=format_inr(tot_cap_locked),
        subtext="Excess inventory value",
        icon="⚠️",
        border_color="#D97706",
        badge_text="OVERSTOCK",
        badge_class="badge-markdown-clear"
    )

with c4:
    ratio = (tot_cap_locked / tot_inv_val * 100.0) if tot_inv_val > 0 else 0
    render_kpi_card(
        title="Capital Lockup Ratio",
        value=f"{ratio:.1f}%",
        subtext="Tied capital vs total inventory",
        icon="📊",
        border_color="#7C3AED",
        badge_text="RATIO",
        badge_class="badge-investigate"
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Category Financial Breakdown Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.5rem;'>🔴 Revenue at Risk by Product Category</h4>", unsafe_allow_html=True)
    cat_risk = df_impact.groupby('category')['revenue_at_risk'].sum().reset_index()
    
    fig_cat_rev = px.bar(
        cat_risk,
        x='category',
        y='revenue_at_risk',
        color='category',
        color_discrete_sequence=['#DC2626', '#D97706', '#2563EB', '#7C3AED'],
        text_auto='.2s'
    )
    
    layout = get_plotly_layout("Potential Stockout Revenue Loss (₹)")
    layout['height'] = 380
    layout['xaxis']['title'] = "Category"
    layout['yaxis']['title'] = "Revenue at Risk (₹)"
    fig_cat_rev.update_layout(**layout)
    st.plotly_chart(fig_cat_rev, use_container_width=True)

with col2:
    st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.5rem;'>🟡 Capital Tied Up by Product Category</h4>", unsafe_allow_html=True)
    cat_locked = df_impact.groupby('category')['capital_locked'].sum().reset_index()
    
    fig_cat_lock = px.bar(
        cat_locked,
        x='category',
        y='capital_locked',
        color='category',
        color_discrete_sequence=['#D97706', '#4F46E5', '#059669', '#2563EB'],
        text_auto='.2s'
    )
    
    layout_lock = get_plotly_layout("Excess Inventory Capital Locked (₹)")
    layout_lock['height'] = 380
    layout_lock['xaxis']['title'] = "Category"
    layout_lock['yaxis']['title'] = "Capital Locked (₹)"
    fig_cat_lock.update_layout(**layout_lock)
    st.plotly_chart(fig_cat_lock, use_container_width=True)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Priority Financial Review List Table
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>🏆 Priority Financial Risk Review List</h4>", unsafe_allow_html=True)

st.dataframe(
    df_impact.sort_values('revenue_at_risk', ascending=False)[[
        'sku_id', 'category', 'recommended_action', 'revenue_at_risk', 'capital_locked', 'on_hand_units', 'lead_time_demand', 'business_reason'
    ]],
    column_config={
        'sku_id': "SKU Identifier",
        'category': "Category",
        'recommended_action': "Action Flag",
        'revenue_at_risk': st.column_config.NumberColumn("Revenue at Risk (₹)", format="₹%.2f"),
        'capital_locked': st.column_config.NumberColumn("Capital Locked (₹)", format="₹%.2f"),
        'on_hand_units': st.column_config.NumberColumn("On-Hand Stock", format="%d units"),
        'lead_time_demand': st.column_config.NumberColumn("Lead Time Demand", format="%.1f units"),
        'business_reason': "Financial Rationale"
    },
    use_container_width=True
)

st.markdown("""
<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 0.85rem 1.25rem; margin-top: 1.5rem; color: #64748B; font-size: 0.82rem;">
    📌 <strong>Decision-Support Disclaimer:</strong> Impact estimates are decision-support estimates based on the available forecast and inventory data. Estimates represent potential revenue loss or capital lockup rather than guaranteed accounting savings.
</div>
""", unsafe_allow_html=True)
