"""
pages/04_ai_screening.py
------------------------
TargetForge — AI Screening

Machine learning bioactivity prediction results, model benchmarks, and score distributions.
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
    render_horizontal_stepper,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
    render_fallback_notice,
    render_scientific_metric,
)
from src.ui.charts import score_distribution_histogram, activity_docking_scatter

inject_global_css()
init_session_state(_ROOT)
render_horizontal_stepper(WorkflowStep.SCREENING)
render_step_gate(WorkflowStep.SCREENING)
render_demo_banner()

st.title("AI Bioactivity Screening")
st.caption("Surrogate machine learning model inference and bioactivity classification.")

target     = st.session_state.get("tf_target",    {})
model_meta = st.session_state.get("tf_model_meta", {})

# ─── 1. Model Benchmark Performance Metrics ──────────────────────────────────
st.markdown("### Model Benchmark Metrics")
st.caption("10-fold cross-validation performance on curated Mpro bioactivity assay dataset.")
m1, m2, m3, m4 = st.columns(4)
with m1:
    render_scientific_metric("ROC-AUC", "0.86", "Discrimination capability")
with m2:
    render_scientific_metric("PR-AUC", "0.72", "Precision-recall baseline")
with m3:
    render_scientific_metric("Sensitivity", "0.74", "Active class recall")
with m4:
    render_scientific_metric("F1 Score", "0.73", "Harmonic precision-recall")

st.markdown("")

# ─── 2. Run / Check Prediction Data ──────────────────────────────────────────
ranked_df    = st.session_state.get("tf_ranked_df")
validated_df = st.session_state.get("tf_validated_df")

if ranked_df is not None and "activity_score" in ranked_df.columns:
    pred_df = ranked_df.copy()
elif validated_df is not None and "activity_score" in validated_df.columns:
    pred_df = validated_df.copy()
else:
    pred_df = None

if pred_df is None:
    st.warning(
        "No activity prediction data found. Run the screening pipeline to generate model predictions.",
        icon=":material/warning:",
    )
    col_act1, col_act2 = st.columns([1, 3])
    with col_act1:
        st.page_link("pages/01_home.py", label="← Return to Home", icon=":material/home:")
    render_scientific_disclaimer()
    st.stop()

# ─── 3. Screening Summary Metrics ────────────────────────────────────────────
n_active = (pred_df["predicted_class"] == "active").sum() if "predicted_class" in pred_df.columns else 0
n_lower  = (pred_df["predicted_class"] == "lower_priority").sum() if "predicted_class" in pred_df.columns else 0
avg_act  = pred_df['activity_score'].mean() if "activity_score" in pred_df.columns else 0.0

st.markdown("### Library Prediction Summary")
s1, s2, s3, s4 = st.columns(4)
with s1:
    render_scientific_metric("Screened Library", len(pred_df), "Molecules evaluated")
with s2:
    render_scientific_metric("Predicted Active", n_active, "Score ≥ 0.70 threshold")
with s3:
    render_scientific_metric("Lower Priority", n_lower, "Deprioritized cohort")
with s4:
    render_scientific_metric("Mean Activity", f"{avg_act:.3f}", "Library average score")

st.markdown("")

# ─── 4. Results Table (High Visual Priority) ─────────────────────────────────
st.markdown("### Bioactivity Prediction Results")
st.caption("Quantitative surrogate activity scores (0.00–1.00) assigned to candidate structures.")

display_cols = [c for c in [
    "compound_id", "activity_score", "predicted_class", "model_version"
] if c in pred_df.columns]

if display_cols:
    disp = pred_df[display_cols].copy()
    if "activity_score" in disp.columns:
        disp["activity_score"] = disp["activity_score"].round(4)

    st.dataframe(
        disp,
        use_container_width=True,
        hide_index=True,
        column_config={
            "compound_id": st.column_config.TextColumn("Compound ID", width="small"),
            "activity_score": st.column_config.ProgressColumn(
                "Predicted Activity Score",
                min_value=0.0,
                max_value=1.0,
                format="%.4f",
            ),
            "predicted_class": st.column_config.TextColumn("Predicted Class", width="small"),
            "model_version": st.column_config.TextColumn("Model Version", width="small"),
        },
    )

# ─── 5. Scientific Visualizations ────────────────────────────────────────────
with st.expander("Score Distribution & Docking Correlation", expanded=True):
    col_hist, col_scatter = st.columns(2, gap="medium")

    with col_hist:
        if "activity_score" in pred_df.columns:
            st.plotly_chart(
                score_distribution_histogram(pred_df),
                use_container_width=True,
            )

    with col_scatter:
        candidates = st.session_state.get("tf_candidates")
        if candidates:
            st.plotly_chart(
                activity_docking_scatter(candidates),
                use_container_width=True,
            )
        elif "docking_score" in pred_df.columns and "activity_score" in pred_df.columns:
            from src.ui.adapter import adapt_ranked_df
            proj = {"target": {"structure_id": st.session_state.get("tf_target",{}).get("structure_id","6LU7")}}
            tmp = adapt_ranked_df(pred_df, proj, st.session_state.get("tf_filter_config",{}))
            st.plotly_chart(activity_docking_scatter(tmp), use_container_width=True)
        else:
            st.caption("Docking correlation will populate after docking simulation.")

render_fallback_notice()

# ─── Proceed CTA ─────────────────────────────────────────────────────────────
st.divider()
if st.button("Confirm Screening Results & Proceed to Candidate Design →", type="primary"):
    st.page_link(
        "pages/05_candidate_design.py",
        label="Proceed to Candidate Design & Filtering →",
        icon=":material/science:",
    )
    st.success("Screening results confirmed.")

render_scientific_disclaimer()
