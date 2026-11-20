#!/bin/bash
# 自動投稿用の仕上げ: 生成した動画の頭を切り、1080x1920 に揃え（上下はぼかし）、合成効果音を付ける。
# 使い方: finish.sh in.mp4 out.mp4 開始秒 "0.4:toss" "1.2:land" ...
#   開始秒: 冒頭の止まっている部分を何秒切るか（0 なら切らない）
#   効果音: ../motion/sfx.py の種類（toss land steps jump thud cheer clatter pop splash beat）を「切った後の秒数:種類」で並べる
set -e
IN="$1"; OUT="$2"; START="$3"; shift 3
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp --suffix=.mp4)"
FIT="split[f][b];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];[f]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p"
ffmpeg -v error -y -ss "$START" -i "$IN" -an -vf "$FIT" -c:v libx264 -crf 18 -pix_fmt yuv420p "$TMP"
python3 "$HERE/../motion/sfx.py" "$TMP" "$OUT" "$@"
rm -f "$TMP"
