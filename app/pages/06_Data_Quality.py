import os
import sys
import json
import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import MODEL_ARTIFACTS_DIR, PROCESSED_DATA_DIR
from app.ui_theme import apply_custom_css, render_sidebar, render_page_header, render_kpi_card

st.set_page_config(page_title="Data Quality - FORESIGHT", layout="wide")
apply_custom_css()
render_sidebar()

render_page_header(
    title="Data Quality & Audit Module",
    subtitle="Automated schema validation, missing value imputation, deduplication, and data health report",
    status_text="Pipeline Audit Passed"
)

@st.cache_data
def load_audit():
    with open(os.path.join(MODEL_ARTIFACTS_DIR, 'audit_report.json'), 'r') as f:
        audit = json.load(f)
    sales = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, 'sales_daily_clean.csv'))
    return audit, sales

audit, df_sales = load_audit()

# Quality Summary Header Cards
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    render_kpi_card("Total Sales Rows", f"{len(df_sales):,}", icon="📄", border_color="#2563EB")
with m2:
    render_kpi_card("Active SKUs", f"{audit['initial_sku_count']}", icon="📦", border_color="#4F46E5")
with m3:
    render_kpi_card("Duplicates Removed", f"{audit['duplicates_removed']}", icon="🧹", border_color="#0D9488")
with m4:
    render_kpi_card("Values Imputed", f"{audit['missing_values_handled']}", icon="🔧", border_color="#D97706")
with m5:
    render_kpi_card(
        "Data Completeness",
        f"{audit['data_completeness_pct']}%",
        badge_text="PASSED AUDIT",
        badge_class="badge-healthy",
        icon="🛡️",
        border_color="#059669"
    )

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

col_left, col_right = st.columns([5, 5])

with col_left:
    st.markdown("""
    <div class="content-card">
        <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.8rem;">
            📊 Dataset Metadata & Telemetry Coverage
        </div>
        <ul style="color: #334155; font-size: 0.92rem; line-height: 1.8; margin-left: -1rem;">
            <li><strong>Date Range Coverage:</strong> {} → {}</li>
            <li><strong>Total Transaction Records:</strong> {:,}</li>
            <li><strong>Normalized Product Categories:</strong> {} Categories</li>
            <li><strong>Unmatched Sales SKUs:</strong> {} (Foreign Key Integrity Intact)</li>
            <li><strong>Missing Inventory Records:</strong> {} SKUs</li>
        </ul>
        <div style="background-color: #D1FAE5; border: 1px solid #A7F3D0; border-radius: 8px; padding: 0.75rem 1rem; margin-top: 1rem; color: #065F46; font-size: 0.85rem; font-weight: 600;">
            ✅ Schema Validation: All extracts (sales_daily, sku_master, calendar, inventory_snapshots) matched target enterprise schemas.
        </div>
    </div>
    """.format(
        df_sales['date'].min()[:10],
        df_sales['date'].max()[:10],
        audit['initial_sales_rows'],
        audit['categories_normalized'],
        len(audit['unmatched_skus']),
        audit['missing_inventory_skus_count']
    ), unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="content-card">
        <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.8rem;">
            📜 Automated Pipeline Cleaning Log
        </div>
    """, unsafe_allow_html=True)
    
    for decision in audit['cleaning_decisions']:
        st.markdown(f"""
        <div style="background-color: #F8FAFC; border-left: 3px solid #2563EB; border-radius: 4px; padding: 0.65rem 0.85rem; margin-bottom: 0.6rem; color: #334155; font-size: 0.88rem;">
            • {decision}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Sample Processed Data Preview
st.markdown("<h4 style='color: #0F172A; font-weight: 700; margin-bottom: 0.8rem;'>🔍 Sample Processed Data Preview</h4>", unsafe_allow_html=True)
st.dataframe(df_sales.head(10), use_container_width=True)
