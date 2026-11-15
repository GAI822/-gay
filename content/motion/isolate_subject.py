"""動きの元の動画から主役の人物だけを残し、他の人物と背景を無地にした動画を作る。

動きを移す処理（Genjutsu）は、動きの元に映っている他の人物まで出してしまうため、主役以外を消してから渡す。
人物の検出と切り抜きは YOLOv8 seg（人物クラスのみ）。各コマで、大きく映っていて前のコマの主役に近い人物を主役とする。
使い方: python3 isolate_subject.py in.mp4 out.mp4
"""
import subprocess
import sys

import cv2
import numpy as np
from ultralytics import YOLO

BG = np.array((128, 128, 128), np.float32)  # 無地のグレー


def main():
    src, dst = sys.argv[1], sys.argv[2]
    model = YOLO("yolov8s-seg.pt")
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                            "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", dst],
                           stdin=subprocess.PIPE)
    prev, prev_mask, n = None, None, 0
    for r in model(src, classes=[0], stream=True, verbose=False, retina_masks=True):
        frame = r.orig_img
        mask = None
        if r.masks is not None and len(r.boxes):
            boxes = r.boxes.xyxy.cpu().numpy()
            area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
            cent = np.stack([(boxes[:, 0] + boxes[:, 2]) / 2, (boxes[:, 1] + boxes[:, 3]) / 2], 1)
            score = area if prev is None else area / (1 + np.hypot(*(cent - prev).T) / 80)
            i = int(np.argmax(score))
            prev = cent[i]
            mask = r.masks.data[i].cpu().numpy()
            mask = cv2.resize(mask, (w, h)) > 0.5
        if mask is None:
            mask = prev_mask if prev_mask is not None else np.zeros((h, w), bool)
        prev_mask = mask
        m = cv2.dilate(mask.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
        m = cv2.GaussianBlur(m, (0, 0), 2)[..., None]
        out = frame.astype(np.float32) * m + BG * (1 - m)
        enc.stdin.write(out.astype(np.uint8).tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    print("wrote", dst, n, "frames")


if __name__ == "__main__":
    main()
