from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.pipeline.run_demo import run_demo

result = run_demo(ROOT)
print(result[["rank", "compound_id", "activity_score", "docking_score", "final_score"]].to_string(index=False))
