"""
src/ui/components.py
--------------------
Reusable Streamlit UI components for TargetForge.

All functions here return None and render directly into Streamlit's
active rendering context.  They are imported and called by page modules.

Owned by: M4 (Frontend/UI Lead)
"""
from __future__ import annotations

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
# Sidebar workflow progress tracker
# ---------------------------------------------------------------------------

def render_sidebar_progress() -> None:
    """Render the workflow progress tracker in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<p style="color:#8AA4B8;font-size:0.72rem;font-weight:600;'
            'text-transform:uppercase;letter-spacing:0.08em;margin:0 0 0.4rem 0">'
            "WORKFLOW PROGRESS</p>",
            unsafe_allow_html=True,
        )
        status_icons = {
            StepStatus.COMPLETED: "✅",
            StepStatus.CURRENT:   "▶",
            StepStatus.LOCKED:    "🔒",
            StepStatus.FAILED:    "❌",
        }
        status_styles = {
            StepStatus.COMPLETED: "color:#6EE7B7",
            StepStatus.CURRENT:   "color:#93C5FD;font-weight:600",
            StepStatus.LOCKED:    "color:#4A5568;opacity:0.6",
            StepStatus.FAILED:    "color:#FCA5A5",
        }
        for step in WorkflowStep:
            icon, label = STEP_LABELS[step]
            status      = get_step_status(step)
            s_icon      = status_icons.get(status, "🔒")
            style       = status_styles.get(status, "color:#CBD5E1")
            st.markdown(
                f'<div style="{style};font-size:0.85rem;padding:0.2rem 0.5rem;'
                f'border-radius:5px;margin:0.1rem 0">'
                f'{s_icon} {icon} {label}</div>',
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
            '<p><strong>Demo Mode</strong> — All scores are deterministic '
            'computational estimates derived from compound identifiers. '
            'They are not validated scientific results.</p>'
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
        '<strong>Scientific Limitation:</strong> TargetForge is a hackathon prototype. '
        'All results are computational hypotheses. Activity scores use deterministic '
        'demo values; docking scores are fallback estimates. This output does not '
        'establish safety, efficacy, clinical benefit, or regulatory approval of any '
        'molecule. Laboratory validation is required before drawing scientific conclusions.'
        '</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Navigation gate (prerequisite check)
# ---------------------------------------------------------------------------

def render_step_gate(step: WorkflowStep) -> None:
    """
    Check whether the given workflow step is accessible.
    If not, display a warning, a link to the previous step, and call st.stop().
    """
    if is_step_accessible(step):
        return

    from src.ui.state import PREREQUISITES, STEP_LABELS
    prereq_key = PREREQUISITES[step]
    # Find which step owns that key
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
            prev_step_label = f"{STEP_LABELS[s][0]} {STEP_LABELS[s][1]}"
            prev_page_path  = PAGE_PATHS[s]
            break

    icon, label = STEP_LABELS[step]
    st.warning(
        f"**{label}** requires **{prev_step_label}** to be completed first.",
        icon=":material/lock:",
    )
    st.page_link(prev_page_path, label=f"Go to {prev_step_label}", icon=":material/arrow_forward:")
    st.stop()


# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------

def render_kpi_row(candidates: list[FrontendCandidate]) -> None:
    """Four-column KPI metrics strip."""
    if not candidates:
        return
    top = candidates[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Candidates Ranked",  len(candidates))
    c2.metric("Top Candidate",       top.candidate_id)
    c3.metric("Top Activity Score",  f"{top.activity_score:.3f}")
    c4.metric("Top Final Score",     f"{top.final_score:.3f}")


# ---------------------------------------------------------------------------
# 2D molecular structure rendering
# ---------------------------------------------------------------------------

def render_molecule(smiles: str, width: int = 380, height: int = 240) -> None:
    """
    Render a 2D molecular structure using RDKit SVG.
    Falls back to a clear SMILES-text notice if RDKit is unavailable or
    the SMILES cannot be parsed.
    """
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
            f'<div style="background:#fff;border:1px solid {COLORS["border"]};'
            f'border-radius:8px;padding:8px;display:inline-block;">'
            f"{svg}</div>",
            unsafe_allow_html=True,
        )
    except ImportError:
        _molecule_unavailable(smiles, "RDKit is not installed in this environment.")
    except Exception as exc:
        _molecule_unavailable(smiles, str(exc))


def _molecule_unavailable(smiles: str, reason: str) -> None:
    st.info(
        f"**⚠ Molecular structure visualization unavailable**\n\n"
        f"*{reason}*\n\n"
        f"**SMILES:** `{smiles}`",
        icon="🧪",
    )


# ---------------------------------------------------------------------------
# Candidate detail card
# ---------------------------------------------------------------------------

def render_candidate_card(candidate: FrontendCandidate, show_structure: bool = True) -> None:
    """Expandable detail card for a single candidate."""
    rank_medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(candidate.rank, f"#{candidate.rank}")
    with st.expander(
        f"{rank_medal} **{candidate.candidate_id}** — Final Score: {candidate.final_score:.3f}",
        expanded=(candidate.rank == 1),
    ):
        col_struct, col_info = st.columns([1, 2])
        with col_struct:
            if show_structure:
                render_molecule(candidate.smiles, width=320, height=210)
            st.caption(f"SMILES: `{candidate.smiles}`")

        with col_info:
            # Score table
            st.markdown("**Scores**")
            score_data = {
                "Score": ["Activity", "Docking (raw)", "Property", "Novelty", "**Final**"],
                "Value": [
                    f"{candidate.activity_score:.4f}",
                    f"{candidate.docking.score_raw:.3f} kcal/mol"
                    if candidate.docking.score_raw is not None else "N/A",
                    f"{candidate.property_score:.1f}",
                    f"{candidate.novelty_score:.2f}",
                    f"**{candidate.final_score:.4f}**",
                ],
                "Label": [
                    demo_field_html("activity_score") if candidate.is_demo else "",
                    demo_field_html("docking_score")  if candidate.is_demo else "",
                    "",
                    demo_field_html("novelty_score")  if candidate.is_demo else "",
                    "",
                ],
            }
            for name, val, lbl in zip(score_data["Score"], score_data["Value"], score_data["Label"]):
                cols = st.columns([2, 2, 1])
                cols[0].markdown(name)
                cols[1].markdown(val)
                if lbl:
                    cols[2].markdown(lbl, unsafe_allow_html=True)

            st.markdown("---")
            # Descriptor table
            st.markdown("**Molecular Properties**")
            p = candidate.properties
            desc_rows = [
                ("MW",              f"{p.mw:.2f} Da"),
                ("LogP",            f"{p.logp:.3f}"),
                ("HBD",             str(p.hbd)),
                ("HBA",             str(p.hba)),
                ("TPSA",            f"{p.tpsa:.1f} Å²"),
                ("Rotatable Bonds", str(p.rotatable_bonds)),
            ]
            for label, value in desc_rows:
                r1, r2 = st.columns([1, 1])
                r1.caption(label)
                r2.markdown(value)

            # Filter status
            st.markdown("---")
            fstatus = candidate.filter.status
            fkind   = "pass" if fstatus == "PASS" else "rejected"
            st.markdown(
                f"**Filter Status:** {badge_html(fstatus, fkind)}",
                unsafe_allow_html=True,
            )
            if candidate.filter.reasons:
                for reason in candidate.filter.reasons:
                    st.caption(f"  • {reason}")

            # Docking status
            dkind = "fallback" if "FALLBACK" in candidate.docking.docking_status else "pass"
            st.markdown(
                f"**Docking Status:** {badge_html(candidate.docking.docking_status, dkind)}  "
                f"| **Receptor:** {candidate.docking.receptor_id or 'N/A'}",
                unsafe_allow_html=True,
            )

        # Demo warnings
        if candidate.warnings:
            with st.expander("⚠ Demo value notices", expanded=False):
                for w in candidate.warnings:
                    st.caption(f"• {w}")


# ---------------------------------------------------------------------------
# Score breakdown component
# ---------------------------------------------------------------------------

def render_score_breakdown(candidate: FrontendCandidate, weights: dict) -> None:
    """Render the score_waterfall chart for a single candidate."""
    from src.ui.charts import score_waterfall
    st.plotly_chart(score_waterfall(candidate, weights), use_container_width=True)


# ---------------------------------------------------------------------------
# Filter badge
# ---------------------------------------------------------------------------

def render_filter_badge(filter_result: FilterResult) -> None:
    """Inline PASS / REJECTED badge with reasons tooltip."""
    if filter_result.status == "PASS":
        st.markdown(badge_html("✓ PASS", "pass"), unsafe_allow_html=True)
    else:
        st.markdown(badge_html("✗ REJECTED", "rejected"), unsafe_allow_html=True)
        if filter_result.reasons:
            for r in filter_result.reasons:
                st.caption(f"  — {r}")


# ---------------------------------------------------------------------------
# Demo field label (inline amber chip)
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
<p><strong>⚠ Demo & Fallback Values in This View</strong></p>
<p>• <strong>activity_score</strong>: deterministic hash value (SHA-256 of compound ID) — not a real ML prediction.</p>
<p>• <strong>docking_score</strong>: FALLBACK_DEMO — computed from SHA-256 hash, range −7.2 to −8.4 kcal/mol. No real docking was performed.</p>
<p>• <strong>novelty_score</strong>: hardcoded to 0.5 for all demo compounds.</p>
<p>These values will be replaced by validated model outputs and real docking results during implementation.</p>
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
            st.markdown(f"✅ ~~{stage}~~")
        elif i == current_idx:
            st.markdown(f"⏳ **{stage}...**")
        else:
            st.markdown(f"⬜ {stage}")


# ---------------------------------------------------------------------------
# What-if analysis label / banner
# ---------------------------------------------------------------------------

def render_whatif_label() -> None:
    """Prominent banner labeling the what-if ranking analysis section."""
    st.markdown(
        """<div class="tf-whatif-banner">
<p>⚠ <strong>What-If Ranking Analysis</strong> — Adjust weights below to explore how
different scoring priorities would affect candidate ordering.
This is a <em>frontend simulation only</em> and does <strong>not modify the official
computational ranking above</strong>.</p>
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Property radar (wrapper around charts.property_radar)
# ---------------------------------------------------------------------------

def render_property_radar(
    candidate: FrontendCandidate,
    limits: dict,
    title: str | None = None,
) -> None:
    """Render the property radar chart via st.plotly_chart."""
    from src.ui.charts import property_radar
def _molecule_unavailable(smiles: str, reason: str) -> None:
    st.info(
        f"**⚠ Molecular structure visualization unavailable**\n\n"
        f"*{reason}*\n\n"
        f"**SMILES:** `{smiles}`",
        icon="🧪",
    )


# ---------------------------------------------------------------------------
# Candidate detail card
# ---------------------------------------------------------------------------

def render_candidate_card(candidate: FrontendCandidate, show_structure: bool = True) -> None:
    """Expandable detail card for a single candidate."""
    rank_medal = {1: "Rank 1", 2: "Rank 2", 3: "Rank 3"}.get(candidate.rank, f"Rank {candidate.rank}")
    with st.expander(
        f"{rank_medal} | **{candidate.candidate_id}** — Final Score: {candidate.final_score:.3f}",
        expanded=(candidate.rank == 1),
    ):
        col_struct, col_info = st.columns([1, 2])
        with col_struct:
            if show_structure:
                render_molecule(candidate.smiles, width=320, height=210)
            st.caption(f"SMILES: `{candidate.smiles}`")

        with col_info:
            # Score table
            st.markdown("**Scores**")
            score_data = {
                "Score": ["Activity", "Docking (raw)", "Property", "Novelty", "**Final**"],
                "Value": [
                    f"{candidate.activity_score:.4f}",
                    f"{candidate.docking.score_raw:.3f} kcal/mol"
                    if candidate.docking.score_raw is not None else "N/A",
                    f"{candidate.property_score:.1f}",
                    f"{candidate.novelty_score:.2f}",
                    f"**{candidate.final_score:.4f}**",
                ],
                "Label": [
                    demo_field_html("activity_score") if candidate.is_demo else "",
                    demo_field_html("docking_score")  if candidate.is_demo else "",
                    "",
                    demo_field_html("novelty_score")  if candidate.is_demo else "",
                    "",
                ],
            }
            for name, val, lbl in zip(score_data["Score"], score_data["Value"], score_data["Label"]):
                cols = st.columns([2, 2, 1])
                cols[0].markdown(name)
                cols[1].markdown(val)
                if lbl:
                    cols[2].markdown(lbl, unsafe_allow_html=True)

            st.markdown("---")
            # Descriptor table
            st.markdown("**Molecular Properties**")
            p = candidate.properties
            desc_rows = [
                ("MW",              f"{p.mw:.2f} Da"),
                ("LogP",            f"{p.logp:.3f}"),
                ("HBD",             str(p.hbd)),
                ("HBA",             str(p.hba)),
                ("TPSA",            f"{p.tpsa:.1f} Å²"),
                ("Rotatable Bonds", str(p.rotatable_bonds)),
            ]
            for label, value in desc_rows:
                r1, r2 = st.columns([1, 1])
                r1.caption(label)
                r2.markdown(value)

            # Filter status
            st.markdown("---")
            fstatus = candidate.filter.status
            fkind   = "pass" if fstatus == "PASS" else "rejected"
            st.markdown(
                f"**Filter Status:** {badge_html(fstatus, fkind)}",
                unsafe_allow_html=True,
            )
            if candidate.filter.reasons:
                for reason in candidate.filter.reasons:
                    st.caption(f"  • {reason}")

            # Docking status
            dkind = "fallback" if "FALLBACK" in candidate.docking.docking_status else "pass"
            st.markdown(
                f"**Docking Status:** {badge_html(candidate.docking.docking_status, dkind)}  "
                f"| **Receptor:** {candidate.docking.receptor_id or 'N/A'}",
                unsafe_allow_html=True,
            )

        # Demo warnings
        if candidate.warnings:
            with st.expander("⚠ Demo value notices", expanded=False):
                for w in candidate.warnings:
                    st.caption(f"• {w}")


# ---------------------------------------------------------------------------
# Score breakdown component
# ---------------------------------------------------------------------------

def render_score_breakdown(candidate: FrontendCandidate, weights: dict) -> None:
    """Render the score_waterfall chart for a single candidate."""
    from src.ui.charts import score_waterfall
    st.plotly_chart(score_waterfall(candidate, weights), use_container_width=True)


# ---------------------------------------------------------------------------
# Filter badge
# ---------------------------------------------------------------------------

def render_filter_badge(filter_result: FilterResult) -> None:
    """Inline PASS / REJECTED badge with reasons tooltip."""
    if filter_result.status == "PASS":
        st.markdown(badge_html("✓ PASS", "pass"), unsafe_allow_html=True)
    else:
        st.markdown(badge_html("✗ REJECTED", "rejected"), unsafe_allow_html=True)
        if filter_result.reasons:
            for r in filter_result.reasons:
                st.caption(f"  — {r}")


# ---------------------------------------------------------------------------
# Demo field label (inline amber chip)
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
<p><strong>⚠ Demo & Fallback Values in This View</strong></p>
<p>• <strong>activity_score</strong>: deterministic hash value (SHA-256 of compound ID) — not a real ML prediction.</p>
<p>• <strong>docking_score</strong>: FALLBACK_DEMO — computed from SHA-256 hash, range −7.2 to −8.4 kcal/mol. No real docking was performed.</p>
<p>• <strong>novelty_score</strong>: hardcoded to 0.5 for all demo compounds.</p>
<p>These values will be replaced by validated model outputs and real docking results during implementation.</p>
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
            st.markdown(f"✅ ~~{stage}~~")
        elif i == current_idx:
            st.markdown(f"⏳ **{stage}...**")
        else:
            st.markdown(f"⬜ {stage}")


# ---------------------------------------------------------------------------
# What-if analysis label / banner
# ---------------------------------------------------------------------------

def render_whatif_label() -> None:
    """Prominent banner labeling the what-if ranking analysis section."""
    st.markdown(
        """<div class="tf-whatif-banner">
<p>⚠ <strong>What-If Ranking Analysis</strong> — Adjust weights below to explore how
different scoring priorities would affect candidate ordering.
This is a <em>frontend simulation only</em> and does <strong>not modify the official
computational ranking above</strong>.</p>
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Property radar (wrapper around charts.property_radar)
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
# Redesigned Custom Components
# ---------------------------------------------------------------------------

def render_top_navbar() -> None:
    """Render a horizontal top navbar using Streamlit columns and page links."""
    c_brand, c0, c1, c2, c3, c4, c5, c6, c7, c_help = st.columns(
        [1.8, 0.8, 1.2, 1.2, 1.1, 1.3, 1.2, 1.1, 0.8, 0.5],
        gap="small"
    )
    
    with c_brand:
        st.markdown(
            '<a href="http://localhost:8501" style="text-decoration:none; display:flex; align-items:center;">'
            '<svg viewBox="0 0 24 24" width="20" height="20" stroke="#00B4D8" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:middle; margin-right:6px; margin-bottom:3px;">'
            '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="18" r="2.5"/><circle cx="19" cy="18" r="2.5"/>'
            '<line x1="12" y1="7.5" x2="6.5" y2="15.5"/><line x1="12" y1="7.5" x2="17.5" y2="15.5"/><line x1="7.5" y1="18" x2="16.5" y2="18"/>'
            '</svg>'
            '<h3 style="margin: 0; font-size: 1.25rem; font-weight:700; color:#E2E8F0 !important; display:inline-block; vertical-align:middle;">'
            'Target<span style="color:#00B4D8;">Forge</span>'
            '</h3>'
            '</a>',
            unsafe_allow_html=True
        )
        
    with c0:
        st.page_link("pages/01_home.py", label="Home", icon=":material/home:")
    with c1:
        st.page_link("pages/02_target_explorer.py", label="Target Explorer", icon=":material/track_changes:")
    with c2:
        st.page_link("pages/03_dataset_manager.py", label="Dataset Manager", icon=":material/database:")
    with c3:
        st.page_link("pages/04_ai_screening.py", label="AI Screening", icon=":material/hub:")
    with c4:
        st.page_link("pages/05_candidate_design.py", label="Candidate Design", icon=":material/science:")
    with c5:
        st.page_link("pages/06_docking_analysis.py", label="Docking Analysis", icon=":material/join_inner:")
    with c6:
        st.page_link("pages/07_final_ranking.py", label="Final Ranking", icon=":material/leaderboard:")
    with c7:
        st.page_link("pages/08_reports.py", label="Reports", icon=":material/description:")
        
    with c_help:
        st.markdown(
            '<div style="text-align:right; padding-top:4px;" title="Documentation">'
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="transition: stroke 0.2s ease; cursor:pointer;" onmouseover="this.style.stroke=\'#00B4D8\'" onmouseout="this.style.stroke=\'#94A3B8\'">'
            '<circle cx="12" cy="12" r="10"/>'
            '<path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>'
            '<line x1="12" y1="17" x2="12.01" y2="17"/>'
            '</svg>'
            '</div>',
            unsafe_allow_html=True
        )
        
    st.markdown('<hr style="margin: 0.5rem 0 1.5rem 0; border-color: #1A365D;">', unsafe_allow_html=True)


def render_horizontal_stepper(current_step: WorkflowStep) -> None:
    """Render a horizontal stepper progress tracker matching the mockup."""
    from src.ui.state import WorkflowStep, StepStatus, get_step_status
    
    steps = [
        (WorkflowStep.TARGET, "1", "Target"),
        (WorkflowStep.DATASET, "2", "Data"),
        (WorkflowStep.SCREENING, "3", "AI"),
        (WorkflowStep.DESIGN, "4", "Candidates"),
        (WorkflowStep.DOCKING, "5", "Docking"),
        (WorkflowStep.RANKING, "6", "Ranking"),
    ]
    
    # Calculate active line width (0% to 100%)
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


def render_hero_banner() -> None:
    """Render the hero section banner with molecular background and professional scientific copy."""
    hero_html = """<div class="hero-section">
<div class="hero-content">
<h1>Deciphering Molecular Complexity<br>into High-Confidence <span>Therapeutics.</span></h1>
<p>Leveraging advanced machine learning models and structure-based docking to prioritize lead candidates with speed and precision.</p>
</div>
</div>"""
    st.markdown(hero_html, unsafe_allow_html=True)


def render_stats_ticker(candidates: list[FrontendCandidate] | None = None) -> None:
    """Render the dynamic metrics strip below the hero section."""
    target_name = st.session_state.get("tf_target", {}).get("name", "SARS-CoV-2 Mpro")
    
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
            
    ticker_html = f"""<div class="hero-ticker">
<div class="hero-ticker-item">
<svg viewBox="0 0 24 24" width="14" height="14" stroke="#00B4D8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:middle; margin-right:6px; margin-bottom:2px;"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
<strong>{screened_count}</strong> molecules screened
</div>
<div class="hero-ticker-item">
<svg viewBox="0 0 24 24" width="14" height="14" stroke="#00B4D8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:middle; margin-right:6px; margin-bottom:2px;"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
Target: <strong>{target_name}</strong>
</div>
<div class="hero-ticker-item">
<svg viewBox="0 0 24 24" width="14" height="14" stroke="#00B4D8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:middle; margin-right:6px; margin-bottom:2px;"><circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-8.4 8.4M12 8v8M8 12h8"/></svg>
Best docking score: <strong>{best_score:.1f} kcal/mol</strong>
</div>
<div class="hero-ticker-item">
<svg viewBox="0 0 24 24" width="14" height="14" stroke="#00B4D8" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:middle; margin-right:6px; margin-bottom:2px;"><path d="M16.3 11 12 3H8l4.3 8M5 21h14M19 21l-7-13M5 21l7-13"/></svg>
Candidates generated: <strong>{candidates_count}</strong>
</div>
</div>"""
    st.markdown(ticker_html, unsafe_allow_html=True)
