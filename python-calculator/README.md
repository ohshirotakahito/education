# Python Calculator

追加ライブラリなしで動く、Tkinter製のデスクトップ計算機です。

## 起動方法

`start_calculator.bat` をダブルクリックします。またはPowerShellで実行します。

```powershell
cd D:\GitHub\Education\python-calculator
python app.py
```

## キーボード

- `Enter`: 計算
- `Backspace`: 1文字削除
- `Esc`: クリア
- 数字、演算子、括弧は直接入力可能

画面上部の「横型にする／縦型にする」ボタンでレイアウトをいつでも切り替えられます。関数電卓を開いた状態でも切り替え可能です。

## テスト

```powershell
python -m unittest test_calculator.py
```
