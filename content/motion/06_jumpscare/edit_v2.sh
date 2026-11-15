#!/bin/bash
# 企画6 v2: 冒頭の待ち時間を削り、0.3秒でジャンプが始まる版（バイラル予測でフック28点と低かったため）
set -e
cd "$(dirname "$0")"
FONT=/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf
CAP="drawtext=fontfile=$FONT:text='びっくりさせても無表情':fontsize=72:fontcolor=white:borderw=7:bordercolor=black:x=(w-tw)/2:y=150,drawtext=fontfile=$FONT:text='Jump scare. No reaction.':fontsize=50:fontcolor=white:borderw=6:bordercolor=black:x=(w-tw)/2:y=245"
ffmpeg -v error -y -i take_b.mp4 -filter_complex "\
[0:v]trim=3.0:5.5,setpts=PTS-STARTPTS[v1];[0:a]atrim=3.0:5.5,asetpts=PTS-STARTPTS[a1];\
[0:v]trim=3.2:4.3,setpts=(PTS-STARTPTS)*2.5,drawtext=fontfile=$FONT:text='スローで / slow-mo':fontsize=56:fontcolor=yellow:borderw=6:bordercolor=black:x=(w-tw)/2:y=h-360[v2];[0:a]atrim=3.2:4.3,asetpts=PTS-STARTPTS,atempo=0.5,atempo=0.8[a2];\
[0:v]trim=7.9:9.0,setpts=PTS-STARTPTS[v3];[0:a]atrim=7.9:9.0,asetpts=PTS-STARTPTS[a3];\
[v1][a1][v2][a2][v3][a3]concat=n=3:v=1:a=1[v][a];[v]$CAP,fps=30[vo]" \
  -map "[vo]" -map "[a]" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart hai_jumpscare_v2_coldopen.mp4
