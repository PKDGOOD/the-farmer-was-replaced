#!/bin/zsh
# clauding 플레이스루 코드를 라이브 게임 세이브 폴더로 배포한다.
# 게임의 File Watcher가 켜져 있으면 저장 즉시 인게임에 반영된다.
# save.json(게임 상태)은 건드리지 않는다.
set -e
HERE="${0:A:h}"
SRC="$HERE/clauding"
DST="/Users/dion/Library/Application Support/com.TheFarmerWasReplaced.TheFarmerWasReplaced/Saves/clauding"

cp "$SRC"/*.py "$DST"/
cp "$HERE/STRATEGY.md" "$DST"/ 2>/dev/null || true

echo "Deployed to $DST:"
ls -1 "$DST"/*.py
