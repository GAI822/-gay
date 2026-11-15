#!/bin/bash
# 企画7 作り直し版（字幕なし）。
#   take_v2: 奥のドア前から投げる → 助走 → 跳んで着地（毛色が正しいグレーの部分だけ使う）
#   take_v3: 腕を力んで斜め下に下ろした決めポーズ（end_frame_pose.png を最後のコマに指定。走る途中は毛色が紺色に崩れたので使わない）
# 投げた後に奥で立ち止まる2〜4秒は切る。決めポーズは最後のコマで1秒止めて、ゆっくり寄る。
set -e
cd "$(dirname "$0")"
OUT="洗濯物をかごに入れただけ.mp4"
ffmpeg -v error -y -i take_v2.mp4 -i take_v3.mp4 -filter_complex "\
[0:v]trim=0.6:2.0,setpts=PTS-STARTPTS,fps=30,format=yuv420p[a];\
[0:v]trim=4.3:6.35,setpts=PTS-STARTPTS,fps=30,format=yuv420p[b];\
[1:v]trim=7.35:8.04,setpts=PTS-STARTPTS,fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration=1.1[c0];\
[c0]scale=iw*1.08:-1,zoompan=z='min(1+0.0018*on,1.08)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1276:fps=30[c];\
[a][b]concat=n=2:v=1:a=0[ab];\
[ab]settb=1/30[ab2];[c]settb=1/30[c2];[ab2][c2]xfade=transition=fade:duration=0.2:offset=3.25[v]" \
  -map "[v]" -an -c:v libx264 -crf 18 -pix_fmt yuv420p _silent.mp4
python3 ../sfx.py _silent.mp4 "$OUT" "0.3:toss" "1.25:land" "1.45:steps" "2.5:jump" "3.1:thud" "3.25:cheer"
rm _silent.mp4
