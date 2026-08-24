"""Generate deterministic demo 1H NMR spectra for the Streamlit app.

These spectra are educational simulations, not measured reference spectra.
"""
from pathlib import Path

import numpy as np
import pandas as pd


SAMPLES = {
    "ethyl_acetate": {
        "name": "Ethyl acetate", "formula": "C4H8O2",
        "peaks": [(1.25, 1.0), (1.31, .55), (1.19, .55), (2.05, .9),
                  (4.12, .75), (4.06, .25), (4.18, .25)],
    },
    "acetone": {
        "name": "Acetone", "formula": "C3H6O", "peaks": [(2.17, 1.0)],
    },
    "propanal": {
        "name": "Propanal", "formula": "C3H6O",
        "peaks": [(1.05, .8), (1.11, .4), (.99, .4), (2.45, .65),
                  (2.38, .25), (2.52, .25), (9.75, .3)],
    },
    "allyl_alcohol": {
        "name": "Allyl alcohol", "formula": "C3H6O",
        "peaks": [(4.15, .65), (5.22, .42), (5.34, .42), (5.92, .58)],
    },
    "ethanol": {
        "name": "Ethanol", "formula": "C2H6O",
        "peaks": [(1.18, 1.0), (1.24, .52), (1.12, .52), (3.65, .72),
                  (3.59, .25), (3.71, .25)],
    },
    "benzene": {
        "name": "Benzene", "formula": "C6H6", "peaks": [(7.26, 1.0)],
    },
    "toluene": {
        "name": "Toluene", "formula": "C7H8",
        "peaks": [(2.34, .75), (7.12, .36), (7.20, .48), (7.28, .32)],
    },
    "ethylbenzene": {
        "name": "Ethylbenzene", "formula": "C8H10",
        "peaks": [(1.22, .8), (1.28, .4), (1.16, .4), (2.65, .55),
                  (2.58, .2), (2.72, .2), (7.18, .35), (7.27, .5)],
    },
    "anisole": {
        "name": "Anisole", "formula": "C7H8O",
        "peaks": [(3.79, .75), (6.90, .38), (6.98, .32), (7.25, .5)],
    },
    "benzaldehyde": {
        "name": "Benzaldehyde", "formula": "C7H6O",
        "peaks": [(7.48, .34), (7.62, .4), (7.88, .5), (10.02, .28)],
    },
}


def generate(peaks, seed):
    ppm = np.linspace(0, 12, 2401)
    rng = np.random.default_rng(seed)
    intensity = 0.002 + rng.normal(0, 0.00035, ppm.size)
    for center, height in peaks:
        width = 0.018 if center < 8.8 else 0.025
        intensity += height * np.exp(-0.5 * ((ppm - center) / width) ** 2)
    return pd.DataFrame({"ppm": ppm.round(3), "intensity": intensity.round(6)})


def main():
    directory = Path(__file__).parent / "sample"
    directory.mkdir(exist_ok=True)
    manifest = []
    for seed, (slug, spec) in enumerate(SAMPLES.items(), start=1):
        filename = f"{slug}.csv"
        generate(spec["peaks"], seed).to_csv(directory / filename, index=False)
        manifest.append({"file": filename, "compound": spec["name"], "formula": spec["formula"]})
    pd.DataFrame(manifest).to_csv(directory / "samples.csv", index=False)
    print(f"Generated {len(manifest)} sample spectra in {directory}")


if __name__ == "__main__":
    main()
