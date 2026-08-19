"""
pages/07_final_ranking.py
-------------------------
TargetForge — Final Ranking

Multi-objective candidate ranking, score breakdown, and what-if sensitivity analysis.
SECTION A: Official immutable backend ranking.
SECTION B: What-if weight sensitivity simulation (frontend only).
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
    render_top_navbar,
    render_horizontal_stepper,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
    render_candidate_card,
    render_fallback_notice,
    render_whatif_label,
    render_kpi_row,
    render_scientific_metric,
)
from src.ui.charts import (
    score_waterfall,
    score_bar_chart,
    whatif_comparison_chart,
)
from src.ui.adapter import (
    build_ranking_table_df,
    build_ranking_csv,
    compute_whatif_ranking,
    adapt_ranked_df,
)

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.RANKING)
render_step_gate(WorkflowStep.RANKING)
render_demo_banner()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION A — Official Ranking Results
# ══════════════════════════════════════════════════════════════════════════════
st.title("Final Candidate Prioritization")
st.caption("Multi-objective composite scoring combining bioactivity, docking affinity, drug-likeness, and scaffold novelty.")

candidates = st.session_state.get("tf_candidates")
ranked_df  = st.session_state.get("tf_ranked_df")
target     = st.session_state.get("tf_target",   {})
weights    = st.session_state.get("tf_weights",  {})

if not candidates:
    st.warning("No ranking data found. Run the screening pipeline from Home.", icon=":material/warning:")
    st.page_link("pages/01_home.py", label="← Return to Home", icon=":material/home:")
    render_scientific_disclaimer()
    st.stop()

# ─── 1. Compact KPI Row ──────────────────────────────────────────────────────
render_kpi_row(candidates)
st.markdown("")

# ─── 2. Main Content: Prioritized Candidates Ranking Table ───────────────────
st.markdown("### Prioritized Lead Candidates")
st.caption("Compounds ranked by multi-objective composite score (`configs/project.yaml`).")

table_df = build_ranking_table_df(candidates)
st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn("Rank", width="small"),
        "Compound ID": st.column_config.TextColumn("Compound ID", width="small"),
        "Composite Final Score": st.column_config.ProgressColumn(
            "Final Composite Score",
            min_value=0.0,
            max_value=1.0,
            format="%.4f",
        ),
        "Activity Score": st.column_config.NumberColumn("Activity (0–1)", format="%.4f"),
        "Docking Affinity (kcal/mol)": st.column_config.NumberColumn("Docking (kcal/mol)", format="%.2f"),
        "Property Score": st.column_config.NumberColumn("Property (0–1)", format="%.2f"),
        "Novelty Score": st.column_config.NumberColumn("Novelty (0–1)", format="%.2f"),
        "Predicted Class": st.column_config.TextColumn("Class", width="small"),
        "Filter Status": st.column_config.TextColumn("Filter", width="small"),
    },
)

# Download CSV Action
col_dl, col_spacer = st.columns([1.5, 3])
with col_dl:
    csv_data = build_ranking_csv(candidates)
    st.download_button(
        "Download Prioritization CSV",
        data=csv_data,
        file_name="targetforge_lead_ranking.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("")

# ─── 3. Top Candidate Analysis & Horizontal Stacked Score Breakdown ──────────
st.markdown("### Top Prioritized Lead Analysis")
if candidates:
    top_cand = candidates[0]
    st.plotly_chart(score_waterfall(top_cand, weights), use_container_width=True)

# ─── 4. Detailed Candidate Structural Cards ──────────────────────────────────
st.markdown("#### Candidate Details")
for cand in candidates:
    render_candidate_card(cand, show_structure=True)

with st.expander("Cohort Score Component Distribution", expanded=False):
    st.plotly_chart(score_bar_chart(candidates), use_container_width=True)

render_fallback_notice()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION B — What-If Ranking Sensitivity Simulation (Frontend Only)
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
with st.expander("What-If Weight Sensitivity Simulation (Frontend Only)", expanded=False):
    render_whatif_label()

    st.caption(
        "Evaluate rank stability across alternative objective weightings. "
        "The official computational score remains locked."
    )

    wi_defaults = st.session_state.get("tf_whatif_weights") or dict(weights)
    wc1, wc2, wc3, wc4 = st.columns(4)
    wa = wc1.slider("Activity Weight",  0.0, 1.0, wi_defaults.get("activity_weight", 0.40), 0.05, key="wi_a")
    wd = wc2.slider("Docking Weight",   0.0, 1.0, wi_defaults.get("docking_weight",  0.30), 0.05, key="wi_d")
    wp = wc3.slider("Property Weight",  0.0, 1.0, wi_defaults.get("property_weight", 0.20), 0.05, key="wi_p")
    wn = wc4.slider("Novelty Weight",   0.0, 1.0, wi_defaults.get("novelty_weight",  0.10), 0.05, key="wi_n")

    total_w = wa + wd + wp + wn
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"Weights sum to {total_w:.2f} (normalized total = 1.00).", icon=":material/warning:")

    whatif_weights = {
        "activity_weight": wa,
        "docking_weight":  wd,
        "property_weight": wp,
        "novelty_weight":  wn,
    }
    st.session_state["tf_whatif_weights"] = whatif_weights

    whatif_candidates = compute_whatif_ranking(candidates, whatif_weights)
    st.session_state["tf_whatif_candidates"] = whatif_candidates

    st.markdown("#### Simulated vs Official Rank Comparison")
    wi_rows = []
    for c in whatif_candidates:
        orig = next((o for o in candidates if o.candidate_id == c.candidate_id), None)
        orig_rank = orig.rank if orig else "—"
        rank_change = (orig.rank - c.whatif_rank) if orig and orig.rank and c.whatif_rank else 0
        arrow = f"▲ +{rank_change}" if rank_change > 0 else (f"▼ {rank_change}" if rank_change < 0 else "=")
        wi_rows.append({
            "Simulated Rank": c.whatif_rank,
            "Official Rank":  orig_rank,
            "Rank Shift":     arrow,
            "Compound ID":    c.candidate_id,
            "Simulated Score": f"{c.whatif_score:.4f}" if c.whatif_score else "N/A",
            "Official Score":  f"{c.final_score:.4f}",
        })
    st.dataframe(
        pd.DataFrame(wi_rows),
        use_container_width=True,
        hide_index=True,
    )
    st.plotly_chart(
        whatif_comparison_chart(candidates, whatif_candidates),
        use_container_width=True,
    )

# ─── Proceed CTA ─────────────────────────────────────────────────────────────
st.divider()
st.page_link(
    "pages/08_reports.py",
    label="Generate Screening Reports & Exports →",
    icon=":material/description:",
)

render_scientific_disclaimer()
