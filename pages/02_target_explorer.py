"""
pages/02_target_explorer.py
---------------------------
TargetForge — Target Explorer

Compact Scientific Target Analysis Workspace:
1. Disease & Molecular Target selection
2. Target Summary card & biological profile
3. Catalytic binding pocket metrics & subsite details
4. Validation evidence & literature citations
5. Centered 3D protein structure preview (PDB: 6LU7) with interactive controls

Owned by: M4 (Frontend/UI Lead)
"""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import streamlit.components.v1 as components

from src.ui.state import init_session_state, WorkflowStep
from src.ui.theme import inject_global_css, badge_html, COLORS
from src.ui.components import (
    render_top_navbar,
    render_horizontal_stepper,
    render_scientific_disclaimer,
    render_demo_banner,
    render_scientific_metric,
)

inject_global_css()
init_session_state(_ROOT)
render_top_navbar()
render_horizontal_stepper(WorkflowStep.TARGET)
render_demo_banner()

# ─── Compact Page Header ─────────────────────────────────────────────────────
st.markdown(
    """<div style="margin-bottom: 8px;">
<h2 style="font-size: 20px; font-weight: 700; color: #F8FAFC; margin: 0 0 2px 0;">Target Explorer</h2>
<p style="font-size: 12px; color: #A1ABB3; margin: 0;">Biological target validation, binding pocket analysis, and structural receptor workspace.</p>
</div>""",
    unsafe_allow_html=True,
)

# ─── Retrieve State Data ─────────────────────────────────────────────────────
target  = st.session_state.get("tf_target", {})
weights = st.session_state.get("tf_weights", {})
filters = st.session_state.get("tf_filter_config", {})

# ─── Two-Column Compact Scientific Workspace ─────────────────────────────────
col_left, col_right = st.columns([1.1, 1.25], gap="medium")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN: Target Selection, Summary Card, Pocket, Evidence, CTA
# ══════════════════════════════════════════════════════════════════════════════
with col_left:
    
    # 1. Target Specification Selectors
    st.markdown("<h4 style='font-size: 13.5px; font-weight: 600; color: #F8FAFC; margin: 0 0 6px 0;'>Target Specification</h4>", unsafe_allow_html=True)
    
    disease_options = [
        "COVID-19 (Viral Infectious Disease)",
        "Oncology (Kinase Signaling Pathways)",
        "Inflammation & Autoimmune",
    ]
    selected_disease = st.selectbox(
        "Disease Indication",
        options=disease_options,
        index=0,
        label_visibility="visible",
        help="Select clinical indication for target prioritization.",
    )
    
    target_options = [
        "SARS-CoV-2 Main Protease (Mpro / 3CLpro, PDB: 6LU7)",
        "SARS-CoV-2 Papain-Like Protease (PLpro, PDB: 6W9C)",
        "Human TMPRSS2 Serine Protease (Homology Model)",
    ]
    selected_target = st.selectbox(
        "Molecular Target",
        options=target_options,
        index=0,
        label_visibility="visible",
        help="Select validated biological macromolecule receptor.",
    )
    
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)

    # 2. Compact Target Summary Card
    st.markdown("<h4 style='font-size: 13.5px; font-weight: 600; color: #F8FAFC; margin: 0 0 6px 0;'>Target Summary</h4>", unsafe_allow_html=True)
    
    summary_card_html = """<div class="tf-card" style="padding: 10px 14px; margin-bottom: 8px;">
<div style="display: grid; grid-template-columns: 1fr 1.3fr; gap: 4px 12px; font-size: 12px;">
<div style="color: #A1ABB3;">Gene Name</div><div style="color: #F8FAFC; font-weight: 600;">Mpro / nsp5</div>
<div style="color: #A1ABB3;">UniProt ID</div><div style="color: #00BFA6; font-weight: 600;">P0DTD1</div>
<div style="color: #A1ABB3;">Protein Class</div><div style="color: #F8FAFC; font-weight: 500;">Cysteine Protease</div>
<div style="color: #A1ABB3;">Organism</div><div style="color: #F8FAFC; font-weight: 500;">SARS-CoV-2</div>
<div style="color: #A1ABB3;">Druggability</div><div style="color: #10B981; font-weight: 600;">High (Class I Pocket)</div>
<div style="color: #A1ABB3;">Function</div><div style="color: #F8FAFC; font-weight: 500;">Cleaves viral pp1a / pp1ab</div>
<div style="color: #A1ABB3;">Structure Method</div><div style="color: #F8FAFC; font-weight: 500;">X-ray (2.16 Å Resolution)</div>
</div>
</div>"""
    st.markdown(summary_card_html, unsafe_allow_html=True)

    # 3. Catalytic Binding Pocket
    st.markdown("<h4 style='font-size: 13.5px; font-weight: 600; color: #F8FAFC; margin: 0 0 6px 0;'>Catalytic Binding Pocket</h4>", unsafe_allow_html=True)
    
    pocket_card_html = """<div class="tf-card" style="padding: 10px 14px; margin-bottom: 8px;">
<div style="display: flex; gap: 10px; margin-bottom: 8px;">
<div style="flex: 1; background: #161C24; border: 1px solid #232D38; border-radius: 6px; padding: 6px 10px;">
<div style="font-size: 10px; color: #A1ABB3; font-weight: 600; text-transform: uppercase;">Pocket Volume</div>
<div style="font-size: 15px; font-weight: 700; color: #F8FAFC;">342 Å³</div>
</div>
<div style="flex: 1; background: #161C24; border: 1px solid #232D38; border-radius: 6px; padding: 6px 10px;">
<div style="font-size: 10px; color: #A1ABB3; font-weight: 600; text-transform: uppercase;">Druggability Index</div>
<div style="font-size: 15px; font-weight: 700; color: #00BFA6;">0.84</div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 4px 10px; font-size: 11.5px;">
<div style="color: #A1ABB3;">Catalytic Dyad</div><div style="color: #F59E0B; font-weight: 600;">His41, Cys145</div>
<div style="color: #A1ABB3;">S1 Subsite</div><div style="color: #F8FAFC;">Phe140, Leu141, Asn142, His163</div>
<div style="color: #A1ABB3;">S2 Subsite</div><div style="color: #F8FAFC;">Met49, Tyr54, Met165, Asp187</div>
<div style="color: #A1ABB3;">S4 Subsite</div><div style="color: #F8FAFC;">Leu167, Pro168, Thr190, Gln192</div>
</div>
</div>"""
    st.markdown(pocket_card_html, unsafe_allow_html=True)

    # 4. Validation Evidence & Literature
    st.markdown("<h4 style='font-size: 13.5px; font-weight: 600; color: #F8FAFC; margin: 0 0 6px 0;'>Validation Evidence & Literature</h4>", unsafe_allow_html=True)
    
    literature_html = """<div class="tf-card" style="padding: 10px 14px; margin-bottom: 12px;">
<div style="padding: 4px 0; border-bottom: 1px solid #232D38;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:12px; font-weight:600; color:#F8FAFC;"><span style="color:#00BFA6;">▪</span> Structure of Mpro from SARS-CoV-2 and inhibitor discovery</span>
<span class="tf-badge tf-badge-pass">PDB: 6LU7</span>
</div>
<div style="font-size:11px; color:#A1ABB3; margin-left:10px;">Jin et al., Nature (2020) 582:289–293</div>
</div>
<div style="padding: 4px 0; margin-top: 4px;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:12px; font-weight:600; color:#F8FAFC;"><span style="color:#00BFA6;">▪</span> Crystal structure of main protease with α-ketoamide inhibitors</span>
<span class="tf-badge tf-badge-pass">PDB: 6Y2F</span>
</div>
<div style="font-size:11px; color:#A1ABB3; margin-left:10px;">Zhang et al., Science (2020) 368:409–412</div>
</div>
</div>"""
    st.markdown(literature_html, unsafe_allow_html=True)

    # 5. Primary Confirm Target CTA Button
    if st.button("Confirm Target & Continue →", type="primary", use_container_width=True):
        st.page_link("pages/03_dataset_manager.py", label="Proceed to Dataset Manager →", icon=":material/database:")
        st.success("Target profile confirmed and locked.")


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN: Centered 3D Protein Structure Workspace
# ══════════════════════════════════════════════════════════════════════════════
with col_right:
    st.markdown("<h4 style='font-size: 13.5px; font-weight: 600; color: #F8FAFC; margin: 0 0 6px 0;'>Protein Structure Workspace</h4>", unsafe_allow_html=True)
    
    pdb_id = target.get("structure_id", "6LU7")
    
    st.markdown(
        """<div class="tf-card" style="padding: 12px 14px 10px 14px; margin-bottom: 8px;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px; border-bottom: 1px solid #232D38; padding-bottom: 6px;">
<div>
<span style="font-size: 13.5px; font-weight: 700; color: #F8FAFC;">Protein Structure Preview</span>
<span style="font-size: 11.5px; color: #A1ABB3; margin-left: 8px;">PDB ID: <strong style="color: #00BFA6;">6LU7</strong></span>
</div>
<span class="tf-badge tf-badge-pass">X-ray 2.16 Å</span>
</div>""",
        unsafe_allow_html=True,
    )
    
    mol_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js"></script>
  <style>
    body {{ margin: 0; padding: 0; background-color: #080F14; overflow: hidden; font-family: 'Inter', sans-serif; }}
    #viewer-container {{ width: 100%; height: 380px; position: relative; border-radius: 6px; overflow: hidden; background: radial-gradient(circle at center, #11161D 0%, #080F14 100%); }}
    .controls-overlay {{
      position: absolute;
      bottom: 8px;
      left: 8px;
      right: 8px;
      display: flex;
      gap: 5px;
      z-index: 100;
      background: rgba(17, 22, 29, 0.90);
      backdrop-filter: blur(8px);
      border: 1px solid #232D38;
      padding: 4px 8px;
      border-radius: 6px;
    }}
    .btn-ctrl {{
      background: #161C24;
      border: 1px solid #232D38;
      color: #F8FAFC;
      padding: 3px 7px;
      font-size: 10.5px;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .btn-ctrl:hover {{
      background: #00BFA6;
      border-color: #00BFA6;
      color: #080F14;
    }}
    .legend-tag {{
      font-size: 10.5px;
      color: #A1ABB3;
      display: flex;
      align-items: center;
      gap: 3px;
      margin-left: auto;
    }}
    .legend-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      display: inline-block;
    }}
  </style>
</head>
<body>
  <div id="viewer-container">
    <div id="gldiv" style="width: 100%; height: 100%;"></div>
    <div class="controls-overlay">
      <button class="btn-ctrl" onclick="toggleSpin()">Spin</button>
      <button class="btn-ctrl" onclick="setRibbonStyle()">Ribbon</button>
      <button class="btn-ctrl" onclick="setSecondaryStructure()">Secondary Structure</button>
      <button class="btn-ctrl" onclick="setSurfaceStyle()">Surface</button>
      <button class="btn-ctrl" onclick="highlightBindingSite()">Catalytic Site</button>
      <button class="btn-ctrl" onclick="resetView()">Reset</button>
      <div class="legend-tag">
        <span class="legend-dot" style="background:#00BFA6;"></span> Ribbon
        <span class="legend-dot" style="background:#F59E0B; margin-left:4px;"></span> His41/Cys145
      </div>
    </div>
  </div>

  <script>
    let viewer = null;
    let isSpinning = false;
    let surf = null;

    function applyCartoonRibbon(v) {{
      v.setStyle({{hetflag: false}}, {{cartoon: {{color: '#00BFA6', thickness: 0.45, style: 'oval', opacity: 0.95}}}});
      // Highlight Catalytic Dyad in rich amber sticks
      v.addStyle({{resi: [41, 145]}}, {{stick: {{colorscheme: 'orangeCarbon', radius: 0.35}}, sphere: {{scale: 0.25, colorscheme: 'orangeCarbon'}}}});
      // Highlight bound inhibitor/ligand in yellow-green sticks
      v.addStyle({{hetflag: true}}, {{stick: {{colorscheme: 'greenCarbon', radius: 0.28}}}});
      v.addLabels([
        {{text: "His41", position: {{resi: 41}}, fontColor: "#F8FAFC", backgroundColor: "rgba(17,22,29,0.85)", fontSize: 10}},
        {{text: "Cys145", position: {{resi: 145}}, fontColor: "#F8FAFC", backgroundColor: "rgba(17,22,29,0.85)", fontSize: 10}}
      ]);
    }}

    document.addEventListener("DOMContentLoaded", function() {{
      let element = document.getElementById('gldiv');
      let config = {{ backgroundColor: '#080F14', antialias: true }};
      viewer = $3Dmol.createViewer(element, config);

      $3Dmol.download('pdb:{pdb_id}', viewer, {{multimodel: false, frames: false}}, function() {{
        applyCartoonRibbon(viewer);
        viewer.zoomTo();
        viewer.render();
      }});
    }});

    function toggleSpin() {{
      if (!viewer) return;
      isSpinning = !isSpinning;
      viewer.spin(isSpinning ? "y" : false);
    }}

    function setRibbonStyle() {{
      if (!viewer) return;
      if (surf) {{ viewer.removeSurface(surf); surf = null; }}
      applyCartoonRibbon(viewer);
      viewer.render();
    }}

    function setSecondaryStructure() {{
      if (!viewer) return;
      if (surf) {{ viewer.removeSurface(surf); surf = null; }}
      viewer.setStyle({{hetflag: false}}, {{cartoon: {{colorscheme: 'ssJmol', thickness: 0.45, opacity: 0.95}}}});
      viewer.addStyle({{resi: [41, 145]}}, {{stick: {{colorscheme: 'orangeCarbon', radius: 0.35}}}});
      viewer.addStyle({{hetflag: true}}, {{stick: {{colorscheme: 'greenCarbon', radius: 0.28}}}});
      viewer.render();
    }}

    function setSurfaceStyle() {{
      if (!viewer) return;
      if (surf) {{ viewer.removeSurface(surf); surf = null; }}
      viewer.setStyle({{hetflag: false}}, {{cartoon: {{color: '#00BFA6', opacity: 0.3}}}});
      surf = viewer.addSurface($3Dmol.SurfaceType.MS, {{opacity: 0.65, color: '#161C24'}});
      viewer.render();
    }}

    function highlightBindingSite() {{
      if (!viewer) return;
      viewer.zoomTo({{resi: [41, 49, 140, 141, 142, 143, 145, 163, 165, 166, 187, 189]}});
      viewer.render();
    }}

    function resetView() {{
      if (!viewer) return;
      if (isSpinning) {{ viewer.spin(false); isSpinning = false; }}
      if (surf) {{ viewer.removeSurface(surf); surf = null; }}
      applyCartoonRibbon(viewer);
      viewer.zoomTo();
      viewer.render();
    }}
  </script>
</body>
</html>
"""
    components.html(mol_html, height=386)
    
    st.markdown(
        """<div style="font-size:11px; color:#A1ABB3; margin-top:6px; line-height:1.4;">
<strong>Structure Notes:</strong> SARS-CoV-2 Mpro catalytic dyad (His41/Cys145) highlighted in amber. Drag to rotate, scroll to zoom.
</div>
</div>""",
        unsafe_allow_html=True,
    )
    
    # Compact scoring configuration expander
    with st.expander("Multi-Objective Scoring Weights & Thresholds", expanded=False):
        from src.ui.charts import weights_bar
        st.plotly_chart(weights_bar(weights), use_container_width=True)
        
        c_w1, c_w2, c_w3, c_w4 = st.columns(4)
        with c_w1:
            render_scientific_metric("Activity", f"{weights.get('activity_weight', 0.40):.0%}", "Bioactivity")
        with c_w2:
            render_scientific_metric("Docking", f"{weights.get('docking_weight', 0.30):.0%}", "Binding energy")
        with c_w3:
            render_scientific_metric("Property", f"{weights.get('property_weight', 0.20):.0%}", "Lipinski")
        with c_w4:
            render_scientific_metric("Novelty", f"{weights.get('novelty_weight', 0.10):.0%}", "Scaffold")

render_scientific_disclaimer()
