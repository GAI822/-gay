"""drivers.json の素材を Mixkit から落とし、動きの部分だけ切り出して縦長（720x1280）にする。
人物（YOLOv8）の左右の位置の中央値を中心に、高さいっぱいの 9:16 で切り抜く。入りきらない幅の動きは、縮小して上下を無地で埋める（ぼかした人影があると動き移しが失敗するため）。
出力: drivers/<id>.mp4（git には入れない）。使い方: python3 prep_driver.py [id ...]"""
import json, os, subprocess, sys
import numpy as np
from ultralytics import YOLO
D = json.load(open("drivers.json"))
ids = sys.argv[1:] or [d["id"] for d in D]
model = YOLO("yolov8n.pt")
for d in D:
    if d["id"] not in ids:
        continue
    raw = f"raw_{d['id']}.mp4"
    if not os.path.exists(raw):
        subprocess.run(["curl", "-s", "-m", "120", "-o", raw, f"https://assets.mixkit.co/videos/{d['id']}/{d['id']}-720.mp4"], check=True)
    a, b = d["trim"]
    cut = f"cut_{d['id']}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", raw, "-an", "-vf", "fps=30",
                    "-c:v", "libx264", "-crf", "18", cut], check=True)
    xs, x0s, x1s, W, H = [], [], [], None, None
    for r in model(cut, classes=[0], stream=True, verbose=False, vid_stride=5):
        H, W = r.orig_shape
        if len(r.boxes):
            bx = r.boxes.xyxy.cpu().numpy()
            k = int(np.argmax((bx[:, 2] - bx[:, 0]) * (bx[:, 3] - bx[:, 1])))
            x0, _, x1, _ = bx[k]
            xs.append((x0 + x1) / 2); x0s.append(x0); x1s.append(x1)
    cx = float(np.median(xs)) if xs else W / 2
    span = (float(np.percentile(x1s, 95)) - float(np.percentile(x0s, 5))) if xs else 0
    cw = int(H * 9 / 16) // 2 * 2
    if span <= cw * 0.95:
        x = int(min(max(cx - cw / 2, 0), W - cw))
        vf = f"crop={cw}:{H}:{x}:0,scale=720:1280"
    else:  # 動きが横に広い: 動きの範囲を切り出して縮小し、上下を無地で埋める
        sw = int(min(W, span * 1.1)) // 2 * 2
        x = int(min(max(cx - sw / 2, 0), W - sw))
        vf = f"crop={sw}:{H}:{x}:0,scale=720:-2,pad=720:1280:0:(oh-ih)/2:color=0x202020"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", cut, "-vf", vf, "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", f"{d['id']}.mp4"], check=True)
    os.remove(cut)
    print(d["id"], d["move"], f"W={W} span={span:.0f} cw={cw}", "pad" if span > cw * 0.95 else "crop")
