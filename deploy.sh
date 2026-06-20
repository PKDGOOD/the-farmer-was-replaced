#!/bin/zsh
# clauding 플레이스루 코드를 라이브 게임 세이브 폴더로 배포한다.
# 게임의 File Watcher가 켜져 있으면 저장 즉시 인게임에 반영된다.
# save.json(게임 상태)은 건드리지 않는다.
set -e
HERE="${0:A:h}"
SRC="$HERE/clauding"
DST="/Users/dion/Library/Application Support/com.TheFarmerWasReplaced.TheFarmerWasReplaced/Saves/clauding"

# Only deploy .py code (ASCII-only). Do NOT copy Korean .md docs into the
# live save: the in-game editor throws IndexOutOfRangeException on non-ASCII.
cp "$SRC"/*.py "$DST"/

# Guard: refuse to deploy any .py containing non-ASCII (would break the editor).
if LC_ALL=C grep -lP '[^\x00-\x7F]' "$DST"/*.py 2>/dev/null; then
    echo "ERROR: non-ASCII found in deployed .py above. The in-game editor will break." >&2
    exit 1
fi

echo "Deployed to $DST:"
ls -1 "$DST"/*.py
