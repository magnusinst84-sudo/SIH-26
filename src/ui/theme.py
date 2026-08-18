"""
src/ui/theme.py
---------------
Premium dark scientific workspace theme for TargetForge.
Colors are based on a cool cyan, deep space blue, and purple palette.

Authoritative palette:
  Background : #030A16  (Deep space blue)
  Surface    : #091427  (Dark translucent surface)
  Surface Glow: #0E1E38 (Active/hover surface)
  Border     : #1A365D  (Steel blue border)
  Teal/Cyan  : #00B4D8  (Glowing cyan primary accent)
  Blue       : #0077B6  (Secondary accent)
  Text       : #E2E8F0  (Main bright text)
  Muted      : #94A3B8  (Cool gray/blue muted text)

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
    "bg":           "#030A16",
    "surface":      "#091427",
    "surface_glow": "#0E1E38",
    "border":       "#1A365D",
    "teal":         "#00B4D8",
    "blue":         "#0077B6",
    "cyan":         "#90E0EF",
    "text":         "#E2E8F0",
    "muted":        "#94A3B8",
    "navy":         "#091427",
    "navy_light":   "#0E1E38",
    # Status / badge colours
    "pass_bg":      "rgba(16, 185, 129, 0.15)",
    "pass_text":    "#34D399",
    "pass_border":  "rgba(16, 185, 129, 0.4)",
    "reject_bg":    "rgba(239, 68, 68, 0.15)",
    "reject_text":  "#F87171",
    "reject_border": "rgba(239, 68, 68, 0.4)",
    "demo_bg":      "rgba(245, 158, 11, 0.15)",
    "demo_text":    "#FBBF24",
    "demo_border":  "rgba(245, 158, 11, 0.4)",
    "locked_bg":    "rgba(107, 114, 128, 0.15)",
    "locked_text":  "#9CA3AF",
    "locked_border": "rgba(107, 114, 128, 0.3)",
    "current_bg":   "rgba(59, 130, 246, 0.2)",
    "current_text": "#60A5FA",
    "current_border": "rgba(59, 130, 246, 0.5)",
    # Chart palette
    "chart": ["#00B4D8", "#0077B6", "#90E0EF", "#F59E0B", "#EF4444", "#8B5CF6"],
}

# Plotly theming constants (imported by charts.py)
CHART_TEMPLATE  = "plotly_dark"
CHART_FONT      = dict(family="Inter, Arial, sans-serif", color=COLORS["text"], size=12)
CHART_BGCOLOR   = COLORS["surface"]
CHART_PAPER     = COLORS["bg"]
CHART_COLORS    = COLORS["chart"]


def get_hero_bg_base64() -> str:
    """Read the hero background image from assets and encode to base64."""
    try:
        root = Path(__file__).resolve().parent.parent.parent
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
    """Inject the TargetForge global stylesheet once per page load."""
    base64_bg = get_hero_bg_base64()
    
    # If the image was loaded successfully, use it in CSS, otherwise fallback to gradient
    hero_bg_css = f"background-image: linear-gradient(rgba(3, 10, 22, 0.72), rgba(3, 10, 22, 0.88)), url('data:image/jpeg;base64,{base64_bg}');" if base64_bg else "background: linear-gradient(135deg, #030A16 0%, #091427 50%, #0E1E38 100%);"

    _CSS = f"""
<style>
/* ─── Google Fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ─── Global App Layout ──────────────────────────────────────  */
html, body, .stApp {{
    background-color: #030A16 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #E2E8F0;
}}

/* ─── Main Content Area ─────────────────────────────────────  */
.main .block-container {{
    padding-top: 1rem;
    padding-bottom: 2.5rem;
    max-width: 1200px;
}}

/* ─── Hide Sidebar Globally ─────────────────────────────────  */
[data-testid="stSidebar"] {{
    display: none !important;
}}
[data-testid="collapsedControl"] {{
    display: none !important;
}}

/* ─── Navbar Styles ──────────────────────────────────────────  */
.tf-navbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(9, 20, 39, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #1A365D;
    padding: 0.75rem 1.5rem;
    position: sticky;
    top: 0;
    z-index: 999;
    margin-bottom: 1.5rem;
    border-radius: 8px;
}}

.tf-navbar-brand {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 700;
    font-size: 1.25rem;
    color: #E2E8F0 !important;
    text-decoration: none !important;
}}

.tf-navbar-brand span {{
    color: #00B4D8;
}}

/* Native Page Link Styling inside Navbar */
div[data-testid="stPageLink"] {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}}

div[data-testid="stPageLink"] a {{
    background: transparent !important;
    border: none !important;
    color: #94A3B8 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
    text-decoration: none !important;
}}

div[data-testid="stPageLink"] a:hover {{
    color: #00B4D8 !important;
    background: rgba(0, 180, 216, 0.08) !important;
}}

/* Target active page link by aria-selected or style override */
div[data-testid="stPageLink"] a[aria-selected="true"] {{
    color: #00B4D8 !important;
    font-weight: 600 !important;
    background: rgba(0, 180, 216, 0.12) !important;
    border-bottom: 2px solid #00B4D8;
    border-bottom-left-radius: 0px !important;
    border-bottom-right-radius: 0px !important;
}}

/* ─── Typography ─────────────────────────────────────────────  */
h1, h2, h3, h4 {{
    color: #E2E8F0 !important;
    font-weight: 600;
}}
h1 {{ font-weight: 700; letter-spacing: -0.025em; }}
p  {{ color: #94A3B8; line-height: 1.6; }}

/* ─── Metrics / Cards ────────────────────────────────────────  */
[data-testid="metric-container"] {{
    background: rgba(9, 20, 39, 0.6) !important;
    border: 1px solid #1A365D !important;
    border-radius: 10px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 4px 12px rgba(3, 10, 22, 0.5) !important;
    backdrop-filter: blur(8px);
}}
[data-testid="stMetricLabel"] {{ 
    color: #94A3B8 !important; 
    font-size: 0.78rem !important;
    font-weight: 600 !important; 
    text-transform: uppercase; 
    letter-spacing: 0.06em; 
}}
[data-testid="stMetricValue"] {{ 
    color: #00B4D8 !important; 
    font-weight: 700 !important; 
}}

/* ─── Custom Card Containers ─────────────────────────────────  */
.tf-card {{
    background: rgba(9, 20, 39, 0.6);
    border: 1px solid #1A365D;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(3, 10, 22, 0.5);
    backdrop-filter: blur(8px);
}}
.tf-card-sm {{
    background: rgba(9, 20, 39, 0.4);
    border: 1px solid #1A365D;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 8px rgba(3, 10, 22, 0.3);
    backdrop-filter: blur(6px);
}}

/* ─── Buttons ────────────────────────────────────────────────  */
.stButton > button {{
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
}}
.stButton > button[kind="primary"] {{
    background-color: #00B4D8 !important;
    border-color: #00B4D8 !important;
    color: #030A16 !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: #90E0EF !important;
    border-color: #90E0EF !important;
    box-shadow: 0 0 15px rgba(0, 180, 216, 0.4) !important;
    transform: translateY(-1px);
}}
.stButton > button[kind="secondary"] {{
    border-color: #1A365D !important;
    color: #E2E8F0 !important;
    background: rgba(9, 20, 39, 0.5) !important;
}}
.stButton > button[kind="secondary"]:hover {{
    border-color: #00B4D8 !important;
    color: #00B4D8 !important;
    background: rgba(0, 180, 216, 0.05) !important;
}}

/* ─── DataFrames / Tables ────────────────────────────────────  */
.stDataFrame {{ border: 1px solid #1A365D; border-radius: 8px; overflow: hidden; }}

/* ─── Sliders ────────────────────────────────────────────────  */
.stSlider > div > div > div > div {{ background-color: #00B4D8 !important; }}

/* ─── Tabs ───────────────────────────────────────────────────  */
[data-baseweb="tab-list"] {{ border-bottom: 1.5px solid #1A365D; gap: 0; }}
[data-baseweb="tab"] {{
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: #94A3B8;
    padding: 0.5rem 1rem;
}}
[aria-selected="true"][data-baseweb="tab"] {{
    color: #00B4D8 !important;
    font-weight: 600;
    border-bottom: 2px solid #00B4D8;
    background: transparent;
}}

/* ─── Alert / Expanders ──────────────────────────────────────  */
.stAlert {{ border-radius: 8px !important; background-color: rgba(9, 20, 39, 0.7) !important; border: 1px solid #1A365D !important; }}
[data-testid="stExpander"] {{
    border: 1px solid #1A365D;
    border-radius: 8px;
    background: rgba(9, 20, 39, 0.5);
}}
[data-testid="stExpander"] summary {{ font-weight: 500; color: #E2E8F0; }}

/* ─── Progress bars ──────────────────────────────────────────  */
.stProgress > div > div {{ background-color: #00B4D8 !important; }}
hr {{ border-color: #1A365D !important; }}

/* ─── Hero Section (Overlaid Text and image bg) ──────────────  */
.hero-section {{
    {hero_bg_css}
    background-size: cover;
    background-position: center;
    border-radius: 14px;
    padding: 4rem 3rem 2rem 3rem;
    margin-bottom: 0.5rem;
    position: relative;
    border: 1px solid #1A365D;
    box-shadow: 0 4px 20px rgba(0, 180, 216, 0.15);
    overflow: hidden;
}}
.hero-content {{
    position: relative;
    z-index: 2;
    max-width: 750px;
}}
.hero-section h1 {{ 
    color: #FFFFFF !important; 
    font-size: 2.75rem; 
    line-height: 1.15;
    margin-bottom: 1rem; 
    font-weight: 700;
    letter-spacing: -0.03em;
}}
.hero-section h1 span {{
    color: #00B4D8;
}}
.hero-section p {{ 
    color: #CBD5E1 !important; 
    font-size: 1.125rem; 
    margin-bottom: 2rem;
    line-height: 1.5;
}}

/* Hero Ticker Panel (translucent bar at the bottom) */
.hero-ticker {{
    background: rgba(9, 20, 39, 0.85);
    border-top: 1px solid #1A365D;
    border-bottom: 1px solid #1A365D;
    padding: 0.75rem 2rem;
    margin-bottom: 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #94A3B8;
    box-shadow: 0 4px 12px rgba(3, 10, 22, 0.4);
}}
.hero-ticker-item {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
}}
.hero-ticker-item strong {{
    color: #00B4D8;
}}

/* ─── Horizontal Stepper Stepper (Mockup) ───────────────────  */
.stepper-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    padding: 1.5rem 1rem;
    margin-bottom: 2rem;
    background: rgba(9, 20, 39, 0.4);
    border: 1px solid #1A365D;
    border-radius: 10px;
}}

.stepper-line-bg {{
    position: absolute;
    top: 50%;
    left: 8%;
    right: 8%;
    height: 2px;
    background: #1A365D;
    z-index: 1;
    transform: translateY(-50%);
}}

.stepper-line-active {{
    position: absolute;
    top: 50%;
    left: 8%;
    height: 2px;
    background: #00B4D8;
    z-index: 1;
    transform: translateY(-50%);
    transition: width 0.3s ease;
}}

.stepper-step {{
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 2;
    width: 60px;
    text-align: center;
}}

.stepper-circle {{
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #091427;
    border: 2px solid #1A365D;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 600;
    color: #94A3B8;
    transition: all 0.3s ease;
}}

.stepper-label {{
    font-size: 0.78rem;
    margin-top: 0.4rem;
    color: #94A3B8;
    font-weight: 500;
    white-space: nowrap;
    transition: all 0.3s ease;
}}

/* Stepper step state modifiers */
.stepper-step.completed .stepper-circle {{
    background: #00B4D8;
    border-color: #00B4D8;
    color: #030A16;
}}
.stepper-step.completed .stepper-label {{
    color: #00B4D8;
}}

.stepper-step.current .stepper-circle {{
    border-color: #00B4D8;
    color: #00B4D8;
    box-shadow: 0 0 10px rgba(0, 180, 216, 0.4);
}}
.stepper-step.current .stepper-label {{
    color: #E2E8F0;
    font-weight: 600;
}}

.stepper-step.locked {{
    opacity: 0.6;
}}

/* Badges */
.tf-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    border: 1px solid transparent;
    letter-spacing: 0.02em;
}}
.tf-badge-pass      {{ background: rgba(16, 185, 129, 0.15); color: #34D399; border-color: rgba(16, 185, 129, 0.4); }}
.tf-badge-rejected  {{ background: rgba(239, 68, 68, 0.15); color: #F87171; border-color: rgba(239, 68, 68, 0.4); }}
.tf-badge-demo      {{ background: rgba(245, 158, 11, 0.15); color: #FBBF24; border-color: rgba(245, 158, 11, 0.4); }}
.tf-badge-fallback  {{ background: rgba(245, 158, 11, 0.15); color: #FBBF24; border-color: rgba(245, 158, 11, 0.4); }}
.tf-badge-locked    {{ background: rgba(107, 114, 128, 0.15); color: #9CA3AF; border-color: rgba(107, 114, 128, 0.3); }}
.tf-badge-completed {{ background: rgba(16, 185, 129, 0.15); color: #34D399; border-color: rgba(16, 185, 129, 0.4); }}
.tf-badge-current   {{ background: rgba(59, 130, 246, 0.2); color: #60A5FA; border-color: rgba(59, 130, 246, 0.5); }}
.tf-badge-active    {{ background: rgba(16, 185, 129, 0.15); color: #34D399; border-color: rgba(16, 185, 129, 0.4); }}
.tf-badge-lower     {{ background: rgba(255, 255, 255, 0.05); color: #94A3B8; border-color: rgba(255, 255, 255, 0.1); }}

/* Demo banner */
.tf-demo-panel {{
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    margin-bottom: 1.5rem;
}}
.tf-demo-panel p {{ color: #FBBF24 !important; margin: 0; font-size: 0.88rem; }}
.tf-demo-panel strong {{ color: #F59E0B !important; }}

/* What-if banner */
.tf-whatif-banner {{
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.25);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
}}
.tf-whatif-banner p {{ color: #FBBF24 !important; margin: 0; font-weight: 500; }}

/* Rank Row Highlights */
.rank-1 {{ background: linear-gradient(90deg, rgba(234, 179, 8, 0.1) 0%, transparent 100%);
           border-left: 4px solid #EAB308; padding-left: 0.75rem; }}
.rank-2 {{ background: linear-gradient(90deg, rgba(148, 163, 184, 0.1) 0%, transparent 100%);
           border-left: 4px solid #94A3B8; padding-left: 0.75rem; }}
.rank-3 {{ background: linear-gradient(90deg, rgba(249, 115, 22, 0.1) 0%, transparent 100%);
           border-left: 4px solid #F97316; padding-left: 0.75rem; }}

/* Footer */
.tf-disclaimer {{
    font-size: 0.78rem;
    color: #64748B;
    border-top: 1px solid #1A365D;
    padding-top: 1rem;
    margin-top: 2rem;
    line-height: 1.6;
}}
</style>
"""
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Badge HTML helpers
# ---------------------------------------------------------------------------

def badge_html(text: str, kind: str = "demo") -> str:
    """Return inline HTML for a styled badge span."""
    return f'<span class="tf-badge tf-badge-{kind}">{text}</span>'


def demo_field_html(field_name: str) -> str:
    """Return a small amber DEMO inline marker for a named field."""
    return (
        f'<span title="{field_name} is a deterministic demo value. '
        f'Not a validated scientific result." '
        f'class="tf-badge tf-badge-demo">DEMO</span>'
    )
