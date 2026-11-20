"""tabs/ から再生100万回以上のショートを集め（1チャンネル20本まで）、動きの型ごとに集計して report_stats.txt を出す。

型はタイトルのキーワードで分ける。ハイ（無表情の猫）で再現できるかの目安も付ける。
"""
import collections
import glob
import json
import re
import statistics as st

TYPES = {  # 型: (キーワード, ハイで文章から再現できるか)
    "dance_trend": (r"danc|dance|踊|ダンス|challenge|チャレンジ|trend|shuffle|moonwalk|baile|danza|춤|choreo|twerk", True),
    "fail": (r"fail|失敗|oops|fall|falls|slip|ミス|転", True),
    "prank": (r"prank|ドッキリ|いたずら|scare|surprise|broma", False),
    "reaction": (r"reaction|react|リアクション|反応|face when", True),
    "trick_skill": (r"trick shot|trickshot|神業|skill|perfect|catch|flip|parkour|satisfying|一発", True),
    "skit_pov": (r"\bpov\b|skit|コント|あるある|relatable|when you|when your|types of|be like", True),
    "lip_sync": (r"lip ?sync|口パク|singing|sing|歌", True),
    "sport": (r"goal|soccer|football|basketball|nba|サッカー|野球|ゴール|celebrat", True),
    "family_kids": (r"\bkid|kids|baby|子ども|子供|赤ちゃん|grandma|grandpa|dad|mom|父|母|family|家族", False),
}
SKIP_CH = re.compile(r"kids|nursery|cocomelon|pinkfong|disney|music|records|official|vevo|news|tv\b", re.I)

rows, seen = [], set()
for f in glob.glob("tabs/*.json"):
    d = json.load(open(f))
    ch = d.get("channel") or ""
    if SKIP_CH.search(ch):
        continue
    E = sorted([e for e in d.get("entries", []) if (e.get("view_count") or 0) >= 1_000_000], key=lambda e: -e["view_count"])[:20]
    for e in E:
        if e["id"] in seen:
            continue
        seen.add(e["id"])
        t = e.get("title") or ""
        rows.append({"id": e["id"], "title": t, "views": e["view_count"], "channel": ch,
                     "subs": d.get("channel_follower_count"),
                     "types": [k for k, (p, _) in TYPES.items() if re.search(p, t, re.I)]})
rows.sort(key=lambda r: -r["views"])
json.dump(rows, open("dataset.json", "w"), ensure_ascii=False, indent=0)

out = []
P = lambda *a: out.append(" ".join(str(x) for x in a))
V = [r["views"] for r in rows]
P("n =", len(rows), "| channels =", len({r['channel'] for r in rows}), "| views median =", f"{st.median(V):,.0f}" if V else "-")
P("\n--- 動きの型（タイトルのキーワード）: 本数 / 再生数中央値 / ハイで再現 ---")
for k, (_, ok) in TYPES.items():
    s = [r["views"] for r in rows if k in r["types"]]
    if s:
        P(f"{k:12s} {len(s):5d} ({len(s)/len(rows):.0%})  median {st.median(s):>12,.0f}  {'○' if ok else '×'}")
P("型なし", sum(1 for r in rows if not r["types"]))
for k, (_, ok) in TYPES.items():
    S = [r for r in rows if k in r["types"]][:12]
    if S:
        P(f"\n--- {k} 上位 ---")
        for r in S:
            P(f"{r['views']:>12,} {r['channel'][:22]:22s} | {r['title'][:80]}")
P("\n--- 型なし 上位40 ---")
for r in [r for r in rows if not r["types"]][:40]:
    P(f"{r['views']:>12,} {r['channel'][:22]:22s} | {r['title'][:80]}")
open("report_stats.txt", "w").write("\n".join(out))
print("\n".join(out[:20]))
