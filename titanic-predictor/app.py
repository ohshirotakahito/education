"""health_data_dirty.csv の品質チェックと探索を行う Streamlit アプリ。"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data" / "health_data_dirty.csv"
NUMERIC_HEALTH_COLUMNS = [
    "Age",
    "Height_cm",
    "Weight_kg",
    "BMI",
    "Systolic_BP",
    "Diastolic_BP",
    "Glucose",
    "Cholesterol",
    "Exercise_min_week",
    "Sleep_hours",
]
VALID_RANGES = {
    "Age": (0, 120),
    "Height_cm": (100, 250),
    "Weight_kg": (20, 300),
    "BMI": (10, 80),
    "Systolic_BP": (70, 250),
    "Diastolic_BP": (40, 150),
    "Glucose": (40, 400),
    "Cholesterol": (80, 500),
    "Exercise_min_week": (0, 1_500),
    "Sleep_hours": (0, 24),
}
PLOTLY_CONFIG = {"displaylogo": False, "responsive": True}

st.set_page_config(
    page_title="Health Data Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --ink: #17202a; --muted: #667085; --teal: #087f8c; --coral: #e76f51; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: var(--ink); }
    .stApp { background: linear-gradient(135deg, #f8fbfb 0%, #eef5f3 55%, #fff8f1 100%); }
    [data-testid="stSidebar"] { background: #183b43; }
    [data-testid="stSidebar"] * { color: #edf8f5; }
    [data-testid="stMetric"] { background: rgba(255,255,255,.8); border: 1px solid #dce8e5; border-radius: 10px; padding: 16px; }
    .hero { padding: 20px 0 8px; }
    .eyebrow { color: var(--teal); font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .subtitle { color: var(--muted); font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data(source: str | bytes) -> pd.DataFrame:
    if isinstance(source, bytes):
        from io import BytesIO

        return pd.read_csv(BytesIO(source))
    return pd.read_csv(source)


def prepare_analysis_data(data: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """数値列を復元しながら、分析を歪めるデータ品質問題を検出する。"""
    analysis_data = data.copy()
    warnings: list[dict[str, object]] = []

    for column in NUMERIC_HEALTH_COLUMNS:
        if column not in data.columns:
            continue
        missing = data[column].isna()
        if missing.any():
            warnings.append({
                "種類": "欠損値",
                "列": column,
                "件数": int(missing.sum()),
                "詳細": "値が空欄です",
            })
        converted = pd.to_numeric(data[column], errors="coerce")
        invalid = data[column].notna() & converted.isna()
        if invalid.any():
            warnings.append({
                "種類": "数値変換失敗",
                "列": column,
                "件数": int(invalid.sum()),
                "詳細": f"数値として解釈できない値: {', '.join(data.loc[invalid, column].astype(str).unique()[:3])}",
            })
        analysis_data[column] = converted

        if column in VALID_RANGES:
            minimum, maximum = VALID_RANGES[column]
            out_of_range = converted.notna() & ~converted.between(minimum, maximum)
            if out_of_range.any():
                warnings.append({
                    "種類": "範囲外",
                    "列": column,
                    "件数": int(out_of_range.sum()),
                    "詳細": f"許容範囲 {minimum:g}〜{maximum:g}: {', '.join(data.loc[out_of_range, column].astype(str).unique()[:3])}",
                })

    if "ID" in data.columns:
        duplicate_id = data["ID"].duplicated(keep=False) & data["ID"].notna()
        if duplicate_id.any():
            warnings.append({
                "種類": "重複ID",
                "列": "ID",
                "件数": int(duplicate_id.sum()),
                "詳細": f"重複したID: {', '.join(data.loc[duplicate_id, 'ID'].astype(str).unique()[:5])}",
            })

    if "Risk_Group" in data.columns:
        normalized = data["Risk_Group"].astype("string").str.strip().str.lower()
        known = {"low", "medium", "high"}
        invalid_category = data["Risk_Group"].notna() & ~normalized.isin(known)
        if invalid_category.any():
            warnings.append({
                "種類": "未知カテゴリ",
                "列": "Risk_Group",
                "件数": int(invalid_category.sum()),
                "詳細": f"想定外の値: {', '.join(data.loc[invalid_category, 'Risk_Group'].astype(str).unique()[:5])}",
            })
        case_variants = data["Risk_Group"].dropna().astype(str).str.lower().nunique() < data["Risk_Group"].dropna().nunique()
        if case_variants:
            warnings.append({
                "種類": "カテゴリ表記ゆれ",
                "列": "Risk_Group",
                "件数": int(data["Risk_Group"].nunique()),
                "詳細": "大文字・小文字が統一されていません",
            })

    return analysis_data, warnings


st.markdown(
    '<div class="hero"><div class="eyebrow">Health Data Studio</div>'
    '<h1>健康データを、ひと目で読み解く</h1>'
    '<div class="subtitle">表・統計・分布・関係性をひとつのワークスペースで探索します。</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("データソース")
    uploaded = st.file_uploader("CSVファイルを選択", type="csv")
    st.caption("初期データ: data/health_data_dirty.csv")

try:
    data = load_data(uploaded.getvalue() if uploaded else str(DEFAULT_DATA))
except Exception as error:
    st.error(f"CSVを読み込めませんでした: {error}")
    st.stop()

analysis_data, data_warnings = prepare_analysis_data(data)
numeric_columns = analysis_data.select_dtypes(include="number").columns.tolist()
if not numeric_columns:
    st.error("数値列がないため、グラフを作成できません。")
    st.stop()

missing_values = int(data.isna().sum().sum())
st.subheader("データ品質チェック")
if data_warnings:
    st.warning(f"{len(data_warnings)}種類の問題を検出しました。解析前に内容を確認してください。", icon="⚠️")
    warning_table = pd.DataFrame(data_warnings)
    with st.expander("検出した問題の詳細", expanded=True):
        st.dataframe(warning_table, use_container_width=True, hide_index=True)
else:
    st.success("問題は検出されませんでした。")

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("レコード数", f"{len(data):,}")
metric2.metric("項目数", len(data.columns))
metric3.metric("数値項目", len(numeric_columns))
metric4.metric("欠損値", f"{missing_values:,}")

tabs = st.tabs(["データ表", "基本統計量", "ヒストグラム", "散布図", "相関行列"])

with tabs[0]:
    st.subheader("データ表")
    st.caption(f"{len(data):,} 行 × {len(data.columns)} 列")
    st.dataframe(data, use_container_width=True, height=560, hide_index=True)
    st.download_button(
        "CSVをダウンロード",
        data.to_csv(index=False).encode("utf-8-sig"),
        file_name="health_data_export.csv",
        mime="text/csv",
    )

with tabs[1]:
    st.subheader("基本統計量")
    st.caption("数値列は平均・標準偏差・四分位数、カテゴリ列は件数と最頻値を表示します。")
    statistics = data.describe(include="all").transpose()
    statistics.insert(0, "データ型", data.dtypes.astype(str))
    st.dataframe(statistics, use_container_width=True, height=560)

with tabs[2]:
    st.subheader("ヒストグラム")
    histogram_column = st.selectbox("表示する列", numeric_columns, key="histogram-column")
    bins = st.slider("ビン数", min_value=5, max_value=50, value=20, step=1)
    figure = px.histogram(
        analysis_data,
        x=histogram_column,
        nbins=bins,
        color_discrete_sequence=["#087f8c"],
        template="plotly_white",
        labels={histogram_column: histogram_column, "count": "件数"},
    )
    figure.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20), bargap=0.08)
    st.plotly_chart(figure, use_container_width=True, config=PLOTLY_CONFIG)

with tabs[3]:
    st.subheader("散布図")
    x_axis, y_axis = st.columns(2)
    x_column = x_axis.selectbox("X軸", numeric_columns, index=0, key="scatter-x")
    y_column = y_axis.selectbox("Y軸", numeric_columns, index=min(1, len(numeric_columns) - 1), key="scatter-y")
    category_columns = data.select_dtypes(exclude="number").columns.tolist()
    color_column = st.selectbox("色分け（任意）", ["なし", *category_columns], key="scatter-color")
    figure = px.scatter(
        analysis_data,
        x=x_column,
        y=y_column,
        color=None if color_column == "なし" else color_column,
        template="plotly_white",
        color_discrete_sequence=["#e76f51", "#087f8c", "#f4a261", "#264653"],
        hover_data=data.columns.tolist(),
    )
    figure.update_traces(marker={"size": 9, "opacity": 0.78, "line": {"width": 0.5, "color": "white"}})
    figure.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(figure, use_container_width=True, config=PLOTLY_CONFIG)

with tabs[4]:
    st.subheader("相関行列")
    st.caption("Pearson相関係数。1に近いほど正の相関、-1に近いほど負の相関です。")
    correlation = analysis_data[numeric_columns].corr()
    figure = go.Figure(
        go.Heatmap(
            z=correlation.values,
            x=correlation.columns,
            y=correlation.columns,
            zmin=-1,
            zmax=1,
            colorscale=[[0, "#e76f51"], [0.5, "#f7f4ef"], [1, "#087f8c"]],
            text=correlation.round(2).values,
            texttemplate="%{text}",
            hovertemplate="%{x} × %{y}<br>相関係数: %{z:.3f}<extra></extra>",
            colorbar={"title": "相関"},
        )
    )
    figure.update_layout(height=max(540, len(numeric_columns) * 55), margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(figure, use_container_width=True, config=PLOTLY_CONFIG)