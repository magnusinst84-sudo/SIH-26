"""
src/ui/charts.py
----------------
Plotly chart factory functions for TargetForge.

All charts use the light scientific theme (plotly_white template, Inter font).
Charts are consumed by Streamlit pages via st.plotly_chart(...).

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
        "font":           CHART_FONT,
        "plot_bgcolor":   CHART_BGCOLOR,
        "paper_bgcolor":  CHART_PAPER,
        "margin":         dict(l=40, r=20, t=40, b=40),
        "legend":         dict(
                              font=dict(size=11, color=COLORS["text"]),
                              bgcolor="rgba(0,0,0,0)",
                          ),
        **overrides,
    }


def _apply_base(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=COLORS["navy"], weight=600)),
        height=height,
        **_base_layout(),
    )
    fig.update_xaxes(gridcolor="#EFF2F7", linecolor=COLORS["border"], zerolinecolor="#EFF2F7")
    fig.update_yaxes(gridcolor="#EFF2F7", linecolor=COLORS["border"], zerolinecolor="#EFF2F7")
    return fig


# ---------------------------------------------------------------------------
# 1. Activity vs Docking scatter plot
# ---------------------------------------------------------------------------

def activity_docking_scatter(candidates: list[FrontendCandidate]) -> go.Figure:
    """Scatter: activity_score vs docking_score, coloured by predicted_class."""
    if not candidates:
        return _empty_chart("No candidate data available")

    ids     = [c.candidate_id   for c in candidates]
    acts    = [c.activity_score  for c in candidates]
    docks   = [c.docking.score_raw if c.docking.score_raw is not None else 0.0
               for c in candidates]
    classes = [c.predicted_class for c in candidates]
    finals  = [c.final_score     for c in candidates]

    color_map = {"active": COLORS["teal"], "lower_priority": COLORS["muted"]}

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
            textfont     = dict(size=10, color=COLORS["muted"]),
            marker = dict(
                size   = [12 + finals[i] * 10 for i in mask],
                color  = color,
                opacity= 0.82,
                line   = dict(width=1.5, color="white"),
            ),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Activity score: %{x:.3f}<br>"
                "Docking score: %{y:.3f} kcal/mol<br>"
                "<extra></extra>"
            ),
        ))

    _apply_base(fig, "Activity vs Docking Score", height=420)
    fig.update_xaxes(title_text="Activity Score (demo)",      range=[0.55, 1.01])
    fig.update_yaxes(title_text="Docking Score (kcal/mol)",   autorange=True)
    fig.add_annotation(
        text="⚠ Both axes show deterministic demo values",
        xref="paper", yref="paper", x=0, y=1.06,
        showarrow=False,
        font=dict(size=10, color=COLORS["demo_text"]),
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Grouped score bar chart (activity / property / novelty / final)
# ---------------------------------------------------------------------------

def score_bar_chart(candidates: list[FrontendCandidate]) -> go.Figure:
    """Grouped bar chart: score components per compound."""
    if not candidates:
        return _empty_chart("No candidate data available")

    ids = [c.candidate_id for c in candidates]

    fig = go.Figure()
    series = [
        ("Activity Score",  [c.activity_score  for c in candidates], COLORS["teal"]),
        ("Property Score",  [c.property_score  for c in candidates], COLORS["blue"]),
        ("Novelty Score",   [c.novelty_score   for c in candidates], COLORS["cyan"]),
        ("Final Score",     [c.final_score     for c in candidates], COLORS["navy"]),
    ]
    for name, vals, color in series:
        fig.add_trace(go.Bar(
            name=name,
            x=ids,
            y=vals,
            marker_color=color,
            marker_line=dict(width=0),
            opacity=0.88,
        ))

    _apply_base(fig, "Score Comparison by Candidate", height=400)
    fig.update_layout(barmode="group", bargap=0.18, bargroupgap=0.05)
    fig.update_xaxes(title_text="Compound ID")
    fig.update_yaxes(title_text="Score (0–1)", range=[0, 1.05])
    return fig


# ---------------------------------------------------------------------------
# 3. Score waterfall (weighted components → final_score for one candidate)
# ---------------------------------------------------------------------------

def score_waterfall(candidate: FrontendCandidate, weights: dict) -> go.Figure:
    """Waterfall chart showing weighted score contribution to final_score."""
    aw = weights.get("activity_weight",  0.40)
    dw = weights.get("docking_weight",   0.30)
    pw = weights.get("property_weight",  0.20)
    nw = weights.get("novelty_weight",   0.10)

    labels = [
        f"Activity ({aw:.0%})",
        f"Docking ({dw:.0%})",
        f"Property ({pw:.0%})",
        f"Novelty ({nw:.0%})",
        "Final Score",
    ]
    contributions = [
        aw * candidate.activity_norm,
        dw * candidate.docking_norm,
        pw * candidate.property_score,
        nw * candidate.novelty_score,
    ]
    values   = contributions + [sum(contributions)]
    measures = ["relative"] * 4 + ["total"]

    fig = go.Figure(go.Waterfall(
        orientation = "v",
        measure     = measures,
        x           = labels,
        y           = values,
        text        = [f"{v:.3f}" for v in values],
        textposition = "outside",
        connector   = dict(line=dict(color=COLORS["border"], width=1)),
        increasing  = dict(marker_color=COLORS["teal"]),
        decreasing  = dict(marker_color=COLORS["muted"]),
        totals      = dict(marker_color=COLORS["navy"]),
    ))
    _apply_base(fig, f"Score Breakdown — {candidate.candidate_id}", height=380)
    fig.update_yaxes(title_text="Score contribution")
    return fig


# ---------------------------------------------------------------------------
# 4. Docking score horizontal bar chart
# ---------------------------------------------------------------------------

def docking_score_bar(candidates: list[FrontendCandidate]) -> go.Figure:
    """Horizontal bar: docking score per compound (lower = better)."""
    if not candidates:
        return _empty_chart("No docking data available")

    sorted_cands = sorted(
        candidates,
        key=lambda c: c.docking.score_raw or 0.0,
    )  # most negative first = best
    ids    = [c.candidate_id            for c in sorted_cands]
    scores = [c.docking.score_raw or 0.0 for c in sorted_cands]
    colors = [
        COLORS["teal"] if s == min(scores) else COLORS["blue"]
        for s in scores
    ]

    fig = go.Figure(go.Bar(
        x            = scores,
        y            = ids,
        orientation  = "h",
        marker_color = colors,
        marker_line  = dict(width=0),
        text         = [f"{s:.3f}" for s in scores],
        textposition = "outside",
        hovertemplate = "<b>%{y}</b><br>Docking score: %{x:.3f} kcal/mol<extra></extra>",
    ))
    _apply_base(fig, "Docking Score by Compound (lower = stronger binding)", height=320)
    fig.update_xaxes(title_text="Docking Score (kcal/mol)")
    fig.update_yaxes(title_text="")
    fig.add_annotation(
        text="⚠ FALLBACK_DEMO values — not real docking simulation",
        xref="paper", yref="paper", x=0, y=1.06,
        showarrow=False,
        font=dict(size=10, color=COLORS["demo_text"]),
    )
    return fig


# ---------------------------------------------------------------------------
# 5. Property radar chart
# ---------------------------------------------------------------------------

def property_radar(
    candidate: FrontendCandidate,
    limits: dict,
    title: Optional[str] = None,
) -> go.Figure:
    """Spider/radar: descriptor values as fraction of Lipinski limit."""
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
    # Clamp normalised values to [0, 1.3] so chart remains readable
    cats   = list(lims.keys())
    vals   = [min(raw[c] / lims[c], 1.3) if lims[c] else 0 for c in cats]
    cats_r = cats + [cats[0]]
    vals_r = vals + [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r    = vals_r,
        theta= cats_r,
        fill = "toself",
        fillcolor = f"rgba(15,118,110,0.12)",
        line = dict(color=COLORS["teal"], width=2),
        name = candidate.candidate_id,
    ))
    # Limit boundary
    fig.add_trace(go.Scatterpolar(
        r    = [1.0] * (len(cats) + 1),
        theta= cats_r,
        mode = "lines",
        line = dict(color=COLORS["border"], width=1.5, dash="dot"),
        name = "Threshold",
    ))
    _apply_base(fig, title or f"Properties — {candidate.candidate_id}", height=350)
    fig.update_layout(
        polar = dict(
            bgcolor    = CHART_BGCOLOR,
            radialaxis = dict(
                visible    = True,
                range      = [0, 1.3],
                tickvals   = [0, 0.5, 1.0],
                ticktext   = ["0%", "50%", "100%"],
                tickfont   = dict(size=9, color=COLORS["muted"]),
                gridcolor  = "#EFF2F7",
            ),
            angularaxis = dict(gridcolor="#EFF2F7"),
        ),
        showlegend = True,
    )
    return fig


# ---------------------------------------------------------------------------
# 6. Filter funnel
# ---------------------------------------------------------------------------

def filter_funnel(total: int, passed: int, rejected: int) -> go.Figure:
    """Funnel chart showing compound counts through filter stages."""
    fig = go.Figure(go.Funnel(
        y          = ["Loaded", "Validated", "Filter PASS", "Docked"],
        x          = [total,    total,       passed,        min(passed, 5)],
        textinfo   = "value+percent initial",
        marker     = dict(color=[
            COLORS["navy"], COLORS["blue"], COLORS["teal"], COLORS["cyan"]
        ]),
        connector  = dict(line=dict(width=2, color=COLORS["border"])),
    ))
    _apply_base(fig, "Compound Funnel", height=320)
    return fig


# ---------------------------------------------------------------------------
# 7. Validation bar chart
# ---------------------------------------------------------------------------

def validation_bar(valid_n: int, rejected_n: int) -> go.Figure:
    """Simple bar: valid vs rejected compound counts."""
    fig = go.Figure(go.Bar(
        x            = ["Valid", "Rejected"],
        y            = [valid_n, rejected_n],
        marker_color  = [COLORS["teal"], COLORS["reject_text"]],
        text         = [valid_n, rejected_n],
        textposition = "outside",
        width        = 0.4,
    ))
    _apply_base(fig, "Validation Results", height=300)
    fig.update_yaxes(title_text="Count", rangemode="tozero")
    return fig


# ---------------------------------------------------------------------------
# 8. Activity score distribution histogram
# ---------------------------------------------------------------------------

def score_distribution_histogram(df: pd.DataFrame, col: str = "activity_score") -> go.Figure:
    """Histogram of activity scores across all compounds."""
    if df is None or df.empty or col not in df.columns:
        return _empty_chart("No score data available")

    fig = px.histogram(
        df, x=col, nbins=12,
        color_discrete_sequence=[COLORS["teal"]],
        template=CHART_TEMPLATE,
        labels={col: "Activity Score (demo)"},
        opacity=0.82,
    )
    _apply_base(fig, "Activity Score Distribution", height=320)
    fig.update_xaxes(title_text="Activity Score")
    fig.update_yaxes(title_text="Count")
    fig.add_annotation(
        text="⚠ Deterministic demo values",
        xref="paper", yref="paper", x=1, y=1.06,
        showarrow=False, xanchor="right",
        font=dict(size=10, color=COLORS["demo_text"]),
    )
    return fig


# ---------------------------------------------------------------------------
# 9. What-if comparison chart
# ---------------------------------------------------------------------------

def whatif_comparison_chart(
    candidates: list[FrontendCandidate],
    whatif_candidates: list[FrontendCandidate],
) -> go.Figure:
    """Side-by-side bar: official final_score vs what-if score per compound."""
    if not candidates or not whatif_candidates:
        return _empty_chart("No data for comparison")

    ids      = [c.candidate_id for c in candidates]
    official = [c.final_score  for c in candidates]
    whatif_map = {c.candidate_id: c.whatif_score or 0.0 for c in whatif_candidates}
    whatif   = [whatif_map.get(cid, 0.0) for cid in ids]

    fig = go.Figure([
        go.Bar(
            name         = "Official Score (backend)",
            x            = ids,
            y            = official,
            marker_color = COLORS["navy"],
            opacity      = 0.85,
            marker_line  = dict(width=0),
        ),
        go.Bar(
            name         = "What-If Score (frontend analysis)",
            x            = ids,
            y            = whatif,
            marker_color = COLORS["teal"],
            opacity      = 0.72,
            marker_line  = dict(width=0),
        ),
    ])
    _apply_base(fig, "Official vs What-If Ranking Comparison", height=380)
    fig.update_layout(barmode="group", bargap=0.18)
    fig.update_xaxes(title_text="Compound ID")
    fig.update_yaxes(title_text="Score (0–1)", range=[0, 1.05])
    return fig


# ---------------------------------------------------------------------------
# 10. Property filter heatmap
# ---------------------------------------------------------------------------

def filter_heatmap(filtered_df: pd.DataFrame, ui_config: dict) -> go.Figure:
    """Heatmap: compound × property pass/fail matrix (1=PASS, 0=FAIL)."""
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
        f"Compound {i+1}" for i in range(len(filtered_df))
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

    colorscale = [[0, COLORS["reject_bg"]], [1, COLORS["pass_bg"]]]
    fig = go.Figure(go.Heatmap(
        z           = matrix,
        x           = ids,
        y           = props_used,
        colorscale  = colorscale,
        showscale   = False,
        text        = [["✓" if v else "✗" for v in row] for row in matrix],
        texttemplate= "%{text}",
        textfont    = dict(size=14),
        hovertemplate = "%{y}: %{z}<extra></extra>",
    ))
    _apply_base(fig, "Property Filter Pass/Fail Matrix", height=280)
    fig.update_yaxes(title_text="")
    fig.update_xaxes(title_text="Compound ID")
    return fig


# ---------------------------------------------------------------------------
# 11. Ranking weights pie chart
# ---------------------------------------------------------------------------

def weights_pie(weights: dict) -> go.Figure:
    """Pie chart of ranking weight distribution."""
    labels = ["Activity", "Docking", "Property", "Novelty"]
    values = [
        weights.get("activity_weight",  0.40),
        weights.get("docking_weight",   0.30),
        weights.get("property_weight",  0.20),
        weights.get("novelty_weight",   0.10),
    ]
    fig = go.Figure(go.Pie(
        labels       = labels,
        values       = values,
        marker       = dict(colors=CHART_COLORS[:4],
                           line=dict(color="#FFFFFF", width=2)),
        textinfo     = "label+percent",
        textfont     = dict(size=11, color=COLORS["text"]),
        hovertemplate= "%{label}: %{value:.0%}<extra></extra>",
        hole         = 0.35,
    ))
    _apply_base(fig, "Ranking Weight Distribution", height=300)
    return fig


# ---------------------------------------------------------------------------
# Helper: empty placeholder chart
# ---------------------------------------------------------------------------

def _empty_chart(message: str = "No data") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color=COLORS["muted"]),
    )
    _apply_base(fig, height=300)
    return fig
