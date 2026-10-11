"""ミーム動画風のアップテンポBGMを自作する（既存曲・サンプルは使わない）。

構成: 静かな導入 → ドロップ直前に「レコード停止」+ 一瞬の無音 → ドロップ（四つ打ち・カウベル・
うねるベース・覚えやすい2小節フレーズ）。ドロップ後は区間ごとにテンポを上げられる（x1/x2/x3用）。

使い方（ライブラリ）: memebeat.render(total_s, drop_at, sections=[(start, bpm), ...], seed=1) -> int16配列
"""
import numpy as np

SR = 44100


def _env(n, decay):
    return np.exp(-np.arange(n) / SR * decay)


def render(total, drop_at, sections, seed=1):
    rng = np.random.default_rng(seed)
    n = int(total * SR)
    out = np.zeros(n)

    def put(at, sig, gain=1.0):
        a = int(at * SR)
        if 0 <= a < n:
            out[a:a + len(sig)] += gain * sig[:n - a]

    def osc(freq, dur, kind="saw"):
        t = np.arange(int(dur * SR)) / SR
        if kind == "saw":
            return 2 * (freq * t % 1) - 1
        if kind == "sq":
            return np.sign(np.sin(2 * np.pi * freq * t))
        return np.sin(2 * np.pi * freq * t)

    t = np.arange(int(0.3 * SR)) / SR
    kick = np.sin(2 * np.pi * (45 + 160 * np.exp(-t * 35)) * t) * np.exp(-t * 8)
    clap = rng.standard_normal(int(0.15 * SR)) * _env(int(0.15 * SR), 28)
    hat = rng.standard_normal(int(0.04 * SR)) * _env(int(0.04 * SR), 90)
    # カウベル（2つの矩形波を重ねた金属音）
    cow = (osc(540, 0.18, "sq") + osc(800, 0.18, "sq")) * _env(int(0.18 * SR), 18) * 0.5

    root = 55 * 2 ** (rng.integers(0, 7) / 12)
    scale = [0, 3, 5, 7, 10, 12]
    hook = rng.choice(scale, 8)  # 2小節の覚えやすいフレーズ
    hook[0], hook[4] = 0, 7

    # 導入: 軽いプラック + だんだん上がるライザー
    beat0 = 60 / sections[0][1]
    k = 0
    while k * beat0 < drop_at - 0.5:
        tt = k * beat0
        put(tt, osc(root * 4 * 2 ** (hook[k % 8] / 12), beat0 * 0.4, "sin") * _env(int(beat0 * 0.4 * SR), 12), 0.25)
        put(tt + beat0 / 2, hat, 0.06)
        k += 1
    rl = max(0.2, drop_at - 0.35)
    tt = np.arange(int(rl * SR)) / SR
    riser = rng.standard_normal(len(tt)) * (tt / rl) ** 2 * 0.15
    put(0, riser)
    # レコード停止（音程が落ちて止まる）→ 一瞬の無音 → ドロップ
    st = np.arange(int(0.3 * SR)) / SR
    stop = np.sin(2 * np.pi * np.cumsum(root * 4 * (1 - st / 0.3) ** 2) / SR) * (1 - st / 0.3) * 0.4
    put(drop_at - 0.45, stop)

    # ドロップ以降: 区間ごとのテンポで刻む
    bounds = [s for s, _ in sections] + [total]
    for i, (start, bpm) in enumerate(sections):
        start = max(start, drop_at)
        beat = 60 / bpm
        b = 0
        while start + b * beat < bounds[i + 1]:
            tt = start + b * beat
            put(tt, kick, 0.9)
            if b % 2 == 1:
                put(tt, clap, 0.35)
            put(tt + beat / 2, hat, 0.12)
            if b % 4 in (0, 3):
                put(tt + beat * 0.75, cow, 0.18)
            # うねるベース（1拍ごとに音量が揺れる）
            f = root * 2 ** (hook[(b // 2) % 8] / 12)
            seg = osc(f, beat * 0.95, "saw")
            seg *= 0.5 + 0.5 * np.sin(np.linspace(0, 2 * np.pi, len(seg)))
            put(tt, seg, 0.22)
            put(tt, osc(f * 4, beat * 0.45, "sq") * _env(int(beat * 0.45 * SR), 9), 0.08)
            b += 1
    # ポンプ感（キックに合わせて全体を少し沈める）は省略し、最後に正規化
    out /= max(1e-9, np.abs(out).max()) / 0.85
    return (out * 32767).astype(np.int16)
