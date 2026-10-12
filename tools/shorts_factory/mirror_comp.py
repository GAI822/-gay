"""鏡の中を犬の映像に差し替え、手前の猫は残す合成。"""
import subprocess
import sys

import cv2
import numpy as np
from rembg import new_session, remove

src, dog, out = sys.argv[1:4]
CX, CY, R = 575, 677, 438            # 鏡のガラス部分（検出値）
SPLIT_X, SPLIT_Y = 600, 1100         # これより左 or 下の前景は「手前の猫」とみなす
sess = new_session("isnet-general-use")
a, b = cv2.VideoCapture(src), cv2.VideoCapture(dog)
W, H, fps = int(a.get(3)), int(a.get(4)), a.get(5)
yy, xx = np.mgrid[0:H, 0:W]
circle = (((xx - CX) ** 2 + (yy - CY) ** 2) <= R ** 2).astype(np.float32)
circle = cv2.GaussianBlur(circle, (0, 0), 3)
near = ((xx < SPLIT_X) | (yy > SPLIT_Y)).astype(np.uint8)
ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                       "-r", str(fps), "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264",
                       "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "copy", "-shortest", out], stdin=subprocess.PIPE)
last_dog = None
while True:
    ok, f = a.read()
    if not ok:
        break
    okd, d = b.read()
    d = d if okd else last_dog
    last_dog = d
    dh, dw = d.shape[:2]
    side = int(min(dw, dh) * 0.82)
    cx, cy = dw // 2, int(dh * 0.43)
    crop = d[cy - side // 2: cy + side // 2, cx - side // 2: cx + side // 2]
    plate = np.zeros_like(f)
    plate[CY - R: CY + R, CX - R: CX + R] = cv2.resize(crop, (2 * R, 2 * R))
    m = np.array(remove(cv2.cvtColor(f, cv2.COLOR_BGR2RGB), session=sess, only_mask=True))
    # 手前の猫と鏡の中の像を、色の境目で切り分ける（watershed）
    inside = ((xx - CX) ** 2 + (yy - CY) ** 2) <= (R - 20) ** 2
    markers = np.zeros((H, W), np.int32)
    markers[m < 40] = 1                                            # 背景
    markers[(m > 200) & ~inside & (xx < CX)] = 2                   # 手前の猫（鏡の外の体）
    markers[(m > 200) & inside & (xx > CX + 20)] = 3  # 鏡の中の像
    markers = cv2.watershed(f.copy(), markers)
    fg = (markers == 2).astype(np.uint8)
    fg = cv2.dilate(fg, np.ones((5, 5), np.uint8))
    fg = cv2.GaussianBlur(fg.astype(np.float32), (0, 0), 2)
    alpha = (circle * (1 - fg))[..., None]
    comp = (plate * alpha + f * (1 - alpha)).astype(np.uint8)
    ff.stdin.write(comp.tobytes())
ff.stdin.close()
ff.wait()
print(out)
