import pandas as pd

try:
    from rdkit import Chem
    from rdkit.Chem import Crippen, Descriptors, Lipinski
except ImportError:
    Chem = None


def calculate_descriptors(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    if Chem is None:
        for column in ["molecular_weight", "logp", "tpsa"]:
            output[column] = 0.0
        for column in ["hbd", "hba", "rotatable_bonds"]:
            output[column] = 0
        return output
    values = []
    for smiles in output["canonical_smiles"]:
        molecule = Chem.MolFromSmiles(smiles)
        values.append({
            "molecular_weight": Descriptors.MolWt(molecule),
            "logp": Crippen.MolLogP(molecule),
            "hbd": Lipinski.NumHDonors(molecule),
            "hba": Lipinski.NumHAcceptors(molecule),
            "tpsa": Descriptors.TPSA(molecule),
            "rotatable_bonds": Lipinski.NumRotatableBonds(molecule),
        })
    return pd.concat([output.reset_index(drop=True), pd.DataFrame(values)], axis=1)
