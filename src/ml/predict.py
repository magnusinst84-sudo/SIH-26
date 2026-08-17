import hashlib
import pandas as pd


def demo_predict(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()

    def score(compound_id: str) -> float:
        digest = hashlib.sha256(compound_id.encode()).hexdigest()
        return round(0.60 + int(digest[:8], 16) / 0xFFFFFFFF * 0.38, 4)

    output["activity_score"] = output["compound_id"].map(score)
    output["predicted_class"] = output["activity_score"].ge(0.75).map(
        {True: "active", False: "lower_priority"}
    )
    output["model_version"] = "demo_v1"
    return output.sort_values("activity_score", ascending=False).reset_index(drop=True)
