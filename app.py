"""
app.py — TargetForge entry point and navigation router.

Responsibilities (ONLY):
  1. Add repo root to sys.path.
  2. Call st.set_page_config.
  3. Inject global CSS.
  4. Initialise session state.
  5. Define st.Page objects for all 8 workflow pages.
  6. Call st.navigation to dispatch to the active page.

All content is rendered in the individual page modules under pages/.
This file does NOT render any content itself.

Team ownership: M4 (Frontend/UI Lead) owns app.py and pages/*.
                Do not modify src/ml/, src/pipeline/, src/ranking/,
                src/docking/, src/data/, src/chemistry/, src/molecular_ai/,
                configs/, data/, tests/, or scripts/.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import streamlit as st

from src.ui.theme import inject_global_css
from src.ui.state import init_session_state

# ─── Page config (must be the very first Streamlit call) ─────────────────────
st.set_page_config(
    page_title          = "TargetForge",
    page_icon           = "src/ui/assets/favicon.png",
    layout              = "wide",
    initial_sidebar_state = "expanded",
)

# ─── Global CSS + session state (idempotent) ──────────────────────────────────
inject_global_css()
init_session_state(ROOT)

# ─── Page definitions ─────────────────────────────────────────────────────────
pages = [
    st.Page("pages/01_home.py",             title="Home",             icon=":material/home:", default=True),
    st.Page("pages/02_target_explorer.py",  title="Target Explorer",  icon=":material/track_changes:"),
    st.Page("pages/03_dataset_manager.py",  title="Dataset Manager",  icon=":material/database:"),
    st.Page("pages/04_ai_screening.py",     title="AI Screening",     icon=":material/hub:"),
    st.Page("pages/05_candidate_design.py", title="Candidate Design", icon=":material/science:"),
    st.Page("pages/06_docking_analysis.py", title="Docking Analysis", icon=":material/join_inner:"),
    st.Page("pages/07_final_ranking.py",    title="Final Ranking",    icon=":material/leaderboard:"),
    st.Page("pages/08_reports.py",          title="Reports",          icon=":material/description:"),
]

# ─── Sidebar branding ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding: 0 4px 16px 4px; border-bottom: 1px solid #232D38; margin-bottom: 12px;">'
        '<span style="font-size: 18px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em;">'
        'Target<span style="color: #00BFA6;">Forge</span>'
        '</span>'
        '<div style="font-size: 11px; color: #A1ABB3; margin-top: 2px;">Scientific Decision Support</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ─── Navigation dispatch ──────────────────────────────────────────────────────
pg = st.navigation(pages)
pg.run()
