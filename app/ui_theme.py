import streamlit as st
import plotly.graph_objects as go

def apply_custom_css():
    """Injects custom SaaS design system CSS into Streamlit."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* App Background */
        .stApp {
            background-color: #F8FAFC;
            color: #0F172A;
        }

        /* Main Layout Padding */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1400px;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid #1E293B;
        }

        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }

        [data-testid="stSidebar"] .stRadio label {
            color: #CBD5E1 !important;
        }

        .sidebar-brand {
            padding: 0.5rem 0 1rem 0;
            border-bottom: 1px solid #1E293B;
            margin-bottom: 1.2rem;
        }

        .brand-logo-text {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: #38BDF8 !important;
            text-transform: uppercase;
        }

        .brand-title {
            font-size: 1.6rem;
            font-weight: 800;
            color: #FFFFFF !important;
            margin-top: 0.1rem;
            letter-spacing: -0.02em;
        }

        .brand-subtitle {
            font-size: 0.85rem;
            color: #94A3B8 !important;
            font-weight: 400;
        }

        .sidebar-status-box {
            background-color: rgba(30, 41, 59, 0.7);
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 0.75rem;
            margin-top: 1.5rem;
            font-size: 0.8rem;
        }

        .status-dot {
            height: 8px;
            width: 8px;
            background-color: #10B981;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }

        /* Top Page Header */
        .page-header-container {
            background: linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%);
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.25rem 1.6rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .page-header-title {
            font-size: 1.65rem;
            font-weight: 700;
            color: #0F172A;
            margin: 0;
            letter-spacing: -0.02em;
        }

        .page-header-sub {
            font-size: 0.9rem;
            color: #64748B;
            margin-top: 0.2rem;
        }

        .pipeline-badge {
            background-color: #EFF6FF;
            color: #2563EB;
            border: 1px solid #BFDBFE;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        /* KPI Card Styling */
        .kpi-card-v2 {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            position: relative;
            height: 100%;
        }

        .kpi-card-v2:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-color: #CBD5E1;
        }

        .kpi-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .kpi-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .kpi-icon {
            font-size: 1.2rem;
            opacity: 0.85;
        }

        .kpi-value-main {
            font-size: 1.65rem;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }

        .kpi-subtext {
            font-size: 0.78rem;
            color: #64748B;
            margin-top: 0.35rem;
        }

        /* Status & Risk Badges */
        .badge-pill {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }

        .badge-reorder-now {
            background-color: #FEE2E2;
            color: #DC2626;
            border: 1px solid #FCA5A5;
        }

        .badge-markdown-clear {
            background-color: #FEF3C7;
            color: #D97706;
            border: 1px solid #FDE68A;
        }

        .badge-investigate {
            background-color: #F3E8FF;
            color: #7C3AED;
            border: 1px solid #DDD6FE;
        }

        .badge-healthy {
            background-color: #D1FAE5;
            color: #059669;
            border: 1px solid #A7F3D0;
        }

        .badge-monitor {
            background-color: #FEF9C3;
            color: #CA8A04;
            border: 1px solid #FEF08A;
        }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            border-radius: 12px;
            padding: 2rem;
            color: #FFFFFF;
            margin-bottom: 1.8rem;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        }

        .hero-title {
            font-size: 1.8rem;
            font-weight: 800;
            color: #FFFFFF;
            margin: 0;
            letter-spacing: -0.02em;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #94A3B8;
            margin-top: 0.4rem;
            margin-bottom: 0;
            font-weight: 400;
        }

        /* Content Cards */
        .content-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.4rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }

        /* Streamlit Dataframe & Table tweaks */
        [data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            overflow: hidden;
            background-color: #FFFFFF;
        }

        /* Metric widget styling override if standard metrics used */
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            color: #64748B !important;
            text-transform: uppercase;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #0F172A !important;
        }

        /* Custom Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #F1F5F9;
            padding: 6px;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.88rem;
            color: #64748B;
            padding: 0 16px;
            border: none !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #2563EB !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders consistent corporate sidebar header, branding, and status footer."""
    st.sidebar.markdown("""
    <div class="sidebar-brand">
        <div class="brand-logo-text">NORTHBAY LIVING</div>
        <div class="brand-title">FORESIGHT</div>
        <div class="brand-subtitle">Demand & Inventory Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div class="sidebar-status-box">
        <div><span class="status-dot"></span> <strong>Analytics System Online</strong></div>
        <div style="font-size:0.72rem; color: #94A3B8; margin-top:0.3rem;">Model Engine v1.0 • Connected</div>
    </div>
    <div style="margin-top: 1.5rem; text-align: center; font-size: 0.75rem; color: #64748B;">
        FORESIGHT Enterprise v1.0
    </div>
    """, unsafe_allow_html=True)

def render_page_header(title, subtitle, status_text="Data Pipeline Connected"):
    """Renders top header banner for pages."""
    st.markdown(f"""
    <div class="page-header-container">
        <div>
            <h1 class="page-header-title">{title}</h1>
            <div class="page-header-sub">{subtitle}</div>
        </div>
        <div>
            <span class="pipeline-badge">
                <span style="height: 6px; width: 6px; background-color: #2563EB; border-radius: 50%;"></span>
                {status_text}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero_banner(title, subtitle):
    """Renders executive hero banner."""
    st.markdown(f"""
    <div class="hero-banner">
        <h2 class="hero-title">{title}</h2>
        <p class="hero-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(title, value, subtext=None, icon="📊", border_color="#2563EB", badge_text=None, badge_class="badge-healthy"):
    """Renders HTML card for KPIs."""
    badge_html = f'<div style="margin-top:0.4rem;"><span class="badge-pill {badge_class}">{badge_text}</span></div>' if badge_text else ''
    subtext_html = f'<div class="kpi-subtext">{subtext}</div>' if subtext else ''
    
    st.markdown(f"""
    <div class="kpi-card-v2" style="border-top: 3px solid {border_color};">
        <div class="kpi-card-header">
            <span class="kpi-label">{title}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value-main">{value}</div>
        {badge_html}
        {subtext_html}
    </div>
    """, unsafe_allow_html=True)

def render_risk_badge(action):
    """Returns HTML snippet for risk action badges."""
    action_str = str(action).upper()
    if 'REORDER' in action_str:
        return '<span class="badge-pill badge-reorder-now">REORDER NOW</span>'
    elif 'MARKDOWN' in action_str or 'CLEAR' in action_str:
        return '<span class="badge-pill badge-markdown-clear">MARKDOWN / CLEAR</span>'
    elif 'INVESTIGATE' in action_str:
        return '<span class="badge-pill badge-investigate">INVESTIGATE</span>'
    elif 'HEALTHY' in action_str:
        return '<span class="badge-pill badge-healthy">HEALTHY</span>'
    else:
        return f'<span class="badge-pill badge-monitor">{action_str}</span>'

def get_plotly_layout(title=""):
    """Returns consistent light SaaS template settings for Plotly charts."""
    return dict(
        title=dict(
            text=title,
            font=dict(family="Inter, sans-serif", size=15, color="#0F172A", weight=700),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#475569", size=12),
        margin=dict(l=45, r=30, t=50, b=45),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            zeroline=False,
            title_font=dict(size=12, color="#64748B")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            linecolor="#E2E8F0",
            zeroline=False,
            title_font=dict(size=12, color="#64748B")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color="#475569")
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=12,
            font_family="Inter, sans-serif",
            font_color="#FFFFFF"
        )
    )
