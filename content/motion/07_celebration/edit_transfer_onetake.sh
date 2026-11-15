#!/bin/bash
# 企画7 動き移しノーカット版（字幕なし）:
#   ノーカット版の通しの動き（motion_src/driving_onetake.mp4）を、グレーのハイの画像に移し直した1本（Genjutsu Lite 720p）。
#   ハイは画像から描き直されるので、毛色が紺色に崩れない。途中は切らず、1080x1920 に拡大して効果音を付ける。
set -e
cd "$(dirname "$0")"
OUT="洗濯物をかごに入れただけ_動き移しノーカット版.mp4"
ffmpeg -v error -y -i motion_src/transfer_onetake.mp4 -an -vf "scale=1080:1920:flags=lanczos,setsar=1" -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../sfx.py _silent.mp4 "$OUT" "0.45:toss" "1.75:land" "2.5:steps" "5.0:jump" "5.75:thud" "5.8:cheer"
rm _silent.mp4
