# NMR Structure Finder

¹H NMRスペクトル（CSVまたはJCAMP-DX）と分子式から、登録済み化合物の候補構造を順位付きで表示する試作アプリです。

既定ではPubChem PUG RESTを使い、分子式に一致する候補を最大80件追加します。取得できない場合はローカル候補ライブラリだけで解析を続行します。PubChem候補のNMR領域は、SMILESの官能基から簡易推定したものです。

## 起動方法

一番簡単な方法は `start_nmr_app.bat` をダブルクリックすることです。

VS Codeでは「実行とデバッグ」を開き、`NMRアプリを起動`を選択して実行できます。右上の「Pythonファイルを実行」は使用しないでください。

```powershell
cd nmr-structure
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

ブラウザで表示された画面から `sample/ethyl_acetate.csv` をアップロードし、分子式に `C4H8O2` を入力すると動作を確認できます。

## サンプルデータ

`sample` フォルダには10種類のシミュレーションスペクトルがあります。ファイルと分子式の対応は `sample/samples.csv` を参照してください。これらはアプリの操作確認用であり、実測の標準スペクトルではありません。

## CSV形式

1列目を `ppm`、2列目を `intensity` とします。ppmは昇順・降順のどちらでも構いません。

## 重要な制限

このアプリは構造決定を保証しません。候補は `data/compounds.csv` に登録された化合物だけです。¹H NMRだけでは異性体を一意に区別できない場合があります。研究判断には、積分値、多重度、¹³C、COSY、HSQC、HMBC、MSなどを併用してください。
