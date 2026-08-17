import pandas as pd


def minmax(series: pd.Series) -> pd.Series:
    low, high = series.min(), series.max()
    if high == low:
        return pd.Series(1.0, index=series.index)
    return (series - low) / (high - low)


def rank_candidates(frame: pd.DataFrame, weights: dict) -> pd.DataFrame:
    output = frame.copy()
    output["activity_norm"] = minmax(output["activity_score"])
    output["docking_norm"] = 1 - minmax(output["docking_score"])
    output["novelty_score"] = 0.5
    output["final_score"] = (
        weights["activity_weight"] * output["activity_norm"]
        + weights["docking_weight"] * output["docking_norm"]
        + weights["property_weight"] * output["property_score"]
        + weights["novelty_weight"] * output["novelty_score"]
    )
    output = output.sort_values("final_score", ascending=False).reset_index(drop=True)
    output["rank"] = output.index + 1
    output["status"] = "priority computational candidate"
    return output
