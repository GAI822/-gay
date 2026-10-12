"""猫の鳴き声風の歌声で「猫ふんじゃった（ノミのワルツ）」を4声（S/A/T/B）合唱する音源を合成する。

メロディーは作曲者不詳の古い曲で著作権の保護期間外とされる。日本語歌詞（著作物）は使わず「にゃ」で歌う。
声は倍音の重ね合わせで作り、母音のフォルマントを「ん→ぃ→あ（→お）」と動かして猫らしくする。

使い方: python3 tools/shorts_factory/meowchoir.py out.wav [--tempo 160]
"""
import argparse
import wave

import numpy as np

SR = 44100
# 音名 → MIDI番号（変ト長調＝黒鍵のキー）
N = {"Gb2": 42, "Db3": 49, "F3": 53, "Ab3": 56, "Bb3": 58, "Cb4": 59, "Db4": 61, "Eb4": 63,
     "Gb4": 66, "Ab4": 68, "Bb4": 70, "Db5": 73, "Eb5": 75}


def hz(note):
    return 440.0 * 2 ** ((N[note] - 69) / 12)


# (音名 or None=休符, 拍数)。3/4拍子。1小節目の前にアウフタクト（8分音符2つ）
SOPRANO = [("Eb5", .5), ("Db5", .5),
           ("Gb4", 1), ("Gb4", 1), ("Eb5", .5), ("Db5", .5),
           ("Gb4", 1), ("Gb4", 1), ("Eb5", .5), ("Db5", .5),
           ("Gb4", 1), ("Db5", 1), ("Bb4", 1),
           ("Gb4", 2.5)]


def accompaniment(bars=4, final_beats=2.5):
    """ワルツの伴奏: バスは1拍目、アルトとテノールは2・3拍目。アウフタクトの拍は属和音寄りにする。"""
    alto, tenor, bass = [(None, 1)], [(None, 1)], [(None, 1)]  # アウフタクト分は休み
    for b in range(bars - 1):
        bass += [("Gb2" if b != 2 else "Db3", 1), (None, 2)]
        alto += [(None, 1), ("Db4", 1), ("Cb4" if b < 2 else "Db4", 1)]
        tenor += [(None, 1), ("Bb3", 1), ("Ab3" if b < 2 else "Bb3", 1)]
    bass += [("Gb2", final_beats)]
    alto += [("Db4", final_beats)]
    tenor += [("Bb3", final_beats)]
    return alto, tenor, bass


VOICES = {  # フォルマントの倍率（小さい猫ほど高い）、明るさ、音量、左右の位置
    "S": dict(formant=1.18, bright=1.0, gain=1.0, pan=-0.25),
    "A": dict(formant=1.06, bright=0.9, gain=0.75, pan=0.25),
    "T": dict(formant=0.94, bright=0.8, gain=0.75, pan=-0.15),
    "B": dict(formant=0.82, bright=0.65, gain=0.9, pan=0.15),
}


def meow(f0, dur, voice, rng):
    v = VOICES[voice]
    n = int(dur * SR)
    t = np.arange(n) / SR
    # 音の高さ: 下からすくい上げ → ビブラート → 長い音は最後に少し下がる（「にゃ〜お」）
    scoop = 1 - 0.12 * np.exp(-t / 0.035)
    vib = 1 + 0.012 * np.sin(2 * np.pi * 5.6 * t) * np.clip((t - 0.12) / 0.1, 0, 1)
    tail = 1 - 0.08 * np.clip((t - (dur - 0.15)) / 0.15, 0, 1) if dur > 0.6 else 1.0
    f = f0 * scoop * vib * tail
    phase = 2 * np.pi * np.cumsum(f) / SR
    # 母音: ん(250/1500) → ぃ(400/2300) → あ(850/1400) → お(500/900, 長い音のみ)
    k = v["formant"]
    f1 = np.interp(t, [0, .04, .09, .16, max(.17, dur - .2), dur], [250, 400, 700, 850, 850, 500 if dur > .6 else 850]) * k
    f2 = np.interp(t, [0, .04, .09, .16, max(.17, dur - .2), dur], [1500, 2300, 1800, 1400, 1400, 900 if dur > .6 else 1400]) * k
    out = np.zeros(n)
    for h in range(1, int(5000 / f0) + 1):
        fh = f * h
        env = (np.exp(-((fh - f1) / 160) ** 2) + 0.7 * np.exp(-((fh - f2) / 260) ** 2)
               + 0.25 * np.exp(-((fh - 3200 * k) / 400) ** 2)) * (h ** -0.6) * v["bright"] ** (h / 6)
        out += env * np.sin(h * phase)
    nasal = np.clip(t / 0.04, 0, 1) * 0.6 + 0.4          # 頭の「ん」は少し弱く
    amp = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.05) * nasal
    breath = 0.02 * rng.standard_normal(n) * amp
    return (out / (np.abs(out).max() + 1e-9) * amp + breath) * v["gain"]


def render(part, voice, beat, rng):
    total = sum(b for _, b in part) * beat
    y = np.zeros(int(total * SR) + SR)
    pos = 0.0
    for note, beats in part:
        if note:
            dur = beats * beat * (0.92 if beats < 2 else 0.98)
            s = meow(hz(note), dur, voice, rng)
            a = int(pos * SR)
            y[a:a + len(s)] += s
        pos += beats * beat
    return y


def reverb(x, seconds=1.2, mix=0.22, rng=None):
    rng = rng or np.random.default_rng(0)
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 4.5)
    wet = np.fft.irfft(np.fft.rfft(x, len(x) + n) * np.fft.rfft(ir, len(x) + n))[:len(x)]
    wet /= np.abs(wet).max() + 1e-9
    return (1 - mix) * x / (np.abs(x).max() + 1e-9) + mix * wet


def build(path, tempo=160):
    rng = np.random.default_rng(4353)
    beat = 60 / tempo
    alto, tenor, bass = accompaniment()
    parts = {"S": SOPRANO, "A": alto, "T": tenor, "B": bass}
    length = max(int(sum(b for _, b in p) * beat * SR) + SR for p in parts.values())
    left, right = np.zeros(length), np.zeros(length)
    for name, part in parts.items():
        y = render(part, name, beat, rng)[:length]
        y = np.pad(y, (0, length - len(y)))
        pan = VOICES[name]["pan"]
        left += y * (1 - pan) / 2
        right += y * (1 + pan) / 2
    left, right = reverb(left, rng=rng), reverb(right, rng=np.random.default_rng(7))
    end = int((sum(b for _, b in SOPRANO) * beat + 0.6) * SR)
    st = np.stack([left[:end], right[:end]], 1)
    st = st / (np.abs(st).max() + 1e-9) * 0.8
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    return end / SR


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--tempo", type=float, default=160)
    a = ap.parse_args()
    print(f"{a.out} {build(a.out, a.tempo):.2f}s")
