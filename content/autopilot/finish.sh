#!/bin/bash
# 自動投稿用の仕上げ: 生成した動画の頭を切り、1080x1920 に揃え（上下はぼかし）、合成効果音を付ける。
# 使い方: [TEASER="オチの秒:長さ"] finish.sh in.mp4 out.mp4 開始秒 "0.4:toss" "1.2:land" ...
#   開始秒: 冒頭の止まっている部分を何秒切るか（0 なら切らない）
#   効果音: ../motion/sfx.py の種類を「切った後の秒数:種類」で並べる
#   TEASER: オチの一番いい瞬間（切った後の秒数）と長さ。指定すると、その場面を冒頭に先出しし（既定0.9秒）、
#           巻き戻し音と白い一瞬のフラッシュを挟んで本編につなぐ。効果音の秒数は本編の秒数のまま書けばよい（自動でずらす）。
set -e
IN="$1"; OUT="$2"; START="$3"; shift 3
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp --suffix=.mp4)"; TMP2="$(mktemp --suffix=.mp4)"
FIT="split[f][b];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];[f]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p"
ffmpeg -v error -y -ss "$START" -i "$IN" -an -vf "$FIT" -c:v libx264 -crf 18 -pix_fmt yuv420p "$TMP"
if [ -n "$TEASER" ]; then
  T="${TEASER%%:*}"; D="${TEASER#*:}"; [ "$D" = "$TEASER" ] && D=0.9
  ffmpeg -v error -y -i "$TMP" -filter_complex "\
[0:v]trim=start=$T:duration=$D,setpts=PTS-STARTPTS[t];\
[0:v]trim=start=$T:duration=0.067,setpts=PTS-STARTPTS,eq=brightness=0.6:contrast=0.4[w];\
[0:v]setpts=PTS-STARTPTS[m];[t][w][m]concat=n=3:v=1:a=0,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 18 "$TMP2"
  OFF=$(python3 -c "print(round($D+0.067,3))")
  EV=()
  for e in "$@"; do
    at="${e%%:*}"; k="${e#*:}"
    EV+=("$(python3 -c "print(round($at+$OFF,3))"):$k")
    python3 -c "import sys;a=$at;sys.exit(0 if $T-0.05<=a<$T+$D else 1)" && EV+=("$(python3 -c "print(round($at-$T,3))"):$k")
  done
  EV+=("$(python3 -c "print(round($D-0.2,3))"):rewind")
  python3 "$HERE/../motion/sfx.py" "$TMP2" "$OUT" "${EV[@]}"
else
  python3 "$HERE/../motion/sfx.py" "$TMP" "$OUT" "$@"
fi
rm -f "$TMP" "$TMP2"
