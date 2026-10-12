"""「AIが考えた理解不能なネコチューバーたち」形式の総集編ショートを組み立てる。

AIで生成した短い場面（各5秒前後）を順につなぎ、画面上部にシリーズ名、
下部にセリフ字幕（日本語を大きく＋英語を小さく）を焼き込む。音声は各クリップの生成音（鳴き声・環境音）。

使い方: python3 tools/shorts_factory/nekotuber.py skits.json --id nekotuber_001 --out out/
skits.json: {"clips": [{"file": "a.mp4", "ja": "...", "en": "...", "zh": "...", "es": "..."}, ...]}
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
CJK_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"  # index 0 = Japanese
FALLBACK = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
SERIES = {"ja": "AIが考えた理解不能なネコチューバーたち", "en": "Incomprehensible Cat YouTubers, imagined by AI",
          "zh": "AI想象的看不懂的猫咪博主们", "es": "Gatos youtubers incomprensibles, imaginados por IA"}
DESC = {"ja": "どのネコチューバーが一番わけわからなかった？コメントで番号を教えてね！（AI生成の映像です）",
        "en": "Which cat YouTuber made the least sense? Comment the number! (AI-generated video)",
        "zh": "哪个猫咪博主最让人看不懂？评论告诉我编号！（AI生成视频）",
        "es": "¿Qué gato youtuber tuvo menos sentido? ¡Comenta el número! (video generado con IA)"}


def series_name(part):
    if part <= 1:
        return SERIES
    suffix = {"ja": f" その{part}", "en": f" Part {part}", "zh": f" 第{part}弹", "es": f" Parte {part}"}
    return {k: v + suffix[k] for k, v in SERIES.items()}


def font(size):
    try:
        return ImageFont.truetype(CJK_BOLD, size, index=0)
    except OSError:
        return ImageFont.truetype(FALLBACK, size)


def wrap(d, text, f, maxw):
    """スペースで優先的に改行し、長い部分は文字単位で折り返す（数字・英単語は途中で切らない）。"""
    lines = []
    for part in text.split():
        cur = ""
        for tok in re.findall(r"[0-9A-Za-z.,!?]+|.", part):
            if d.textlength(cur + tok, font=f) > maxw and cur:
                lines.append(cur)
                cur = ""
            cur += tok
        if cur:
            lines.append(cur)
    return lines


def overlay_png(path, num, ja, en, series_ja=SERIES["ja"]):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 上部: シリーズ名の帯（参考シリーズのタイトル帯に倣う）
    size = 50
    while d.textlength(series_ja, font=font(size)) > W - 120 and size > 30:
        size -= 2  # 帯からはみ出さないよう縮める
    fs = font(size)
    d.rounded_rectangle([40, 120, W - 40, 220], radius=24, fill=(255, 255, 255, 235))
    d.text((W / 2, 170), series_ja, font=fs, fill=(220, 20, 40), anchor="mm")
    d.text((W / 2, 262), f"#{num}", font=font(56), fill="white", anchor="mm", stroke_width=6, stroke_fill="black")
    # 下部: セリフ字幕
    fj, fe = font(66), font(38)
    y = 1430
    for line in wrap(d, ja, fj, W - 120):
        d.text((W / 2, y), line, font=fj, fill="white", anchor="mm", stroke_width=8, stroke_fill="black")
        y += 86
    d.text((W / 2, y + 6), en, font=fe, fill=(255, 235, 120), anchor="mm", stroke_width=5, stroke_fill="black")
    img.save(path)


def ff(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]))


def build(cfg_path, vid, outdir, part=1):
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    parts, lens = [], []
    for i, c in enumerate(cfg["clips"], 1):
        png = out / f"_{vid}_{i}.png"
        overlay_png(png, i, c["ja"], c["en"], series_name(part)["ja"])
        seg = out / f"_{vid}_{i}.mp4"
        has_audio = b"audio" in subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", c["file"]])
        audio_in = [] if has_audio else ["-f", "lavfi", "-t", "10", "-i", "anullsrc=r=44100:cl=stereo"]
        amap = "0:a" if has_audio else "2:a"
        ff("-i", c["file"], "-i", str(png), *audio_in, "-filter_complex",
           "[0:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=30[b];"
           "[b][1:v]overlay=0:0[v]", "-map", "[v]", "-map", amap, "-shortest",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
           "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "160k", str(seg))
        parts.append(seg)
        lens.append(dur(seg))
        png.unlink()
    lst = out / f"_{vid}_list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    mp4 = out / f"{vid}.mp4"
    # 音量をそろえ、音割れを防ぐ
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "copy",
       "-af", "loudnorm=I=-15:TP=-2:LRA=11", "-c:a", "aac", "-ar", "44100", "-b:a", "160k", str(mp4))
    for p in [*parts, lst]:
        p.unlink()

    def ts(x):
        return f"00:00:{int(x):02d},{int((x % 1) * 1000):03d}"
    starts = [sum(lens[:i]) for i in range(len(lens) + 1)]
    for lang in ("en", "ja", "zh", "es"):
        (out / f"{vid}.{lang}.srt").write_text("\n".join(
            f"{k + 1}\n{ts(starts[k])} --> {ts(starts[k + 1])}\n{c[lang]}\n"
            for k, c in enumerate(cfg["clips"])), encoding="utf-8")
    meta = {"id": vid, "format": "nekotuber", "duration_s": round(starts[-1], 1), "ai_generated": True,
            "synthetic_disclosure": True,
            "assets": "video and sound generated by AI (Higgsfield/Kling 3.0) from original prompts; "
                      "captions written for this video (original)",
            "title": {k: f"{v} \U0001F431 #shorts" for k, v in series_name(part).items()},
            "description": DESC, "hashtags": ["#shorts", "#cat", "#aivideo"],
            "clips": [{k: c[k] for k in ("ja", "en")} for c in cfg["clips"]]}
    (out / f"{vid}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return mp4


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("skits")
    ap.add_argument("--id", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--part", type=int, default=1, help="シリーズ番号（2以上で「その2」等を表示）")
    a = ap.parse_args()
    print(build(a.skits, a.id, a.out, a.part))
