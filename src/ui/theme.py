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
    font-size: 14px;
    line-height: 1.5;
}}

/* ─── Main Content Container ───────────────────────────────── */
.main .block-container {{
    padding-top: 1.25rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1260px;
}}

/* ─── Sidebar Styling ──────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background-color: #11161D !important;
    border-right: 1px solid #232D38 !important;
    width: 250px !important;
    min-width: 250px !important;
    max-width: 250px !important;
    padding-top: 1rem !important;
    font-family: 'Inter', sans-serif !important;
}}

[data-testid="stSidebar"] span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] .material-symbols-rounded {{
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}}

[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
    color: #A1ABB3 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    transition: all 0.15s ease !important;
    margin-bottom: 2px !important;
}}

[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
    background-color: #161C24 !important;
    color: #F8FAFC !important;
}}

[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a.active {{
    background-color: rgba(0, 191, 166, 0.14) !important;
    color: #00BFA6 !important;
    font-weight: 600 !important;
    border-left: 3px solid #00BFA6 !important;
}}

/* ─── Typography & Headings ────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Inter', sans-serif !important;
    color: #F8FAFC !important;
    letter-spacing: -0.02em;
}}

h1 {{
    font-size: 26px !important;
    font-weight: 700 !important;
    margin-bottom: 0.25rem !important;
}}

h2 {{
    font-size: 22px !important;
    font-weight: 700 !important;
    margin-top: 1.25rem !important;
    margin-bottom: 0.5rem !important;
}}

h3 {{
    font-size: 18px !important;
    font-weight: 600 !important;
    margin-top: 1.25rem !important;
    margin-bottom: 0.4rem !important;
}}

h4 {{
    font-size: 15px !important;
    font-weight: 600 !important;
}}

p, span, label, div {{
    font-family: 'Inter', sans-serif;
}}

.stCaption, [data-testid="stCaptionContainer"] {{
    color: #A1ABB3 !important;
    font-size: 13px !important;
    margin-bottom: 12px !important;
}}

/* ─── Compact Scientific Cards ─────────────────────────────── */
.tf-card {{
    background: #11161D;
    border: 1px solid #232D38;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    margin-bottom: 12px;
}}

.tf-card-elevated {{
    background: #161C24;
    border: 1px solid #232D38;
    border-radius: 10px;
    padding: 18px 20px;
}}

/* ─── Compact Scientific Metric Card ────────────────────────── */
.tf-metric-card {{
    background: #11161D;
    border: 1px solid #232D38;
    border-radius: 8px;
    padding: 14px 16px;
    min-height: 86px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}

.tf-metric-label {{
    font-size: 11px;
    font-weight: 600;
    color: #A1ABB3;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}}

.tf-metric-value {{
    font-size: 20px;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.2;
}}

.tf-metric-context {{
    font-size: 12px;
    color: #A1ABB3;
    margin-top: 4px;
}}

/* ─── Buttons ──────────────────────────────────────────────── */
button[kind="primary"], .stButton > button[kind="primary"],
.stButton > button:first-child[data-testid="stBaseButton-primary"] {{
    background-color: #00BFA6 !important;
    color: #080F14 !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    height: 42px !important;
    border-radius: 6px !important;
    padding: 0 1.25rem !important;
    box-shadow: 0 2px 8px rgba(0, 191, 166, 0.25) !important;
    transition: all 0.15s ease !important;
}}

button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {{
    background-color: #00A892 !important;
    box-shadow: 0 4px 12px rgba(0, 191, 166, 0.35) !important;
}}

button[kind="secondary"], .stButton > button[kind="secondary"],
.stButton > button:first-child[data-testid="stBaseButton-secondary"] {{
    background-color: #161C24 !important;
    color: #F8FAFC !important;
    border: 1px solid #232D38 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    height: 40px !important;
    border-radius: 6px !important;
    padding: 0 1rem !important;
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
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 4px;
    letter-spacing: 0.02em;
}}

.tf-badge-pass {{
    background: rgba(0, 191, 166, 0.14);
    color: #00BFA6;
    border: 1px solid rgba(0, 191, 166, 0.35);
}}

.tf-badge-rejected {{
    background: rgba(239, 68, 68, 0.14);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.35);
}}

.tf-badge-demo {{
    background: rgba(245, 158, 11, 0.14);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.35);
}}

.tf-badge-locked {{
    background: #161C24;
    color: #64748B;
    border: 1px solid #232D38;
}}

/* ─── Data Tables (Streamlit Dataframe) ─────────────────────── */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
    border: 1px solid #232D38 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #11161D !important;
}}

/* ─── Horizontal Stepper ───────────────────────────────────── */
.stepper-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    padding: 12px 0 20px 0;
    max-width: 860px;
    margin: 0 auto;
}}

.stepper-line-bg {{
    position: absolute;
    top: 26px;
    left: 24px;
    right: 24px;
    height: 2px;
    background: #232D38;
    z-index: 1;
}}

.stepper-line-active {{
    position: absolute;
    top: 26px;
    left: 24px;
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
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #11161D;
    border: 2px solid #232D38;
    color: #A1ABB3;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
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
    box-shadow: 0 0 0 4px rgba(0, 191, 166, 0.18);
}}

.stepper-label {{
    font-size: 11px;
    font-weight: 600;
    color: #A1ABB3;
    margin-top: 6px;
    text-transform: capitalize;
}}

.stepper-step.current .stepper-label {{
    color: #00BFA6;
    font-weight: 700;
}}

/* ─── Notice Panels ────────────────────────────────────────── */
.tf-demo-panel {{
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.25);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 13px;
    color: #F59E0B;
}}

.tf-demo-panel code {{
    background: rgba(245, 158, 11, 0.15);
    color: #F8FAFC;
    padding: 2px 4px;
    border-radius: 3px;
}}

.tf-whatif-banner {{
    background: rgba(0, 191, 166, 0.08);
    border: 1px solid rgba(0, 191, 166, 0.25);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 13px;
    color: #00BFA6;
}}

.tf-disclaimer {{
    font-size: 12px;
    color: #64748B;
    padding: 12px 0;
    line-height: 1.5;
}}

/* ─── Form Inputs ──────────────────────────────────────────── */
div[data-baseweb="select"] > div,
.stTextInput > div > div > input,
.stNumberInput > div > div > input {{
    background-color: #11161D !important;
    border: 1px solid #232D38 !important;
    border-radius: 6px !important;
    color: #F8FAFC !important;
    font-size: 13px !important;
}}

div[data-baseweb="select"] > div:hover,
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {{
    border-color: #00BFA6 !important;
}}

/* ─── Expanders ────────────────────────────────────────────── */
details {{
    background: #11161D !important;
    border: 1px solid #232D38 !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}}

details summary {{
    color: #F8FAFC !important;
    font-size: 13px !important;
    font-weight: 600 !important;
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
