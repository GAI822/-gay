"""企画C「新入りマロ」をつなぐ。cuts.json の順にカットを切り出して 1080x1920/30fps にそろえ、
先出し（冒頭0.9秒）→本編。split のカットは左右2画面（ハイ｜マロ）。最後に曲（music.mp3）と効果音を重ねる。
使い方: python3 edit.py  → out/新入りマロ.mp4"""
import json, os, subprocess, sys
sys.path.insert(0, "../../motion")
C = json.load(open("cuts.json"))
os.makedirs("out", exist_ok=True); os.makedirs("tmp", exist_ok=True)
FIT = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
def run(a): subprocess.run(["ffmpeg", "-v", "error", "-y"] + a, check=True)
parts = []
for i, c in enumerate(C["cuts"]):
    o = f"tmp/c{i:02d}.mp4"
    if c.get("split"):
        L, R = c["split"]
        run(["-ss", str(L["ss"]), "-t", str(c["t"]), "-i", L["src"], "-ss", str(R["ss"]), "-t", str(c["t"]), "-i", R["src"],
             "-filter_complex", "[0:v]scale=-2:1920,crop=540:1920[l];[1:v]scale=-2:1920,crop=540:1920[r];[l][r]hstack,setsar=1,fps=30,format=yuv420p,drawbox=x=537:y=0:w=6:h=1920:color=white@0.9:t=fill[v]",
             "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "18", o])
    else:
        run(["-ss", str(c["ss"]), "-t", str(c["t"]), "-i", c["src"], "-vf", FIT, "-an", "-c:v", "libx264", "-crf", "18", o])
    parts.append(o)
# 先出し: teaser で指定したカットの中の秒
tz = C["teaser"]; tsrc = parts[tz["cut"]]
run(["-ss", str(tz["at"]), "-t", "0.9", "-i", tsrc, "-an", "-c:v", "libx264", "-crf", "18", "tmp/teaser.mp4"])
run(["-ss", str(tz["at"]), "-t", "0.067", "-i", tsrc, "-vf", "eq=brightness=0.6:contrast=0.4", "-an", "-c:v", "libx264", "-crf", "18", "tmp/flash.mp4"])
lst = ["tmp/teaser.mp4", "tmp/flash.mp4"] + parts
open("tmp/list.txt", "w").write("".join(f"file '{os.path.basename(p)}'\n" for p in lst))
run(["-f", "concat", "-safe", "0", "-i", "tmp/list.txt", "-c", "copy", "tmp/video.mp4"])
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "tmp/video.mp4"], capture_output=True, text=True).stdout)
# 効果音（本編の秒数で書く → 先出し分ずらす）
off = 0.967
ev = [f"{round(float(e.split(':')[0]) + off, 3)}:{e.split(':')[1]}" for e in C["sfx"]] + ["0.7:rewind"]
subprocess.run(["python3", "../../motion/sfx.py", "tmp/video.mp4", "tmp/sfx.mp4"] + ev, check=True)
# 曲を重ねる（曲は小さめ、最後1.5秒でフェードアウト）。music2 があれば指定の秒（本編の秒）から2曲目を重ねる
if os.path.exists("music.mp3"):
    ms = C.get("music_start", 0); mend = min(dur, 47 - ms)
    m2 = C.get("music2")
    ins = ["-i", "tmp/sfx.mp4", "-i", "music.mp3"]
    fc = f"[1:a]atrim={ms},asetpts=PTS-STARTPTS,atrim=0:{dur},volume={C.get('music_vol', 0.55)},afade=t=out:st={mend - 1.5}:d=1.5[m]"
    if m2:
        ins += ["-i", m2["file"]]
        at = m2["at"] + off
        if "main_fade_at" in m2:  # 2曲目の前に1曲目を下げる
            fa = m2["main_fade_at"] + off
            fc = fc.replace("[m]", f",afade=t=out:st={fa}:d=1.0[m]")
        fc += f";[2:a]volume={m2.get('vol', 0.6)},adelay={int(at*1000)}|{int(at*1000)},apad,atrim=0:{dur},afade=t=out:st={dur-1.0}:d=1.0[w];[0:a][m][w]amix=inputs=3:duration=first:normalize=0[a]"
    else:
        fc += ";[0:a][m]amix=inputs=2:duration=first:normalize=0[a]"
    run(ins + ["-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "out/新入りマロ.mp4"])
else:
    os.replace("tmp/sfx.mp4", "out/新入りマロ.mp4")
print("wrote out/新入りマロ.mp4", round(dur, 2))
