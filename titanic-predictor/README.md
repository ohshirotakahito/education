# Titanic 生存者予測

## 健康データ解析GUI

`data/health_data_dirty.csv` を読み込み、データ表、基本統計量、ヒストグラム、散布図、相関行列をタブで確認できます。欠損値、数値変換失敗、範囲外値、重複ID、カテゴリ表記ゆれも自動検出して警告します。

```powershell
cd D:\GitHub\Education\titanic-predictor
python -m pip install -r requirements.txt
streamlit run app.py
```

ブラウザーで画面が開いたら、左側のファイル選択から別のCSVを読み込むこともできます。

`Titanic-Dataset.csv` から `Survived`（生存: 1、死亡: 0）を予測する機械学習モデルです。
欠損値は中央値または最頻値で補完し、`Sex` と `Embarked` はOne-Hot EncodingしてからRandom Forestで学習します。

## セットアップ

```powershell
cd D:\GitHub\Education\titanic-predictor
python -m pip install -r requirements.txt
```

## 学習と評価

CSVのパスを指定して実行します。

```powershell
python titanic_model.py
```

`Titanic-Dataset.csv` がプロジェクト内、または `Downloads\archive (1)` にある場合は自動で読み込みます。
別の場所にある場合はCSVのパスを指定します。

```powershell
python titanic_model.py "C:\path\to\Titanic-Dataset.csv"
```

実行すると、テストデータの正解率、混同行列、分類レポートを表示し、
同じフォルダーに `titanic_model.pkl` を保存します。

## 可視化

次のコマンドで `titanic_visualizations.png` を生成します。

```powershell
python visualize.py "C:\Users\ohshi\Downloads\archive (1)\Titanic-Dataset.csv"
```

画像には、男女別・客室クラス別の生存率、年齢分布、混同行列、
モデルの特徴量重要度を表示します。

## 複数モデルの比較

ロジスティック回帰、Random Forest、SVM、XGBoost、LightGBMを5分割交差検証で比較できます。
既定では正解率が最も高いモデルを選び、全データで再学習して保存します。

```powershell
python compare_models.py "C:\Users\ohshi\Downloads\archive (1)\Titanic-Dataset.csv"
```

生存者のF1スコアを基準に選ぶ場合は、次のように実行します。

```powershell
python compare_models.py "C:\Users\ohshi\Downloads\archive (1)\Titanic-Dataset.csv" --metric f1
```

## 特徴量重要度

XGBoostのPermutation Importanceで、元の特徴量を1列ずつシャッフルしたときの
正解率低下を調べられます。値が大きい特徴量ほど予測に重要です。

```powershell
python feature_importance.py "C:\Users\ohshi\Downloads\archive (1)\Titanic-Dataset.csv"
```

## テスト

```powershell
python -m unittest test_titanic_model.py
```

## 使用している特徴量

`Pclass`, `Sex`, `Age`, `SibSp`, `Parch`, `Fare`, `Embarked`

名前やチケット番号などの高カーディナリティ列は、単純なモデルでの過学習を避けるため使用していません。