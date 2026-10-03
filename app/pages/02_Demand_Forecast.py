import os
import sys
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(APP_DIR)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.config import PROCESSED_DATA_DIR
from ui_theme import apply_custom_css, render_sidebar, render_page_header, render_kpi_card, render_risk_badge, get_plotly_layout

st.set_page_config(page_title="Demand Forecast - FORESIGHT", layout="wide")
apply_custom_css()
render_sidebar()

render_page_header(
    title="Demand Forecast Workspace",
    subtitle="Weekly SKU-level demand projections with uncertainty intervals and model telemetry",
    status_text="Forecasting Engine Active"
)

@st.cache_data
def load_data():
    forecast_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'forecast_outputs.csv'))
    weekly_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'weekly_features.csv'))
    impact_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'risk_impact_matrix.csv'))
    return forecast_df, weekly_df, impact_df

df_forecast, df_weekly, df_impact = load_data()

# Workspace Control Bar
st.markdown("""
<div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
    <div style="font-size: 0.88rem; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.8rem;">
        🎛️ Catalog Selection & Forecast Filters
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([3, 3, 4, 2])
with c1:
    categories = ['All'] + sorted(df_impact['category'].unique().tolist())
    selected_cat = st.selectbox("Product Category", categories)

with c2:
    if selected_cat != 'All':
        subcats = ['All'] + sorted(df_impact[df_impact['category'] == selected_cat]['subcategory'].unique().tolist())
    else:
        subcats = ['All'] + sorted(df_impact['subcategory'].unique().tolist())
    selected_subcat = st.selectbox("Subcategory", subcats)

with c3:
    filtered_impact = df_impact.copy()
    if selected_cat != 'All':
        filtered_impact = filtered_impact[filtered_impact['category'] == selected_cat]
    if selected_subcat != 'All':
        filtered_impact = filtered_impact[filtered_impact['subcategory'] == selected_subcat]
    
    sku_list = filtered_impact['sku_id'].tolist()
    if len(sku_list) > 0:
        selected_sku = st.selectbox("Select Target SKU", sku_list)
    else:
        st.warning("No SKUs match the selected filters.")
        st.stop()

with c4:
    st.selectbox("Forecast Horizon", ["8 Weeks (Standard)"], disabled=True)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Visualizing Selected SKU Telemetry
sku_hist = df_weekly[df_weekly['sku_id'] == selected_sku].tail(26)
sku_fcst = df_forecast[df_forecast['sku_id'] == selected_sku]
sku_info = df_impact[df_impact['sku_id'] == selected_sku].iloc[0]

# Metrics Summary Grid for Target SKU
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    render_kpi_card("Category", sku_info['category'], icon="📁", border_color="#2563EB")
with m2:
    render_kpi_card("Subcategory", sku_info['subcategory'], icon="🏷️", border_color="#4F46E5")
with m3:
    render_kpi_card("8-Wk Total Forecast", f"{sku_info['forecast_8w_demand']:.0f} units", icon="📈", border_color="#0D9488")
with m4:
    render_kpi_card("On Hand Stock", f"{sku_info['on_hand_units']} units", icon="📦", border_color="#D97706")
with m5:
    render_kpi_card(
        "Recommended Action",
        sku_info['recommended_action'],
        badge_text=sku_info['recommended_action'],
        badge_class="badge-reorder-now" if sku_info['recommended_action'] == 'REORDER NOW' else ("badge-markdown-clear" if sku_info['recommended_action'] == 'MARKDOWN / CLEAR' else "badge-healthy"),
        icon="🎯",
        border_color="#DC2626" if sku_info['recommended_action'] == 'REORDER NOW' else "#059669"
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Interactive Plotly Forecast Chart
fig = go.Figure()

# 1. Historical Actual Demand
fig.add_trace(go.Scatter(
    x=sku_hist['week_date'],
    y=sku_hist['weekly_units'],
    mode='lines+markers',
    name='Historical Actual Demand',
    line=dict(color='#2563EB', width=2.5),
    marker=dict(size=6, color='#2563EB')
))

# 2. Model Forecast
fig.add_trace(go.Scatter(
    x=sku_fcst['forecast_week'],
    y=sku_fcst['forecast'],
    mode='lines+markers',
    name=f"Forecast ({sku_fcst['model'].iloc[0]})",
    line=dict(color='#4F46E5', width=3, dash='solid'),
    marker=dict(size=7, color='#4F46E5')
))

# 3. Uncertainty Interval (80% Bound)
fig.add_trace(go.Scatter(
    x=sku_fcst['forecast_week'].tolist() + sku_fcst['forecast_week'].tolist()[::-1],
    y=sku_fcst['upper_bound'].tolist() + sku_fcst['lower_bound'].tolist()[::-1],
    fill='toself',
    fillcolor='rgba(79, 70, 229, 0.12)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=True,
    name='80% Confidence Interval'
))

layout = get_plotly_layout(f"Weekly Demand Projection & 8-Week Forward Forecast for {selected_sku}")
layout['height'] = 450
layout['hovermode'] = "x unified"
layout['xaxis']['title'] = "Week Date"
layout['yaxis']['title'] = "Weekly Demand (Units)"
fig.update_layout(**layout)

st.plotly_chart(fig, use_container_width=True)

# Explanation Banner
st.markdown("""
<div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1.5rem; color: #1E40AF; font-size: 0.9rem;">
    💡 <strong>Forecast Interpretation:</strong> The forecast estimates future weekly demand using historical sales patterns and available features (lags, rolling averages, calendar signals). The shaded band represents the 80% confidence bounds accounting for empirical model variance.
</div>
""", unsafe_allow_html=True)

# Detailed Forecast Breakdown Table
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>📋 Weekly Forecast Breakdown Schedule</h4>", unsafe_allow_html=True)

st.dataframe(
    sku_fcst[['forecast_week', 'forecast', 'lower_bound', 'upper_bound', 'model']],
    column_config={
        'forecast_week': "Week Beginning",
        'forecast': st.column_config.NumberColumn("Predicted Demand (Units)", format="%.1f"),
        'lower_bound': st.column_config.NumberColumn("Lower Estimate (80%)", format="%.1f"),
        'upper_bound': st.column_config.NumberColumn("Upper Estimate (80%)", format="%.1f"),
        'model': "Forecasting Model Engine"
    },
    use_container_width=True
)
