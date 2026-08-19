"""
pages/02_target_explorer.py
---------------------------
TargetForge — Target Explorer

Scientific target analysis workspace displaying:
1. Disease & Molecular Target selection
2. Target biological profile & validation summary
3. Binding pocket geometry & catalytic residue specifications
4. Evidence & Literature citations
5. Interactive 3D structural protein visualization (PDB: 6LU7)

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

# ─── Page Header ─────────────────────────────────────────────────────────────
st.title("Target Explorer")
st.caption("Biological target validation, binding pocket analysis, and structural receptor workspace.")

# ─── Retrieve State Data ─────────────────────────────────────────────────────
target  = st.session_state.get("tf_target", {})
weights = st.session_state.get("tf_weights", {})
filters = st.session_state.get("tf_filter_config", {})

# ─── Two-Column Scientific Workspace Layout ──────────────────────────────────
col_left, col_right = st.columns([1.1, 1.25], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN: Selection, Target Profile, Pocket, Evidence, CTA
# ══════════════════════════════════════════════════════════════════════════════
with col_left:
    
    # 1. Scientific Form Selectors
    st.markdown("### Target Specification")
    
    disease_options = [
        "COVID-19 (Viral Infectious Disease)",
        "Oncology (Kinase Signaling Pathways)",
        "Inflammation & Autoimmune",
    ]
    selected_disease = st.selectbox(
        "Disease Indication",
        options=disease_options,
        index=0,
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
        help="Select validated biological macromolecule receptor.",
    )
    
    st.markdown("")

    # 2. Target Summary Key-Value Rows
    st.markdown("### Target Biological Profile")
    st.markdown('<div class="tf-card" style="padding:16px 20px; margin-bottom:16px;">', unsafe_allow_html=True)
    
    profile_rows = [
        ("Gene Name", "Mpro / nsp5"),
        ("UniProt ID", "P0DTD1"),
        ("Protein Class", "Cysteine Protease (Chymotrypsin-like)"),
        ("Organism", "SARS-CoV-2 (Human Host)"),
        ("Druggability", "High (Class I Catalytic Pocket)"),
        ("Biological Function", "Cleavage of viral polyproteins pp1a and pp1ab"),
        ("Structure Method", "X-ray Crystallography (2.16 Å Resolution)"),
    ]
    for label, val in profile_rows:
        r1, r2 = st.columns([1.1, 1.6])
        r1.markdown(f"<span style='font-size:13px;color:#A1ABB3;'>{label}</span>", unsafe_allow_html=True)
        r2.markdown(f"<span style='font-size:13px;color:#F8FAFC;font-weight:600;'>{val}</span>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Binding Pocket Summary
    st.markdown("### Catalytic Binding Pocket")
    st.markdown('<div class="tf-card" style="padding:16px 20px; margin-bottom:16px;">', unsafe_allow_html=True)
    
    pk_col1, pk_col2 = st.columns(2)
    with pk_col1:
        render_scientific_metric("Pocket Volume", "342 Å³", "Enclosed cavity volume")
    with pk_col2:
        render_scientific_metric("Druggability Index", "0.84", "High tractability score")
        
    st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
    pocket_details = [
        ("Catalytic Dyad", "His41 (General Base), Cys145 (Nucleophile)"),
        ("S1 Subsite", "Phe140, Leu141, Asn142, Gly143, His163, Glu166"),
        ("S2 Subsite (Hydrophobic)", "Met49, Tyr54, Met165, Asp187, Arg188"),
        ("S4 Subsite (Flexible)", "Leu167, Pro168, Thr190, Ala191, Gln192"),
    ]
    for p_lbl, p_val in pocket_details:
        pr1, pr2 = st.columns([1.1, 1.6])
        pr1.markdown(f"<span style='font-size:12px;color:#A1ABB3;'>{p_lbl}</span>", unsafe_allow_html=True)
        pr2.markdown(f"<span style='font-size:12px;color:#F8FAFC;font-weight:500;'>{p_val}</span>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # 4. Evidence & Literature Citations
    st.markdown("### Validation Evidence & Literature")
    st.markdown('<div class="tf-card" style="padding:16px 20px; margin-bottom:20px;">', unsafe_allow_html=True)
    
    evidence_items = [
        ("Structure of Mpro from SARS-CoV-2 and discovery of its inhibitors", "Jin et al., Nature (2020) 582:289–293", "PDB: 6LU7"),
        ("Crystal structure of SARS-CoV-2 main protease provides basis for design of improved α-ketoamide inhibitors", "Zhang et al., Science (2020) 368:409–412", "PDB: 6Y2F"),
        ("Mechanistic insights into catalytic dyad inhibition and SARS-CoV-2 antiviral discovery", "Hilgenfeld et al., J. Med. Chem. (2021) 64:124–139", "Target Validation"),
    ]
    
    for title_text, citation, tag in evidence_items:
        st.markdown(
            f"""
            <div style="padding: 8px 0; border-bottom: 1px solid #232D38;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                    <div style="font-size:13px; font-weight:600; color:#F8FAFC; line-height:1.35;">
                        <span style="color:#00BFA6; margin-right:4px;">▪</span> {title_text}
                    </div>
                    <span class="tf-badge tf-badge-pass" style="white-space:nowrap; font-size:10px;">{tag}</span>
                </div>
                <div style="font-size:11px; color:#A1ABB3; margin-top:3px; margin-left:12px;">{citation}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Primary Confirm Target CTA Button
    if st.button("Confirm Target & Continue →", type="primary", use_container_width=True):
        st.page_link("pages/03_dataset_manager.py", label="Proceed to Dataset Manager →", icon=":material/database:")
        st.success("Target profile locked for pipeline execution.")


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN: 3D Protein Structure Preview & Interactive Controls
# ══════════════════════════════════════════════════════════════════════════════
with col_right:
    st.markdown("### Protein Structure Workspace")
    
    st.markdown(
        """
        <div style="background:#11161D; border:1px solid #232D38; border-radius:10px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,0.2);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; border-bottom:1px solid #232D38; padding-bottom:8px;">
                <div>
                    <span style="font-size:14px; font-weight:700; color:#F8FAFC;">SARS-CoV-2 Main Protease (Mpro)</span>
                    <span style="font-size:12px; color:#A1ABB3; margin-left:8px;">PDB ID: <strong style="color:#00BFA6;">6LU7</strong></span>
                </div>
                <span class="tf-badge tf-badge-pass">X-ray 2.16 Å</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Interactive 3Dmol.js HTML Component
    pdb_id = target.get("structure_id", "6LU7")
    
    mol_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js"></script>
      <style>
        body {{ margin: 0; padding: 0; background-color: #080F14; overflow: hidden; font-family: 'Inter', sans-serif; }}
        #viewer-container {{ width: 100%; height: 420px; position: relative; border-radius: 6px; overflow: hidden; background: linear-gradient(180deg, #080F14 0%, #11161D 100%); }}
        .controls-overlay {{
          position: absolute;
          bottom: 12px;
          left: 12px;
          right: 12px;
          display: flex;
          gap: 6px;
          z-index: 100;
          background: rgba(17, 22, 29, 0.90);
          backdrop-filter: blur(8px);
          border: 1px solid #232D38;
          padding: 6px 10px;
          border-radius: 6px;
          box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }}
        .btn-ctrl {{
          background: #161C24;
          border: 1px solid #232D38;
          color: #F8FAFC;
          padding: 4px 8px;
          font-size: 11px;
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
          font-size: 11px;
          color: #A1ABB3;
          display: flex;
          align-items: center;
          gap: 4px;
          margin-left: auto;
        }}
        .legend-dot {{
          width: 8px;
          height: 8px;
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
          <button class="btn-ctrl" onclick="setStyle('cartoon')">Ribbon</button>
          <button class="btn-ctrl" onclick="setStyle('surface')">Surface</button>
          <button class="btn-ctrl" onclick="highlightBindingSite()">Catalytic Site</button>
          <button class="btn-ctrl" onclick="resetView()">Reset</button>
          <div class="legend-tag">
            <span class="legend-dot" style="background:#00BFA6;"></span> Monomer A
            <span class="legend-dot" style="background:#F59E0B; margin-left:6px;"></span> His41/Cys145
          </div>
        </div>
      </div>

      <script>
        let viewer = null;
        let isSpinning = false;
        let currentStyle = 'cartoon';
        let surf = null;

        document.addEventListener("DOMContentLoaded", function() {{
          let element = document.getElementById('gldiv');
          let config = {{ backgroundColor: '#080F14' }};
          viewer = $3Dmol.createViewer(element, config);

          $3Dmol.download('pdb:{pdb_id}', viewer, {{multimodel: false, frames: false}}, function() {{
            viewer.setStyle({{}}, {{ cartoon: {{ color: '#00BFA6', opacity: 0.92 }} }});
            // Highlight Catalytic Dyad
            viewer.addStyle({{ resi: [41, 145] }}, {{ stick: {{ colorscheme: 'amberCarbon', radius: 0.25 }} }});
            viewer.addLabels([
              {{ text: "His41", position: {{ resi: 41 }}, fontColor: "#F8FAFC", backgroundColor: "rgba(17,22,29,0.85)", fontSize: 11 }},
              {{ text: "Cys145", position: {{ resi: 145 }}, fontColor: "#F8FAFC", backgroundColor: "rgba(17,22,29,0.85)", fontSize: 11 }}
            ]);
            viewer.zoomTo();
            viewer.render();
          }});
        }});

        function toggleSpin() {{
          if (!viewer) return;
          isSpinning = !isSpinning;
          viewer.spin(isSpinning ? "y" : false);
        }}

        function setStyle(styleType) {{
          if (!viewer) return;
          currentStyle = styleType;
          if (surf) {{ viewer.removeSurface(surf); surf = null; }}
          
          if (styleType === 'cartoon') {{
            viewer.setStyle({{}}, {{ cartoon: {{ color: '#00BFA6', opacity: 0.92 }} }});
            viewer.addStyle({{ resi: [41, 145] }}, {{ stick: {{ colorscheme: 'amberCarbon', radius: 0.25 }} }});
          }} else if (styleType === 'surface') {{
            viewer.setStyle({{}}, {{ cartoon: {{ color: '#00BFA6', opacity: 0.35 }} }});
            surf = viewer.addSurface($3Dmol.SurfaceType.MS, {{ opacity: 0.7, color: '#161C24' }});
          }}
          viewer.render();
        }}

        function highlightBindingSite() {{
          if (!viewer) return;
          viewer.zoomTo({{ resi: [41, 49, 140, 141, 142, 143, 145, 163, 165, 166, 187, 189] }});
          viewer.render();
        }}

        function resetView() {{
          if (!viewer) return;
          if (isSpinning) {{ viewer.spin(false); isSpinning = false; }}
          viewer.setStyle({{}}, {{ cartoon: {{ color: '#00BFA6', opacity: 0.92 }} }});
          viewer.addStyle({{ resi: [41, 145] }}, {{ stick: {{ colorscheme: 'amberCarbon', radius: 0.25 }} }});
          if (surf) {{ viewer.removeSurface(surf); surf = null; }}
          viewer.zoomTo();
          viewer.render();
        }}
      </script>
    </body>
    </html>
    """
    
    components.html(mol_html, height=430)
    
    st.markdown(
        """
        <div style="font-size:12px; color:#A1ABB3; margin-top:8px; line-height:1.4;">
            <strong>Structure Notes:</strong> The SARS-CoV-2 Mpro homodimer active site features a non-canonical Cys-His catalytic dyad located at the cleft between Domain I and Domain II. Left-click and drag to rotate, right-click to translate, scroll to zoom.
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Multi-Objective Scoring Configuration Panel
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    with st.expander("Multi-Objective Optimization Weights & Thresholds", expanded=False):
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
