from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.pipeline.run_demo import run_demo

st.set_page_config(page_title="TargetForge", page_icon="🧬", layout="wide")
st.title("TargetForge")
st.caption("AI-assisted target-specific virtual screening")
st.info("Demo: COVID-19 → SARS-CoV-2 Mpro/3CLpro. Results are computational hypotheses and require laboratory validation.")

with st.sidebar:
    st.header("Workflow")
    st.write("1. Select target")
    st.write("2. Validate compounds")
    st.write("3. Predict activity")
    st.write("4. Filter candidates")
    st.write("5. Dock top candidates")
    st.write("6. Rank results")
    run = st.button("Run demo screening", type="primary")

if run:
    with st.spinner("Running TargetForge demonstration pipeline..."):
        results = run_demo(ROOT)
    st.success("Screening complete")
else:
    path = ROOT / "results" / "final_ranking.csv"
    results = pd.read_csv(path) if path.exists() else None

if results is not None and not results.empty:
    first = results.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Candidates ranked", len(results))
    c2.metric("Top candidate", first["compound_id"])
    c3.metric("Activity score", f"{first['activity_score']:.3f}")
    c4.metric("Final score", f"{first['final_score']:.3f}")
    st.subheader("Final candidate ranking")
    columns = ["rank", "compound_id", "activity_score", "docking_score", "property_score", "final_score", "status"]
    st.dataframe(results[[c for c in columns if c in results.columns]], use_container_width=True, hide_index=True)
    st.subheader("Score comparison")
    chart_cols = [c for c in ["activity_score", "property_score", "final_score"] if c in results.columns]
    st.bar_chart(results.set_index("compound_id")[chart_cols])
    st.download_button("Download ranking CSV", results.to_csv(index=False), "targetforge_ranking.csv", "text/csv")
else:
    st.warning("Run the demonstration pipeline or execute scripts/prepare_demo.py first.")

st.divider()
st.caption("TargetForge is a hackathon prototype. It does not establish safety, efficacy, or clinical approval.")
