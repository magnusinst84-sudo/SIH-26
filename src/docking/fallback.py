import hashlib
import pandas as pd


def fallback_docking(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()

    def score(compound_id: str) -> float:
        digest = hashlib.sha256(compound_id.encode()).hexdigest()
        return round(-7.2 - int(digest[:8], 16) / 0xFFFFFFFF * 1.2, 3)

    output["docking_score"] = output["compound_id"].map(score)
    output["docking_status"] = "FALLBACK_DEMO"
    output["is_fallback"] = True
    return output
