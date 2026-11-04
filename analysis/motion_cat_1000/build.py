"""tabs/ から再生100万回以上・猫関連のショートを抜き出して dataset.json を作る。"""
import json, glob, re
CAT = re.compile(r"\bcats?\b|kitt(y|en|ens)|meow|gato|gatito|chat\b|kucing|猫|ねこ|ネコ|にゃん|ニャン|고양이|냥|кот|кошк|mèo|แมว|pisic|kedi|katze|miau|feline", re.I)
EXCLUDE = {"Doja Cat", "BLACK CAT", "GIRLSET", "MibaGlitch", "American Mona (skate boat turtle)", "TrainFun Tv", "JISOO", "biz", "DNCE"}
seen, rows = set(), []
for f in glob.glob("tabs/*.json") + glob.glob("tabs_deep/*.json"):
    d = json.load(open(f))
    for e in d.get("entries", []):
        v = e.get("view_count") or 0
        if v < 1_000_000 or e["id"] in seen: continue
        t = e.get("title") or ""
        if not CAT.search(t) or d.get("channel") in EXCLUDE: continue
        seen.add(e["id"])
        rows.append({"id": e["id"], "title": t, "views": v, "duration": e.get("duration"),
                     "channel": d.get("channel"), "channel_id": d.get("channel_id"), "subs": d.get("channel_follower_count"),
                     "cat_in_title": bool(CAT.search(t))})
rows.sort(key=lambda r: -r["views"])
json.dump(rows, open("dataset.json", "w"), ensure_ascii=False, indent=0)
import collections
print("rows", len(rows), "cat_in_title", sum(r["cat_in_title"] for r in rows), "channels", len({r["channel"] for r in rows}))
for ch, n in collections.Counter(r["channel"] for r in rows).most_common(30): print(n, ch)
