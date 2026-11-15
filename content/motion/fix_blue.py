"""生成動画で灰色の猫が紺色に寄った部分だけ、色味を抜いて明るくし、灰色に戻す。

Kling は大きく動く場面でブルーグレーの猫を紺色にしやすい。部屋は暖色なので、青い画素だけを直せば背景はほぼ変わらない。
使い方: python3 fix_blue.py in.mp4 out.mp4 [彩度の残す割合=0.25] [明るさの倍率=1.35]
"""
import subprocess
import sys

import cv2
import numpy as np


def fix(frame, keep_sat, gain):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # 青〜紺（OpenCV の色相 95〜135）で、ある程度色が付いている画素。境目はぼかしてなじませる
    mask = ((h > 95) & (h < 135) & (s > 40)).astype(np.float32)
    mask = cv2.GaussianBlur(mask, (0, 0), 3)
    s *= 1 - mask * (1 - keep_sat)
    v *= 1 + mask * (gain - 1)
    hsv[..., 1], hsv[..., 2] = s, np.clip(v, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    keep_sat = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
    gain = float(sys.argv[4]) if len(sys.argv) > 4 else 1.35
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                            "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", dst],
                           stdin=subprocess.PIPE)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        enc.stdin.write(fix(frame, keep_sat, gain).tobytes())
    enc.stdin.close()
    enc.wait()
    print("wrote", dst)


if __name__ == "__main__":
    main()
