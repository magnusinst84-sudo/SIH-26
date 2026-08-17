from pathlib import Path
import pandas as pd
import yaml

from src.data.loader import load_compounds
from src.data.validator import validate_compounds
from src.chemistry.descriptors import calculate_descriptors
from src.ml.predict import demo_predict
from src.molecular_ai.filters import apply_filters
from src.docking.fallback import fallback_docking
from src.ranking.score import rank_candidates


def run_demo(root: str | Path = ".") -> pd.DataFrame:
    root = Path(root)
    with open(root / "configs/project.yaml", encoding="utf-8") as handle:
        project = yaml.safe_load(handle)
    with open(root / "configs/filters.yaml", encoding="utf-8") as handle:
        filters = yaml.safe_load(handle)
    frame = load_compounds(root / "data/samples/demo_compounds.csv")
    valid, rejected = validate_compounds(frame)
    valid = calculate_descriptors(valid)
    predicted = demo_predict(valid)
    filtered = apply_filters(predicted, filters)
    dockable = filtered[filtered["filter_status"] == "PASS"].head(5)
    docked = fallback_docking(dockable)
    ranked = rank_candidates(docked, project["ranking"])
    output_dir = root / "results"
    output_dir.mkdir(exist_ok=True)
    valid.to_csv(output_dir / "validated_molecules.csv", index=False)
    rejected.to_csv(output_dir / "rejected_molecules.csv", index=False)
    ranked.to_csv(output_dir / "final_ranking.csv", index=False)
    return ranked
