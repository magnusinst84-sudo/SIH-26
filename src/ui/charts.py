"""
src/ui/charts.py
----------------
Scientific analytical Plotly chart factory functions for TargetForge.

Dark modern scientific palette:
- Restrained color palette (#00BFA6, #F59E0B, #38BDF8, #818CF8, #A1ABB3)
- Clean gridlines (#1E293B) and zero lines
- High contrast axis labels and units
- Horizontal bars and stacked/grouped bars (no pie charts for score breakdowns)

Owned by: M4 (Frontend/UI Lead)
"""
from __future__ import annotations

from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.ui.schema import FrontendCandidate
from src.ui.theme import (
    CHART_COLORS,
    CHART_FONT,
    CHART_BGCOLOR,
    CHART_PAPER,
    CHART_TEMPLATE,
    COLORS,
)

# ---------------------------------------------------------------------------
# Shared layout defaults
# ---------------------------------------------------------------------------

def _base_layout(**overrides) -> dict:
    return {
        "font":           dict(family="Inter, sans-serif", color="#F8FAFC", size=11),
        "plot_bgcolor":   "#11161D",
        "paper_bgcolor":  "rgba(0,0,0,0)",
        "margin":         dict(l=45, r=20, t=35, b=35),
        "legend":         dict(
                              font=dict(size=10, color="#A1ABB3"),
                              bgcolor="rgba(17, 22, 29, 0.85)",
                              bordercolor="#232D38",
                              borderwidth=1,
                              orientation="h",
                              yanchor="bottom",
                              y=1.02,
                              xanchor="right",
                              x=1,
                          ),
        **overrides,
    }


def _apply_base(fig: go.Figure, title: str = "", height: int = 340) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#F8FAFC", weight=600)),
        height=height,
        template="plotly_dark",
        **_base_layout(),
    )
    fig.update_xaxes(
        gridcolor="#1E293B",
        linecolor="#232D38",
        zerolinecolor="#232D38",
        tickfont=dict(size=10, color="#A1ABB3"),
        title_font=dict(size=11, color="#F8FAFC"),
    )
    fig.update_yaxes(
        gridcolor="#1E293B",
        linecolor="#232D38",
        zerolinecolor="#232D38",
        tickfont=dict(size=10, color="#A1ABB3"),
        title_font=dict(size=11, color="#F8FAFC"),
    )
    return fig


# ---------------------------------------------------------------------------
# 1. Activity vs Docking scatter plot
# ---------------------------------------------------------------------------

def activity_docking_scatter(candidates: list[FrontendCandidate]) -> go.Figure:
    """Scientific scatter: activity_score vs docking_score with class distinction."""
    if not candidates:
        return _empty_chart("No candidate data available")

    ids     = [c.candidate_id   for c in candidates]
    acts    = [c.activity_score  for c in candidates]
    docks   = [c.docking.score_raw if c.docking.score_raw is not None else 0.0
               for c in candidates]
    classes = [c.predicted_class for c in candidates]
    finals  = [c.final_score     for c in candidates]

    color_map = {"active": "#00BFA6", "lower_priority": "#64748B"}

    fig = go.Figure()
    for cls, color in color_map.items():
        mask = [i for i, c in enumerate(classes) if c == cls]
        if not mask:
            continue
        fig.add_trace(go.Scatter(
            x    = [acts[i]  for i in mask],
            y    = [docks[i] for i in mask],
            mode = "markers+text",
            name = cls.replace("_", " ").title(),
            text = [ids[i] for i in mask],
            textposition = "top center",
            textfont     = dict(size=9, color="#A1ABB3"),
            marker = dict(
                size   = [8 + finals[i] * 6 for i in mask],
                color  = color,
                opacity= 0.88,
                line   = dict(width=1, color="#11161D"),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Activity score: %{x:.3f}<br>"
                "Docking affinity: %{y:.3f} kcal/mol<br>"
                "<extra></extra>"
            ),
        ))

    _apply_base(fig, "Activity Prediction vs Docking Affinity", height=350)
    fig.update_xaxes(title_text="Predicted Activity Score (0.0–1.0)", range=[0.55, 1.02])
    fig.update_yaxes(title_text="Docking Energy (kcal/mol)", autorange=True)
    return fig


# ---------------------------------------------------------------------------
# 2. Horizontal Grouped Score Bar Chart
# ---------------------------------------------------------------------------

def score_bar_chart(candidates: list[FrontendCandidate]) -> go.Figure:
    """Grouped bar chart showing multi-objective score components per compound."""
    if not candidates:
        return _empty_chart("No candidate data available")

    ids = [c.candidate_id for c in candidates]

    fig = go.Figure()
    series = [
        ("Activity",  [c.activity_score  for c in candidates], "#00BFA6"),
        ("Docking",   [c.docking_norm    for c in candidates], "#38BDF8"),
        ("Property",  [c.property_score  for c in candidates], "#F59E0B"),
        ("Novelty",   [c.novelty_score   for c in candidates], "#818CF8"),
        ("Final",     [c.final_score     for c in candidates], "#FFFFFF"),
    ]
    for name, vals, color in series:
        fig.add_trace(go.Bar(
            name=name,
            x=ids,
            y=vals,
            marker_color=color,
            marker_line=dict(width=0),
            opacity=0.9,
        ))

    _apply_base(fig, "Candidate Score Components (Normalized 0.0–1.0)", height=330)
    fig.update_layout(barmode="group", bargap=0.2, bargroupgap=0.06)
    fig.update_xaxes(title_text="Compound ID")
    fig.update_yaxes(title_text="Score Fraction (0.0–1.0)", range=[0, 1.05])
    return fig


# ---------------------------------------------------------------------------
# 3. Horizontal Stacked Score Breakdown
# ---------------------------------------------------------------------------

def score_waterfall(candidate: FrontendCandidate, weights: dict) -> go.Figure:
    """Horizontal stacked bar chart showing weighted contributions to the final score."""
    aw = weights.get("activity_weight",  0.40)
    dw = weights.get("docking_weight",   0.30)
    pw = weights.get("property_weight",  0.20)
    nw = weights.get("novelty_weight",   0.10)

    c_act  = aw * candidate.activity_norm
    c_dock = dw * candidate.docking_norm
    c_prop = pw * candidate.property_score
    c_nov  = nw * candidate.novelty_score
    final  = candidate.final_score

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=f"Activity ({aw:.0%})",
        y=[candidate.candidate_id],
        x=[c_act],
        orientation="h",
        marker_color="#00BFA6",
        text=[f"{c_act:.3f}"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#080F14", size=10, weight=600),
        hovertemplate="Activity contribution: %{x:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name=f"Docking ({dw:.0%})",
        y=[candidate.candidate_id],
        x=[c_dock],
        orientation="h",
        marker_color="#38BDF8",
        text=[f"{c_dock:.3f}"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#080F14", size=10, weight=600),
        hovertemplate="Docking contribution: %{x:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name=f"Property ({pw:.0%})",
        y=[candidate.candidate_id],
        x=[c_prop],
        orientation="h",
        marker_color="#F59E0B",
        text=[f"{c_prop:.3f}"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#080F14", size=10, weight=600),
        hovertemplate="Property contribution: %{x:.4f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name=f"Novelty ({nw:.0%})",
        y=[candidate.candidate_id],
        x=[c_nov],
        orientation="h",
        marker_color="#818CF8",
        text=[f"{c_nov:.3f}"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="#FFFFFF", size=10),
        hovertemplate="Novelty contribution: %{x:.4f}<extra></extra>",
    ))

    _apply_base(fig, f"Score Breakdown — {candidate.candidate_id} (Final: {final:.4f})", height=160)
    fig.update_layout(
        barmode="stack",
        margin=dict(l=65, r=20, t=30, b=30),
    )
    fig.update_xaxes(title_text="Weighted Score Contribution", range=[0, 1.0])
    fig.update_yaxes(title_text="")
    return fig


# ---------------------------------------------------------------------------
# 4. Docking score horizontal bar chart
# ---------------------------------------------------------------------------

def docking_score_bar(candidates: list[FrontendCandidate]) -> go.Figure:
    """Horizontal bar chart of calculated docking affinity (lower = stronger binding)."""
    if not candidates:
        return _empty_chart("No docking data available")

    sorted_cands = sorted(
        candidates,
        key=lambda c: c.docking.score_raw or 0.0,
    )
    ids    = [c.candidate_id            for c in sorted_cands]
    scores = [c.docking.score_raw or 0.0 for c in sorted_cands]
    colors = [
        "#00BFA6" if s == min(scores) else "#38BDF8"
        for s in scores
    ]

    fig = go.Figure(go.Bar(
        x            = scores,
        y            = ids,
        orientation  = "h",
        marker_color = colors,
        marker_line  = dict(width=0),
        text         = [f"{s:.2f} kcal/mol" for s in scores],
        textposition = "inside",
        insidetextanchor = "end",
        textfont     = dict(size=10, color="#080F14", weight=600),
        hovertemplate = "<b>%{y}</b><br>Calculated affinity: %{x:.3f} kcal/mol<extra></extra>",
    ))
    _apply_base(fig, "Docking Binding Energy (kcal/mol, lower is stronger)", height=260)
    fig.update_xaxes(title_text="Calculated Binding Affinity (kcal/mol)")
    fig.update_yaxes(title_text="")
    return fig


# ---------------------------------------------------------------------------
# 5. Property radar chart
# ---------------------------------------------------------------------------

def property_radar(
    candidate: FrontendCandidate,
    limits: dict,
    title: Optional[str] = None,
) -> go.Figure:
    """Analytical spider/radar: descriptor values normalized against Lipinski limits."""
    props = candidate.properties
    lims  = {
        "MW":              limits.get("max_molecular_weight", 500),
        "LogP":            limits.get("max_logp",             5.0),
        "HBD":             limits.get("max_hbd",              5),
        "HBA":             limits.get("max_hba",              10),
        "TPSA":            limits.get("max_tpsa",             140),
        "Rot. Bonds":      limits.get("max_rotatable_bonds",  10),
    }
    raw = {
        "MW":         props.mw,
        "LogP":       props.logp,
        "HBD":        props.hbd,
        "HBA":        props.hba,
        "TPSA":       props.tpsa,
        "Rot. Bonds": props.rotatable_bonds,
    }
    cats   = list(lims.keys())
    vals   = [min(raw[c] / lims[c], 1.3) if lims[c] else 0 for c in cats]
    cats_r = cats + [cats[0]]
    vals_r = vals + [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r    = vals_r,
        theta= cats_r,
        fill = "toself",
        fillcolor = "rgba(0, 191, 166, 0.18)",
        line = dict(color="#00BFA6", width=1.5),
        name = candidate.candidate_id,
    ))
    fig.add_trace(go.Scatterpolar(
        r    = [1.0] * (len(cats) + 1),
        theta= cats_r,
        mode = "lines",
        line = dict(color="#F59E0B", width=1.5, dash="dot"),
        name = "Threshold (100%)",
    ))
    _apply_base(fig, title or f"Properties — {candidate.candidate_id}", height=280)
    fig.update_layout(
        polar = dict(
            bgcolor    = "#11161D",
            radialaxis = dict(
                visible    = True,
                range      = [0, 1.3],
                tickvals   = [0.5, 1.0],
                ticktext   = ["50%", "100%"],
                tickfont   = dict(size=8, color="#A1ABB3"),
                gridcolor  = "#1E293B",
            ),
            angularaxis = dict(
                gridcolor="#1E293B",
                tickfont=dict(size=9, color="#F8FAFC"),
            ),
        ),
        showlegend = True,
    )
    return fig


# ---------------------------------------------------------------------------
# 6. Filter funnel
# ---------------------------------------------------------------------------

def filter_funnel(total: int, passed: int, rejected: int) -> go.Figure:
    """Horizontal funnel chart showing compound progression through stages."""
    stages = ["Loaded", "Validated", "Filter Pass", "Docked"]
    counts = [total, total, passed, min(passed, 5)]

    fig = go.Figure(go.Funnel(
        y          = stages,
        x          = counts,
        textinfo   = "value+percent initial",
        textfont   = dict(size=10, color="#F8FAFC"),
        marker     = dict(color=["#818CF8", "#38BDF8", "#00BFA6", "#F59E0B"]),
        connector  = dict(line=dict(width=1, color="#232D38")),
    ))
    _apply_base(fig, "Pipeline Filtering Funnel", height=260)
    return fig


# ---------------------------------------------------------------------------
# 7. Validation bar chart
# ---------------------------------------------------------------------------

def validation_bar(valid_n: int, rejected_n: int) -> go.Figure:
    """Compact bar chart of validated vs rejected molecule counts."""
    fig = go.Figure(go.Bar(
        x            = ["Valid", "Rejected"],
        y            = [valid_n, rejected_n],
        marker_color  = ["#00BFA6", "#EF4444"],
        text         = [valid_n, rejected_n],
        textposition = "outside",
        textfont     = dict(size=11, color="#F8FAFC"),
        width        = 0.35,
    ))
    _apply_base(fig, "Structure Validation", height=250)
    fig.update_yaxes(title_text="Molecules", rangemode="tozero")
    return fig


# ---------------------------------------------------------------------------
# 8. Activity score distribution histogram
# ---------------------------------------------------------------------------

def score_distribution_histogram(df: pd.DataFrame, col: str = "activity_score") -> go.Figure:
    """Analytical histogram of activity scores across compound library."""
    if df is None or df.empty or col not in df.columns:
        return _empty_chart("No score data available")

    fig = px.histogram(
        df, x=col, nbins=10,
        color_discrete_sequence=["#00BFA6"],
        template="plotly_dark",
        labels={col: "Predicted Activity Score"},
        opacity=0.85,
    )
    _apply_base(fig, "Activity Score Distribution", height=260)
    fig.update_xaxes(title_text="Predicted Activity Score (0.0–1.0)")
    fig.update_yaxes(title_text="Molecule Frequency (Count)")
    return fig


# ---------------------------------------------------------------------------
# 9. What-if comparison chart
# ---------------------------------------------------------------------------

def whatif_comparison_chart(
    candidates: list[FrontendCandidate],
    whatif_candidates: list[FrontendCandidate],
) -> go.Figure:
    """Grouped bar: official final score vs simulated what-if score."""
    if not candidates or not whatif_candidates:
        return _empty_chart("No data for comparison")

    ids      = [c.candidate_id for c in candidates]
    official = [c.final_score  for c in candidates]
    whatif_map = {c.candidate_id: c.whatif_score or 0.0 for c in whatif_candidates}
    whatif   = [whatif_map.get(cid, 0.0) for cid in ids]

    fig = go.Figure([
        go.Bar(
            name         = "Official Score",
            x            = ids,
            y            = official,
            marker_color = "#38BDF8",
            opacity      = 0.9,
            marker_line  = dict(width=0),
        ),
        go.Bar(
            name         = "Simulated Score",
            x            = ids,
            y            = whatif,
            marker_color = "#00BFA6",
            opacity      = 0.85,
            marker_line  = dict(width=0),
        ),
    ])
    _apply_base(fig, "Official vs Simulated Score Comparison", height=280)
    fig.update_layout(barmode="group", bargap=0.2)
    fig.update_xaxes(title_text="Compound ID")
    fig.update_yaxes(title_text="Score (0.0–1.0)", range=[0, 1.05])
    return fig


# ---------------------------------------------------------------------------
# 10. Property filter heatmap
# ---------------------------------------------------------------------------

def filter_heatmap(filtered_df: pd.DataFrame, ui_config: dict) -> go.Figure:
    """Pass/Fail matrix heatmap for physicochemical property thresholds."""
    if filtered_df is None or filtered_df.empty:
        return _empty_chart("No filter data available")

    prop_cols = {
        "MW":    ("molecular_weight", ui_config.get("max_molecular_weight", 500)),
        "LogP":  ("logp",             ui_config.get("max_logp",             5.0)),
        "HBD":   ("hbd",              ui_config.get("max_hbd",              5)),
        "HBA":   ("hba",              ui_config.get("max_hba",              10)),
        "TPSA":  ("tpsa",             ui_config.get("max_tpsa",             140)),
        "RotB":  ("rotatable_bonds",  ui_config.get("max_rotatable_bonds",  10)),
    }

    ids = filtered_df["compound_id"].tolist() if "compound_id" in filtered_df.columns else [
        f"CMP-{i+1:03d}" for i in range(len(filtered_df))
    ]

    matrix = []
    props_used = []
    for prop_label, (col, limit) in prop_cols.items():
        if col in filtered_df.columns:
            row_vals = (filtered_df[col] <= limit).astype(int).tolist()
            matrix.append(row_vals)
            props_used.append(prop_label)

    if not matrix:
        return _empty_chart("No descriptor columns available")

    colorscale = [[0, "rgba(239, 68, 68, 0.25)"], [1, "rgba(0, 191, 166, 0.25)"]]
    fig = go.Figure(go.Heatmap(
        z           = matrix,
        x           = ids,
        y           = props_used,
        colorscale  = colorscale,
        showscale   = False,
        text        = [["PASS" if v else "FAIL" for v in row] for row in matrix],
        texttemplate= "%{text}",
        textfont    = dict(size=10, color="#F8FAFC"),
        hovertemplate = "%{y}: %{text}<extra></extra>",
    ))
    _apply_base(fig, "Lipinski & Property Compliance Matrix", height=240)
    fig.update_yaxes(title_text="")
    fig.update_xaxes(title_text="Compound ID")
    return fig


# ---------------------------------------------------------------------------
# 11. Ranking weights horizontal bar chart
# ---------------------------------------------------------------------------

def weights_bar(weights: dict) -> go.Figure:
    """Horizontal stacked bar of ranking weight distribution."""
    labels = ["Activity", "Docking", "Property", "Novelty"]
    values = [
        weights.get("activity_weight",  0.40),
        weights.get("docking_weight",   0.30),
        weights.get("property_weight",  0.20),
        weights.get("novelty_weight",   0.10),
    ]
    colors = ["#00BFA6", "#38BDF8", "#F59E0B", "#818CF8"]

    fig = go.Figure()
    for lbl, val, col in zip(labels, values, colors):
        fig.add_trace(go.Bar(
            name=f"{lbl} ({val:.0%})",
            y=["Weights"],
            x=[val],
            orientation="h",
            marker_color=col,
            text=[f"{lbl}<br>{val:.0%}"],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(size=10, color="#080F14", weight=600),
            hovertemplate=f"{lbl} weight: %{{x:.0%}}<extra></extra>",
        ))

    _apply_base(fig, "Multi-Objective Ranking Weights", height=130)
    fig.update_layout(
        barmode="stack",
        margin=dict(l=30, r=20, t=25, b=25),
        showlegend=False,
    )
    fig.update_xaxes(title_text="Fraction (Total = 100%)", range=[0, 1.0])
    fig.update_yaxes(visible=False)
    return fig


def weights_pie(weights: dict) -> go.Figure:
    """Backward compatibility alias pointing to weights_bar."""
    return weights_bar(weights)


# ---------------------------------------------------------------------------
# Helper: empty placeholder chart
# ---------------------------------------------------------------------------

def _empty_chart(message: str = "No data") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=12, color="#A1ABB3"),
    )
    _apply_base(fig, height=240)
    return fig
