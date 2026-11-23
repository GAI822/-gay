"""moves.py の検索語で YouTube を検索し、動画を集める（discover.json）。長さ90秒以下だけ残す。"""
import json, subprocess, concurrent.futures as cf
from moves import MOVES
Q = [(k, q) for k, v in MOVES.items() for q in v[1]]
def run(kq):
    k, q = kq
    try:
        r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch150:{q}"], capture_output=True, text=True, timeout=400)
        return k, q, json.loads(r.stdout)["entries"]
    except Exception:
        return k, q, []
out = {}
with cf.ThreadPoolExecutor(6) as ex:
    for k, q, E in ex.map(run, Q):
        n = 0
        for e in E:
            if not e or (e.get("duration") or 999) > 90:
                continue
            n += 1
            v = out.setdefault(e["id"], {"id": e["id"], "title": e.get("title") or "", "views": e.get("view_count") or 0,
                                         "duration": e.get("duration"), "channel": e.get("channel"), "queries": []})
            v["queries"].append(k)
        print(k, q, len(E), n, flush=True)
json.dump(list(out.values()), open("discover.json", "w"), ensure_ascii=False)
print("unique", len(out))
