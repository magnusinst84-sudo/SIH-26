"""
pages/01_home.py
----------------
TargetForge — Home Page

Cinematic full-screen amber molecular hero (100vh, NO sidebar), followed by
6-step workflow stepper, 3 information cards, and interactive demo execution.

Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys
import time
import base64

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.ui.state import init_session_state, populate_from_pipeline, WorkflowStep
from src.ui.theme import inject_global_css, COLORS
from src.ui.components import (
    render_scientific_disclaimer,
    render_demo_banner,
    render_kpi_row,
    render_loading_stages,
)
from src.ui.charts import score_bar_chart

# Ensure state and CSS are initialised (idempotent)
inject_global_css()
init_session_state(_ROOT)

# ─── HIDE SIDEBAR ON HOME PAGE ONLY & EDGE-TO-EDGE HERO ──────────────────────
st.markdown(
"""<style>
/* Completely hide sidebar on Home page */
[data-testid="stSidebar"], 
[data-testid="collapsedControl"], 
section[data-testid="stSidebar"] {
    display: none !important;
}
/* Full-bleed edge-to-edge layout for cinematic hero */
.stApp [data-testid="stMainBlockContainer"],
.main .block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 1;
}
#hero-heading {
    color: #F8FAFC !important;
}
</style>""",
    unsafe_allow_html=True,
)

# ─── LOAD AMBER HERO IMAGE AS BASE64 ─────────────────────────────────────────
hero_img_path = _ROOT / "src" / "ui" / "assets" / "amber_molecular_hero.jpg"
if not hero_img_path.exists():
    hero_img_path = _ROOT / "src" / "ui" / "assets" / "molecular_hero_bg.jpg"

hero_bg_b64 = ""
if hero_img_path.exists():
    with open(hero_img_path, "rb") as f:
        hero_bg_b64 = base64.b64encode(f.read()).decode()

candidates = st.session_state.get("tf_candidates")
target_name = st.session_state.get("tf_target", {}).get("name", "EGFR kinase")
screened_count = 478
best_score = -8.2
candidates_count = 120

validated_df = st.session_state.get("tf_validated_df")
if validated_df is not None and not validated_df.empty:
    screened_count = len(validated_df)

if candidates:
    candidates_count = len(candidates)
    scores = [c.docking.score_raw for c in candidates if c.docking.score_raw is not None]
    if scores:
        best_score = min(scores)

# ─── FULL-SCREEN CINEMATIC HERO (100vh) ──────────────────────────────────────
hero_html = f"""<div style="position: relative; width: 100%; min-height: 100vh; background: linear-gradient(90deg, rgba(8, 15, 20, 0.96) 0%, rgba(8, 15, 20, 0.88) 40%, rgba(8, 15, 20, 0.35) 70%, rgba(8, 15, 20, 0.05) 100%), url('data:image/jpeg;base64,{hero_bg_b64}') center right / cover no-repeat; display: flex; flex-direction: column; justify-content: space-between; padding: 28px 56px 36px 56px; box-sizing: border-box;">
<!-- Top Navigation Overlay -->
<div style="display: flex; justify-content: space-between; align-items: center; width: 100%; padding-bottom: 20px;">
<div style="display: flex; align-items: center; gap: 10px;">
<svg viewBox="0 0 24 24" width="24" height="24" stroke="#00BFA6" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block;">
<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/>
<line x1="12" y1="7.5" x2="6.5" y2="15.5"/><line x1="12" y1="7.5" x2="17.5" y2="15.5"/><line x1="7.5" y1="18" x2="16.5" y2="18"/>
</svg>
<span style="font-size: 20px; font-weight: 700; color: #F8FAFC; letter-spacing: -0.02em;">
Target<span style="color: #00BFA6;">Forge</span>
</span>
</div>
<div style="display: flex; align-items: center; gap: 26px; font-size: 13px; font-weight: 500;">
<a href="/" target="_self" style="color: #00BFA6; text-decoration: none; font-weight: 600;">Home</a>
<a href="/target_explorer" target="_self" style="color: #A1ABB3; text-decoration: none; transition: color 0.15s ease;">Target Explorer</a>
<a href="/dataset_manager" target="_self" style="color: #A1ABB3; text-decoration: none; transition: color 0.15s ease;">Dataset Manager</a>
<a href="/ai_screening" target="_self" style="color: #A1ABB3; text-decoration: none; transition: color 0.15s ease;">AI Screening</a>
<a href="/candidate_design" target="_self" style="color: #A1ABB3; text-decoration: none; transition: color 0.15s ease;">Candidate Design</a>
<a href="/docking_analysis" target="_self" style="color: #A1ABB3; text-decoration: none; transition: color 0.15s ease;">Docking Analysis</a>
<a href="/final_ranking" target="_self" style="color: #A1ABB3; text-decoration: none; transition: color 0.15s ease;">Final Ranking</a>
<a href="/reports" target="_self" style="color: #A1ABB3; text-decoration: none; transition: color 0.15s ease;">Reports</a>
<div style="width: 26px; height: 26px; border-radius: 50%; border: 1px solid #232D38; display: flex; align-items: center; justify-content: center; color: #A1ABB3; font-size: 13px; cursor: pointer;">?</div>
</div>
</div>

<!-- Center Main Copy -->
<div style="max-width: 720px; margin-top: auto; margin-bottom: auto; padding: 40px 0;">
<h1 id="hero-heading" style="font-size: 54px; line-height: 1.12; font-weight: 800; color: #F8FAFC !important; margin: 0 0 20px 0; letter-spacing: -0.03em;">
Turning molecular<br>
complexity into<br>
clear, confident<br>
<span style="color: #00BFA6;">decisions.</span>
</h1>
<p style="font-size: 16px; line-height: 1.55; color: #A1ABB3; margin: 0 0 32px 0; max-width: 580px;">
AI-assisted virtual screening to identify high-potential molecules faster and smarter.
</p>
<div style="display: flex; gap: 14px; align-items: center;">
<a href="/target_explorer" target="_self" style="display: inline-flex; align-items: center; gap: 8px; background: #00BFA6; color: #080F14; font-weight: 700; font-size: 14px; padding: 12px 24px; border-radius: 6px; text-decoration: none; box-shadow: 0 2px 10px rgba(0, 191, 166, 0.35);">
Start Analysis →
</a>
<a href="#pipeline-runner" style="display: inline-flex; align-items: center; gap: 8px; background: rgba(22, 28, 36, 0.6); color: #F8FAFC; border: 1px solid rgba(255, 255, 255, 0.2); font-weight: 600; font-size: 14px; padding: 12px 22px; border-radius: 6px; text-decoration: none;">
Explore Demo <span style="font-size: 11px;">▷</span>
</a>
</div>
</div>

<!-- Bottom Slim Info Strip -->
<div style="display: flex; flex-wrap: wrap; align-items: center; background: rgba(17, 22, 29, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 12px 24px; color: #A1ABB3; font-size: 13px; gap: 20px;">
<a href="#pipeline-runner" style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid rgba(255, 255, 255, 0.2); display: flex; align-items: center; justify-content: center; color: #F8FAFC; text-decoration: none; font-size: 14px;">
↓
</a>
<div style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.12); padding: 4px 12px; border-radius: 20px; font-size: 12px; color: #A1ABB3; font-weight: 500;">
AI-assisted screening
</div>
<div>{screened_count} molecules screened</div>
<div style="color: #64748B;">•</div>
<div>Target: <strong style="color: #F8FAFC;">{target_name}</strong></div>
<div style="color: #64748B;">•</div>
<div>Best docking score: <strong style="color: #00BFA6;">{best_score:.1f} kcal/mol</strong></div>
<div style="color: #64748B;">•</div>
<div>Candidates generated: <strong style="color: #F8FAFC;">{candidates_count}</strong></div>
<div style="margin-left: auto; color: #64748B; font-weight: 700; letter-spacing: 2px;">— —</div>
</div>
</div>"""

st.markdown(hero_html, unsafe_allow_html=True)

# ─── BELOW HERO WORKSPACE CONTAINER ──────────────────────────────────────────
st.markdown(
    '<div id="pipeline-runner" style="max-width: 1220px; margin: 0 auto; padding: 56px 24px 32px 24px;">',
    unsafe_allow_html=True,
)

# ─── B. WORKFLOW STEPPER (Below Hero) ────────────────────────────────────────
st.markdown(
"""<div class="stepper-container" style="margin-bottom: 40px;">
<div class="stepper-line-bg"></div>
<div class="stepper-line-active" style="width: 0%;"></div>
<div class="stepper-step current"><div class="stepper-circle">1</div><div class="stepper-label">Target</div></div>
<div class="stepper-step"><div class="stepper-circle">2</div><div class="stepper-label">Data</div></div>
<div class="stepper-step"><div class="stepper-circle">3</div><div class="stepper-label">AI</div></div>
<div class="stepper-step"><div class="stepper-circle">4</div><div class="stepper-label">Candidates</div></div>
<div class="stepper-step"><div class="stepper-circle">5</div><div class="stepper-label">Docking</div></div>
<div class="stepper-step"><div class="stepper-circle">6</div><div class="stepper-label">Ranking</div></div>
</div>""",
    unsafe_allow_html=True,
)

# ─── C. INFORMATION CARDS ROW (Matching Reference Style) ─────────────────────
cols = st.columns(3, gap="medium")

with cols[0]:
    st.markdown("""<div class="tf-card" style="height: 100%; padding: 24px; border-radius: 12px; background: #11161D; border: 1px solid #232D38;">
<div style="width: 36px; height: 36px; border-radius: 50%; border: 1.5px solid #00BFA6; display: flex; align-items: center; justify-content: center; color: #00BFA6; margin-bottom: 16px;">
<svg viewBox="0 0 24 24" width="18" height="18" stroke="#00BFA6" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
</svg>
</div>
<h4 style="margin-top:0; color:#F8FAFC; font-size:16px; font-weight:700;">The Problem</h4>
<p style="font-size:13px; color:#A1ABB3; line-height:1.55; margin-bottom:0;">
Drug discovery is slow, expensive, and uncertain. Finding the right molecules for the right target is like finding a needle in a haystack.
</p>
</div>""", unsafe_allow_html=True)

with cols[1]:
    st.markdown("""<div class="tf-card" style="height: 100%; padding: 24px; border-radius: 12px; background: #11161D; border: 1px solid #232D38;">
<div style="width: 36px; height: 36px; border-radius: 50%; border: 1.5px solid #00BFA6; display: flex; align-items: center; justify-content: center; color: #00BFA6; margin-bottom: 16px;">
<svg viewBox="0 0 24 24" width="18" height="18" stroke="#00BFA6" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M9 18h6"/><path d="M10 22h4"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>
</svg>
</div>
<h4 style="margin-top:0; color:#F8FAFC; font-size:16px; font-weight:700;">Our Solution</h4>
<p style="font-size:13px; color:#A1ABB3; line-height:1.55; margin-bottom:0;">
TargetForge combines curated data, AI models, and structure-based methods to prioritize the most promising molecules early.
</p>
</div>""", unsafe_allow_html=True)

with cols[2]:
    st.markdown("""<div class="tf-card" style="height: 100%; padding: 24px; border-radius: 12px; background: #11161D; border: 1px solid #232D38;">
<div style="width: 36px; height: 36px; border-radius: 50%; border: 1.5px solid #00BFA6; display: flex; align-items: center; justify-content: center; color: #00BFA6; margin-bottom: 16px;">
<svg viewBox="0 0 24 24" width="18" height="18" stroke="#00BFA6" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>
</div>
<h4 style="margin-top:0; color:#F8FAFC; font-size:16px; font-weight:700;">Scientific Disclaimer</h4>
<p style="font-size:13px; color:#A1ABB3; line-height:1.55; margin-bottom:0;">
Predictions are computational and require experimental validation. Use results as decision-support, not as a substitute for experiments.
</p>
</div>""", unsafe_allow_html=True)

# ─── DEMO PIPELINE EXECUTION ACTION ──────────────────────────────────────────
st.markdown("<div style='margin-top: 36px;'></div>", unsafe_allow_html=True)
col_run, col_step = st.columns([1.2, 1], gap="large")

with col_run:
    run_btn = st.button(
        "Execute End-to-End Demo Screening",
        type="primary",
        use_container_width=True,
        help="Run the complete TargetForge demo pipeline end-to-end.",
    )

with col_step:
    st.page_link(
        "pages/02_target_explorer.py",
        label="→ Launch Step-by-Step Target Analysis",
        icon=":material/track_changes:",
    )

if run_btn:
    stages = [
        "Loading compound library",
        "Validating SMILES structures",
        "Calculating molecular descriptors",
        "Predicting biological activity",
        "Applying property filters",
        "Running docking simulation (fallback)",
        "Ranking and scoring candidates",
    ]
    stage_container = st.empty()
    with st.spinner("Running TargetForge computational screening pipeline…"):
        from src.pipeline.run_demo import run_demo
        for idx in range(len(stages)):
            with stage_container.container():
                render_loading_stages(stages, idx)
            time.sleep(0.18)
        ranked_df = run_demo(_ROOT)
        populate_from_pipeline(_ROOT, ranked_df)

    stage_container.empty()
    st.success("Screening complete! Candidate results are ready.")
    st.rerun()

# ─── RESULTS SUMMARY IF PIPELINE HAS RUN ──────────────────────────────────
candidates = st.session_state.get("tf_candidates")
if candidates:
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    render_demo_banner()
    render_kpi_row(candidates)
    st.markdown("")

    tab_chart, tab_info = st.tabs(["Score Summary", "Run Configuration"])
    with tab_chart:
        st.plotly_chart(score_bar_chart(candidates), use_container_width=True)
        st.page_link("pages/07_final_ranking.py", label="View Full Ranking Table →", icon=":material/leaderboard:")

    with tab_info:
        target = st.session_state.get("tf_target", {})
        weights = st.session_state.get("tf_weights", {})
        st.markdown(f"""
| Parameter | Value |
|---|---|
| Disease Indication | {target.get('disease','N/A')} |
| Biological Target | {target.get('name','N/A')} |
| Target Structure (PDB) | {target.get('structure_id','N/A')} |
| Surrogate Model | {target.get('model_version','demo_v1')} |
| Multi-Objective Weights | Activity {weights.get('activity_weight',0.4):.0%} / Docking {weights.get('docking_weight',0.3):.0%} / Property {weights.get('property_weight',0.2):.0%} / Novelty {weights.get('novelty_weight',0.1):.0%} |
""")

render_scientific_disclaimer()
st.markdown("</div>", unsafe_allow_html=True)
