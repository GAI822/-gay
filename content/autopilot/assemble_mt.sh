#!/bin/bash
# 前半（Kling で作った場面の動画）と、オチ（人の動きをハイに移した動画）をつなぎ、オチの決めの瞬間を冒頭に先出しして効果音を付ける。
# 使い方: assemble_mt.sh setup.mp4 punch.mp4 out.mp4 <前半の頭を切る秒> <オチの頭を切る秒> <オチの長さ> <先出しする秒（オチの中の秒）> "<秒>:<効果音>" ...
#   効果音の秒数は「つないだ本編」の秒数で書く（先出し分は自動でずらす）。
set -e
SETUP="$1"; PUNCH="$2"; OUT="$3"; S0="$4"; P0="$5"; PL="$6"; PT="$7"; shift 7
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp --suffix=.mp4)"
FIT="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
ffmpeg -v error -y -ss "$S0" -i "$SETUP" -ss "$P0" -t "$PL" -i "$PUNCH" -filter_complex \
 "[0:v]$FIT[a];[1:v]$FIT[b];[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 18 "$TMP"
SL=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SETUP" | python3 -c "import sys;print(float(sys.stdin.read())-$S0)")
T=$(python3 -c "print(round($SL+$PT,3))")
TEASER="$T:0.9" bash "$HERE/finish.sh" "$TMP" "$OUT" 0 "$@"
rm -f "$TMP"
