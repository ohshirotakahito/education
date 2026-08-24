# MY FIT — Tシャツサイズ提案アプリ

身長、胸囲、肩幅、好みの着用感から、Tシャツのおすすめサイズを表示するStreamlitアプリです。性別の推測は行いません。

## 起動

```powershell
cd D:\GitHub\Education\size-recommender
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

表示された `http://localhost:8501` をブラウザで開きます。

## テスト

```powershell
python -m unittest test_recommender.py
```

## サイズ表の変更

実際に販売する商品の寸法に合わせて、`recommender.py` の `SIZES` を変更してください。商品胸囲は身幅の2倍の値を指定します。
