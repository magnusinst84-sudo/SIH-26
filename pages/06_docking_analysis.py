"""
pages/06_docking_analysis.py
-----------------------------
TargetForge — Docking Analysis

Displays docking scores with explicit FALLBACK_DEMO transparency.
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

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
)
from src.ui.charts import docking_score_bar

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.DOCKING)
render_step_gate(WorkflowStep.DOCKING)

st.title("Docking Analysis")
st.caption("Binding affinity estimates for top candidates.")

render_demo_banner()

# ─── Mandatory FALLBACK notice ───────────────────────────────────────────────
st.markdown("""
<div class="tf-demo-panel">
<p><strong>Docking Scores — FALLBACK_DEMO</strong></p>
<p>Docking scores in this demonstration are <strong>deterministic fallback values</strong>
computed from SHA-256(compound_id) and are in the range −7.2 to −8.4 kcal/mol.
<strong>No real molecular docking simulation</strong> (AutoDock Vina, Glide, DOCK, etc.)
was performed.</p>
<p>Real docking requires the prepared receptor file:
<code>data/targets/mpro_6lu7_prepared.pdbqt</code>.
Replace <code>src/docking/fallback.py</code> with a real docking integration.</p>
</div>
""", unsafe_allow_html=True)

# ─── Data ────────────────────────────────────────────────────────────────────
candidates = st.session_state.get("tf_candidates")
ranked_df  = st.session_state.get("tf_ranked_df")
target     = st.session_state.get("tf_target", {})

if not candidates:
    st.warning("No docking data found. Run the demo pipeline from Home first.", icon=":material/warning:")
    st.page_link("pages/01_home.py", label="← Go to Home", icon=":material/home:")
    render_scientific_disclaimer()
    st.stop()

# ─── Target receptor card ────────────────────────────────────────────────────
col_rec, col_meta = st.columns(2)
with col_rec:
    st.markdown(
        f'<div class="tf-card-sm">'
        f'<strong>Receptor</strong><br>'
        f'<span style="color:{COLORS["text"]}">{target.get("name","SARS-CoV-2 Mpro")}</span><br>'
        f'PDB: {target.get("structure_id","6LU7")} &nbsp;'
        f'{badge_html("FALLBACK_DEMO", "fallback")}'
        f'</div>',
        unsafe_allow_html=True,
    )
with col_meta:
    docking_meta = st.session_state.get("tf_docking_meta") or {}
    st.markdown(
        f'<div class="tf-card-sm">'
        f'<strong>Docking Tool</strong><br>'
        f'<span style="color:{COLORS["muted"]};font-size:0.9rem">'
        f'Tool: {docking_meta.get("tool","fallback")}<br>'
        f'Is fallback: {docking_meta.get("is_fallback",True)}<br>'
        f'Pose file: N/A (demo mode)<br>'
        f'Interaction residues: N/A (demo mode)'
        f'</span></div>',
        unsafe_allow_html=True,
    )

# ─── Docking score bar chart ──────────────────────────────────────────────────
st.plotly_chart(docking_score_bar(candidates), use_container_width=True)

# ─── Docking results table ────────────────────────────────────────────────────
st.markdown("### Docking Results Table")

import pandas as pd
rows = []
for c in candidates:
    rows.append({
        "Rank":            c.rank,
        "Compound ID":     c.candidate_id,
        "Docking Score":   f"{c.docking.score_raw:.3f}" if c.docking.score_raw is not None else "N/A",
        "Score Norm.":     f"{c.docking.score_normalized:.4f}" if c.docking.score_normalized is not None else "N/A",
        "Docking Status":  c.docking.docking_status,
        "Receptor":        c.docking.receptor_id or "N/A",
        "Pose File":       "N/A (demo mode)",
        "Interactions":    "N/A (demo mode)",
    })
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
st.caption("All docking scores are FALLBACK_DEMO values — not real docking results.")

# ─── Per-compound expandable cards ───────────────────────────────────────────
st.divider()
st.markdown("### Compound Detail Cards")
for cand in candidates:
    render_candidate_card(cand, show_structure=True)

render_fallback_notice()

# ─── Proceed ─────────────────────────────────────────────────────────────────
st.divider()
st.page_link(
    "pages/07_final_ranking.py",
    label="Proceed to Final Ranking →",
    icon=":material/leaderboard:",
)

render_scientific_disclaimer()
