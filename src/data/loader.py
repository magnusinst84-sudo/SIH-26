from pathlib import Path
import pandas as pd


def load_compounds(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Compound file not found: {path}")
    frame = pd.read_csv(path)
    required = {"compound_id", "smiles"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return frame
