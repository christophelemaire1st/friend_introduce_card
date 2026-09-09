#!/bin/sh
base="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo 'Python 3 is required. See readme.txt.' >&2
  read -r answer
  exit 1
fi
exec python3 "$base/Word配置.py" --pause "$@"
