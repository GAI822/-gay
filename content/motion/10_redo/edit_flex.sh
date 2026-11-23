#!/bin/bash
# 企画04 筋肉ポーズ版: 腕立て1回（元動画の0〜2.3秒）→ ムキムキのハイがポーズ（動き移し）
# 動き移しの出力は横長で、右下に元動画の観客の頭が写るため、左から幅1000pxだけ使う
set -e
cd "$(dirname "$0")"
ffmpeg -v error -y -i ../../autopilot/20261121_04/take.mp4 -i flex_take.mp4 -filter_complex "\
[0:v]trim=0:2.3,setpts=PTS-STARTPTS,scale=1080:1920,fps=30,setsar=1[a];\
[1:v]crop=1000:720:0:0,split[f1][f2];\
[f1]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.08[bg];\
[f2]scale=1080:-2[fg];\
[bg][fg]overlay=0:(H-h)/2,fps=30,setsar=1[b];\
[a][b]concat=n=2:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p flex_cut.mp4
python3 ../sfx.py flex_cut.mp4 "ハイの日常_筋トレ初日_筋肉ポーズ.mp4" "0.7:thud" "1.6:jump" "2.3:pop" "2.4:beat" "4.4:beat" "3.0:cheer"
