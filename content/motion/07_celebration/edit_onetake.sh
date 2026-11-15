#!/bin/bash
# 企画7 ノーカット版（字幕なし）: Kling pro 8秒の1本撮り（take_onetake.mp4）。
#   走る〜跳ぶ間に毛色が紺色に寄ったので、../fix_blue.py で青い画素だけ灰色に戻した（take_onetake_colorfix.mp4）。
#   途中は切らない。投げる前に止まっている最初の1.0秒だけ削り、合成効果音を付ける。
set -e
cd "$(dirname "$0")"
[ -f take_onetake_colorfix.mp4 ] || python3 ../fix_blue.py take_onetake.mp4 take_onetake_colorfix.mp4 0.2 1.7
OUT="洗濯物をかごに入れただけ_ノーカット版.mp4"
ffmpeg -v error -y -ss 1.0 -i take_onetake_colorfix.mp4 -an -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../sfx.py _silent.mp4 "$OUT" "0.45:toss" "1.75:land" "2.6:steps" "5.1:jump" "5.95:thud" "6.0:cheer"
rm _silent.mp4
