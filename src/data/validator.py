import pandas as pd

try:
    from rdkit import Chem
except ImportError:
    Chem = None


def validate_compounds(frame: pd.DataFrame):
    valid_rows, rejected_rows, seen = [], [], set()
    for record in frame.to_dict(orient="records"):
        smiles = str(record.get("smiles", "")).strip()
        canonical = smiles
        valid = bool(smiles)
        reason = None
        if Chem is not None and valid:
            molecule = Chem.MolFromSmiles(smiles)
            valid = molecule is not None
            if valid:
                canonical = Chem.MolToSmiles(molecule)
        if not valid:
            reason = "invalid_smiles"
        elif canonical in seen:
            valid = False
            reason = "duplicate_structure"
        if valid:
            seen.add(canonical)
            record["canonical_smiles"] = canonical
            valid_rows.append(record)
        else:
            record["rejection_reason"] = reason
            rejected_rows.append(record)
    return pd.DataFrame(valid_rows), pd.DataFrame(rejected_rows)
