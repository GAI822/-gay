#!/bin/bash
# 企画8「昼寝中に氷水」（字幕なし）:
#   前半 motion_src/transfer_prank.mp4: ハンモックで昼寝中のハイに、クロがバケツの氷水を浴びせる（いたずら動画の2人の動きを移した）
#   後半 motion_src/transfer_taunt.mp4: ずぶ濡れのハイが、黒いズボンのダンサーの動きでクロを煽る
# 前半は横長なので、ハンモックとクロが収まる正方形に切り詰めてから、比率の違う2本を 1080x1920 に揃え（上下はぼかし）、合成効果音を付ける。
set -e
cd "$(dirname "$0")"
OUT="ハイの日常_昼寝中に氷水.mp4"
FIT="split[f][b];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];[f]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p,settb=1/30"
ffmpeg -v error -y -i motion_src/transfer_prank.mp4 -i motion_src/transfer_taunt.mp4 -filter_complex "\
[0:v]crop=832:832:240:0,setpts=PTS-STARTPTS,$FIT[a];[1:v]setpts=PTS-STARTPTS,$FIT[b];[a][b]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -an -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../sfx.py _silent.mp4 "$OUT" "0.35:splash" "0.6:clatter" "1.6:thud" "2.6:steps" "4.0:beat" "6.0:beat"
rm _silent.mp4
