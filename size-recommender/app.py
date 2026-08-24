import pandas as pd
import streamlit as st

from recommender import FIT_EASE, SIZES, fit_description, recommend_size


st.set_page_config(page_title="MY FIT — Tシャツサイズ提案", page_icon="👕", layout="wide")

st.markdown("""
<style>
    .block-container {max-width: 1050px; padding-top: 3rem;}
    .hero {padding: 2.5rem; border-radius: 1.5rem; background: #151513; color: white; margin-bottom: 2rem;}
    .hero small {letter-spacing: .18em; color: #ff6048;}
    .hero h1 {font-size: clamp(2.7rem, 7vw, 5rem); margin: .5rem 0; letter-spacing: -.06em;}
    .result {padding: 1.5rem; border-left: 6px solid #e33a25; background: #f2f0e9; margin: 1rem 0;}
    .result strong {font-size: 3rem;}
</style>
<div class="hero"><small>PERSONAL SIZE GUIDE</small><h1>MY FIT</h1><p>身体の寸法と好きな着用感から、ちょうどいいTシャツサイズを提案します。</p></div>
""", unsafe_allow_html=True)

input_col, guide_col = st.columns([1.2, 0.8], gap="large")

with input_col:
    st.subheader("身体情報を入力")
    height = st.number_input("身長（cm）", 130.0, 220.0, 170.0, 1.0)
    chest = st.number_input("胸囲（cm）", 60.0, 160.0, 90.0, 1.0, help="胸の一番高い位置を水平に一周して測ります")
    shoulder = st.number_input("肩幅（cm）", 30.0, 75.0, 44.0, 0.5, help="背中側で、左右の肩先を直線で測ります")
    fit = st.select_slider("好みの着用感", options=list(FIT_EASE), value="標準")
    submitted = st.button("おすすめサイズを見る", type="primary", use_container_width=True)

with guide_col:
    st.subheader("正しい測り方")
    st.markdown("""
1. 薄手の服か肌着の上から測る
2. メジャーを強く締めすぎない
3. 胸囲は床と平行に一周する
4. 肩幅は背中側の肩先から肩先まで

数値に迷った場合は、普段よく着るTシャツを平置きして比較するのがおすすめです。
""")

if submitted:
    try:
        ranking = recommend_size(height, chest, shoulder, fit)
    except ValueError as error:
        st.error(str(error))
        st.stop()

    best = ranking[0]
    second = ranking[1]
    st.divider()
    st.subheader("あなたへの提案")
    result_col, reason_col = st.columns([0.8, 1.2], gap="large")
    with result_col:
        st.markdown(f'<div class="result">おすすめサイズ<br><strong>{best["size"]}</strong><br>{fit_description(best["chest_gap"])}</div>', unsafe_allow_html=True)
        st.metric("身幅のゆとり（周囲）", f'{best["chest_gap"]:.0f} cm')
    with reason_col:
        st.write(f"**{best['size']}サイズ**は、入力した胸囲に対して約 **{best['chest_gap']:.0f} cm** のゆとりがあります。希望した「{fit}」に最も近いバランスです。")
        st.write(f"少し違う印象にしたい場合の次点は **{second['size']}サイズ**です。")
        if best["size"] == "S" and best["chest_gap"] < 6:
            st.warning("Sでもタイトになる可能性があります。実寸表を確認してください。")
        if best["size"] == "XXL" and best["chest_gap"] < FIT_EASE[fit]:
            st.warning("希望するゆとりを十分に確保できない可能性があります。より大きい規格も検討してください。")

    comparison = pd.DataFrame(ranking[:3]).rename(columns={
        "size": "サイズ", "chest_gap": "胸囲のゆとり(cm)",
        "garment_chest": "商品胸囲(cm)", "garment_shoulder": "商品肩幅(cm)",
        "garment_length": "着丈(cm)", "score": "差のスコア",
    })
    comparison["着用イメージ"] = comparison["胸囲のゆとり(cm)"].map(fit_description)
    st.subheader("上位3サイズの比較")
    st.dataframe(comparison[["サイズ", "着用イメージ", "胸囲のゆとり(cm)", "商品肩幅(cm)", "着丈(cm)"]], hide_index=True, use_container_width=True)

st.divider()
st.subheader("このアプリの商品サイズ表")
size_table = pd.DataFrame([{"サイズ": s.name, "商品胸囲(cm)": s.garment_chest, "肩幅(cm)": s.garment_shoulder, "着丈(cm)": s.garment_length} for s in SIZES])
st.dataframe(size_table, hide_index=True, use_container_width=True)
st.caption("提案はこのサイズ表に基づく目安です。生地の伸縮性、デザイン、測定誤差によって着用感は変わります。性別の推測や判定には使用していません。")
