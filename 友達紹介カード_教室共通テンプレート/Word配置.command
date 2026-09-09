#!/bin/zsh
# 編集済みHTMLから、A4・10面のWord（表1ページ・裏1ページ）を作成します。
set -euo pipefail
base="$(cd -- "$(dirname -- "$0")" && pwd)"
tools="$base/Word配置ツール"

# 対象HTML：引数があればそれ、なければフォルダ内で最も新しい「_編集済み.html」。
source_file="${1:-}"
if [[ -z "$source_file" ]]; then
  source_file="$(ls -t "$base"/*_編集済み.html 2>/dev/null | head -n 1 || true)"
fi
if [[ -z "$source_file" || ! -f "$source_file" ]]; then
  print -u2 '編集済みHTMLが見つかりません。'
  print -u2 'テンプレートを開いて「編集済みHTMLを保存」で保存し、このフォルダに置いてから、もう一度実行してください。'
  exit 1
fi

# 実行環境：Codex同梱のものがあれば使い、なければシステムのNode.js／Pythonを使う。
runtime="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies"
if [[ -x "$runtime/node/bin/node" && -x "$runtime/python/bin/python3" ]]; then
  node_bin="$runtime/node/bin/node"; py_bin="$runtime/python/bin/python3"
  export NODE_PATH="$runtime/node/node_modules"
else
  node_bin="$(command -v node || true)"; py_bin="$(command -v python3 || true)"
fi
if [[ -z "$node_bin" || -z "$py_bin" ]]; then
  print -u2 'Node.js と Python3 が必要です。作成担当者（情報システム担当）に依頼してください。'
  print -u2 'この処理を動かせない教室は、PDFを配布してもらってください。'
  exit 1
fi

assets="$base/Word用素材"
fail(){ print -u2 ""; print -u2 "----------------------------------------"; print -u2 "Wordファイルは作成されませんでした。"; print -u2 "上の内容を確認して、やり直してください。"; print -u2 "----------------------------------------"; exit 1 }
print "元データ： $(basename "$source_file")"
"$node_bin" "$tools/export.cjs" "$source_file" "$assets" || fail

# 出力ファイル名は教室名から決める。
out="$("$py_bin" - "$assets" <<'PY'
import json,sys,pathlib,re
info=json.loads((pathlib.Path(sys.argv[1])/'書き出し情報.json').read_text(encoding='utf-8'))
name=re.sub(r'^久保田学園[\s　]*','',(info.get('school') or '').strip()) or '教室名未設定'
print('友達紹介カード_'+re.sub(r'[/:]','_',name)+'.docx')
PY
)"
"$py_bin" "$tools/place.py" "$tools" "$assets" "$base/$out" || fail

print "完了しました。「$out」をWordで開いて印刷してください。"
