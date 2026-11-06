"""「POV: あなたは冷蔵庫」の絵コンテ動画（静止画＋ズーム＋効果音）を作る。

本番は Kling で動かす。これはクレジットが無い間に、間（ま）とオチを確認するための試作。
使い方: python3 make_animatic.py  → fridge_animatic.mp4（1080x1920, 約10秒）
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

HERE = Path(__file__).resolve().parent
DUO = HERE.parents[2] / "character/hai/05_duo_kitchen.png"
REVEAL = HERE / "f3_reveal_b.png"
W, H, FPS = 1080, 1920, 30
SR = 44100
FONTS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"]
FONT = next(f for f in FONTS if Path(f).exists())

# (秒, 種類, ズーム開始, ズーム終了)  open=冷蔵庫が開いている / closed=閉まって真っ暗 / reveal=中の黒猫
SHOTS = [
    (2.0, "open", 1.00, 1.06),
    (0.6, "closed", 0, 0),
    (1.8, "open", 1.12, 1.18),
    (0.5, "closed", 0, 0),
    (1.4, "open", 1.28, 1.34),
    (0.4, "closed", 0, 0),
    (0.9, "open", 1.55, 1.62),
    (2.4, "reveal", 1.00, 1.04),
]


def fridge_light(img):
    """冷蔵庫の庫内灯に照らされたような、青白くて明るい光にする。"""
    img = ImageEnhance.Brightness(img).enhance(1.15)
    a = np.asarray(img).astype(np.float32)
    a[..., 2] = np.clip(a[..., 2] * 1.18 + 12, 0, 255)
    a[..., 0] = a[..., 0] * 0.9
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    cy, cx = a.shape[0] * 0.45, a.shape[1] * 0.5
    d = np.sqrt(((yy - cy) / a.shape[0]) ** 2 + ((xx - cx) / a.shape[1]) ** 2)
    a *= np.clip(1.25 - d * 1.1, 0.35, 1.2)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def zoomed(img, z, center=(0.5, 0.42)):
    w, h = img.size
    cw, ch = w / z, h / z
    x0 = min(max(center[0] * w - cw / 2, 0), w - cw)
    y0 = min(max(center[1] * h - ch / 2, 0), h - ch)
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)


def caption(frame):
    d = ImageDraw.Draw(frame)
    f1, f2 = ImageFont.truetype(FONT, 64), ImageFont.truetype(FONT, 44)
    for text, font, y in (("POV: あなたは冷蔵庫", f1, 150), ("POV: you are the fridge", f2, 235)):
        tw = d.textlength(text, font=font)
        d.text(((W - tw) / 2, y), text, font=font, fill="white", stroke_width=6, stroke_fill="black")
    return frame


def tone(sec, freq, amp, decay=0.0):
    t = np.arange(int(sec * SR)) / SR
    return amp * np.sin(2 * np.pi * freq * t) * np.exp(-decay * t)


def noise(sec, amp, decay):
    t = np.arange(int(sec * SR)) / SR
    return amp * np.random.default_rng(0).standard_normal(len(t)) * np.exp(-decay * t)


def build_audio(path):
    total = sum(s[0] for s in SHOTS)
    out = np.zeros(int(total * SR) + SR)
    t0 = 0.0
    for dur, kind, *_ in SHOTS:
        i = int(t0 * SR)
        if kind in ("open", "reveal"):
            seal = noise(0.12, 0.25, 30)                        # パッキンが離れる「ペタッ」
            hum = tone(dur, 110, 0.05) + tone(dur, 220, 0.02)   # 庫内のモーター音
            out[i:i + len(seal)] += seal
            out[i:i + len(hum)] += hum
        else:
            thud = tone(0.25, 70, 0.6, 18)  # 閉まる「バタン」
            thud[: int(0.08 * SR)] += noise(0.08, 0.3, 40)
            out[i:i + len(thud)] += thud
        t0 += dur
    out = out[: int(total * SR)]
    out /= max(1e-6, np.abs(out).max()) / 0.8
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


def main():
    duo = fridge_light(Image.open(DUO).convert("RGB"))
    reveal = fridge_light(Image.open(REVEAL).convert("RGB"))
    tmp = HERE / "_frames"
    tmp.mkdir(exist_ok=True)
    n = 0
    for dur, kind, z0, z1 in SHOTS:
        frames = int(round(dur * FPS))
        for k in range(frames):
            z = z0 + (z1 - z0) * k / max(frames - 1, 1)
            if kind == "closed":
                fr = Image.new("RGB", (W, H), (6, 6, 8))
            elif kind == "open":
                fr = zoomed(duo, z)
            else:
                fr = zoomed(reveal, z, center=(0.3, 0.45))
            caption(fr).save(tmp / f"{n:05d}.png")
            n += 1
    build_audio(HERE / "_audio.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%05d.png"),
                    "-i", str(HERE / "_audio.wav"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(HERE / "fridge_animatic.mp4")], check=True)
    for p in tmp.iterdir():
        p.unlink()
    tmp.rmdir()
    (HERE / "_audio.wav").unlink()
    print("wrote", HERE / "fridge_animatic.mp4", n, "frames")


if __name__ == "__main__":
    main()
