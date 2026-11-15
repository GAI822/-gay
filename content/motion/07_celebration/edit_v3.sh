#!/bin/bash
# 企画7 動き移し版（字幕なし）:
#   take_v2 の「奥のドア前から靴下を投げてかごに入る」場面 → motion_src/transfer_lite.mp4（中継映像の動きをハイに移したゴールパフォーマンス）
# 比率の違う2本を 1080x1920 に揃える（はみ出さない大きさに縮め、上下はぼかした同じ映像で埋める）。最後のポーズは0.8秒止める。
set -e
cd "$(dirname "$0")"
OUT="洗濯物をかごに入れただけ_動き移し版.mp4"
FIT="split[f][b];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];[f]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p,settb=1/30"
ffmpeg -v error -y -i take_v2.mp4 -i motion_src/transfer_lite.mp4 -filter_complex "\
[0:v]trim=0.6:2.0,setpts=PTS-STARTPTS,$FIT[a];\
[1:v]setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.8,$FIT[b];\
[a][b]concat=n=2:v=1:a=0[v]" -map "[v]" -an -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../sfx.py _silent.mp4 "$OUT" "0.3:toss" "1.25:land" "1.45:steps" "3.0:jump" "3.75:thud" "3.8:cheer"
rm _silent.mp4
