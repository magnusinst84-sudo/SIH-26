from pathlib import Path
from src.pipeline.run_demo import run_demo


def test_demo_pipeline_creates_ranking():
    root = Path(__file__).resolve().parents[1]
    result = run_demo(root)
    assert not result.empty
    assert {"rank", "compound_id", "final_score"}.issubset(result.columns)
    assert result["rank"].min() == 1
