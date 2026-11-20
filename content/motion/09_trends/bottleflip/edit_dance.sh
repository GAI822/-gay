#!/bin/bash
# ボトルフリップ成功 → ダンス:
#   take.mp4 の 0.6〜3.4秒（投げる→ボトルが立つ→成功が分かるまで）
#   → motion_src/transfer_dance_v2.mp4（送られたダンス動画の動きを、部屋の中ほどに立つハイに移した4秒）
# 1080x1920 に揃え（上下はぼかし）、合成効果音（投げる・着地・ポン・ダンスのリズム）を付ける。
set -e
cd "$(dirname "$0")"
OUT="ハイの日常_ボトルフリップ成功ダンス.mp4"
FIT="split[f][b];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30[bg];[f]scale=1080:1920:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p,settb=1/30"
ffmpeg -v error -y -i take.mp4 -i motion_src/transfer_dance_v2.mp4 -filter_complex "\
[0:v]trim=0.6:3.4,setpts=PTS-STARTPTS,$FIT[a];[1:v]setpts=PTS-STARTPTS,$FIT[b];[a][b]concat=n=2:v=1:a=0[v]" \
  -map "[v]" -an -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../../sfx.py _silent.mp4 "$OUT" "0.55:toss" "1.9:thud" "2.0:pop" "2.8:beat" "4.8:beat"
rm _silent.mp4
