import pandas as pd
from src.ranking.score import rank_candidates


def test_rank_candidates_orders_by_score():
    frame = pd.DataFrame({
        "compound_id": ["A", "B"],
        "activity_score": [0.9, 0.7],
        "docking_score": [-8.0, -7.0],
        "property_score": [1.0, 1.0],
    })
    result = rank_candidates(frame, {
        "activity_weight": 0.4,
        "docking_weight": 0.3,
        "property_weight": 0.2,
        "novelty_weight": 0.1,
    })
    assert result.iloc[0]["compound_id"] == "A"
