import pandas as pd


def apply_filters(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    output = frame.copy()
    passed = (
        output["molecular_weight"].le(config["max_molecular_weight"])
        & output["logp"].le(config["max_logp"])
        & output["hbd"].le(config["max_hbd"])
        & output["hba"].le(config["max_hba"])
        & output["tpsa"].le(config["max_tpsa"])
    )
    output["filter_status"] = passed.map({True: "PASS", False: "REJECTED"})
    output["property_score"] = passed.astype(float)
    return output
