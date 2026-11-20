"""検索で「人間の面白いダンス・動き・おもしろ動画」のショートを探し、動画IDとチャンネルを集める（discover.json）。"""
import json, subprocess, concurrent.futures as cf
Q = ["funny dance shorts", "dance challenge shorts", "viral dance trend", "tiktok dance trend 2026", "funny dance moves",
     "dad dance funny", "office dance funny", "awkward dance shorts", "synchronized dance funny", "dance fail shorts",
     "funny walk shorts", "slow motion funny", "reaction funny shorts", "prank shorts funny", "jump scare reaction",
     "trick shot shorts", "satisfying catch shorts", "parkour fail funny", "gym fail funny", "kitchen fail funny",
     "pov funny shorts", "skit shorts comedy", "relatable skit shorts", "lip sync funny shorts", "meme dance",
     "goal celebration funny", "victory dance funny", "robot dance funny", "moonwalk shorts", "shuffle dance",
     "おもしろ動画 ダンス", "変なダンス", "ダンス 流行り shorts", "おもしろ 動き", "あるある コント shorts", "ドッキリ shorts",
     "踊ってみた 面白い", "神業 shorts", "失敗 おもしろ", "충격 춤", "baile gracioso", "danza divertida", "drôle danse",
     "funny freeze frame", "mirror dance funny", "duo dance funny", "family dance trend", "grandma dance funny", "kids dance trend"]
def run(q):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch100:{q}"], capture_output=True, text=True, timeout=300)
    try: return q, json.loads(r.stdout)["entries"]
    except Exception: return q, []
out = {}
with cf.ThreadPoolExecutor(6) as ex:
    for q, E in ex.map(run, Q):
        print(q, len(E), flush=True)
        for e in E:
            v = out.setdefault(e["id"], {"id": e["id"], "title": e.get("title"), "duration": e.get("duration"),
                                         "channel_id": e.get("channel_id"), "channel": e.get("channel"), "queries": []})
            v["queries"].append(q)
json.dump(list(out.values()), open("discover.json", "w"), ensure_ascii=False)
print("unique", len(out))
