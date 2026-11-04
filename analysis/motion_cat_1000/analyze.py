"""dataset.json（再生100万回以上の猫ショート）を分類・集計し、サムネを解析して report_stats.txt を出す。"""
import json, re, os, subprocess, statistics as st, collections, concurrent.futures as cf
import cv2, numpy as np
R = json.load(open("dataset.json"))
D = {v["id"]: v for v in json.load(open("discover.json"))}
for r in R:
    if r.get("duration") is None and r["id"] in D: r["duration"] = D[r["id"]].get("duration")
    r["found_by_motion_query"] = r["id"] in D

# ---- 形式の分類（タイトル＋チャンネル名のキーワード）----
K = {
 "ai":        r"\bai\b|a\.i\.|人工知能|ＡＩ|sora|kling|veo|seedance|hailuo|runway|pika|生成",
 "dance":     r"danc|dance|踊|ダンス|舞|춤|baila|joget|twerk|moonwalk|chipi|apt\b|oiia|vibing|vibe|groove|shuffle",
 "fight":     r"kung ?fu|karate|box|fight|ninja|カンフー|ボクシング|空手|喧嘩|戦",
 "music":     r"song|sing|歌|music|cover|remix|meow ?meow|ソング|beat|bgm",
 "story":     r"story|part ?\d|その\d|続き|episode|物語|日記|ストーリー|sad|泣|crying|abandon|hospital|rescue|保護",
 "human_like":r"like (a )?human|人間|二足|two legs|stand(s|ing)? up|立って|walk(s|ing)? like|human",
 "meme":      r"meme|ミーム|oiia|maxwell|banana cat|huh cat|happy cat|sad cat|chipi|bongo",
 "kids_anim": r"kids|nursery|baby shark|pinkfong|cocomelon|gabby|animation|animated|アニメ|cartoon|dodo kids|bebefinn",
 "pov":       r"\bpov\b",
 "food":      r"cook|料理|ごはん|food|eat|食べ|kitchen",
}
for r in R:
    s = (r["title"] + " " + (r["channel"] or "")).lower()
    r["tags"] = [k for k, p in K.items() if re.search(p, s, re.I)]
    t = r["title"]
    r["t_len"] = len(t); r["t_hash"] = t.count("#"); r["t_emoji"] = len(re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", t))
    r["t_q"] = "?" in t or "？" in t; r["t_ex"] = "!" in t or "！" in t
    r["lang"] = "ja" if re.search(r"[぀-ヿ]", t) else "ko" if re.search(r"[가-힯]", t) else "zh" if re.search(r"[一-鿿]", t) else "latin"
    r["no_words"] = len(re.sub(r"#\S+|[\U0001F300-\U0001FAFF☀-➿\s\W]", "", t)) == 0

# ---- サムネ（Shorts の自動サムネ＝動画内の1フレーム）----
os.makedirs("thumbs", exist_ok=True)
def get(r):
    f = f"thumbs/{r['id']}.jpg"
    if not os.path.exists(f):
        for n in ("oar2.jpg", "hq2.jpg", "hqdefault.jpg"):
            if subprocess.run(["curl", "-sSf", "-o", f, f"https://i.ytimg.com/vi/{r['id']}/{n}"], capture_output=True).returncode == 0: break
    return f if os.path.exists(f) else None
with cf.ThreadPoolExecutor(16) as ex: paths = list(ex.map(get, R))
cat = cv2.CascadeClassifier("haarcascade_frontalcatface_extended.xml")
def thumb_feats(f):
    im = cv2.imread(f)
    if im is None: return {}
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); h, w = g.shape
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    faces = cat.detectMultiScale(g, 1.1, 3, minSize=(int(w * .08), int(w * .08)))
    fa = max((fw * fh for x, y, fw, fh in faces), default=0) / (w * h)
    txt = subprocess.run(["tesseract", f, "-", "-l", "eng+jpn", "--psm", "11"], capture_output=True, text=True).stdout
    words = [x for x in re.findall(r"[A-Za-z]{3,}|[぀-ヿ一-鿿]{2,}", txt)]
    return {"bright": float(g.mean()), "sat": float(hsv[..., 1].mean()), "contrast": float(g.std()),
            "catface": len(faces) > 0, "catface_area": fa, "ocr_words": len(words)}
with cf.ThreadPoolExecutor(4) as ex:
    for r, ft in zip(R, ex.map(lambda p: thumb_feats(p) if p else {}, paths)): r.update(ft)
json.dump(R, open("dataset_features.json", "w"), ensure_ascii=False, indent=0)

# ---- 集計 ----
out = []
P = lambda *a: out.append(" ".join(str(x) for x in a))
V = [r["views"] for r in R]
P("n =", len(R), "| channels =", len({r['channel'] for r in R}), "| views median =", f"{st.median(V):,.0f}", "| total =", f"{sum(V):,}")
P("found by motion/AI-cat search queries:", sum(r["found_by_motion_query"] for r in R))
P("\n--- 形式（タイトルのキーワード）: 本数 / 再生数中央値 ---")
for k in K:
    sub = [r["views"] for r in R if k in r["tags"]]
    if sub: P(f"{k:10s} {len(sub):5d} ({len(sub)/len(R):.0%})  median {st.median(sub):>12,.0f}")
P("\n--- 長さ（分かったもの）---")
du = [r["duration"] for r in R if r.get("duration")]
if du:
    P("n", len(du), "median", st.median(du), "s | quartiles", st.quantiles(du, n=4))
    for lo, hi in [(0, 10), (10, 15), (15, 20), (20, 30), (30, 45), (45, 61), (61, 999)]:
        s = [r["views"] for r in R if r.get("duration") and lo <= r["duration"] < hi]
        if s: P(f"  {lo:>3}-{hi:<3}s {len(s):4d}  median {st.median(s):>12,.0f}")
P("\n--- タイトル ---")
P("len median", st.median(r["t_len"] for r in R), "| hashtag>0", f"{sum(r['t_hash']>0 for r in R)/len(R):.0%}",
  "| emoji>0", f"{sum(r['t_emoji']>0 for r in R)/len(R):.0%}", "| ?", f"{sum(r['t_q'] for r in R)/len(R):.0%}",
  "| !", f"{sum(r['t_ex'] for r in R)/len(R):.0%}", "| 言葉なし", f"{sum(r['no_words'] for r in R)/len(R):.0%}")
P("lang", collections.Counter(r["lang"] for r in R).most_common())
P("\n--- サムネ（動画内フレーム）---")
T = [r for r in R if "bright" in r]
P("n", len(T), "| 猫の顔が正面で写る", f"{sum(r['catface'] for r in T)/len(T):.0%}",
  "| 顔が画面の10%以上（アップ）", f"{sum(r['catface_area']>=.10 for r in T)/len(T):.0%}",
  "| 文字あり(3語以上)", f"{sum(r['ocr_words']>=3 for r in T)/len(T):.0%}",
  "| 明るさ中央値", round(st.median(r['bright'] for r in T)), "| 彩度中央値", round(st.median(r['sat'] for r in T)))
P("\n--- チャンネル規模と再生数（登録者に対する倍率）---")
X = [r for r in R if r.get("subs")]
ratio = [r["views"] / max(r["subs"], 1) for r in X]
P("views/subs median", round(st.median(ratio), 1), "| 登録者10万未満のチャンネルの動画", f"{sum(r['subs']<1e5 for r in X)/len(X):.0%}",
  "| 1万未満", f"{sum(r['subs']<1e4 for r in X)/len(X):.0%}")
c = collections.Counter(r["channel"] for r in R)
P("本数上位チャンネル", c.most_common(15))
P("1本だけ100万超えのチャンネル", sum(1 for v in c.values() if v == 1), "/", len(c))
P("\n--- 再生数トップ30 ---")
for r in R[:30]: P(f"{r['views']:>12,} {str(r.get('duration')):>4}s {r['tags']} {r['channel'][:22]} | {r['title'][:70]}")
P("\n--- AI 系トップ30 ---")
for r in [r for r in R if "ai" in r["tags"]][:30]: P(f"{r['views']:>12,} {str(r.get('duration')):>4}s {r['tags']} {r['channel'][:22]} | {r['title'][:70]}")
open("report_stats.txt", "w").write("\n".join(out)); print("\n".join(out))
