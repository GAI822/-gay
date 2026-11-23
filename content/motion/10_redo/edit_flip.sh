#!/bin/bash
# 企画03 ちゃぶ台返し版: 冒頭2秒を切り、ぶつかる瞬間に画面を揺らし、こたつの天板が画面をふさぐコマ（6.85秒）で止めて揺らす。その後のハイの顔の大写しは腹に模様が出るので使わない
set -e
cd "$(dirname "$0")"
SHAKE="crop=iw*0.9:ih*0.9:iw*0.05+iw*0.045*sin(t*95):ih*0.05+ih*0.045*cos(t*77),scale=720:1280"
ffmpeg -v error -y -i flip_take.mp4 -filter_complex "\
[0:v]trim=2.0:6.55,setpts=PTS-STARTPTS,scale=720:1280,fps=24[a];\
[0:v]trim=6.55:6.85,setpts=PTS-STARTPTS,$SHAKE,fps=24[b];\
[0:v]trim=6.80:6.85,setpts=PTS-STARTPTS,fps=24,tpad=stop_mode=clone:stop_duration=0.6,$SHAKE,eq=brightness=0.25*exp(-t*12):eval=frame[c];\
[a][b][c]concat=n=3:v=1:a=0[v]" -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p flip_cut.mp4
bash ../../autopilot/finish.sh flip_cut.mp4 "ハイの日常_リモート会議_ちゃぶ台返し.mp4" 0 "0.2:steps" "1.4:steps" "3.4:jump" "4.0:toss" "4.5:clatter" "4.6:thud" "4.75:thud"
