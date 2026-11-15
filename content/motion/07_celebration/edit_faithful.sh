#!/bin/bash
# 企画7 中継忠実ノーカット版（字幕なし）:
#   送られた中継映像の「走り出し〜ゴールパフォーマンスの着地」を、主役の選手だけ残した動きの元（../isolate_subject.py）にして
#   ハイに移した1本（motion_src/transfer_faithful_v2.mp4、Genjutsu Lite 720p）。途中は切らない。
#   832x1108 を 1080x1920 に揃え（上下はぼかし）、合成効果音を付ける。
set -e
cd "$(dirname "$0")"
OUT="洗濯物をかごに入れただけ_中継忠実ノーカット版.mp4"
FIT="split[f][b];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];[f]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p"
ffmpeg -v error -y -i motion_src/transfer_faithful_v2.mp4 -an -vf "$FIT" -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../sfx.py _silent.mp4 "$OUT" "0.0:steps" "0.9:steps" "2.2:jump" "2.95:thud" "3.0:cheer"
rm _silent.mp4
