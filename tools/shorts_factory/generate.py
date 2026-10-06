"""言語不要の「違うのはどれ？」3段階パズル・ショートを自動生成する。

分析(analysis/shorts_627)で伸びた「当てさせる」「段階型」「1秒で分かる」を満たす形式。
映像・音楽・効果音はすべてこのスクリプトが生成するオリジナル（第三者の素材を使わない）。

使い方: python3 tools/shorts_factory/generate.py --seed 123 --out out/
出力: <id>.mp4 / <id>.json(多言語メタデータ) / <id>.<lang>.srt
"""
import argparse
import colorsys
import json
import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LEVELS = [  # (グリッド数, 色差(明度), 考える秒数)
    (4, 0.16, 3.0),
    (6, 0.09, 3.5),
    (8, 0.045, 4.0),
]
REVEAL_S = 1.2
INTRO_S = 0.6
LANGS = {
    "en": ("Find the odd one out!", "Can you beat Level 3?", "Comment how many levels you solved!"),
    "ja": ("違うのはどれ？", "レベル3まで見つけられる？", "何問正解したかコメントしてね！"),
    "zh": ("找出不一样的那个！", "你能通过第3关吗？", "评论告诉我你答对了几关！"),
    "es": ("¡Encuentra el diferente!", "¿Puedes superar el nivel 3?", "¡Comenta cuántos niveles resolviste!"),
}


def font(size):
    return ImageFont.truetype(FONT, size)


def shape(draw, kind, cx, cy, r, fill, angle=0.0):
    if kind == "circle":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    elif kind == "square":
        draw.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=r * 0.3, fill=fill)
    else:  # arrow (向き違い問題用の三角形)
        pts = [(0, -1), (0.85, 0.75), (-0.85, 0.75)]
        a = math.radians(angle)
        draw.polygon([(cx + r * (x * math.cos(a) - y * math.sin(a)),
                       cy + r * (x * math.sin(a) + y * math.cos(a))) for x, y in pts], fill=fill)


class Puzzle:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.mode = self.rng.choice(["color", "color", "rotate"])
        self.kind = "arrow" if self.mode == "rotate" else self.rng.choice(["circle", "square"])
        self.hue = self.rng.random()
        self.bg = tuple(int(c * 255) for c in colorsys.hls_to_rgb((self.hue + 0.5) % 1, 0.12, 0.35))
        self.levels = []
        for n, delta, think in LEVELS:
            odd = (self.rng.randrange(n), self.rng.randrange(n))
            self.levels.append(dict(n=n, delta=delta, think=think, odd=odd,
                                    base_angle=self.rng.choice([0, 90, 180, 270])))

    def timeline(self):
        t, segs = INTRO_S, []
        for i, lv in enumerate(self.levels):
            segs.append((i, t, t + lv["think"], t + lv["think"] + REVEAL_S))
            t += lv["think"] + REVEAL_S
        return segs, t + 0.8

    def frame(self, t, segs, total):
        img = Image.new("RGB", (W, H), self.bg)
        d = ImageDraw.Draw(img)
        cur = next((s for s in segs if s[1] - INTRO_S <= t < s[3]), segs[-1])
        i, start, think_end, end = cur
        lv = self.levels[i]
        # 上部: レベル表示（数字と記号だけ = 言語不要）
        d.text((W / 2, 230), f"LV {i + 1}/3", font=font(110), fill="white", anchor="mm")
        for k in range(3):
            col = "white" if k <= i else (90, 90, 90)
            d.ellipse([W / 2 - 75 + k * 60, 320, W / 2 - 45 + k * 60, 350], fill=col)
        # グリッド
        n, area = lv["n"], 960
        cell = area / n
        x0, y0 = (W - area) / 2, 520
        base_l = 0.55
        base = colorsys.hls_to_rgb(self.hue, base_l, 0.75)
        odd_c = colorsys.hls_to_rgb(self.hue, base_l + lv["delta"], 0.75)
        for gy in range(n):
            for gx in range(n):
                is_odd = (gx, gy) == lv["odd"]
                c = odd_c if (is_odd and self.mode == "color") else base
                angle = lv["base_angle"] + (25 + 20 * (3 - i) if is_odd and self.mode == "rotate" else 0)
                shape(d, self.kind, x0 + cell * (gx + .5), y0 + cell * (gy + .5), cell * 0.38,
                      tuple(int(v * 255) for v in c), angle)
        # 残り時間バー or 正解表示
        if t < think_end:
            p = max(0.0, min(1.0, (think_end - t) / lv["think"]))
            d.rounded_rectangle([90, 1600, 90 + 900 * p, 1640], radius=20, fill="white")
            d.text((W / 2, 1760), str(math.ceil(min(think_end - t, lv["think"]))), font=font(120), fill="white", anchor="mm")
        else:
            gx, gy = lv["odd"]
            cx, cy = x0 + cell * (gx + .5), y0 + cell * (gy + .5)
            pulse = 1 + 0.15 * math.sin((t - think_end) * 12)
            r = cell * 0.55 * pulse
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 230, 0), width=14)
            d.text((W / 2, 1720), "✓", font=font(200), fill=(255, 230, 0), anchor="mm")
        return img


def music(total, seed, segs):
    """オリジナルのチップチューン風BGM + カウント音 + 正解音を生成する。"""
    rng = np.random.default_rng(seed)
    t = np.arange(int(total * SR)) / SR
    root = 220 * 2 ** (rng.integers(0, 7) / 12)
    scale = [0, 2, 4, 7, 9, 12, 14, 16]
    bpm = int(rng.choice([118, 124, 128, 132]))
    step = 60 / bpm / 2
    pattern = rng.choice(scale, 16)
    out = np.zeros_like(t)
    for k in range(int(total / step)):
        f = root * 2 ** (pattern[k % 16] / 12)
        a, b = int(k * step * SR), int((k + 0.9) * step * SR)
        tt = t[a:b] - t[a]
        env = np.exp(-tt * 9)
        out[a:b] += 0.18 * np.sign(np.sin(2 * np.pi * f * tt)) * env  # 矩形波メロディ
        if k % 4 == 0:
            out[a:b] += 0.22 * np.sin(2 * np.pi * root / 2 * tt) * np.exp(-tt * 4)  # ベース
    def add(at, freq, dur, vol):
        a = int(at * SR)
        tt = np.arange(int(dur * SR)) / SR
        seg = vol * np.sin(2 * np.pi * freq * tt) * np.exp(-tt * 18)
        out[a:a + len(seg)] += seg[:len(out) - a]
    for _, start, think_end, _ in segs:
        for s in np.arange(think_end - 1, start - 0.01, -1.0):
            add(s, 1500, 0.06, 0.35)  # チック音
        for j, fr in enumerate([880, 1175, 1760]):
            add(think_end + j * 0.07, fr, 0.4, 0.4)  # 正解音
    out /= max(1e-9, np.abs(out).max()) / 0.8
    return (out * 32767).astype(np.int16)


def srt(segs, lang):
    a, b, c = LANGS[lang]
    def ts(x):
        return f"00:00:{int(x):02d},{int((x % 1) * 1000):03d}"
    lines = [(0, segs[0][2], a), (segs[1][1], segs[2][1], b), (segs[2][1], segs[2][3] + 0.8, c)]
    return "\n".join(f"{k + 1}\n{ts(s)} --> {ts(e)}\n{txt}\n" for k, (s, e, txt) in enumerate(lines))


def build(seed, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    vid = f"oddone_{seed}"
    pz = Puzzle(seed)
    segs, total = pz.timeline()
    wav = outdir / f"{vid}.wav"
    import wave
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(music(total, seed, segs).tobytes())
    mp4 = outdir / f"{vid}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20",
                           "-c:a", "aac", "-b:a", "128k", "-shortest", str(mp4)], stdin=subprocess.PIPE)
    for f in range(int(total * FPS)):
        ff.stdin.write(pz.frame(f / FPS, segs, total).tobytes())
    ff.stdin.close()
    ff.wait()
    wav.unlink()
    for lang in LANGS:
        (outdir / f"{vid}.{lang}.srt").write_text(srt(segs, lang), encoding="utf-8")
    meta = {
        "id": vid, "seed": seed, "mode": pz.mode, "duration_s": round(total, 1),
        "answers": [lv["odd"] for lv in pz.levels],
        "assets": "all visuals, music and sound effects generated by generate.py (original)",
        # 「Only 1%」のような根拠のない数字は誇大表示になるので使わない
        "title": {"en": "Can you find Level 3? \U0001F440 #shorts", "ja": "レベル3、見つけられる？\U0001F440 #shorts",
                  "zh": "第3关你能找到吗？\U0001F440 #shorts", "es": "¿Encuentras el nivel 3? \U0001F440 #shorts"},
        "description": {k: f"{v[0]} {v[1]} {v[2]}" for k, v in LANGS.items()},
        "hashtags": ["#shorts", "#puzzle", "#brainteaser"],
    }
    (outdir / f"{vid}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return mp4


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=random.randrange(10**6))
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    print(build(a.seed, a.out))
