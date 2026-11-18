"""音なしで生成した動画に、合成した効果音を時刻指定で重ねる（クレジット節約用。Kling の音ありより1秒あたり0.5クレジット安い）。

使い方: python3 sfx.py in.mp4 out.mp4 "0.4:toss" "1.3:land" "2.0:steps" "3.0:cheer" "5.8:clatter"
音の種類: toss（投げる風切り音） / land（布が落ちる音） / steps（小走りの足音） / jump（踏み切り） /
          thud（着地） / cheer（歓声のような盛り上がり） / clatter（プラスチックが倒れる音） / pop（ポン） /
          splash（水をぶちまける音） / beat（煽りダンス用の2秒のリズム）
"""
import subprocess
import sys
import tempfile
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(t / max(attack, 1e-4), 1) * np.exp(-t / decay)


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def sound(kind):
    if kind == "toss":
        n = int(0.35 * SR)
        x = lowpass(rng.standard_normal(n), 30) * np.sin(np.linspace(0, np.pi, n)) * 0.5
    elif kind == "land":
        n = int(0.2 * SR)
        x = lowpass(rng.standard_normal(n), 60) * env(n, 0.005, 0.05) * 0.8
    elif kind == "steps":
        n = int(0.9 * SR)
        x = np.zeros(n)
        for i in range(5):
            s = int(i * 0.17 * SR)
            m = int(0.06 * SR)
            x[s:s + m] += lowpass(rng.standard_normal(m), 20) * env(m, 0.002, 0.015) * 0.6
    elif kind in ("jump", "thud"):
        n = int(0.3 * SR)
        t = np.arange(n) / SR
        x = np.sin(2 * np.pi * (90 if kind == "thud" else 140) * t) * env(n, 0.002, 0.06) * 0.9
        x[: int(0.03 * SR)] += lowpass(rng.standard_normal(int(0.03 * SR)), 10) * 0.4
    elif kind == "cheer":
        n = int(2.2 * SR)
        x = lowpass(rng.standard_normal(n), 8) - lowpass(rng.standard_normal(n), 80)
        x *= np.minimum(np.arange(n) / (0.25 * SR), 1) * np.exp(-np.arange(n) / (1.6 * SR)) * 0.35
    elif kind == "clatter":
        n = int(0.6 * SR)
        x = np.zeros(n)
        for i, s in enumerate((0, 0.09, 0.2, 0.33)):
            m = int(0.12 * SR)
            k = int(s * SR)
            t = np.arange(m) / SR
            x[k:k + m] += (np.sin(2 * np.pi * (520 - i * 60) * t) + lowpass(rng.standard_normal(m), 6) * 0.6) \
                * env(m, 0.001, 0.03) * (0.7 - i * 0.12)
    elif kind == "pop":
        n = int(0.15 * SR)
        t = np.arange(n) / SR
        x = np.sin(2 * np.pi * (700 - 2500 * t) * t) * env(n, 0.001, 0.03)
    elif kind == "splash":
        n = int(0.9 * SR)
        x = (lowpass(rng.standard_normal(n), 4) * 0.7 + lowpass(rng.standard_normal(n), 25)) * env(n, 0.01, 0.25) * 0.9
    elif kind == "beat":
        n = int(2.0 * SR)
        x = np.zeros(n)
        t = np.arange(int(0.18 * SR)) / SR
        kick = np.sin(2 * np.pi * (120 - 300 * t) * t) * env(len(t), 0.001, 0.05)
        hat = lowpass(rng.standard_normal(int(0.04 * SR)), 2) * env(int(0.04 * SR), 0.001, 0.01) * 0.3
        for i in range(8):
            k = int(i * 0.25 * SR)
            x[k:k + len(kick)] += kick if i % 2 == 0 else 0
            h = k + int(0.125 * SR)
            x[h:h + len(hat)] += hat
    else:
        sys.exit(f"unknown sound: {kind}")
    return x


def main():
    src, dst, *events = sys.argv[1:]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True, check=True).stdout)
    out = np.zeros(int(dur * SR) + SR)
    for e in events:
        at, kind = e.split(":")
        x = sound(kind)
        i = int(float(at) * SR)
        out[i:i + len(x)] += x[: max(0, len(out) - i)]
    out = out[: int(dur * SR)]
    out /= max(1e-6, np.abs(out).max()) / 0.85
    with tempfile.NamedTemporaryFile(suffix=".wav") as w:
        with wave.open(w.name, "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
            f.writeframes((out * 32767).astype(np.int16).tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", w.name, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", dst], check=True)
    print("wrote", dst)


if __name__ == "__main__":
    main()
