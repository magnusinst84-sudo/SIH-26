"""
pages/06_docking_analysis.py
-----------------------------
TargetForge — Docking Analysis

Displays docking binding energies, 3D pose evaluation, and receptor interaction analysis.
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
    render_scientific_metric,
    render_molecule,
)
from src.ui.charts import docking_score_bar

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.DOCKING)
render_step_gate(WorkflowStep.DOCKING)
render_demo_banner()

st.title("Structure-Based Docking Analysis")
st.caption("Receptor-ligand binding affinity calculations, pose evaluation, and catalytic interaction analysis.")

# ─── Scientific Disclaimer Notice ────────────────────────────────────────────
st.markdown(
    '<div class="tf-whatif-banner" style="margin-bottom:16px;">'
    '<p><strong>Docking Notice:</strong> Docking results help prioritize candidates based on theoretical binding free energy '
    'but do not prove biological activity. Experimental in vitro binding assays are required for confirmation.</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ─── Data ────────────────────────────────────────────────────────────────────
candidates = st.session_state.get("tf_candidates")
ranked_df  = st.session_state.get("tf_ranked_df")
target     = st.session_state.get("tf_target", {})

if not candidates:
    st.warning("No docking data found. Run the screening pipeline from Home.", icon=":material/warning:")
    st.page_link("pages/01_home.py", label="← Return to Home", icon=":material/home:")
    render_scientific_disclaimer()
    st.stop()

# ─── Summary KPI Metrics Row ────────────────────────────────────────────────
best_energy = min([c.docking.score_raw for c in candidates if c.docking.score_raw is not None] or [0.0])
avg_energy = sum([c.docking.score_raw for c in candidates if c.docking.score_raw is not None]) / len(candidates) if candidates else 0.0

d1, d2, d3, d4 = st.columns(4)
with d1:
    render_scientific_metric("Target PDB", target.get("structure_id", "6LU7"), target.get("name", "SARS-CoV-2 Mpro"))
with d2:
    render_scientific_metric("Docked Ligands", len(candidates), "Passing filter set")
with d3:
    render_scientific_metric("Peak Binding Energy", f"{best_energy:.2f} kcal/mol", "Strongest affinity pose")
with d4:
    render_scientific_metric("Mean Binding Energy", f"{avg_energy:.2f} kcal/mol", "Docked cohort average")

st.markdown("")

# ─── Three-Column Interactive Docking Inspection Workspace ───────────────────
st.markdown("### Interactive Candidate Docking Inspection")
cand_options = [c.candidate_id for c in candidates]
selected_cid = st.selectbox(
    "Select Candidate for Detailed Pose & Interaction Evaluation",
    options=cand_options,
    index=0,
    help="Select compound to evaluate its binding affinity and active site interaction profile.",
)

sel_cand = next((c for c in candidates if c.candidate_id == selected_cid), candidates[0])

col_pose_left, col_pose_mid, col_pose_right = st.columns([1.1, 1.2, 1.1], gap="medium")

with col_pose_left:
    st.markdown('<div class="tf-card" style="padding:14px; height:100%;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-size:15px;'>Docking Score Summary</h4>", unsafe_allow_html=True)
    
    score_rows = [
        ("Candidate ID", sel_cand.candidate_id),
        ("Prioritization Rank", f"Rank #{sel_cand.rank}"),
        ("Calculated Affinity", f"**{sel_cand.docking.score_raw:.3f} kcal/mol**" if sel_cand.docking.score_raw is not None else "N/A"),
        ("Normalized Score", f"{sel_cand.docking.score_normalized:.4f}" if sel_cand.docking.score_normalized is not None else "N/A"),
        ("Receptor Structure", target.get("structure_id", "6LU7")),
        ("Docking Status", badge_html(sel_cand.docking.docking_status, "pass")),
    ]
    for s_lbl, s_val in score_rows:
        sc1, sc2 = st.columns([1.1, 1.3])
        sc1.markdown(f"<span style='font-size:12px;color:#52606D;'>{s_lbl}</span>", unsafe_allow_html=True)
        sc2.markdown(f"<span style='font-size:12px;color:#102A43;'>{s_val}</span>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

with col_pose_mid:
    st.markdown('<div class="tf-card" style="padding:14px; height:100%; text-align:center;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-size:15px; text-align:left;'>2D Ligand Topology</h4>", unsafe_allow_html=True)
    render_molecule(sel_cand.smiles, width=240, height=150)
    st.caption(f"**SMILES:** `{sel_cand.smiles}`")
    st.markdown("</div>", unsafe_allow_html=True)

with col_pose_right:
    st.markdown('<div class="tf-card" style="padding:14px; height:100%;">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; font-size:15px;'>Pocket Interactions</h4>", unsafe_allow_html=True)
    interactions = [
        ("Catalytic Dyad", "Cys145 (H-Bond), His41 (π-Stack)"),
        ("Oxyanion Hole", "Gly143 (Backbone NH)"),
        ("S1 Pocket", "His163, Glu166 (Ionic)"),
        ("S2 Pocket", "Met49, Met165 (Hydrophobic)"),
        ("Solvent Exposed", "Gln189 (Weak Contact)"),
    ]
    for i_lbl, i_val in interactions:
        ic1, ic2 = st.columns([1.1, 1.4])
        ic1.markdown(f"<span style='font-size:12px;color:#52606D;'>{i_lbl}</span>", unsafe_allow_html=True)
        ic2.markdown(f"<span style='font-size:12px;color:#102A43;font-weight:500;'>{i_val}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

# ─── Primary Visual Priority: Calculated Binding Affinities Table ────────────
st.markdown("### Calculated Binding Affinities")
st.caption("Ligands sorted by calculated binding free energy (lower / more negative kcal/mol indicates stronger binding).")

rows = []
for c in candidates:
    rows.append({
        "Rank":            c.rank,
        "Compound ID":     c.candidate_id,
        "Docking Affinity": f"{c.docking.score_raw:.3f} kcal/mol" if c.docking.score_raw is not None else "N/A",
        "Normalized Score": f"{c.docking.score_normalized:.4f}" if c.docking.score_normalized is not None else "N/A",
        "Receptor ID":     c.docking.receptor_id or "6LU7",
        "Status":          c.docking.docking_status,
    })
st.dataframe(
    pd.DataFrame(rows),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn("Rank", width="small"),
        "Compound ID": st.column_config.TextColumn("Compound ID", width="small"),
        "Docking Affinity": st.column_config.TextColumn("Affinity (kcal/mol)", width="medium"),
        "Normalized Score": st.column_config.TextColumn("Score Norm. (0-1)", width="small"),
        "Receptor ID": st.column_config.TextColumn("Receptor", width="small"),
        "Status": st.column_config.TextColumn("Docking Status", width="small"),
    },
)

# ─── Docking Score Bar Chart ──────────────────────────────────────────────────
with st.expander("Binding Affinity Distribution Chart", expanded=True):
    st.plotly_chart(docking_score_bar(candidates), use_container_width=True)

render_fallback_notice()

# ─── Proceed CTA ─────────────────────────────────────────────────────────────
st.divider()
if st.button("Confirm Docking Affinities & Proceed to Final Ranking →", type="primary"):
    st.page_link(
        "pages/07_final_ranking.py",
        label="Proceed to Final Candidate Ranking →",
        icon=":material/leaderboard:",
    )
    st.success("Docking data confirmed.")

render_scientific_disclaimer()
