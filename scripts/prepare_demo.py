from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "samples" / "demo_compounds.csv"
path.parent.mkdir(parents=True, exist_ok=True)
smiles = [
    "CCO", "CCN", "CCOC", "CC(C)O", "CCC", "c1ccccc1", "Cc1ccccc1",
    "CC(=O)OC1=CC=CC=C1", "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "CCN(CC)CCOC1=CC=CC=C1",
]
rows = [{"compound_id": f"CMP-{i:03d}", "smiles": value, "activity_label": "demo"}
        for i, value in enumerate(smiles, 1)]
with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
print(f"Created {path}")
