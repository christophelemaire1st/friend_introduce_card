#!/usr/bin/env python3
"""Windows/macOS/Linux 共通の Word 書き出しランチャー。"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

BASE = Path(__file__).resolve().parent
TOOLS = BASE / "Word配置ツール"


def select_source(source, base=BASE):
    if source:
        result = Path(source).expanduser().resolve()
    else:
        candidates = [p for p in base.iterdir() if p.is_file() and
                      unicodedata.normalize("NFC", p.name).endswith("_編集済み.html")]
        if not candidates:
            raise ValueError("編集済みHTMLが見つかりません。保存したHTMLをこのフォルダに置いてください。")
        result = max(candidates, key=lambda p: (p.stat().st_mtime_ns, p.name))
    if not result.is_file() or result.suffix.lower() != ".html":
        raise ValueError("入力HTMLが見つかりません: " + str(result))
    return result


def output_name(school):
    name = re.sub(r"^久保田学園[\s　]*", "", school.strip()) or "教室名未設定"
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).rstrip(" .")
    return "友達紹介カード_" + (name or "教室名未設定") + ".docx"


def run(args):
    env = dict(os.environ, PYTHONUTF8="1")
    subprocess.run([str(a) for a in args], cwd=TOOLS, env=env, check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", help="省略時は同じフォルダの最新の _編集済み.html")
    parser.add_argument("--pause", action="store_true", help="終了時にEnterキーを待つ")
    args = parser.parse_args(argv)
    code = 0
    try:
        source = select_source(args.source)
        node = shutil.which("node")
        if not node:
            raise ValueError("Node.jsが見つかりません。readme.txtの初回セットアップを実行してください。")
        python = TOOLS / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if not python.is_file():
            raise ValueError("専用Python環境がありません。readme.txtの初回セットアップを実行してください。")
        run([python, "-c", "import docx"])
        print("元データ: " + str(source), flush=True)
        # 失敗した素材を再利用しない。出力は完成後に置き換える。
        with tempfile.TemporaryDirectory(prefix="friend-card-") as tmp:
            assets = Path(tmp)
            run([node, TOOLS / "export.cjs", source, assets])
            info = json.loads((assets / "書き出し情報.json").read_text(encoding="utf-8"))
            out = BASE / output_name(info.get("school") or "")
            with tempfile.TemporaryDirectory(prefix=".word-", dir=BASE) as staging:
                draft = Path(staging) / out.name
                run([python, TOOLS / "place.py", TOOLS, assets, draft])
                os.replace(draft, out)
        print("完了しました。Wordで開いて印刷してください: " + str(out))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("Wordファイルは作成されませんでした: " + str(error), file=sys.stderr)
        print("readme.txtを確認してください。出力先をWordで開いている場合は閉じてください。", file=sys.stderr)
        code = 1
    except KeyboardInterrupt:
        code = 130
    finally:
        if args.pause:
            try:
                input("Enterキーで閉じます...")
            except (EOFError, KeyboardInterrupt):
                pass
    return code


if __name__ == "__main__":
    raise SystemExit(main())
