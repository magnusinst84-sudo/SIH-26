"""
pages/07_final_ranking.py
--------------------------
TargetForge — Final Ranking

Section A: Official computational ranking (backend, read-only).
Section B: What-if ranking analysis (UI-only, clearly labeled).

INVARIANTS:
  - tf_ranked_df and tf_candidates are NEVER mutated here.
  - What-if results go to tf_whatif_ranked only.
  - Backend final_score and rank are displayed as-is.

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
from src.ui.theme import inject_global_css, badge_html, demo_field_html, COLORS
from src.ui.components import (
    render_top_navbar,
    render_horizontal_stepper,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
    render_kpi_row,
    render_candidate_card,
    render_fallback_notice,
    render_whatif_label,
)
from src.ui.charts import (
    score_bar_chart,
    score_waterfall,
    whatif_comparison_chart,
)
from src.ui.adapter import rerank_candidates
from src.ui.export import build_ranking_csv

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.RANKING)
render_step_gate(WorkflowStep.RANKING)
render_demo_banner()

st.title("Final Ranking")
st.caption("Official computational ranking and what-if weight analysis.")

# ─── Data ────────────────────────────────────────────────────────────────────
candidates = st.session_state.get("tf_candidates") or []
weights    = st.session_state.get("tf_weights")    or {}

if not candidates:
    st.warning("No ranking data found. Run the demo pipeline from Home first.", icon=":material/warning:")
    st.page_link("pages/01_home.py", label="← Go to Home", icon=":material/home:")
    render_scientific_disclaimer()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION A — Official Computational Ranking
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="tf-card" style="border-left:4px solid #102A43">'
    '<h2 style="margin-top:0;color:#102A43">Official Computational Ranking</h2>'
    '<p style="color:#52606D;margin:0">Produced by the TargetForge pipeline using fixed weights '
    'from <code>configs/project.yaml</code>. These values are preserved exactly as computed.</p>'
    '</div>',
    unsafe_allow_html=True,
)

# KPI row
render_kpi_row(candidates)
st.markdown("")

# Ranking weights display (read-only)
with st.expander("Ranking Weights (read-only from project.yaml)", expanded=False):
    for name, key in [
        ("Activity",  "activity_weight"),
        ("Docking",   "docking_weight"),
        ("Property",  "property_weight"),
        ("Novelty",   "novelty_weight"),
    ]:
        w1, w2 = st.columns([3, 1])
        w1.markdown(name)
        w2.markdown(f"**{weights.get(key, 0):.0%}**")

# Score comparison chart
st.plotly_chart(score_bar_chart(candidates), use_container_width=True)

# Score waterfall for top candidate
if candidates:
    st.markdown(f"#### Score Breakdown — Top Candidate: {candidates[0].candidate_id}")
    st.plotly_chart(score_waterfall(candidates[0], weights), use_container_width=True)

# Ranked table
st.markdown("#### Ranked Candidate Table")
rows = []
for c in candidates:
    rows.append({
        "Rank":             c.rank,
        "Compound ID":      c.candidate_id,
        "Activity (DEMO)":  round(c.activity_score, 4),
        "Docking (DEMO)":   round(c.docking.score_raw, 3) if c.docking.score_raw else None,
        "Property":         round(c.property_score, 2),
        "Novelty (DEMO)":   round(c.novelty_score, 2),
        "Final Score":      round(c.final_score, 4),
        "Predicted Class":  c.predicted_class,
        "Status":           c.status,
    })
ranked_disp = pd.DataFrame(rows)
st.dataframe(
    ranked_disp,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Final Score": st.column_config.ProgressColumn(
            "Final Score", min_value=0.0, max_value=1.0, format="%.4f"
        ),
        "Activity (DEMO)": st.column_config.NumberColumn(format="%.4f"),
        "Docking (DEMO)":  st.column_config.NumberColumn(format="%.3f"),
    },
)
st.caption("Activity, Docking, and Novelty columns contain deterministic demo values.")

# Per-compound cards
st.markdown("#### Compound Detail Cards")
for cand in candidates:
    render_candidate_card(cand, show_structure=True)

render_fallback_notice()

# Download
st.divider()
csv_data = build_ranking_csv(candidates)
st.download_button(
    "Download Ranking CSV",
    data=csv_data,
    file_name="targetforge_ranking.csv",
    mime="text/csv",
)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION B — What-If Ranking Analysis
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("What-If Ranking Analysis (Frontend Simulation)", expanded=False):
    render_whatif_label()

    st.markdown("Adjust the scoring weights below to explore alternative ranking priorities.")
    st.caption(
        "These weights recalculate a simulated score using the backend's "
        "pre-normalised `activity_norm` and `docking_norm` values. "
        "The official `final_score` and `rank` are never changed."
    )

    # Weight sliders — stored in tf_whatif_weights
    wi_defaults = st.session_state.get("tf_whatif_weights") or dict(weights)
    wc1, wc2, wc3, wc4 = st.columns(4)
    wa = wc1.slider("Activity weight",  0.0, 1.0, wi_defaults.get("activity_weight", 0.40), 0.05, key="wi_a")
    wd = wc2.slider("Docking weight",   0.0, 1.0, wi_defaults.get("docking_weight",  0.30), 0.05, key="wi_d")
    wp = wc3.slider("Property weight",  0.0, 1.0, wi_defaults.get("property_weight", 0.20), 0.05, key="wi_p")
    wn = wc4.slider("Novelty weight",   0.0, 1.0, wi_defaults.get("novelty_weight",  0.10), 0.05, key="wi_n")

    total_w = wa + wd + wp + wn
    if abs(total_w - 1.0) > 0.01:
        st.warning(
            f"Weights sum to {total_w:.2f} (should be 1.00). "
            "What-if scores may not be directly comparable to official scores.",
            icon=":material/warning:",
        )

    whatif_weights = {
        "activity_weight": wa,
        "docking_weight":  wd,
        "property_weight": wp,
        "novelty_weight":  wn,
    }
    st.session_state["tf_whatif_weights"] = whatif_weights

    if st.button("Reset to Official Weights", key="reset_whatif"):
        for k in ["wi_a", "wi_d", "wi_p", "wi_n"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    # Run what-if reranking (deep copies — originals untouched)
    whatif_candidates = rerank_candidates(candidates, whatif_weights)
    st.session_state["tf_whatif_ranked"] = whatif_candidates

    # Comparison chart
    st.plotly_chart(
        whatif_comparison_chart(candidates, whatif_candidates),
        use_container_width=True,
    )

    # What-if ranking table
    wi_rows = []
    for c in whatif_candidates:
        wi_rows.append({
            "What-If Rank":     c.whatif_rank,
            "Compound ID":      c.candidate_id,
            "What-If Score":    round(c.whatif_score or 0.0, 4),
            "Official Rank":    c.rank,
            "Official Score":   round(c.final_score, 4),
            "Rank Change":      (c.rank - c.whatif_rank) if c.whatif_rank else 0,
        })
    st.dataframe(
        pd.DataFrame(wi_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "What-If Score": st.column_config.ProgressColumn(
                "What-If Score", min_value=0.0, max_value=1.0, format="%.4f"
            ),
        },
    )
    st.caption(
        "What-If Rank and What-If Score are frontend-simulated values. "
        "Official Rank and Official Score reflect the unchanged backend pipeline output."
    )

render_scientific_disclaimer()
