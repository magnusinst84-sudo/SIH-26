"""
pages/04_ai_screening.py
------------------------
TargetForge — AI Screening

Displays activity prediction results from the pipeline.
Does NOT call demo_predict() — reads pre-computed data from session state.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd
import streamlit as st

from src.ui.state import init_session_state, WorkflowStep
from src.ui.theme import inject_global_css, badge_html, COLORS
from src.ui.components import (
    render_sidebar_progress,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
    render_fallback_notice,
)
from src.ui.charts import score_distribution_histogram, activity_docking_scatter

inject_global_css()
init_session_state(_ROOT)
render_sidebar_progress()
render_step_gate(WorkflowStep.SCREENING)

st.title("🤖 AI Screening")
st.caption("Activity prediction results for validated compounds.")

render_demo_banner()

# ─── Model info banner ───────────────────────────────────────────────────────
target     = st.session_state.get("tf_target",    {})
model_meta = st.session_state.get("tf_model_meta", {})

st.markdown(
    f'<div class="tf-card-sm">'
    f'<strong>🤖 Model: </strong>{target.get("model_version","demo_v1")} '
    f'({target.get("model_type","demo_activity_model")})'
    f'&nbsp;&nbsp;'
    f'<span class="tf-badge tf-badge-demo">⚠ DEMO PREDICTIONS</span>'
    f'</div>',
    unsafe_allow_html=True,
)
st.info(
    "Activity scores are **deterministic demo values** derived from the SHA-256 hash "
    "of each compound ID. They are not the output of a trained machine-learning model. "
    "Replace `src/ml/predict.py` with real model predictions during implementation.",
    icon="⚠️",
)

# ─── Activity prediction data ────────────────────────────────────────────────
# Read from session state — ranked_df contains activity scores for docked compounds.
# validated_df contains scores for ALL compounds (after full pipeline run).
ranked_df    = st.session_state.get("tf_ranked_df")
validated_df = st.session_state.get("tf_validated_df")

# Build display DataFrame from whatever is available
if ranked_df is not None and "activity_score" in ranked_df.columns:
    pred_df = ranked_df.copy()
elif validated_df is not None and "activity_score" in validated_df.columns:
    pred_df = validated_df.copy()
else:
    pred_df = None

if pred_df is None:
    st.warning(
        "No activity prediction data found. "
        "Run the demo pipeline from the Home page first.",
        icon="⚠️",
    )
    st.page_link("pages/01_home.py", label="← Go to Home", icon="🏠")
    render_scientific_disclaimer()
    st.stop()

# ─── Metrics ─────────────────────────────────────────────────────────────────
n_active = (pred_df["predicted_class"] == "active").sum() \
    if "predicted_class" in pred_df.columns else 0
n_lower  = (pred_df["predicted_class"] == "lower_priority").sum() \
    if "predicted_class" in pred_df.columns else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Compounds Screened", len(pred_df))
m2.metric("Predicted Active",   n_active)
m3.metric("Lower Priority",     n_lower)
m4.metric("Avg Activity Score",
          f"{pred_df['activity_score'].mean():.3f}"
          if "activity_score" in pred_df.columns else "N/A")

# ─── Results table ───────────────────────────────────────────────────────────
st.markdown("### Prediction Results")

display_cols = [c for c in [
    "compound_id", "activity_score", "predicted_class", "model_version"
] if c in pred_df.columns]

if display_cols:
    disp = pred_df[display_cols].copy()

    def _class_badge(cls: str) -> str:
        if cls == "active":
            return "✅ active"
        return "⬜ lower_priority"

    if "predicted_class" in disp.columns:
        disp["predicted_class"] = disp["predicted_class"].apply(_class_badge)
    if "activity_score" in disp.columns:
        disp["activity_score"] = disp["activity_score"].round(4)

    st.dataframe(
        disp,
        use_container_width=True,
        hide_index=True,
        column_config={
            "activity_score": st.column_config.ProgressColumn(
                "Activity Score ⚠DEMO",
                min_value=0.0,
                max_value=1.0,
                format="%.4f",
            ),
        },
    )
    st.caption("⚠ activity_score and model_version are deterministic demo values.")

# ─── Charts ──────────────────────────────────────────────────────────────────
col_hist, col_scatter = st.columns(2)

with col_hist:
    st.markdown("#### Score Distribution")
    if "activity_score" in pred_df.columns:
        st.plotly_chart(
            score_distribution_histogram(pred_df),
            use_container_width=True,
        )

with col_scatter:
    st.markdown("#### Activity vs Docking Score")
    candidates = st.session_state.get("tf_candidates")
    if candidates:
        st.plotly_chart(
            activity_docking_scatter(candidates),
            use_container_width=True,
        )
    elif "docking_score" in pred_df.columns and "activity_score" in pred_df.columns:
        # Fallback: show from ranked_df directly
        from src.ui.adapter import adapt_ranked_df
        proj = {"target": {"structure_id": st.session_state.get("tf_target",{}).get("structure_id","6LU7")}}
        tmp = adapt_ranked_df(pred_df, proj, st.session_state.get("tf_filter_config",{}))
        st.plotly_chart(activity_docking_scatter(tmp), use_container_width=True)
    else:
        st.caption("Docking scores not yet available — run the full pipeline from Home.")

render_fallback_notice()

# ─── Proceed ─────────────────────────────────────────────────────────────────
st.divider()
st.page_link(
    "pages/05_candidate_design.py",
    label="Proceed to Candidate Design →",
    icon="🧪",
)

render_scientific_disclaimer()
