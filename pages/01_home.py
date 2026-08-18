"""
pages/01_home.py
----------------
TargetForge — Home Page

Landing page with hero section, pipeline CTA, and results summary.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys
import time

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.ui.state import init_session_state, populate_from_pipeline, WorkflowStep
from src.ui.theme import inject_global_css
from src.ui.components import (
    render_top_navbar,
    render_horizontal_stepper,
    render_hero_banner,
    render_stats_ticker,
    render_scientific_disclaimer,
    render_demo_banner,
    render_kpi_row,
    render_loading_stages,
)
from src.ui.charts import score_bar_chart

# Ensure state and CSS are initialised (idempotent)
inject_global_css()
init_session_state(_ROOT)

# Get candidates to populate metrics in ticker
candidates = st.session_state.get("tf_candidates")

# Render top navbar and progress stepper
render_top_navbar()
render_horizontal_stepper(WorkflowStep.TARGET)

# ─── Hero ────────────────────────────────────────────────────────────────────
render_hero_banner()
render_stats_ticker(candidates)

# ─── One-shot demo pipeline trigger ─────────────────────────────────────────
pipeline_ran = st.session_state.get("tf_pipeline_ran", False)

col_run, col_step = st.columns([1, 1], gap="large")

with col_run:
    run_btn = st.button(
        "Run Full Demo Screening",
        type="primary",
        use_container_width=True,
        help="Run the complete TargetForge demo pipeline end-to-end.",
    )

with col_step:
    st.page_link(
        "pages/02_target_explorer.py",
        label="→ Start step-by-step workflow",
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
    with st.spinner("Running TargetForge demonstration pipeline…"):
        from src.pipeline.run_demo import run_demo  # M2 — unchanged call
        for idx in range(len(stages)):
            with stage_container.container():
                render_loading_stages(stages, idx)
            time.sleep(0.18)
        ranked_df = run_demo(_ROOT)
        populate_from_pipeline(_ROOT, ranked_df)

    stage_container.empty()
    st.success("Screening complete! Results are ready.")
    st.rerun()

# ─── Results view ────────────────────────────────────────────────────────────
candidates = st.session_state.get("tf_candidates")

if candidates:
    render_demo_banner()
    render_kpi_row(candidates)
    st.markdown("")

    tab_chart, tab_info = st.tabs(["Score Summary", "About This Run"])
    with tab_chart:
        st.plotly_chart(score_bar_chart(candidates), use_container_width=True)
        st.page_link("pages/07_final_ranking.py", label="View Full Ranking →", icon=":material/leaderboard:")

    with tab_info:
        target = st.session_state.get("tf_target", {})
        weights = st.session_state.get("tf_weights", {})
        st.markdown(f"""
| Field | Value |
|---|---|
| Disease | {target.get('disease','N/A')} |
| Target | {target.get('name','N/A')} |
| PDB Structure | {target.get('structure_id','N/A')} |
| Model | {target.get('model_version','demo_v1')} |
| Ranking weights | Activity {weights.get('activity_weight',0.4):.0%} / Docking {weights.get('docking_weight',0.3):.0%} / Property {weights.get('property_weight',0.2):.0%} / Novelty {weights.get('novelty_weight',0.1):.0%} |
""")

else:
    # No data yet — show info cards
    st.info(
        "Click **Run Full Demo Screening** to execute the TargetForge pipeline, "
        "or use the top navigation menu to proceed step-by-step.",
        icon=":material/info:",
    )
    
    st.markdown("### Platform Overview")
    cols = st.columns(3, gap="medium")
    with cols[0]:
        st.markdown("""
        <div class="tf-card" style="height: 100%;">
            <h4 style="margin-top:0;">The Challenge</h4>
            <p style="font-size:0.88rem; margin-bottom:0;">Traditional drug discovery is a prolonged, resource-intensive process characterized by high attrition rates, where identifying viable hits from chemical space remains a major bottleneck.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="tf-card" style="height: 100%;">
            <h4 style="margin-top:0;">The Solution</h4>
            <p style="font-size:0.88rem; margin-bottom:0;">TargetForge integrates machine learning activity prediction with structure-based docking to execute rapid in silico virtual screening, delivering prioritized candidate leads.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class="tf-card" style="height: 100%;">
            <h4 style="margin-top:0;">Validation Protocol</h4>
            <p style="font-size:0.88rem; margin-bottom:0;">All screening outputs are computational hypotheses designed to guide discovery pipelines. In vitro validation and assays are required for therapeutic confirmation.</p>
        </div>
        """, unsafe_allow_html=True)

render_scientific_disclaimer()
