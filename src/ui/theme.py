"""
src/ui/theme.py
---------------
Light-scientific-workspace theme for TargetForge.

Authoritative palette:
  Background : #F5F7FA
  Surface    : #FFFFFF
  Navy       : #102A43  (nav, headers, primary text)
  Teal       : #0F766E  (primary interactive accent)
  Blue       : #2563EB  (secondary accent)
  Cyan       : #06B6D4  (data/chart accent)
  Borders    : #D9E2EC
  Text       : #243B53
  Muted      : #52606D

The hero-section gradient (Home page only) is dark navy→teal and is
scoped to the .hero-section CSS class — it does NOT become the global theme.

Owned by: M4 (Frontend/UI Lead)
"""
from __future__ import annotations
import streamlit as st

# ---------------------------------------------------------------------------
# Color token dictionary (importable by charts.py, components.py, etc.)
# ---------------------------------------------------------------------------
COLORS = {
    "bg":           "#F5F7FA",
    "surface":      "#FFFFFF",
    "navy":         "#102A43",
    "navy_light":   "#243B53",
    "teal":         "#0F766E",
    "teal_dark":    "#0D6860",
    "blue":         "#2563EB",
    "cyan":         "#06B6D4",
    "border":       "#D9E2EC",
    "text":         "#243B53",
    "muted":        "#52606D",
    # Status / badge colours
    "pass_bg":      "#D1FAE5",
    "pass_text":    "#065F46",
    "pass_border":  "#6EE7B7",
    "reject_bg":    "#FEE2E2",
    "reject_text":  "#991B1B",
    "reject_border": "#FCA5A5",
    "demo_bg":      "#FEF3C7",
    "demo_text":    "#92400E",
    "demo_border":  "#FCD34D",
    "locked_bg":    "#F3F4F6",
    "locked_text":  "#6B7280",
    "locked_border": "#E5E7EB",
    "current_bg":   "#DBEAFE",
    "current_text": "#1E40AF",
    "current_border": "#93C5FD",
    # Chart palette
    "chart": ["#0F766E", "#2563EB", "#06B6D4", "#D97706", "#DC2626", "#7C3AED"],
}

# Plotly theming constants (imported by charts.py)
CHART_TEMPLATE  = "plotly_white"
CHART_FONT      = dict(family="Inter, Arial, sans-serif", color=COLORS["text"], size=12)
CHART_BGCOLOR   = COLORS["surface"]
CHART_PAPER     = COLORS["bg"]
CHART_COLORS    = COLORS["chart"]


# ---------------------------------------------------------------------------
# Global CSS injection
# ---------------------------------------------------------------------------

_CSS = """
<style>
/* ─── Google Fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ─── Global ─────────────────────────────────────────────────  */
html, body, .stApp {
    background-color: #F5F7FA !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #243B53;
}

/* ─── Main Content Area ─────────────────────────────────────  */
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 1200px;
}

/* ─── Sidebar — Dark Navy ────────────────────────────────────  */
[data-testid="stSidebar"] {
    background-color: #102A43 !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
}
[data-testid="stSidebarNavLink"] {
    color: #CBD5E1 !important;
    border-radius: 6px;
    transition: background 0.15s ease;
}
[data-testid="stSidebarNavLink"]:hover {
    background-color: rgba(255,255,255,0.08) !important;
    color: #F1F5F9 !important;
}
[data-testid="stSidebarNavLink"][aria-selected="true"] {
    background-color: rgba(15,118,110,0.35) !important;
    color: #FFFFFF !important;
    font-weight: 600;
    border-left: 3px solid #0F766E;
}

/* ─── Typography ─────────────────────────────────────────────  */
h1 { color: #102A43 !important; font-weight: 700; letter-spacing: -0.025em; }
h2 { color: #102A43 !important; font-weight: 600; letter-spacing: -0.015em; }
h3 { color: #243B53 !important; font-weight: 600; }
h4 { color: #243B53 !important; font-weight: 500; }
p  { color: #243B53; line-height: 1.6; }

/* ─── Metrics ────────────────────────────────────────────────  */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #D9E2EC !important;
    border-radius: 10px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 4px rgba(16,42,67,0.07) !important;
}
[data-testid="stMetricLabel"] { color: #52606D !important; font-size: 0.78rem !important;
    font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { color: #102A43 !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] { font-weight: 500 !important; }

/* ─── Buttons ────────────────────────────────────────────────  */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.18s ease !important;
}
.stButton > button[kind="primary"] {
    background-color: #0F766E !important;
    border-color: #0F766E !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #0D6860 !important;
    border-color: #0D6860 !important;
    box-shadow: 0 4px 14px rgba(15,118,110,0.35) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="secondary"] {
    border-color: #D9E2EC !important;
    color: #243B53 !important;
    background: #FFFFFF !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #0F766E !important;
    color: #0F766E !important;
    background: #F0FDF9 !important;
}

/* ─── DataFrames / Tables ────────────────────────────────────  */
.stDataFrame { border: 1px solid #D9E2EC; border-radius: 8px; overflow: hidden; }
.stDataFrame [data-testid="stDataFrameResizable"] { border-radius: 8px; }

/* ─── Sliders ────────────────────────────────────────────────  */
.stSlider > div > div > div > div { background-color: #0F766E !important; }

/* ─── Tabs ───────────────────────────────────────────────────  */
[data-baseweb="tab-list"] { border-bottom: 2px solid #D9E2EC; gap: 0; }
[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: #52606D;
    padding: 0.5rem 1rem;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #0F766E !important;
    font-weight: 600;
    border-bottom: 2px solid #0F766E;
    background: transparent;
}

/* ─── Alert / Info boxes ─────────────────────────────────────  */
.stAlert { border-radius: 8px !important; }

/* ─── Expanders ──────────────────────────────────────────────  */
[data-testid="stExpander"] {
    border: 1px solid #D9E2EC;
    border-radius: 8px;
    background: #FFFFFF;
}
[data-testid="stExpander"] summary { font-weight: 500; color: #243B53; }

/* ─── Progress bars ──────────────────────────────────────────  */
.stProgress > div > div { background-color: #0F766E !important; }

/* ─── Dividers ───────────────────────────────────────────────  */
hr { border-color: #D9E2EC !important; }

/* ═══════════════════════════════════════════════════════════════
   TargetForge Custom Component Classes
   ═══════════════════════════════════════════════════════════════ */

/* Card container */
.tf-card {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(16,42,67,0.07);
}
.tf-card-sm {
    background: #FFFFFF;
    border: 1px solid #D9E2EC;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(16,42,67,0.05);
}

/* Badges */
.tf-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid transparent;
    letter-spacing: 0.02em;
}
.tf-badge-pass     { background:#D1FAE5; color:#065F46; border-color:#6EE7B7; }
.tf-badge-rejected { background:#FEE2E2; color:#991B1B; border-color:#FCA5A5; }
.tf-badge-demo     { background:#FEF3C7; color:#92400E; border-color:#FCD34D; }
.tf-badge-fallback { background:#FEF3C7; color:#92400E; border-color:#FCD34D; }
.tf-badge-locked   { background:#F3F4F6; color:#6B7280; border-color:#E5E7EB; }
.tf-badge-completed{ background:#D1FAE5; color:#065F46; border-color:#6EE7B7; }
.tf-badge-current  { background:#DBEAFE; color:#1E40AF; border-color:#93C5FD; }
.tf-badge-active   { background:#D1FAE5; color:#065F46; border-color:#6EE7B7; }
.tf-badge-lower    { background:#F3F4F6; color:#374151; border-color:#D1D5DB; }

/* Step row in sidebar workflow tracker */
.tf-step-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.5rem;
    border-radius: 6px;
    margin: 0.1rem 0;
    font-size: 0.875rem;
    color: #CBD5E1;
}
.tf-step-row.completed { color: #6EE7B7; }
.tf-step-row.current   { color: #93C5FD; font-weight: 600; }
.tf-step-row.locked    { color: #64748B; opacity: 0.6; }

/* KPI value emphasis */
.tf-kpi-val { font-size: 2rem; font-weight: 700; color: #102A43; line-height: 1.1; }
.tf-kpi-label { font-size: 0.75rem; font-weight: 500; color: #52606D;
                text-transform: uppercase; letter-spacing: 0.06em; }

/* What-if warning banner */
.tf-whatif-banner {
    background: #FFFBEB;
    border: 1.5px solid #FCD34D;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.tf-whatif-banner p { color: #92400E !important; margin: 0; font-weight: 500; }

/* Fallback / Demo notice panel */
.tf-demo-panel {
    background: #FEF3C7;
    border: 1.5px solid #FCD34D;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
.tf-demo-panel p { color: #92400E !important; margin: 0.3rem 0; font-size: 0.9rem; }
.tf-demo-panel strong { color: #78350F !important; }

/* ─── Hero Section (Home page only — scoped to .hero-section) ─ */
.hero-section {
    background: linear-gradient(135deg, #102A43 0%, #0F4C40 60%, #0F766E 100%);
    border-radius: 14px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 15% 60%, rgba(6,182,212,0.18) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(37,99,235,0.12) 0%, transparent 55%),
        url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23FFFFFF' fill-opacity='0.025'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-section h1 { color: #FFFFFF !important; font-size: 2.4rem; margin-bottom: 0.5rem; }
.hero-section p  { color: rgba(255,255,255,0.88) !important; font-size: 1.1rem; }
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.9) !important;
    margin: 4px 4px 4px 0;
    font-weight: 500;
}

/* ─── Rank Row Highlights ────────────────────────────────────  */
.rank-1 { background: linear-gradient(90deg, #FEF9C3 0%, transparent 100%);
           border-left: 4px solid #EAB308; padding-left: 0.75rem; }
.rank-2 { background: linear-gradient(90deg, #F1F5F9 0%, transparent 100%);
           border-left: 4px solid #94A3B8; padding-left: 0.75rem; }
.rank-3 { background: linear-gradient(90deg, #FEF3E8 0%, transparent 100%);
           border-left: 4px solid #F97316; padding-left: 0.75rem; }

/* ─── Footer / Disclaimer ────────────────────────────────────  */
.tf-disclaimer {
    font-size: 0.78rem;
    color: #52606D;
    border-top: 1px solid #D9E2EC;
    padding-top: 1rem;
    margin-top: 2rem;
    line-height: 1.6;
}
</style>
"""


def inject_global_css() -> None:
    """Inject the TargetForge global stylesheet once per page load."""
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Badge HTML helpers
# ---------------------------------------------------------------------------

def badge_html(text: str, kind: str = "demo") -> str:
    """Return inline HTML for a styled badge span.

    kind: "pass" | "rejected" | "demo" | "fallback" | "locked" |
          "completed" | "current" | "active" | "lower"
    """
    return f'<span class="tf-badge tf-badge-{kind}">{text}</span>'


def demo_field_html(field_name: str) -> str:
    """Return a small amber DEMO inline marker for a named field."""
    return (
        f'<span title="{field_name} is a deterministic demo value. '
        f'Not a validated scientific result." '
        f'class="tf-badge tf-badge-demo">⚠ DEMO</span>'
    )
