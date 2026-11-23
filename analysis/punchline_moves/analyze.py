"""discover.json（今回の検索 2,800本前後）と ../human_motion_1000/dataset.json（再生100万回以上 4,764本）を合わせ、
タイトルから「オチの動き」を判定して集計する。report_stats.txt と moves_stats.json を出す。"""
import json, re, statistics as st
from moves import MOVES
A = json.load(open("discover.json"))
B = json.load(open("../human_motion_1000/dataset.json"))
rows = {}
for r in A:
    rows[r["id"]] = {"id": r["id"], "title": r["title"], "views": r["views"] or 0, "channel": r.get("channel"), "src": "search", "q": r["queries"]}
for r in B:
    rows.setdefault(r["id"], {"id": r["id"], "title": r["title"], "views": r["views"], "channel": r.get("channel"), "src": "1M", "q": []})
rows = list(rows.values())
XP = re.compile(r"tik ?tok|#fyp|foryou|reels?\b|instagram|#viral|threads|twitter|\bx\.com", re.I)
END = re.compile(r"wait for it|wait till the end|watch till the end|the end|ending|plot twist|最後|オチ|まさか|unexpected", re.I)
out, stats = [], {}
P = lambda *a: out.append(" ".join(str(x) for x in a))
P("全体", len(rows), "本 | 検索", sum(r['src']=='search' for r in rows), "| 100万回以上データ", sum(r['src']=='1M' for r in rows))
P("他SNSの転載・流行を示すタイトル（tiktok/reels/instagram/#fyp など）:", sum(bool(XP.search(r['title'])) for r in rows), "本")
P("オチを強調するタイトル（wait for it / ending / plot twist / 最後 など）:", sum(bool(END.search(r['title'])) for r in rows), "本")
P("\n動き | 本数(タイトル一致) | うち再生数が取れた本数 | 再生中央値(取れた分) | 100万回以上の本数 | 他SNS系 | ハイ向き")
for k, (ja, qs, rx, ok, note) in MOVES.items():
    R = [r for r in rows if re.search(rx, r["title"], re.I)]
    R.sort(key=lambda r: -r["views"])
    v = [r["views"] for r in R if r["views"] > 0]
    s = {"ja": ja, "n": len(R), "nv": len(v), "median": int(st.median(v)) if v else 0, "n1m": sum(x >= 1_000_000 for x in v),
         "xp": sum(bool(XP.search(r["title"])) for r in R), "ok": ok, "note": note,
         "top": [(r["views"], r["title"][:90]) for r in R[:6]]}
    stats[k] = s
for k, s in sorted(stats.items(), key=lambda kv: (-kv[1]["n1m"], -kv[1]["median"])):
    P(f"{s['ja'][:18]:18s} {s['n']:5d} {s['nv']:5d} {s['median']:>12,} {s['n1m']:5d} {s['xp']:4d} {'○' if s['ok'] else '×'} {s['note']}")
for k, s in sorted(stats.items(), key=lambda kv: (-kv[1]["n1m"], -kv[1]["median"])):
    P(f"\n--- {s['ja']} 上位 ---")
    for v, t in s["top"]:
        P(f"{v:>13,} | {t}")
open("report_stats.txt", "w").write("\n".join(out))
json.dump(stats, open("moves_stats.json", "w"), ensure_ascii=False, indent=1)
print("\n".join(out[:50]))
