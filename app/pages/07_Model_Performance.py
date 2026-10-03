import os
import sys
import json
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import MODEL_ARTIFACTS_DIR
from app.ui_theme import apply_custom_css, render_sidebar, render_page_header, render_kpi_card

st.set_page_config(page_title="Model Performance - FORESIGHT", layout="wide")
apply_custom_css()
render_sidebar()

render_page_header(
    title="Model Evaluation & Backtesting",
    subtitle="Honest time-series evaluation comparing Seasonal-Naive Baseline against Candidate ML Models",
    status_text="Model Validation Passed"
)

@st.cache_data
def load_metadata():
    with open(os.path.join(MODEL_ARTIFACTS_DIR, 'selection_metadata.json'), 'r') as f:
        meta = json.load(f)
    return meta

meta = load_metadata()

# Selected Model Header Card
st.markdown(f"""
<div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
    <div style="font-size: 0.8rem; font-weight: 700; color: #2563EB; text-transform: uppercase; letter-spacing: 0.05em;">CHAMPION MODEL ENGINE</div>
    <div style="font-size: 1.6rem; font-weight: 800; color: #0F172A; margin-top: 0.2rem;">Selected Model: {meta['final_model']}</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card(
        title="Final Model WAPE",
        value=f"{meta['final_wape'] * 100:.2f}%",
        subtext="Weighted error across active SKUs",
        icon="🎯",
        border_color="#2563EB"
    )

with c2:
    render_kpi_card(
        title="Seasonal-Naive Baseline WAPE",
        value=f"{meta['baseline_wape'] * 100:.2f}%",
        subtext="Prior-year seasonal baseline error",
        icon="📉",
        border_color="#4F46E5"
    )

with c3:
    render_kpi_card(
        title="WAPE Error Reduction",
        value=f"{meta['improvement_pct']:.2f}%",
        subtext="Relative accuracy improvement",
        icon="⚡",
        border_color="#0D9488",
        badge_text="BEATS BASELINE" if meta['status'] == "BEATS BASELINE" else "BASELINE RETAINED",
        badge_class="badge-healthy"
    )

with c4:
    render_kpi_card(
        title="Model Status",
        value=meta['status'],
        subtext="Selection criterion result",
        icon="🛡️",
        border_color="#059669",
        badge_text="VALIDATED",
        badge_class="badge-healthy"
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Model Comparison Table
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>📊 Candidate Model Benchmark Summary</h4>", unsafe_allow_html=True)
df_summary = pd.DataFrame(meta['summary_table'])
st.dataframe(
    df_summary,
    column_config={
        'Model': "Forecasting Algorithm",
        'WAPE': st.column_config.NumberColumn("WAPE Error", format="%.4f"),
        'MAE': st.column_config.NumberColumn("MAE (Units)", format="%.4f"),
        'RMSE': st.column_config.NumberColumn("RMSE (Units)", format="%.4f"),
        'Bias': st.column_config.NumberColumn("Forecast Bias", format="%.4f")
    },
    use_container_width=True
)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Rolling Origin CV Window Details
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>🔄 Rolling-Origin Backtest Windows Details</h4>", unsafe_allow_html=True)
df_windows = pd.DataFrame(meta['window_details'])
st.dataframe(
    df_windows[['window', 'cutoff_date', 'test_end_date', 'test_samples', 'baseline_wape', 'hist_gb_wape', 'rf_wape']],
    column_config={
        'window': "CV Window #",
        'cutoff_date': "Cutoff Date",
        'test_end_date': "Evaluation End Date",
        'test_samples': st.column_config.NumberColumn("Test Samples", format="%d"),
        'baseline_wape': st.column_config.NumberColumn("Baseline WAPE", format="%.4f"),
        'hist_gb_wape': st.column_config.NumberColumn("HistGB WAPE", format="%.4f"),
        'rf_wape': st.column_config.NumberColumn("RandomForest WAPE", format="%.4f")
    },
    use_container_width=True
)

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

# Non-Technical Educational Section
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>💡 Guide for Executive & Operational Decision-Makers</h4>", unsafe_allow_html=True)

with st.expander("❓ What is WAPE and why is it our primary accuracy metric?"):
    st.markdown("""
    **WAPE (Weighted Absolute Percentage Error)** measures overall forecasting error across all products weighted by demand volume.
    $$\\text{WAPE} = \\frac{\\sum |\\text{Actual Demand} - \\text{Forecast}|}{\\sum \\text{Actual Demand}}$$
    * Unlike standard MAPE (which explodes for low-volume items), WAPE weights high-volume products proportionally, making it the supply chain gold standard.
    * A lower WAPE indicates a more accurate forecast.
    """)

with st.expander("❓ What is the Seasonal-Naive Baseline?"):
    st.markdown("""
    The **Seasonal-Naive baseline** assumes that demand for a future week will equal demand from the same week in the previous year (or recent 4-week trend).
    * In client consulting, an ML model must earn its place by measurably beating this baseline.
    * If an ML model fails to beat the baseline, the baseline is retained without fabricating false accuracy.
    """)

with st.expander("❓ How do we guarantee no future information was leaked?"):
    st.markdown("""
    * Every feature (lags, rolling averages, calendar flags) was created strictly using telemetry data available **before** the forecast week.
    * We used **rolling-origin cross-validation** (simulating real weekly forecasting over historical time slices) rather than unrealistic random train-test splitting.
    """)
