from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from rdkit import Chem
from rdkit.Chem import Draw

from analyzer import REGIONS, detect_peaks, rank_candidates, read_spectrum
from pubchem_client import fetch_formula_candidates


ROOT = Path(__file__).parent
st.set_page_config(page_title="NMR Structure Finder", page_icon="⚗️", layout="wide")


@st.cache_data(ttl=86400, show_spinner=False)
def cached_pubchem_candidates(formula, limit):
    return fetch_formula_candidates(formula, max_records=limit)
st.title("NMR Structure Finder")
st.caption("¹H NMRスペクトルと分子式から、登録化合物の候補構造を探索するプロトタイプ")

with st.sidebar:
    st.header("解析条件")
    formula = st.text_input("分子式", value="C4H8O2", help="例: C8H10O")
    uploaded = st.file_uploader("スペクトル", type=["csv", "jdx", "dx", "jcamp"])
    prominence = st.slider("ピーク検出感度", 0.01, 0.30, 0.08, 0.01, help="小さくすると弱いピークも拾います")
    distance = st.slider("ピーク間の最小距離", 2, 50, 8)
    use_pubchem = st.checkbox("PubChemから候補を追加", value=True)
    pubchem_limit = st.select_slider("PubChem候補数", options=[20, 40, 60, 80, 100], value=80, disabled=not use_pubchem)
    analyze = st.button("候補構造を解析", type="primary", use_container_width=True)
    st.divider()
    st.markdown("**試し方**\n\n`sample` フォルダのCSVを選び、対応する分子式を入力して解析します。")
    with st.expander("サンプル10種類の分子式"):
        sample_manifest = pd.read_csv(ROOT / "sample" / "samples.csv")
        for sample in sample_manifest.itertuples():
            st.code(f"{sample.file}\n→ {sample.formula}", language=None)

st.warning("研究支援用の候補提案です。構造を確定するものではありません。溶媒・基準物質・不純物ピークにも注意してください。", icon="⚠️")

if not uploaded:
    st.info("左側からCSVまたはJCAMP-DXファイルをアップロードしてください。")
    st.subheader("入力CSVの例")
    st.code("ppm,intensity\n12.0,0.002\n11.99,0.001\n...", language="csv")
    st.stop()

if analyze:
    try:
        spectrum = read_spectrum(uploaded)
        processed, peaks = detect_peaks(spectrum, prominence, distance)
        library = pd.read_csv(ROOT / "data" / "compounds.csv")
        library["source"] = "Local"
        pubchem_message = None
        if use_pubchem:
            try:
                with st.spinner("PubChemから候補構造を取得しています…"):
                    online = cached_pubchem_candidates(formula, pubchem_limit)
                if not online.empty:
                    library = pd.concat([library, online], ignore_index=True).drop_duplicates("smiles")
            except Exception as error:
                pubchem_message = f"PubChemに接続できなかったため、ローカル候補のみで解析しました（{error}）。"
        candidates = rank_candidates(formula, peaks, library)
    except Exception as exc:
        st.error(f"解析できませんでした: {exc}")
        st.stop()

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("データ点", f"{len(spectrum):,}")
    metric2.metric("検出ピーク", len(peaks))
    metric3.metric("構造候補", len(candidates))
    if pubchem_message:
        st.info(pubchem_message)

    figure = go.Figure()
    figure.add_trace(go.Scatter(x=processed["ppm"], y=processed["corrected"], mode="lines", name="補正後", line=dict(color="#1d3557", width=1.5)))
    figure.add_trace(go.Scatter(x=peaks["ppm"], y=peaks["relative_intensity"], mode="markers", name="検出ピーク", marker=dict(color="#e63946", size=8)))
    figure.update_layout(title="補正済み ¹H NMRスペクトル", xaxis_title="δ / ppm", yaxis_title="相対強度", height=420, margin=dict(l=20, r=20, t=55, b=20))
    figure.update_xaxes(autorange="reversed")
    st.plotly_chart(figure, use_container_width=True)

    with st.expander("検出ピーク一覧"):
        st.dataframe(peaks.round(3), use_container_width=True, hide_index=True)

    st.header("候補構造")
    if candidates.empty:
        st.error("この分子式に一致する化合物が候補ライブラリにありません。`data/compounds.csv` に候補を追加してください。")
    else:
        for rank, compound in candidates.head(8).iterrows():
            with st.container(border=True):
                image_col, detail_col = st.columns([1, 2])
                molecule = Chem.MolFromSmiles(compound["smiles"])
                image_col.image(Draw.MolToImage(molecule, size=(360, 240)), caption=compound["smiles"])
                detail_col.subheader(f"#{rank + 1} {compound['name_ja']} / {compound['name']}")
                detail_col.caption(f"候補ソース: {compound.get('source', 'Local')}")
                detail_col.progress(compound["score"] / 100, text=f"整合スコア {compound['score']:.0f} / 100")
                matched = "、".join(REGIONS[key][2] for key in compound["matched"]) or "なし"
                missing = "、".join(REGIONS[key][2] for key in compound["missing"]) or "なし"
                detail_col.write(f"**一致した領域:** {matched}")
                detail_col.write(f"**未検出の期待領域:** {missing}")
                detail_col.caption(compound["note"])
