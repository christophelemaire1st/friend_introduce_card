# 友達紹介カード

編集用HTMLで写真・QR・教室名を設定し、A4・10面のWordを作成します。
セットアップと印刷手順はテンプレートフォルダの `readme.txt` を参照してください。

## 対応環境と構成

Node.js 22以上、Python 3.10以上、Playwright Chromiumを使用します。

| OS | 起動方法 |
| --- | --- |
| Windows | `Word配置.bat` |
| macOS | `Word配置.command` |
| Linux | `python3 Word配置.py` |

起動ファイルは共通の `Word配置.py` を呼び出すだけです。共通処理が入力HTMLの選択、
依存環境の確認、PNG生成、Word生成、完成ファイルの置き換えを担当します。
`export.cjs` と `place.py` のカード描画・Word配置処理は維持しています。
Codex専用のランタイム探索やzshの構文には依存しません。

- JavaScriptの依存関係は `package-lock.json` と `npm ci` で揃えます。
- Pythonはツールフォルダの `.venv` を使用し、`requirements.txt` から導入します。
- 入力省略時は起動ファイルと同じフォルダの最新の `_編集済み.html` を選びます。
- 明示した相対パスは呼び出し元ディレクトリ基準です。空白・日本語を含むパスに対応します。
- 出力は起動ファイルと同じフォルダ。同じ教室名は成功時に置き換えます。
- 中間素材は一時フォルダに隔離し、変換失敗時は既存のWordを残します。
- 日本語フォントは各PCのインストール状況に依存します。同じ見た目が必要な場合は
  同じフォントを導入して試し刷りしてください。Wordのページ数・表裏位置・QR読み取りの
  最終確認は利用するWordとプリンターで行ってください。

## 検証

リポジトリ直下で `python -m unittest discover -s tests -v` を実行します。
初回セットアップ後、環境変数 `RUN_EXPORT_TESTS=1` を設定すると実際のHTML→Word変換、
20枚の画像配置と寸法、未設定入力の拒否、失敗時の既存出力の保持も検証します。
テスト用の画像は単色画像で、QRの読み取りを検証するものではありません。
GitHub ActionsはWindows・macOS・Ubuntuで同じ変換テストを実行します。
