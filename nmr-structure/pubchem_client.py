"""Small PubChem PUG REST client and structure-based NMR region estimator."""
from urllib.parse import quote

import pandas as pd
import requests
from rdkit import Chem


BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

PATTERNS = {
    "aldehyde": Chem.MolFromSmarts("[CX3H1](=O)[#6,#1]"),
    "acid": Chem.MolFromSmarts("[CX3](=O)[OX2H1]"),
    "alkene": Chem.MolFromSmarts("[CX3H1,CX3H2]=[CX3H1,CX3H2]"),
    "aromatic": Chem.MolFromSmarts("[cH]"),
}


def infer_regions(smiles):
    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        return set()
    regions = {name for name, pattern in PATTERNS.items() if molecule.HasSubstructMatch(pattern)}
    for atom in molecule.GetAtoms():
        hydrogens = atom.GetTotalNumHs()
        if hydrogens == 0:
            continue
        if atom.GetSymbol() == "C" and atom.GetHybridization() == Chem.HybridizationType.SP3:
            regions.add("alkyl")
            if any(neighbor.GetSymbol() in {"O", "N", "S", "F", "Cl", "Br", "I"} for neighbor in atom.GetNeighbors()):
                regions.add("hetero")
        if atom.GetSymbol() in {"O", "N", "S"}:
            regions.add("hetero")
    return regions


def fetch_formula_candidates(formula, max_records=80, timeout=15):
    safe_formula = quote(formula, safe="")
    cid_url = f"{BASE_URL}/compound/fastformula/{safe_formula}/cids/JSON"
    cid_response = requests.get(
        cid_url,
        params={"MaxRecords": min(max_records, 100), "MaxSeconds": 10},
        timeout=timeout,
        headers={"User-Agent": "NMR-Structure-Finder/0.2 (educational prototype)"},
    )
    if cid_response.status_code == 404:
        return pd.DataFrame()
    cid_response.raise_for_status()
    cids = cid_response.json().get("IdentifierList", {}).get("CID", [])[:max_records]
    if not cids:
        return pd.DataFrame()

    properties_url = (
        f"{BASE_URL}/compound/cid/{','.join(map(str, cids))}/property/"
        "MolecularFormula,ConnectivitySMILES,IUPACName,Title/JSON"
    )
    property_response = requests.get(
        properties_url,
        timeout=timeout,
        headers={"User-Agent": "NMR-Structure-Finder/0.2 (educational prototype)"},
    )
    property_response.raise_for_status()
    properties = property_response.json().get("PropertyTable", {}).get("Properties", [])

    rows = []
    for item in properties:
        smiles = item.get("ConnectivitySMILES")
        if not smiles or Chem.MolFromSmiles(smiles) is None:
            continue
        regions = infer_regions(smiles)
        rows.append({
            "name": item.get("Title") or item.get("IUPACName") or f"PubChem CID {item['CID']}",
            "name_ja": item.get("Title") or item.get("IUPACName") or f"PubChem CID {item['CID']}",
            "formula": item.get("MolecularFormula", formula),
            "smiles": smiles,
            "regions": "|".join(sorted(regions)),
            "note": f"PubChem CID {item['CID']}。官能基は構造から自動推定しています。",
            "source": "PubChem",
            "cid": item["CID"],
        })
    return pd.DataFrame(rows).drop_duplicates("smiles") if rows else pd.DataFrame()
