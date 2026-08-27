# Python Tetris

追加ライブラリなしで動く、Tkinter製のテトリスです。

## 起動方法

`start_tetris.bat` をダブルクリックするか、PowerShellで実行します。

```powershell
cd D:\GitHub\Education\tetris
python tetris.py
```

## 操作

- `←` / `→`: 左右移動
- `↓`: 1マス下へ移動
- `↑` または `X`: 回転
- `Space`: 一気に落とす
- `R`: ゲームオーバー後に再スタート

## テスト

```powershell
python -m unittest test_tetris.py
```