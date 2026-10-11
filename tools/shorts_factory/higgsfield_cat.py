"""Higgsfield (Kling 3.0 text-to-video) で「二足歩行で踊る猫」の試作動画を生成する。

認証: 環境変数 HF_API_KEY_ID / HF_API_KEY_SECRET、または Network secrets（api.higgsfield.ai 宛て Authorization: Key <id>:<secret>）
使い方:
  python3 tools/shorts_factory/higgsfield_cat.py --estimate            # 料金見積もりだけ
  python3 tools/shorts_factory/higgsfield_cat.py --out out/ --max-usd 1.5

方針:
- 実在の猫や既存キャラに似せない、オリジナルの3Dカートゥーン猫にする（肖像権・著作権対策）
- 生成音声はオフにし、自作のBGMを重ねる（AI生成音楽が既存曲に似るリスクを避ける）
- メタデータに AI 生成であることを記録する
"""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
import wave
from pathlib import Path

import numpy as np
import requests

API = "https://api.higgsfield.ai"
MODEL = "kling-video/v3.0/std/text-to-video"
SR = 44100
PROMPT = (
    "An original cute cartoon cat character in a stylized 3D animation style, chubby orange tabby with big round "
    "eyes and a tiny red scarf, standing upright on its two hind legs and dancing energetically: bouncing to the "
    "beat, swinging its arms, spinning once, then striking a happy pose facing the camera. Colorful pastel stage "
    "with soft spotlights, full body always visible, vertical framing, smooth motion, family friendly. "
    "No text, no logos, no people."
)


def auth():
    kid, sec = os.environ.get("HF_API_KEY_ID"), os.environ.get("HF_API_KEY_SECRET")
    if kid and sec:
        return {"Authorization": f"Key {kid}:{sec}", "Content-Type": "application/json"}
    # 環境変数がなければ、クラウド環境の Network secrets（api.higgsfield.ai 宛てに
    # Authorization: Key <id>:<secret> を付ける設定）が付与してくれる前提で送る
    return {"Content-Type": "application/json"}


def args_body(duration):
    return {"prompt": PROMPT, "duration": duration, "aspect_ratio": "9:16", "sound": "off", "cfg_scale": 0.5}


def estimate(duration):
    r = requests.post(f"{API}/estimate/{MODEL}", headers=auth(), json=args_body(duration), timeout=30)
    r.raise_for_status()
    return r.json()


def music(seconds, bpm=120, seed=11):
    """一定テンポの自作BGM（キック・スネア・ハイハット・ベース）。"""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    out = np.zeros(n)
    beat = 60 / bpm
    tt = np.arange(int(0.25 * SR)) / SR
    kick = 0.9 * np.sin(2 * np.pi * (50 + 120 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
    snare = 0.3 * rng.standard_normal(int(0.2 * SR)) * np.exp(-np.arange(int(0.2 * SR)) / SR * 22)
    hat = 0.1 * rng.standard_normal(int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / SR * 80)
    root, prog = 55 * 2 ** (rng.integers(0, 12) / 12), [0, 5, 7, 3]
    def put(at, sig):
        a = int(at * SR)
        if a < n:
            out[a:a + len(sig)] += sig[:n - a]
    for i in range(int(seconds / beat) + 1):
        t = i * beat
        put(t, kick)
        if i % 2:
            put(t, snare)
        put(t + beat / 2, hat)
        f = root * 2 ** (prog[(i // 4) % 4] / 12)
        bt = np.arange(int(beat * 0.9 * SR)) / SR
        put(t, 0.2 * (2 * (f * bt % 1) - 1) * np.exp(-bt * 5))
    out /= max(1e-9, np.abs(out).max()) / 0.85
    return (out * 32767).astype(np.int16)


def generate(outdir, duration, max_usd):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    est = estimate(duration)
    print("見積もり:", est)
    if float(est.get("usd", 0)) > max_usd:
        sys.exit(f"見積もり ${est.get('usd')} が上限 ${max_usd} を超えたので中止しました")
    h = {**auth(), "Idempotency-Key": str(uuid.uuid4())}
    r = requests.post(f"{API}/{MODEL}", headers=h, json=args_body(duration), timeout=60)
    r.raise_for_status()
    job = r.json()
    print("受付:", job["request_id"])
    (outdir / "higgsfield_request.json").write_text(json.dumps(job, indent=2))
    wait = 5
    while True:
        time.sleep(wait)
        s = requests.get(job["status_url"], headers=auth(), timeout=30).json()
        print("状態:", s["status"])
        if s["status"] == "completed":
            break
        if s["status"] in ("failed", "nsfw", "canceled"):
            sys.exit(f"生成できませんでした: {s}")
        wait = min(wait * 1.5, 30)
    raw = outdir / "hf_cat_raw.mp4"
    raw.write_bytes(requests.get(s["video"]["url"], timeout=300).content)
    # 自作BGMを重ねて、縦1080x1920に整える
    dur = float(subprocess.check_output(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(raw)]).decode().strip())
    wav = outdir / "hf_cat_bgm.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(music(dur).tobytes())
    vid = f"hfcat_{int(time.time())}"
    mp4 = outdir / f"{vid}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw), "-i", str(wav),
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-c:a", "aac", "-shortest", str(mp4)], check=True)
    wav.unlink()
    langs = {"en": "Dancing cat \U0001F431", "ja": "二足歩行で踊るネコ\U0001F431", "zh": "跳舞的猫\U0001F431",
             "es": "Gato bailarín \U0001F431"}
    desc = {"en": "Rate this dance 1-10 in the comments!", "ja": "このダンス、10点満点で何点？コメントしてね！",
            "zh": "这段舞蹈打几分？1-10分，评论告诉我！", "es": "¡Califica este baile del 1 al 10 en los comentarios!"}
    for lang, text in desc.items():
        (outdir / f"{vid}.{lang}.srt").write_text(f"1\n00:00:00,000 --> 00:00:{int(dur):02d},000\n{text}\n",
                                                  encoding="utf-8")
    meta = {"id": vid, "format": "higgsfield_cat", "model": MODEL, "request_id": job["request_id"],
            "estimate": est, "duration_s": round(dur, 1), "ai_generated": True, "prompt": PROMPT,
            "assets": "video generated by Higgsfield/Kling from an original prompt; music generated by "
                      "higgsfield_cat.py (original)",
            "title": {k: f"{v} #shorts" for k, v in langs.items()}, "description": desc,
            "hashtags": ["#shorts", "#cat", "#dance"]}
    (outdir / f"{vid}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(mp4)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    ap.add_argument("--duration", type=int, default=10)
    ap.add_argument("--max-usd", type=float, default=1.5, help="見積もりがこの金額を超えたら生成しない")
    ap.add_argument("--estimate", action="store_true")
    a = ap.parse_args()
    if a.estimate:
        print(estimate(a.duration))
    else:
        generate(a.out, a.duration, a.max_usd)
