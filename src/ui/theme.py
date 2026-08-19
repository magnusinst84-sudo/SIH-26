"""
src/ui/theme.py
---------------
TargetForge — Modern Dark Scientific Design System & Theme Engine

Colors (from reference):
  Background        : #080F14 (Deep dark scientific canvas)
  Surface           : #11161D (Card and container surfaces)
  Surface Elevated  : #161C24 (Elevated containers, dropdowns, headers)
  Primary Teal      : #00BFA6 (Primary CTA, active states, key metrics)
  Primary Amber     : #F59E0B (Accent highlights, secondary warnings)
  Text Primary      : #F8FAFC (High contrast headers and values)
  Text Secondary    : #A1ABB3 (Muted labels and subtitles)
  Border            : #232D38 (1px crisp structural border)
  Border Subtle     : rgba(255, 255, 255, 0.08)
  Success           : #10B981 (Validation PASS)
  Warning           : #F59E0B (Demo notification)
  Error             : #EF4444 (Rejection)

Owned by: M4 (Frontend/UI Lead)
"""
from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st

# ---------------------------------------------------------------------------
# Color token dictionary
# ---------------------------------------------------------------------------
COLORS = {
    "background":       "#080F14",
    "surface":          "#11161D",
    "surface_elevated": "#161C24",
    "teal":             "#00BFA6",
    "teal_hover":       "#00A892",
    "teal_pale":        "rgba(0, 191, 166, 0.12)",
    "amber":            "#F59E0B",
    "amber_pale":       "rgba(245, 158, 11, 0.12)",
    "blue":             "#38BDF8",
    "purple":           "#818CF8",
    "border":           "#232D38",
    "border_subtle":    "rgba(255, 255, 255, 0.08)",
    "text":             "#F8FAFC",
    "text_secondary":   "#A1ABB3",
    "muted":            "#A1ABB3",
    "success":          "#10B981",
    "warning":          "#F59E0B",
    "error":            "#EF4444",
    
    # Status badges
    "pass_bg":          "rgba(0, 191, 166, 0.12)",
    "pass_text":        "#00BFA6",
    "pass_border":      "rgba(0, 191, 166, 0.35)",
    "reject_bg":        "rgba(239, 68, 68, 0.12)",
    "reject_text":      "#EF4444",
    "reject_border":    "rgba(239, 68, 68, 0.35)",
    "demo_bg":          "rgba(245, 158, 11, 0.12)",
    "demo_text":        "#F59E0B",
    "demo_border":      "rgba(245, 158, 11, 0.35)",
    "locked_bg":        "#161C24",
    "locked_text":      "#64748B",
    "locked_border":    "#232D38",
    "current_bg":       "rgba(0, 191, 166, 0.14)",
    "current_text":     "#00BFA6",
    "current_border":   "#00BFA6",
    
    # Scientific Chart palette
    "chart": ["#00BFA6", "#F59E0B", "#38BDF8", "#818CF8", "#A1ABB3"],
}

# Plotly theming constants (imported by charts.py)
CHART_TEMPLATE  = "plotly_dark"
CHART_FONT      = dict(family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", color="#F8FAFC", size=11)
CHART_BGCOLOR   = "#11161D"
CHART_PAPER     = "rgba(0, 0, 0, 0)"
CHART_COLORS    = COLORS["chart"]


def get_hero_bg_base64() -> str:
    """Read the amber hero background image from assets and encode to base64."""
    try:
        root = Path(__file__).resolve().parent.parent.parent
        img_path = root / "src" / "ui" / "assets" / "amber_molecular_hero.jpg"
        if not img_path.exists():
            img_path = root / "src" / "ui" / "assets" / "molecular_hero_bg.jpg"
        if img_path.exists():
            with open(img_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# Global CSS injection
# ---------------------------------------------------------------------------

def inject_global_css() -> None:
    """Inject the dark scientific workspace stylesheet."""
    _CSS = f"""
<style>
/* ─── Google Fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─── Global Dark Scientific Canvas ────────────────────────── */
html, body, .stApp {{
    background-color: #080F14 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #F8FAFC !important;
    font-size: 13px;
    line-height: 1.45;
}}

/* ─── Main Content Container (Compact & Dense) ─────────────── */
.main .block-container {{
    padding-top: 0.85rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1.75rem !important;
    padding-right: 1.75rem !important;
    max-width: 1260px;
}}

/* ─── Sidebar Styling (High Contrast & Clear Hierarchy) ────── */
[data-testid="stSidebar"] {{
    background-color: #11161D !important;
    border-right: 1px solid #232D38 !important;
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    padding-top: 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
}}

/* All sidebar navigation items (Streamlit native nav links) */
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] a {{
    background-color: transparent !important;
    color: #CBD5E1 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 7px 12px !important;
    border-radius: 6px !important;
    transition: all 0.15s ease !important;
    margin-bottom: 2px !important;
    display: flex !important;
    align-items: center !important;
}}

[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] *,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a * {{
    color: #CBD5E1 !important;
}}

[data-testid="stSidebar"] span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] .material-symbols-rounded {{
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    font-size: 18px !important;
    color: #94A3B8 !important;
    margin-right: 8px !important;
}}

/* Hover state */
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover,
[data-testid="stSidebar"] a:hover {{
    background-color: #161C24 !important;
    color: #FFFFFF !important;
}}

[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover *,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover * {{
    color: #FFFFFF !important;
}}

/* Active Navigation Item */
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] a[aria-current="page"],
[data-testid="stSidebar"] .active {{
    background-color: rgba(0, 191, 166, 0.12) !important;
    border-left: 3px solid #00BFA6 !important;
    color: #00BFA6 !important;
    font-weight: 600 !important;
}}

[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] *,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] *,
[data-testid="stSidebar"] a[aria-current="page"] * {{
    color: #00BFA6 !important;
    font-weight: 600 !important;
}}

[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] span[data-testid="stIconMaterial"] {{
    color: #00BFA6 !important;
}}

/* ─── Typography & Headings ────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Inter', sans-serif !important;
    color: #F8FAFC !important;
    letter-spacing: -0.02em;
}}

h1 {{
    font-size: 21px !important;
    font-weight: 700 !important;
    margin-bottom: 0.15rem !important;
}}

h2 {{
    font-size: 17px !important;
    font-weight: 650 !important;
    margin-top: 0.75rem !important;
    margin-bottom: 0.3rem !important;
}}

h3 {{
    font-size: 14.5px !important;
    font-weight: 600 !important;
    margin-top: 0.65rem !important;
    margin-bottom: 0.25rem !important;
}}

h4 {{
    font-size: 13px !important;
    font-weight: 600 !important;
    margin-top: 0.45rem !important;
    margin-bottom: 0.2rem !important;
}}

p, span, label, div {{
    font-family: 'Inter', sans-serif;
}}

.stCaption, [data-testid="stCaptionContainer"] {{
    color: #A1ABB3 !important;
    font-size: 12px !important;
    margin-bottom: 6px !important;
}}

/* ─── Compact Scientific Cards ─────────────────────────────── */
.tf-card {{
    background: #11161D;
    border: 1px solid #232D38;
    border-radius: 8px;
    padding: 12px 14px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
    margin-bottom: 8px;
}}

.tf-card-elevated {{
    background: #161C24;
    border: 1px solid #232D38;
    border-radius: 8px;
    padding: 12px 14px;
}}

/* ─── Compact Scientific Metric Card ────────────────────────── */
.tf-metric-card {{
    background: #11161D;
    border: 1px solid #232D38;
    border-radius: 6px;
    padding: 8px 10px;
    min-height: 64px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.tf-metric-label {{
    font-size: 10px;
    font-weight: 600;
    color: #A1ABB3;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 2px;
}}

.tf-metric-value {{
    font-size: 16px;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.15;
}}

.tf-metric-context {{
    font-size: 11px;
    color: #A1ABB3;
    margin-top: 2px;
}}

/* ─── Buttons ──────────────────────────────────────────────── */
button[kind="primary"], .stButton > button[kind="primary"],
.stButton > button:first-child[data-testid="stBaseButton-primary"] {{
    background-color: #00BFA6 !important;
    color: #080F14 !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    height: 36px !important;
    border-radius: 6px !important;
    padding: 0 1rem !important;
    box-shadow: 0 2px 6px rgba(0, 191, 166, 0.2) !important;
    transition: all 0.15s ease !important;
}}

button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {{
    background-color: #00A892 !important;
    box-shadow: 0 3px 10px rgba(0, 191, 166, 0.3) !important;
}}

button[kind="secondary"], .stButton > button[kind="secondary"],
.stButton > button:first-child[data-testid="stBaseButton-secondary"] {{
    background-color: #161C24 !important;
    color: #F8FAFC !important;
    border: 1px solid #232D38 !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    height: 34px !important;
    border-radius: 6px !important;
    padding: 0 0.85rem !important;
    transition: all 0.15s ease !important;
}}

button[kind="secondary"]:hover, .stButton > button[kind="secondary"]:hover {{
    background-color: #11161D !important;
    border-color: #00BFA6 !important;
    color: #00BFA6 !important;
}}

/* ─── Badges ───────────────────────────────────────────────── */
.tf-badge {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
    letter-spacing: 0.02em;
}}

.tf-badge-pass {{
    background: rgba(0, 191, 166, 0.12);
    color: #00BFA6;
    border: 1px solid rgba(0, 191, 166, 0.3);
}}

.tf-badge-rejected {{
    background: rgba(239, 68, 68, 0.12);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}}

.tf-badge-demo {{
    background: rgba(245, 158, 11, 0.12);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.3);
}}

.tf-badge-locked {{
    background: #161C24;
    color: #64748B;
    border: 1px solid #232D38;
}}

/* ─── Data Tables (Streamlit Dataframe) ─────────────────────── */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
    border: 1px solid #232D38 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
    background: #11161D !important;
}}

/* ─── Compact Horizontal Stepper ───────────────────────────── */
.stepper-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    padding: 4px 0 10px 0;
    max-width: 640px;
    margin: 0 auto 10px auto;
}}

.stepper-line-bg {{
    position: absolute;
    top: 15px;
    left: 18px;
    right: 18px;
    height: 2px;
    background: #232D38;
    z-index: 1;
}}

.stepper-line-active {{
    position: absolute;
    top: 15px;
    left: 18px;
    height: 2px;
    background: #00BFA6;
    z-index: 2;
    transition: width 0.3s ease;
}}

.stepper-step {{
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 3;
}}

.stepper-circle {{
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #11161D;
    border: 1.5px solid #232D38;
    color: #A1ABB3;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
    transition: all 0.2s ease;
}}

.stepper-step.completed .stepper-circle {{
    background: #10B981;
    border-color: #10B981;
    color: #FFFFFF;
}}

.stepper-step.current .stepper-circle {{
    background: #080F14;
    border-color: #00BFA6;
    color: #00BFA6;
    box-shadow: 0 0 0 3px rgba(0, 191, 166, 0.16);
}}

.stepper-label {{
    font-size: 9.5px;
    font-weight: 600;
    color: #A1ABB3;
    margin-top: 3px;
    text-transform: capitalize;
}}

.stepper-step.current .stepper-label {{
    color: #00BFA6;
    font-weight: 700;
}}

/* ─── Notice Panels (Compact) ──────────────────────────────── */
.tf-demo-panel {{
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.22);
    border-radius: 6px;
    padding: 6px 10px;
    margin-bottom: 8px;
    font-size: 11.5px;
    color: #F59E0B;
}}

.tf-demo-panel code {{
    background: rgba(245, 158, 11, 0.15);
    color: #F8FAFC;
    padding: 1px 4px;
    border-radius: 3px;
}}

.tf-whatif-banner {{
    background: rgba(0, 191, 166, 0.08);
    border: 1px solid rgba(0, 191, 166, 0.22);
    border-radius: 6px;
    padding: 6px 10px;
    margin-bottom: 8px;
    font-size: 11.5px;
    color: #00BFA6;
}}

.tf-disclaimer {{
    font-size: 11px;
    color: #64748B;
    padding: 8px 0;
    line-height: 1.4;
}}

/* ─── Form Inputs (Compact) ────────────────────────────────── */
div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {{
    background-color: #11161D !important;
    border: 1px solid #232D38 !important;
    border-radius: 6px !important;
    color: #F8FAFC !important;
    font-size: 12px !important;
    min-height: 34px !important;
}}

div[data-baseweb="select"] > div:hover,
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {{
    border-color: #00BFA6 !important;
}}

/* ─── Expanders (Compact) ──────────────────────────────────── */
details {{
    background: #11161D !important;
    border: 1px solid #232D38 !important;
    border-radius: 6px !important;
    margin-bottom: 6px !important;
}}

details summary {{
    color: #F8FAFC !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 6px 10px !important;
}}
</style>
"""
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HTML Helpers
# ---------------------------------------------------------------------------

def badge_html(label: str, kind: str = "pass") -> str:
    """Generate a clean status badge HTML without emoji icons."""
    kind_map = {
        "pass":      ("tf-badge-pass", "✓"),
        "rejected":  ("tf-badge-rejected", "×"),
        "demo":      ("tf-badge-demo", "!"),
        "locked":    ("tf-badge-locked", "🔒"),
        "completed": ("tf-badge-pass", "✓"),
        "current":   ("tf-badge-pass", "•"),
    }
    css_class, symbol = kind_map.get(kind.lower(), ("tf-badge-pass", "✓"))
    return f'<span class="tf-badge {css_class}">{symbol} {label}</span>'


def demo_field_html(field_name: str) -> str:
    """Return an amber DEMO indicator."""
    return '<span class="tf-badge tf-badge-demo">DEMO</span>'
