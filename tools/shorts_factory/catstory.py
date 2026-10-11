"""猫ダンスの「ストーリー型」ショートを組み立てる（スピードアップなし）。

構成: 立ち上がり＋不機嫌顔 → 顔アップ → 二足歩行 → ポップダンス → ブレイクダンス → 決め技＋ドヤ顔
各AIクリップは前の場面の最後のコマから生成しているので、同じ猫のままつながる。

使い方:
  python3 tools/shorts_factory/catstory.py --standup s.mp4 --walk w.mp4 --pop p.mp4 --brk b.mp4 \
      --id catstory_001 --out out/
"""
import argparse
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

import memebeat

FIT = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30"
TITLE = {"en": "He stood up and chose violence (dance) \U0001F610 #shorts",
         "ja": "立ち上がった猫、本気で踊り出す\U0001F610 #shorts",
         "zh": "猫站起来后开始认真跳舞\U0001F610 #shorts",
         "es": "El gato se levantó y bailó en serio \U0001F610 #shorts"}
DESC = {"en": "Popping, breaking, and that final face. Rate it 1-10! (AI-generated video)",
        "ja": "ポップ、ブレイク、最後のドヤ顔。10点満点で何点？（AI生成の映像です）",
        "zh": "机械舞、霹雳舞，还有最后的得意脸。打几分？（AI生成视频）",
        "es": "Popping, breaking y esa cara final. ¡Califícalo del 1 al 10! (video generado con IA)"}
SUBS = {"en": ["...", "Not amused.", "Watch this.", "Popping.", "Breaking.", "\U0001F60E"],
        "ja": ["…", "は？", "見てろよ", "ポップ", "ブレイク", "\U0001F60E"],
        "zh": ["……", "哈？", "看好了", "机械舞", "霹雳舞", "\U0001F60E"],
        "es": ["...", "¿Perdón?", "Mira esto.", "Popping.", "Breaking.", "\U0001F60E"]}


def ff(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]))


def enc(src, dst, vf=FIT, pre=()):
    ff(*pre, "-i", str(src), "-an", "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(dst))


def stinger(n_total, at, sr=memebeat.SR):
    """最後のドヤ顔に合わせた決め音（低音ヒット＋上昇音）。"""
    out = np.zeros(n_total)
    t = np.arange(int(1.2 * sr)) / sr
    hit = np.sin(2 * np.pi * (40 + 200 * np.exp(-t * 20)) * t) * np.exp(-t * 3)
    sweep = 0.3 * np.sin(2 * np.pi * (600 + 900 * t) * t) * np.exp(-t * 4)
    a = int(at * sr)
    seg = (hit + sweep)[:max(0, n_total - a)]
    out[a:a + len(seg)] = seg
    return out


def build(a):
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tmp = [out / f"_{a.id}_{k}.mp4" for k in range(7)]
    enc(a.standup, tmp[0])
    enc(a.standup, tmp[1], "crop=iw*0.55:ih*0.32:iw*0.24:ih*0.13,scale=1080:1920:force_original_aspect_ratio=increase,"
                           "crop=1080:1920,fps=30", ("-ss", str(a.face_at), "-t", "0.8"))
    enc(a.walk, tmp[2], pre=("-ss", str(a.walk_from), "-t", str(a.walk_to - a.walk_from)))
    enc(a.pop, tmp[3])
    enc(a.brk, tmp[4])
    # 最後のドヤ顔をアップで強調
    enc(a.brk, tmp[6], f"crop={a.end_crop},scale=1080:1920:force_original_aspect_ratio=increase,"
                       "crop=1080:1920,fps=30", ("-sseof", str(-a.end_face)))
    parts = [*tmp[:5], tmp[6]]
    lens = [dur(p) for p in parts]
    lst = out / f"_{a.id}_list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(tmp[5]))
    st = [sum(lens[:i]) for i in range(len(lens))]
    total = sum(lens)
    wav = out / f"_{a.id}.wav"
    end_hit = total - a.end_face - a.pose_len
    if a.music:
        # 外部の楽曲（利用許諾のあるもの）を指定位置から切り出し、最後をフェードアウト
        ff("-ss", str(a.music_start), "-t", f"{total:.3f}", "-i", str(a.music), "-af",
           f"volume=-3dB,alimiter=limit=0.7:level=false,afade=t=in:d=0.05,afade=t=out:st={total - 0.7:.3f}:d=0.7", "-ar", "44100", str(wav))
    else:
        write_memebeat(wav, total, a.drop, st, end_hit)
    _mux_and_finish(a, out, tmp, lst, wav, st, total, end_hit)
    return out / f"{a.id}.mp4"


def write_memebeat(wav, total, drop, st, end_hit):
    # 音楽: 立ち上がりでドロップ、ブレイクダンスでテンポアップ、最後に決め音
    music = memebeat.render(total, drop, [(0, 150), (st[4], 165)], seed=4353).astype(float)
    music += stinger(len(music), end_hit) * 32767 * 0.6
    music = (music / max(1.0, np.abs(music).max()) * 32767 * 0.85).astype(np.int16)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(memebeat.SR)
        w.writeframes(music.tobytes())


def _mux_and_finish(a, out, tmp, lst, wav, st, total, end_hit):
    mp4 = out / f"{a.id}.mp4"
    ff("-i", str(tmp[5]), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
       "-b:a", "160k", "-shortest", str(mp4))
    for p in [*tmp, lst, wav]:
        p.unlink()

    def ts(x):
        return f"00:00:{int(x):02d},{int((x % 1) * 1000):03d}"
    cues = [(0, a.drop), (a.drop, st[1]), (st[2], st[3]), (st[3], st[4]), (st[4], end_hit), (end_hit, total)]
    for lang, lines in SUBS.items():
        (out / f"{a.id}.{lang}.srt").write_text("\n".join(
            f"{k + 1}\n{ts(x)} --> {ts(y)}\n{txt}\n" for k, ((x, y), txt) in enumerate(zip(cues, lines))),
            encoding="utf-8")
    meta = {"id": a.id, "format": "catstory", "duration_s": round(total, 1),
            "sections": {"standup": 0, "walk": round(st[2], 2), "pop": round(st[3], 2), "break": round(st[4], 2)},
            "ai_generated": True, "synthetic_disclosure": True,
            "assets": "video generated by AI (Higgsfield: Seedance 1.5 / Kling 3.0) from original prompts; "
                      + (f"music: {a.music_credit} (used under the artist's free-use policy with credit)"
                         if a.music else "music generated by memebeat.py and catstory.py (original)"),
            "title": TITLE, "description": dict(DESC), "hashtags": ["#shorts", "#cat", "#dance"]}
    if a.music:
        # TheFatRat の利用条件: 曲名・全アーティスト名・公式動画リンクを説明文に記載（YouTubeのみ対象）
        meta["music"] = {"credit": a.music_credit, "link": a.music_link, "start_s": a.music_start,
                         "platforms": ["youtube"],
                         "note": "Instagram/TikTok are not covered by the free-use policy; use the in-app music library there"}
        for k in meta["description"]:
            meta["description"][k] += f"\n\nMusic: {a.music_credit}\n{a.music_link}"
    (out / f"{a.id}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for k in ("standup", "walk", "pop", "brk"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--drop", type=float, default=0.95)
    ap.add_argument("--face-at", type=float, default=2.6)
    ap.add_argument("--walk-from", type=float, default=0.5)
    ap.add_argument("--walk-to", type=float, default=5.45)
    ap.add_argument("--pose-len", type=float, default=1.8, help="最後の決めポーズ（ドヤ顔）の長さ")
    ap.add_argument("--end-face", type=float, default=0.9, help="最後に足すドヤ顔アップの長さ")
    ap.add_argument("--end-crop", default="iw*0.6:ih*0.3:iw*0.2:ih*0.08",
                    help="ドヤ顔アップの切り抜き範囲（ffmpeg crop の w:h:x:y）")
    ap.add_argument("--music", help="利用許諾のある楽曲ファイル（未指定なら自作BGM）")
    ap.add_argument("--music-start", type=float, default=0.0, help="楽曲の切り出し開始秒")
    ap.add_argument("--music-credit", default="", help="例: TheFatRat - Oblivion (feat. Lola Blanc)")
    ap.add_argument("--music-link", default="", help="公式動画のURL")
    print(build(ap.parse_args()))
