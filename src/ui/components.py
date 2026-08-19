"""
src/ui/components.py
--------------------
Reusable Streamlit UI components for TargetForge with scientific information hierarchy.

All functions here return None and render directly into Streamlit's
active rendering context. They are imported and called by page modules.

Owned by: M4 (Frontend/UI Lead)
"""
from __future__ import annotations

from typing import Optional
import streamlit as st

from src.ui.schema import FrontendCandidate, FilterResult
from src.ui.state import (
    WorkflowStep,
    StepStatus,
    STEP_LABELS,
    PAGE_PATHS,
    get_step_status,
    is_step_accessible,
)
from src.ui.theme import badge_html, demo_field_html, COLORS


# ---------------------------------------------------------------------------
# Scientific Metric Card Helper
# ---------------------------------------------------------------------------

def render_scientific_metric(label: str, value: str | int | float, context: Optional[str] = None) -> None:
    """Render a compact scientific metric card with small label, medium value, and supporting text."""
    ctx_html = f'<div class="tf-metric-context">{context}</div>' if context else ''
    html = f"""
    <div class="tf-metric-card">
        <div class="tf-metric-label">{label}</div>
        <div class="tf-metric-value">{value}</div>
        {ctx_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar workflow progress tracker
# ---------------------------------------------------------------------------

def render_sidebar_progress() -> None:
    """Render the workflow progress tracker in the sidebar."""
    with st.sidebar:
        st.markdown(
            '<p style="color:#A1ABB3;font-size:11px;font-weight:600;'
            'text-transform:uppercase;letter-spacing:0.06em;margin:12px 0 6px 0">'
            "Workflow Progress</p>",
            unsafe_allow_html=True,
        )
        status_styles = {
            StepStatus.COMPLETED: "color:#10B981;font-weight:500",
            StepStatus.CURRENT:   "color:#00BFA6;font-weight:600;background:rgba(0,191,166,0.14);border-left:3px solid #00BFA6",
            StepStatus.LOCKED:    "color:#64748B;opacity:0.65",
            StepStatus.FAILED:    "color:#EF4444",
        }
        icons = {
            StepStatus.COMPLETED: "✓",
            StepStatus.CURRENT:   "•",
            StepStatus.LOCKED:    "🔒",
            StepStatus.FAILED:    "×",
        }
        for step in WorkflowStep:
            _, label = STEP_LABELS[step]
            status      = get_step_status(step)
            style       = status_styles.get(status, "color:#A1ABB3")
            icon        = icons.get(status, "•")
            st.markdown(
                f'<div style="{style};font-size:12px;padding:5px 10px;'
                f'border-radius:4px;margin:2px 0;display:flex;align-items:center;gap:8px;">'
                f'<span style="font-weight:700;">{icon}</span> {label}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("")


# ---------------------------------------------------------------------------
# Demo / fallback banner
# ---------------------------------------------------------------------------

def render_demo_banner() -> None:
    """Amber top-of-page banner for demo mode."""
    demo_mode = st.session_state.get("tf_demo_mode", True)
    if demo_mode:
        st.markdown(
            '<div class="tf-demo-panel">'
            '<p><strong>Demonstration Mode:</strong> Computational values reflect '
            'heuristic scoring parameters. Direct laboratory assay validation is required for discovery confirmation.</p>'
            '</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Scientific disclaimer footer
# ---------------------------------------------------------------------------

def render_scientific_disclaimer() -> None:
    """Standard footer with scientific limitation notice."""
    st.divider()
    st.markdown(
        '<div class="tf-disclaimer">'
        '<strong>Scientific Notice:</strong> TargetForge outputs are in silico computational hypotheses designed to prioritize '
        'experimental leads. Predicted bioactivity scores and docking energies do not constitute confirmed pharmacological efficacy. '
        'In vitro biochemical assays and ADMET validation are required before drawing therapeutic conclusions.'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Navigation gate (prerequisite check)
# ---------------------------------------------------------------------------

def render_step_gate(step: WorkflowStep) -> None:
    """Check whether the given workflow step is accessible."""
    if is_step_accessible(step):
        return

    from src.ui.state import PREREQUISITES, STEP_LABELS
    prereq_key = PREREQUISITES[step]
    prev_step_label = "the previous step"
    prev_page_path  = "pages/01_home.py"
    for s, key in {
        WorkflowStep.TARGET:    "tf_target",
        WorkflowStep.DATASET:   "tf_validated_df",
        WorkflowStep.SCREENING: "tf_predicted_df",
        WorkflowStep.DESIGN:    "tf_filtered_df",
        WorkflowStep.DOCKING:   "tf_docked_df",
        WorkflowStep.RANKING:   "tf_ranked_df",
    }.items():
        if key == prereq_key:
            prev_step_label = f"{STEP_LABELS[s][1]}"
            prev_page_path  = PAGE_PATHS[s]
            break

    _, label = STEP_LABELS[step]
    st.warning(
        f"**{label}** requires **{prev_step_label}** to be executed first.",
        icon=":material/lock:",
    )
    st.page_link(prev_page_path, label=f"Return to {prev_step_label}", icon=":material/arrow_forward:")
    st.stop()


# ---------------------------------------------------------------------------
# KPI row (Compact Scientific Metrics)
# ---------------------------------------------------------------------------

def render_kpi_row(candidates: list[FrontendCandidate]) -> None:
    """Four-column compact scientific KPI metrics strip."""
    if not candidates:
        return
    top = candidates[0]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_scientific_metric("Ranked Leads", len(candidates), "Eligible docked candidates")
    with c2:
        render_scientific_metric("Top Candidate", top.candidate_id, "Rank #1 prioritized compound")
    with c3:
        render_scientific_metric("Peak Activity", f"{top.activity_score:.3f}", "Surrogate bioactivity score")
    with c4:
        render_scientific_metric("Composite Score", f"{top.final_score:.3f}", "Weighted multi-objective score")


# ---------------------------------------------------------------------------
# 2D molecular structure rendering
# ---------------------------------------------------------------------------

def render_molecule(smiles: str, width: int = 280, height: int = 170) -> None:
    """Render a 2D molecular structure using RDKit SVG."""
    if not smiles or smiles.strip() in ("", "nan"):
        st.caption("No SMILES available.")
        return
    try:
        from rdkit import Chem
        from rdkit.Chem.Draw import rdMolDraw2D
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"RDKit could not parse SMILES: {smiles!r}")
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.drawOptions().addStereoAnnotation = True
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #232D38;'
            f'border-radius:6px;padding:6px;display:inline-block;">'
            f"{svg}</div>",
            unsafe_allow_html=True,
        )
    except ImportError:
        _molecule_unavailable(smiles, "RDKit library not initialized.")
    except Exception as exc:
        _molecule_unavailable(smiles, str(exc))


def _molecule_unavailable(smiles: str, reason: str) -> None:
    st.info(
        f"**Molecular structure 2D representation**\n\n"
        f"*{reason}*\n\n"
        f"**SMILES:** `{smiles}`",
        icon=":material/science:",
    )


# ---------------------------------------------------------------------------
# Candidate detail card (Compact Scientific Presentation)
# ---------------------------------------------------------------------------

def render_candidate_card(candidate: FrontendCandidate, show_structure: bool = True) -> None:
    """Compact expandable detail card for a single prioritized candidate."""
    with st.expander(
        f"Rank #{candidate.rank} — {candidate.candidate_id} | Score: {candidate.final_score:.4f} (Activity: {candidate.activity_score:.3f}, Docking: {candidate.docking.score_raw:.2f} kcal/mol)",
        expanded=(candidate.rank == 1),
    ):
        col_struct, col_scores, col_props = st.columns([1.1, 1.3, 1.2], gap="medium")
        
        with col_struct:
            if show_structure:
                render_molecule(candidate.smiles, width=260, height=160)
            st.caption(f"**SMILES:** `{candidate.smiles}`")

        with col_scores:
            st.markdown("<div class='tf-metric-label'>Score Breakdown</div>", unsafe_allow_html=True)
            scores = [
                ("Bioactivity Score", f"{candidate.activity_score:.4f}", demo_field_html("activity")),
                ("Docking Affinity", f"{candidate.docking.score_raw:.3f} kcal/mol" if candidate.docking.score_raw is not None else "N/A", demo_field_html("docking")),
                ("Property Score", f"{candidate.property_score:.2f}", ""),
                ("Novelty Score", f"{candidate.novelty_score:.2f}", demo_field_html("novelty")),
                ("Composite Final", f"**{candidate.final_score:.4f}**", ""),
            ]
            for name, val, tag in scores:
                sc1, sc2 = st.columns([2, 1.5])
                sc1.markdown(f"<span style='font-size:13px;color:#A1ABB3;'>{name}</span>", unsafe_allow_html=True)
                sc2.markdown(f"<span style='font-size:13px;color:#F8FAFC;font-weight:600;'>{val}</span>", unsafe_allow_html=True)

        with col_props:
            st.markdown("<div class='tf-metric-label'>Physicochemical Descriptors</div>", unsafe_allow_html=True)
            p = candidate.properties
            props = [
                ("MW", f"{p.mw:.1f} Da"),
                ("LogP", f"{p.logp:.2f}"),
                ("HBD / HBA", f"{p.hbd} / {p.hba}"),
                ("TPSA", f"{p.tpsa:.1f} Å²"),
                ("Rotatable Bonds", f"{p.rotatable_bonds}"),
            ]
            for label, val in props:
                pc1, pc2 = st.columns([2, 1.5])
                pc1.markdown(f"<span style='font-size:13px;color:#A1ABB3;'>{label}</span>", unsafe_allow_html=True)
                pc2.markdown(f"<span style='font-size:13px;color:#F8FAFC;font-weight:600;'>{val}</span>", unsafe_allow_html=True)

            fstatus = candidate.filter.status
            fkind = "pass" if fstatus == "PASS" else "rejected"
            st.markdown(f"<div style='margin-top:6px;font-size:12px;'>Filter status: {badge_html(fstatus, fkind)}</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Score breakdown component
# ---------------------------------------------------------------------------

def render_score_breakdown(candidate: FrontendCandidate, weights: dict) -> None:
    """Render the score breakdown chart for a single candidate."""
    from src.ui.charts import score_waterfall
    st.plotly_chart(score_waterfall(candidate, weights), use_container_width=True)


# ---------------------------------------------------------------------------
# Filter badge
# ---------------------------------------------------------------------------

def render_filter_badge(filter_result: FilterResult) -> None:
    """Inline PASS / REJECTED badge with reasons."""
    if filter_result.status == "PASS":
        st.markdown(badge_html("PASS", "pass"), unsafe_allow_html=True)
    else:
        st.markdown(badge_html("REJECTED", "rejected"), unsafe_allow_html=True)
        if filter_result.reasons:
            for r in filter_result.reasons:
                st.caption(f"• {r}")


# ---------------------------------------------------------------------------
# Demo field label
# ---------------------------------------------------------------------------

def render_demo_field_label(field_name: str) -> None:
    """Render an inline amber DEMO chip with a tooltip."""
    st.markdown(demo_field_html(field_name), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Fallback / demo notice panel
# ---------------------------------------------------------------------------

def render_fallback_notice() -> None:
    """Prominent amber panel explaining all demo/fallback fields."""
    st.markdown(
        """<div class="tf-demo-panel">
<p><strong>Demonstration Notice:</strong> Activity predictions, docking binding energies, and novelty scores in this session reflect demo computational parameters. Replace pipeline ML models in <code>src/ml/</code> and docking configs in <code>configs/docking.yaml</code> for production assay pipelines.</p>
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Loading stage visualisation
# ---------------------------------------------------------------------------

def render_loading_stages(stages: list[str], current_idx: int) -> None:
    """Animated checklist of pipeline stages during pipeline execution."""
    for i, stage in enumerate(stages):
        if i < current_idx:
            st.markdown(f"<span style='color:#10B981;font-size:13px;font-weight:500;'>✓ {stage}</span>", unsafe_allow_html=True)
        elif i == current_idx:
            st.markdown(f"<span style='color:#00BFA6;font-size:13px;font-weight:600;'>⏳ {stage}...</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:#64748B;font-size:13px;'>○ {stage}</span>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# What-if analysis label / banner
# ---------------------------------------------------------------------------

def render_whatif_label() -> None:
    """Banner labeling the what-if ranking analysis section."""
    st.markdown(
        """<div class="tf-whatif-banner">
<p><strong>What-If Multi-Objective Sensitivity Simulation:</strong> Adjust objective weights below to evaluate sensitivity and rank transitions. Official backend ranking remains unchanged.</p>
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Property radar wrapper
# ---------------------------------------------------------------------------

def render_property_radar(
    candidate: FrontendCandidate,
    limits: dict,
    title: str | None = None,
) -> None:
    """Render the property radar chart via st.plotly_chart."""
    from src.ui.charts import property_radar
    st.plotly_chart(
        property_radar(candidate, limits, title=title),
        use_container_width=True,
    )


# ---------------------------------------------------------------------------


def render_horizontal_stepper(current_step: WorkflowStep) -> None:
    """Render a horizontal stepper progress tracker matching scientific hierarchy."""
    from src.ui.state import WorkflowStep, StepStatus, get_step_status
    
    steps = [
        (WorkflowStep.TARGET, "1", "Target"),
        (WorkflowStep.DATASET, "2", "Data"),
        (WorkflowStep.SCREENING, "3", "AI Screening"),
        (WorkflowStep.DESIGN, "4", "Filtering"),
        (WorkflowStep.DOCKING, "5", "Docking"),
        (WorkflowStep.RANKING, "6", "Ranking"),
    ]
    
    active_idx = int(current_step) - 1
    line_pct = max(0, min(100, (active_idx / 5.0) * 100))
    
    html_steps = []
    for step, num, label in steps:
        status = get_step_status(step)
        
        if step == current_step:
            cls = "current"
        elif status == StepStatus.COMPLETED:
            cls = "completed"
        elif status == StepStatus.LOCKED:
            cls = "locked"
        else:
            cls = ""
            
        html_steps.append(f"""<div class="stepper-step {cls}">
<div class="stepper-circle">{num}</div>
<div class="stepper-label">{label}</div>
</div>""")
        
    steps_html = "\n".join(html_steps)
    
    stepper_html = f"""<div class="stepper-container">
<div class="stepper-line-bg"></div>
<div class="stepper-line-active" style="width: {line_pct}%;"></div>
{steps_html}
</div>"""
    st.markdown(stepper_html, unsafe_allow_html=True)
