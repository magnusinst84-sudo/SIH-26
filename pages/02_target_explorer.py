"""
pages/02_target_explorer.py
---------------------------
TargetForge — Target Explorer

Displays the biological target configuration, ranking weights, and
Lipinski filter thresholds read from backend configs (read-only).
Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.ui.state import init_session_state, WorkflowStep
from src.ui.theme import inject_global_css
from src.ui.components import (
    render_sidebar_progress,
    render_scientific_disclaimer,
    render_demo_banner,
    render_step_gate,
)
from src.ui.charts import weights_pie

inject_global_css()
init_session_state(_ROOT)
render_sidebar_progress()
render_demo_banner()

st.title("🎯 Target Explorer")
st.caption("Review the biological target and screening configuration.")

# ─── Target Info ─────────────────────────────────────────────────────────────
target  = st.session_state.get("tf_target",        {})
weights = st.session_state.get("tf_weights",        {})
filters = st.session_state.get("tf_filter_config",  {})

col_target, col_weights = st.columns([1.2, 1], gap="large")

with col_target:
    st.markdown(
        '<div class="tf-card">'
        '<h3 style="margin-top:0">🦠 Target Profile</h3>',
        unsafe_allow_html=True,
    )
    info = {
        "Disease":        target.get("disease",      "COVID-19"),
        "Target Name":    target.get("name",         "SARS-CoV-2 main protease"),
        "Aliases":        ", ".join(target.get("aliases", ["Mpro", "3CLpro"])),
        "PDB Structure":  target.get("structure_id", "6LU7"),
        "Application":    target.get("application",  "mpro_screening"),
    }
    for label, value in info.items():
        c1, c2 = st.columns([1, 2])
        c1.markdown(f"**{label}**")
        c2.markdown(value)
    st.markdown(
        f'<a href="https://www.rcsb.org/structure/{target.get("structure_id","6LU7")}" '
        f'target="_blank" style="color:#0F766E;font-size:0.88rem">'
        f'🔗 View {target.get("structure_id","6LU7")} on RCSB PDB</a>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Model Info
    st.markdown(
        '<div class="tf-card-sm">'
        f'<strong>🤖 Activity Model</strong><br>'
        f'<span style="color:#52606D;font-size:0.88rem">'
        f'Type: {target.get("model_type","demo_activity_model")}<br>'
        f'Version: {target.get("model_version","demo_v1")}</span>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_weights:
    st.markdown('<div class="tf-card"><h3 style="margin-top:0">⚖️ Ranking Weights</h3>', unsafe_allow_html=True)
    st.caption("These weights combine four score components into the final candidate score. "
               "They are read from `configs/project.yaml` and not editable here.")
    st.plotly_chart(weights_pie(weights), use_container_width=True)
    w_rows = {
        "Activity": weights.get("activity_weight",  0.40),
        "Docking":  weights.get("docking_weight",   0.30),
        "Property": weights.get("property_weight",  0.20),
        "Novelty":  weights.get("novelty_weight",   0.10),
    }
    for name, w in w_rows.items():
        w1, w2 = st.columns([2, 1])
        w1.markdown(name)
        w2.markdown(f"**{w:.0%}**")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Filter Thresholds ───────────────────────────────────────────────────────
st.markdown("### 🧫 Lipinski / Property Filter Thresholds")
st.caption(
    "These are the backend defaults from `configs/filters.yaml`. "
    "You can adjust them interactively on the **Candidate Design** page."
)

f_cols = st.columns(3)
thresholds = [
    ("Molecular Weight", f"≤ {filters.get('max_molecular_weight', 500)} Da"),
    ("LogP",             f"≤ {filters.get('max_logp',             5.0)}"),
    ("HBD",              f"≤ {filters.get('max_hbd',              5)}"),
    ("HBA",              f"≤ {filters.get('max_hba',              10)}"),
    ("TPSA",             f"≤ {filters.get('max_tpsa',             140)} Å²"),
    ("Rot. Bonds",       "≤ 10 (UI-only default)"),
]
for i, (label, val) in enumerate(thresholds):
    with f_cols[i % 3]:
        st.metric(label, val)

# ─── Raw config inspector ────────────────────────────────────────────────────
with st.expander("🔧 Raw project.yaml values", expanded=False):
    st.json({
        "project_name": target.get("project_name"),
        "disease":      target.get("disease"),
        "target":       {
            "name":         target.get("name"),
            "aliases":      target.get("aliases"),
            "structure_id": target.get("structure_id"),
        },
        "model":        {
            "type":    target.get("model_type"),
            "version": target.get("model_version"),
        },
        "ranking":      weights,
    })

with st.expander("🔧 Raw filters.yaml values", expanded=False):
    st.json(filters)

# ─── Proceed CTA ─────────────────────────────────────────────────────────────
st.divider()
if st.button("✅ Confirm Target & Proceed to Dataset Manager", type="primary"):
    st.page_link("pages/03_dataset_manager.py", label="Go to Dataset Manager →", icon="📂")
    st.success("Target confirmed. Proceed to the Dataset Manager.")

render_scientific_disclaimer()
