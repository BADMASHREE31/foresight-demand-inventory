import os
import sys
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import PROCESSED_DATA_DIR
from src.utils import generate_sku_explanation, format_inr
from app.ui_theme import apply_custom_css, render_sidebar, render_page_header, render_kpi_card, get_plotly_layout

st.set_page_config(page_title="SKU Explorer - FORESIGHT", layout="wide")
apply_custom_css()
render_sidebar()

render_page_header(
    title="SKU Deep-Dive Explorer",
    subtitle="Detailed product profile, inventory position, and dynamic operational explanation",
    status_text="SKU Intelligence Active"
)

@st.cache_data
def load_data():
    impact_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'risk_impact_matrix.csv'))
    forecast_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'forecast_outputs.csv'))
    weekly_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'weekly_features.csv'))
    return impact_df, forecast_df, weekly_df

df_impact, df_forecast, df_weekly = load_data()

# SKU Selector Card
st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
    <div style="font-size: 0.88rem; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.6rem;">
        🔍 Select Target SKU to Investigate
    </div>
</div>
""", unsafe_allow_html=True)

selected_sku = st.selectbox("Product SKU Identifier", df_impact['sku_id'].tolist())

sku_data = df_impact[df_impact['sku_id'] == selected_sku].iloc[0]
sku_fcst = df_forecast[df_forecast['sku_id'] == selected_sku]
sku_hist = df_weekly[df_weekly['sku_id'] == selected_sku].tail(26)

# Dynamic NLP Explanation
dynamic_explanation = generate_sku_explanation(sku_data)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Action Banner
action = sku_data['recommended_action']
if action == 'REORDER NOW':
    st.markdown(f"""
    <div style="background-color: #FEE2E2; border: 1px solid #FCA5A5; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; color: #991B1B; font-weight: 600;">
        🚨 <strong>RECOMMENDED ACTION: REORDER NOW</strong> &nbsp;|&nbsp; Estimated Revenue at Risk: <strong>{format_inr(sku_data['revenue_at_risk'])}</strong>
    </div>
    """, unsafe_allow_html=True)
elif action == 'MARKDOWN / CLEAR':
    st.markdown(f"""
    <div style="background-color: #FEF3C7; border: 1px solid #FDE68A; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; color: #92400E; font-weight: 600;">
        ⚠️ <strong>RECOMMENDED ACTION: MARKDOWN / CLEAR</strong> &nbsp;|&nbsp; Estimated Capital Locked: <strong>{format_inr(sku_data['capital_locked'])}</strong>
    </div>
    """, unsafe_allow_html=True)
elif action == 'INVESTIGATE':
    st.markdown("""
    <div style="background-color: #F3E8FF; border: 1px solid #DDD6FE; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; color: #5B21B6; font-weight: 600;">
        🔍 <strong>RECOMMENDED ACTION: INVESTIGATE</strong> &nbsp;|&nbsp; Operations Review Required
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="background-color: #D1FAE5; border: 1px solid #A7F3D0; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; color: #065F46; font-weight: 600;">
        ✅ <strong>RECOMMENDED ACTION: HEALTHY</strong> &nbsp;|&nbsp; Inventory Position Safely Covered
    </div>
    """, unsafe_allow_html=True)

# Dynamic Explanation Box Card
st.markdown(f"""
<div class="content-card">
    <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">
        ❓ Why is this SKU classified as <em>{action}</em>?
    </div>
    <div style="font-size: 0.92rem; color: #334155; line-height: 1.6;">
        {dynamic_explanation}
    </div>
</div>
""", unsafe_allow_html=True)

# Key Metrics Grid
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    render_kpi_card("On-Hand Stock", f"{sku_data['on_hand_units']} units", icon="📦", border_color="#2563EB")
with c2:
    render_kpi_card("On-Order Pipeline", f"{sku_data['on_order_units']} units", icon="🚚", border_color="#4F46E5")
with c3:
    render_kpi_card("Lead Time", f"{sku_data['lead_time_days']} days", icon="⏱️", border_color="#0D9488")
with c4:
    render_kpi_card("Lead Time Demand", f"{sku_data['lead_time_demand']:.1f} units", icon="📊", border_color="#D97706")
with c5:
    render_kpi_card("8-Wk Total Forecast", f"{sku_data['forecast_8w_demand']:.0f} units", icon="📈", border_color="#7C3AED")

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Visual Demand Comparison Chart
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>📊 Demand History & 8-Week Forward Horizon</h4>", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=sku_hist['week_date'],
    y=sku_hist['weekly_units'],
    name="Historical Sales",
    mode='lines+markers',
    line=dict(color="#2563EB", width=2.5),
    marker=dict(size=6)
))

fig.add_trace(go.Scatter(
    x=sku_fcst['forecast_week'],
    y=sku_fcst['forecast'],
    name="Model Forecast",
    mode='lines+markers',
    line=dict(color="#4F46E5", width=3, dash='solid'),
    marker=dict(size=7)
))

fig.add_hline(
    y=sku_data['lead_time_demand'],
    line_dash="dot",
    line_color="#DC2626",
    annotation_text=f"Lead Time Demand ({sku_data['lead_time_demand']:.0f} units)",
    annotation_font=dict(color="#DC2626")
)

layout = get_plotly_layout(f"Demand Telemetry for {selected_sku} ({sku_data['category']} - {sku_data['subcategory']})")
layout['height'] = 420
layout['hovermode'] = "x unified"
layout['xaxis']['title'] = "Week Date"
layout['yaxis']['title'] = "Units / Week"
fig.update_layout(**layout)

st.plotly_chart(fig, use_container_width=True)
