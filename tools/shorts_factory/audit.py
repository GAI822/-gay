"""投稿前の自動監査。1項目でも FAIL があれば終了コード1を返し、投稿を止める。

使い方: python3 tools/shorts_factory/audit.py out/oddone_123.json

これは機械的な一次チェック。法的な適法性を保証するものではないため、
定期実行のClaudeセッションがコマ画像を目視確認し、迷うものは投稿せずユーザーに回す。
"""
import json
import re
import subprocess
import sys
from pathlib import Path

# 炎上・権利侵害につながりやすい語（多言語）。メタデータ・字幕に含まれたら FAIL。
BLOCK = [
    # 政治・歴史・宗教・社会問題
    r"天安門|tiananmen|六四|台湾独立|チベット|新疆|ウイグル|靖国|慰安婦|南京|holocaust|nazi|ナチ|戦争|war\b|guerra|战争",
    r"政治|politic|选举|election|elecci|大統領|president|首相|共産党|communis",
    r"宗教|religion|religi|神様|allah|jesus|キリスト|仏教|宗教",
    r"gender|ジェンダー|性别|género|lgbt|race\b|人種|种族|raza|移民|immigra|差別|discrimin",
    # 性的・暴力・危険行為
    r"sex|セクシー|エロ|色情|sexy|nsfw|porn|kill|殺|死ね|suicide|自殺|drug|麻薬|毒品",
    # 実在の人物・ブランド（肖像権・商標）
    r"@\w+|disney|pokemon|ポケモン|mario|マリオ|nintendo|任天堂|marvel|taylor swift|mrbeast",
    # 誇大表示（根拠のない数字・断定）
    r"\d+\s*%|only\s*\d|天才だけ|IQ\s*\d+|impossible|不可能|guarantee|保証",
]
REQUIRED_LANGS = ["en", "ja", "zh", "es"]


def check(meta_path):
    meta_path = Path(meta_path)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    base = meta_path.with_suffix("")
    mp4 = base.with_suffix(".mp4")
    results = []

    def r(ok, name, detail=""):
        results.append(("PASS" if ok else "FAIL", name, detail))

    texts = [*meta["title"].values(), *meta["description"].values(), *meta["hashtags"]]
    for lang in REQUIRED_LANGS:
        srt = Path(f"{base}.{lang}.srt")
        r(srt.exists(), f"字幕({lang})あり")
        if srt.exists():
            texts.append(srt.read_text(encoding="utf-8"))
    blob = "\n".join(texts)
    hits = sorted({m.group(0) for p in BLOCK for m in re.finditer(p, blob, re.I)})
    r(not hits, "禁止語・誇大表示なし", ", ".join(hits))

    r("original" in meta.get("assets", ""), "素材がすべて自作（著作権・肖像権）", meta.get("assets", ""))

    if mp4.exists():
        p = json.loads(subprocess.check_output(["ffprobe", "-v", "quiet", "-print_format", "json",
                                                "-show_streams", "-show_format", str(mp4)]))
        v = next(s for s in p["streams"] if s["codec_type"] == "video")
        dur = float(p["format"]["duration"])
        r(v["width"] * 16 == v["height"] * 9, "縦型9:16", f'{v["width"]}x{v["height"]}')
        r(dur <= 60, "60秒以内（全プラットフォームでショート扱い）", f"{dur:.1f}s")
        r(any(s["codec_type"] == "audio" for s in p["streams"]), "音声トラックあり")
        vol = subprocess.run(["ffmpeg", "-i", str(mp4), "-af", "volumedetect", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
        peak = float(re.search(r"max_volume: ([-\d.]+)", vol).group(1))
        r(peak <= -0.5, "音割れなし", f"peak {peak} dB")
    else:
        r(False, "動画ファイルあり", str(mp4))

    for status, name, detail in results:
        print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))
    return all(s == "PASS" for s, _, _ in results)


if __name__ == "__main__":
    ok = all([check(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
