#!/bin/bash
# 企画7「洗濯物をかごに入れただけ」: 冒頭の静止1.4秒を切り、字幕と合成効果音を付ける。
set -e
cd "$(dirname "$0")"
FONT=/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf
ffmpeg -v error -y -ss 1.4 -i take.mp4 -vf "drawtext=fontfile=$FONT:text='洗濯物をかごに入れただけ':fontsize=56:fontcolor=white:borderw=7:bordercolor=black:x=(w-tw)/2:y=150,drawtext=fontfile=$FONT:text='When you finally do the laundry':fontsize=42:fontcolor=white:borderw=6:bordercolor=black:x=(w-tw)/2:y=240,fps=30" -an -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../sfx.py _silent.mp4 hai_celebration_final.mp4 "0.35:toss" "1.1:land" "1.35:steps" "1.5:cheer" "2.5:jump" "3.3:thud" "4.4:clatter"
rm _silent.mp4
