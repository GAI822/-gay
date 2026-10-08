"""オリジナルキャラ「コウイカ」が、だんだん速くなる自作曲に合わせて踊るアニメ・ショートを生成する。

分析(analysis/shorts_627)の「段階型（3 Levels）」「1秒で分かる」「言語不要」を、
ダンス×キャラクターに当てはめた形式。キャラ・振付・音楽・効果音はすべてこのスクリプトが生成する。
コウイカは体色を変える生き物なので、ビートごとの色変化をキャラの見せ場にしている。

使い方: python3 tools/shorts_factory/dance.py --seed 123 --out out/
出力: <id>.mp4 / <id>.json(多言語メタデータ) / <id>.<lang>.srt
"""
import argparse
import colorsys
import json
import math
import random
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS, SR = 1080, 1920, 30, 44100
SS = 2  # キャラは2倍で描いて縮小（アンチエイリアス）
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BEATS_PER_STAGE = 12
INTRO, OUTRO = 0.3, 0.9
MOVES = ["bounce", "sway", "wave", "spin", "jump", "wiggle"]

# タイトルは毎回変える（同じタイトルの量産はYouTubeの「量産型コンテンツ」判定のリスク）
TITLES = [
    {"en": "Cuttlefish dance, but it gets faster \U0001F991", "ja": "だんだん速くなるコウイカダンス\U0001F991",
     "zh": "越来越快的墨鱼舞\U0001F991", "es": "El baile de la sepia, cada vez más rápido \U0001F991"},
    {"en": "Speed x3 dance \U0001F991 can you keep up?", "ja": "スピード3倍ダンス\U0001F991ついてこれる？",
     "zh": "三倍速舞蹈\U0001F991你跟得上吗？", "es": "Baile a velocidad x3 \U0001F991 ¿puedes seguirlo?"},
    {"en": "Watch its colors at x3 \U0001F991", "ja": "3倍速で色が変わりまくる\U0001F991",
     "zh": "三倍速时它的颜色变了\U0001F991", "es": "Mira sus colores en x3 \U0001F991"},
    {"en": "Level 1 vs Level 3 dance \U0001F991", "ja": "レベル1とレベル3のダンス\U0001F991",
     "zh": "第1关和第3关的舞蹈\U0001F991", "es": "Baile nivel 1 vs nivel 3 \U0001F991"},
]
DESC = {
    "en": "Which speed was your favorite: x1, x2 or x3? Comment below!",
    "ja": "x1・x2・x3、どのスピードが好き？コメントで教えてね！",
    "zh": "x1、x2、x3，你最喜欢哪个速度？在评论区告诉我！",
    "es": "¿Qué velocidad te gustó más: x1, x2 o x3? ¡Coméntalo!",
}
SUBS = {
    "en": ("Watch it speed up!", "Faster...", "Which speed was best? x1 / x2 / x3"),
    "ja": ("だんだん速くなるよ！", "もっと速く…", "どのスピードが好き？ x1 / x2 / x3"),
    "zh": ("看它越跳越快！", "更快了……", "你喜欢哪个速度？x1 / x2 / x3"),
    "es": ("¡Mira cómo acelera!", "Más rápido...", "¿Cuál velocidad fue mejor? x1 / x2 / x3"),
}


def hsv(h, s, v, a=255):
    r, g, b = colorsys.hsv_to_rgb(h % 1, s, v)
    return (int(r * 255), int(g * 255), int(b * 255), a)


class Show:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        bpm0 = self.rng.choice([96, 100, 104])
        self.bpms = [bpm0, int(bpm0 * 1.35), int(bpm0 * 1.75)]
        self.moves = [self.rng.sample(MOVES, 2) for _ in range(3)]
        self.hue = self.rng.random()
        self.bg_hue = (self.hue + 0.5) % 1
        # 拍の時刻表（ステージごとにテンポが上がる）
        self.beats, t = [], INTRO
        self.stage_start = []
        for bpm in self.bpms:
            self.stage_start.append(t)
            for _ in range(BEATS_PER_STAGE):
                self.beats.append((t, 60 / bpm))
                t += 60 / bpm
        self.end_dance = t
        self.total = t + OUTRO
        self.bubbles = [(self.rng.random() * W, self.rng.random() * H, 6 + self.rng.random() * 18,
                         0.3 + self.rng.random()) for _ in range(28)]

    def beat_at(self, t):
        """(何拍目, 拍内の位相0..1, ステージ番号)"""
        if t < INTRO:
            return 0, 0.0, 0
        for i, (bt, dur) in enumerate(self.beats):
            if t < bt + dur:
                return i, (t - bt) / dur, min(2, i // BEATS_PER_STAGE)
        return len(self.beats) - 1, 1.0, 2

    # ---- 描画 ----
    def background(self, t, beat, phase, stage):
        img = Image.new("RGB", (W, H))
        top, bot = hsv(self.bg_hue, 0.55, 0.22 + 0.06 * stage), hsv(self.bg_hue + 0.08, 0.7, 0.10)
        grad = np.linspace(0, 1, H)[:, None]
        arr = (np.array(top[:3]) * (1 - grad) + np.array(bot[:3]) * grad).astype(np.uint8)
        img = Image.fromarray(np.repeat(arr[:, None, :], W, axis=1).reshape(H, W, 3))
        d = ImageDraw.Draw(img, "RGBA")
        # 拍ごとに広がるリング
        r = 200 + phase * 700
        a = int(110 * (1 - phase))
        d.ellipse([W / 2 - r, 1050 - r, W / 2 + r, 1050 + r], outline=hsv(self.hue + beat * 0.13, 0.5, 1, a), width=10)
        for x, y, s, sp in self.bubbles:
            yy = (y - t * 90 * sp * (1 + stage * 0.6)) % H
            d.ellipse([x - s, yy - s, x + s, yy + s], outline=(255, 255, 255, 70), width=3)
        return img

    def character(self, t, beat, phase, stage, frozen=False):
        S = SS
        cw, ch = 1080 * S, 1400 * S
        layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        move = self.moves[stage][(beat // 4) % 2]
        hit = max(0.0, math.cos(math.pi * phase)) ** 3 if not frozen else 0  # 拍頭で1
        r = 300 * S
        cx, cy = cw / 2, ch * 0.42
        sx, sy = 1 + 0.10 * hit, 1 - 0.12 * hit  # つぶれと伸び
        ang = 0.0
        if move == "sway":
            cx += math.sin(math.pi * (beat + phase)) * 70 * S
            ang = math.sin(math.pi * (beat + phase)) * 10
        elif move == "jump" and beat % 2 == 1:
            cy -= math.sin(math.pi * phase) * 150 * S
        elif move == "spin":
            ang = 360 * ((beat % 4) + phase) / 4 if beat % 4 >= 2 else 0
        elif move == "wiggle":
            cx += math.sin(phase * math.pi * 4) * 25 * S
        col = self.hue + beat * 0.11 + (stage * 0.05 if not frozen else 0)
        body = hsv(col, 0.55, 1.0)
        dark = hsv(col + 0.04, 0.75, 0.75)
        bw, bh = 0.72 * r * sx, 0.95 * r * sy
        # 腕8本（先に描いて胴体の下に）
        base_y = cy + 0.62 * r * sy
        for k in range(8):
            spread = (k - 3.5) / 3.5
            a0 = math.radians(90 + spread * 62)
            amp = {"wave": 0.9, "wiggle": 0.6, "spin": 0.5}.get(move, 0.35)
            lift = -0.9 * hit if move in ("wave", "bounce") and (k + beat) % 2 == 0 else 0
            px, py = cx + spread * 0.5 * bw / r * r, base_y - 0.12 * r
            for i in range(14):
                a = a0 + amp * math.sin(t * 6 * (1 + stage * 0.5) - i * 0.45 + k) * (i / 14) + lift * (i / 14) * spread
                nx, ny = px + math.cos(a) * 0.075 * r, py + math.sin(a) * 0.075 * r
                w = (0.17 - 0.0095 * i) * r
                d.line([px, py, nx, ny], fill=dark, width=int(w))
                d.ellipse([nx - w / 2, ny - w / 2, nx + w / 2, ny + w / 2], fill=dark)
                px, py = nx, ny
        # 胴体（外套膜）とひれ
        fin = 0.12 * r * (1 + 0.4 * math.sin(t * 10))
        d.ellipse([cx - bw - fin, cy - bh * 0.95, cx + bw + fin, cy + bh * 0.9], fill=hsv(col + 0.5, 0.35, 1.0, 200))
        d.ellipse([cx - bw, cy - bh, cx + bw, cy + bh], fill=body)
        # 体色の縞（コウイカの色変化）を胴体の形でくり抜いて重ねる
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).ellipse([cx - bw, cy - bh, cx + bw, cy + bh], fill=255)
        stripes = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stripes)
        off = (t * 220 * (1 + stage)) % (0.5 * r)
        for j in range(-2, 8):
            y0 = cy - bh + j * 0.5 * r + off
            sd.ellipse([cx - bw * 1.2, y0, cx + bw * 1.2, y0 + 0.18 * r], fill=hsv(col + 0.33, 0.6, 0.95, 150))
        stripes.putalpha(ImageChops.multiply(stripes.getchannel("A"), mask))
        layer.alpha_composite(stripes)
        d = ImageDraw.Draw(layer)
        # 目（W字の瞳はコウイカの特徴）とまばたき
        blink = (beat % 8 == 7 and phase < 0.3) or frozen
        for side in (-1, 1):
            ex, ey, er = cx + side * 0.34 * r, cy + 0.32 * r * sy, 0.2 * r
            if blink:
                d.arc([ex - er, ey - er * 0.5, ex + er, ey + er * 0.5], 200, 340, fill=(40, 30, 50), width=int(0.04 * r))
                continue
            d.ellipse([ex - er, ey - er, ex + er, ey + er], fill="white")
            pr = er * 0.62
            d.ellipse([ex - pr, ey - pr * 0.8, ex + pr, ey + pr * 0.8], fill=(35, 25, 45))
            d.line([ex - pr * 0.6, ey - pr * 0.1, ex - pr * 0.3, ey + pr * 0.35, ex, ey, ex + pr * 0.3, ey + pr * 0.35,
                    ex + pr * 0.6, ey - pr * 0.1], fill=(240, 220, 120), width=int(0.025 * r))
            d.ellipse([ex - pr * 0.75, ey - pr * 0.85, ex - pr * 0.25, ey - pr * 0.35], fill="white")
        # ほっぺと口
        for side in (-1, 1):
            hx, hy = cx + side * 0.55 * r, cy + 0.55 * r * sy
            d.ellipse([hx - 0.09 * r, hy - 0.05 * r, hx + 0.09 * r, hy + 0.05 * r], fill=(255, 120, 150, 160))
        mo = 0.05 * r * (1 + 2 * hit)
        d.ellipse([cx - 0.07 * r, cy + 0.55 * r * sy, cx + 0.07 * r, cy + 0.55 * r * sy + mo], fill=(90, 30, 50))
        if ang:
            layer = layer.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
        return layer.resize((cw // S, ch // S), Image.LANCZOS)

    def frame(self, t):
        beat, phase, stage = self.beat_at(t)
        frozen = t >= self.end_dance
        img = self.background(t, beat, phase if not frozen else 1.0, stage)
        ch = self.character(t, beat, phase, stage, frozen=frozen)
        shadow = ch.split()[3].filter(ImageFilter.GaussianBlur(18)).point(lambda a: a * 0.35)
        img.paste((0, 0, 0), (8, 418), shadow)
        img.paste(ch, (0, 390), ch)
        d = ImageDraw.Draw(img, "RGBA")
        f = ImageFont.truetype(FONT, 150)
        label = f"x{stage + 1}"
        # ステージ切り替わり直後は大きく表示（数字だけ = 言語不要）
        since = t - self.stage_start[stage]
        size = int(150 + 120 * max(0.0, 1 - since * 3))
        d.text((W / 2, 300), label, font=ImageFont.truetype(FONT, size), fill="white", anchor="mm",
               stroke_width=10, stroke_fill=(0, 0, 0, 160))
        for k in range(3):
            c = "white" if k <= stage else (255, 255, 255, 70)
            d.rounded_rectangle([W / 2 - 150 + k * 105, 410, W / 2 - 60 + k * 105, 428], radius=9, fill=c)
        if frozen:
            a = int(255 * max(0.0, 1 - (t - self.end_dance) * 4))
            d.rectangle([0, 0, W, H], fill=(255, 255, 255, a))
        return img

    # ---- 音楽 ----
    def music(self, seed):
        rng = np.random.default_rng(seed)
        n = int(self.total * SR)
        out = np.zeros(n)
        root = 55 * 2 ** (rng.integers(0, 12) / 12)
        prog = rng.choice([[0, 5, 7, 3], [0, 7, 9, 5], [0, 3, 5, 7]])
        lead_scale = [0, 3, 5, 7, 10, 12, 15]
        melody = rng.choice(lead_scale, 8)

        def put(at, sig):
            a = int(at * SR)
            out[a:a + len(sig)] += sig[:max(0, n - a)]

        def tone(freq, dur, kind="sine", decay=6.0, vol=0.3):
            tt = np.arange(int(dur * SR)) / SR
            ph = 2 * np.pi * freq * tt
            w = {"sine": np.sin(ph), "saw": 2 * (freq * tt % 1) - 1, "sq": np.sign(np.sin(ph))}[kind]
            return vol * w * np.exp(-tt * decay)

        tt = np.arange(int(0.25 * SR)) / SR
        kick = 0.9 * np.sin(2 * np.pi * (50 + 120 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
        noise = rng.standard_normal(int(0.2 * SR))
        snare = 0.35 * noise * np.exp(-np.arange(len(noise)) / SR * 22)
        hat = 0.12 * rng.standard_normal(int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / SR * 80)
        for i, (bt, dur) in enumerate(self.beats):
            put(bt, kick)
            if i % 2 == 1:
                put(bt, snare)
            put(bt + dur / 2, hat)
            chord = root * 2 ** (prog[(i // 4) % 4] / 12)
            put(bt, tone(chord, dur * 0.9, "saw", 5, 0.18))
            put(bt + dur / 2, tone(chord * 2, dur * 0.4, "saw", 9, 0.08))
            put(bt, tone(chord * 4 * 2 ** (melody[i % 8] / 12), dur * 0.5, "sq", 10, 0.07))
        # 0秒目の「音のフック」: スクロールを止めるための強めのヒット
        put(0, kick * 1.2)
        put(0, tone(root * 8, 0.5, "sq", 6, 0.25) + tone(root * 12, 0.5, "sine", 5, 0.3))
        for s in self.stage_start[1:]:  # ステージ切替の上昇音
            tt = np.arange(int(0.35 * SR)) / SR
            put(s - 0.35, 0.25 * np.sin(2 * np.pi * (300 + 1500 * tt / 0.35) * tt) * (tt / 0.35))
        put(self.end_dance, tone(root * 8, 0.8, "sine", 4, 0.4) + tone(root * 12, 0.8, "sine", 4, 0.25))
        out /= max(1e-9, np.abs(out).max()) / 0.85
        return (out * 32767).astype(np.int16)


def srt(show, lang):
    a, b, c = SUBS[lang]
    def ts(x):
        return f"00:00:{int(x):02d},{int((x % 1) * 1000):03d}"
    s = show.stage_start
    lines = [(0, s[1], a), (s[1], s[2], b), (s[2], show.total, c)]
    return "\n".join(f"{k + 1}\n{ts(x)} --> {ts(y)}\n{txt}\n" for k, (x, y, txt) in enumerate(lines))


def build(seed, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    vid = f"cuttle_{seed}"
    show = Show(seed)
    wav = outdir / f"{vid}.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(show.music(seed).tobytes())
    mp4 = outdir / f"{vid}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "20",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", str(mp4)], stdin=subprocess.PIPE)
    for f in range(int(show.total * FPS)):
        ff.stdin.write(show.frame(f / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    wav.unlink()
    for lang in SUBS:
        (outdir / f"{vid}.{lang}.srt").write_text(srt(show, lang), encoding="utf-8")
    title = show.rng.choice(TITLES)
    meta = {
        "id": vid, "seed": seed, "format": "cuttlefish_dance", "bpms": show.bpms, "moves": show.moves,
        "duration_s": round(show.total, 1),
        "assets": "character, choreography, music and sound effects generated by dance.py (original)",
        "title": {k: f"{v} #shorts" for k, v in title.items()},
        "description": DESC,
        "hashtags": ["#shorts", "#dance", "#animation"],
    }
    (outdir / f"{vid}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return mp4


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=random.randrange(10**6))
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    print(build(a.seed, a.out))
