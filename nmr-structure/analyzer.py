import io
import re
import tempfile
from pathlib import Path

import nmrglue as ng
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.signal import find_peaks
from scipy.sparse.linalg import spsolve


REGIONS = {
    "alkyl": (0.5, 2.2, "アルキル領域"),
    "hetero": (2.2, 4.8, "ヘテロ原子隣接領域"),
    "alkene": (4.5, 6.7, "アルケン領域"),
    "aromatic": (6.5, 8.5, "芳香族領域"),
    "aldehyde": (9.0, 10.5, "アルデヒド領域"),
    "acid": (10.0, 13.5, "カルボン酸領域"),
}


def read_spectrum(uploaded) -> pd.DataFrame:
    suffix = Path(uploaded.name).suffix.lower()
    if suffix == ".csv":
        raw = uploaded.getvalue()
        try:
            frame = pd.read_csv(io.BytesIO(raw), sep=None, engine="python")
        except pd.errors.ParserError as error:
            raise ValueError(
                "CSVを2列として読み込めません。先頭行を ppm,intensity にしてください。"
            ) from error
        if frame.shape[1] < 2:
            raise ValueError("CSVには ppm と intensity の2列が必要です。")
        lowered = {str(c).lower().strip(): c for c in frame.columns}
        ppm_col = lowered.get("ppm", frame.columns[0])
        intensity_col = lowered.get("intensity", frame.columns[1])
        result = frame[[ppm_col, intensity_col]].copy()
        result.columns = ["ppm", "intensity"]
    elif suffix in {".jdx", ".dx", ".jcamp"}:
        with tempfile.NamedTemporaryFile(suffix=suffix) as handle:
            handle.write(uploaded.getvalue())
            handle.flush()
            dic, raw = ng.jcampdx.read(handle.name)
        intensity = np.asarray(raw[0] if isinstance(raw, list) else raw, dtype=float).squeeze()
        first = _number(dic, "FIRSTX", 12.0)
        last = _number(dic, "LASTX", 0.0)
        ppm = np.linspace(first, last, intensity.size)
        result = pd.DataFrame({"ppm": ppm, "intensity": intensity})
    else:
        raise ValueError("CSV、JDX、DXのいずれかを選択してください。")
    result = result.apply(pd.to_numeric, errors="coerce").dropna()
    if len(result) < 20:
        raise ValueError("解析には20点以上のスペクトルデータが必要です。")
    return result.sort_values("ppm").reset_index(drop=True)


def _number(dic, key, fallback):
    for candidate in (key, key.lower(), f"${key}"):
        if candidate in dic:
            value = dic[candidate]
            if isinstance(value, (list, tuple)):
                value = value[0]
            try:
                return float(value)
            except (TypeError, ValueError):
                pass
    return fallback


def baseline_als(y, lam=1e5, p=0.01, iterations=10):
    y = np.asarray(y, dtype=float)
    length = len(y)
    difference = sparse.diags(
        [1.0, -2.0, 1.0], [0, 1, 2], shape=(length - 2, length), format="csc"
    )
    weights = np.ones(length)
    for _ in range(iterations):
        matrix = sparse.spdiags(weights, 0, length, length) + lam * difference.T @ difference
        baseline = spsolve(matrix.tocsc(), weights * y)
        weights = p * (y > baseline) + (1 - p) * (y <= baseline)
    return baseline


def detect_peaks(frame, prominence=0.08, distance=8):
    y = frame["intensity"].to_numpy(dtype=float)
    corrected = y - baseline_als(y)
    scale = np.max(np.abs(corrected)) or 1.0
    corrected /= scale
    indices, props = find_peaks(corrected, prominence=prominence, distance=distance)
    peaks = pd.DataFrame({
        "ppm": frame["ppm"].to_numpy()[indices],
        "relative_intensity": corrected[indices],
        "prominence": props["prominences"],
    }).sort_values("ppm", ascending=False)
    plotted = frame.copy()
    plotted["corrected"] = corrected
    return plotted, peaks.reset_index(drop=True)


def canonical_formula(formula):
    tokens = re.findall(r"([A-Z][a-z]?)(\d*)", formula.replace(" ", ""))
    if not tokens or "".join(a + b for a, b in tokens) != formula.replace(" ", ""):
        raise ValueError("分子式を C8H10O のように入力してください。")
    counts = {element: int(number or 1) for element, number in tokens}
    order = ["C", "H"] + sorted(e for e in counts if e not in {"C", "H"})
    return "".join(e + (str(counts[e]) if counts[e] != 1 else "") for e in order if e in counts)


def observed_regions(peaks):
    values = peaks["ppm"].to_numpy()
    return {key for key, (low, high, _) in REGIONS.items() if np.any((values >= low) & (values <= high))}


def rank_candidates(formula, peaks, library):
    target = canonical_formula(formula)
    candidates = library[library["formula"].map(canonical_formula) == target].copy()
    if candidates.empty:
        return candidates
    observed = observed_regions(peaks)
    rows = []
    for _, compound in candidates.iterrows():
        expected = {x.strip() for x in str(compound["regions"]).split("|") if x.strip()}
        matched = observed & expected
        missing = expected - observed
        unexpected = observed - expected
        score = max(0.0, 100 - 18 * len(missing) - 8 * len(unexpected))
        rows.append({**compound.to_dict(), "score": score, "matched": matched, "missing": missing, "unexpected": unexpected})
    return pd.DataFrame(rows).sort_values(["score", "name"], ascending=[False, True]).reset_index(drop=True)
