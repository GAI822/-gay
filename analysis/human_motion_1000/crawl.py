"""channels.json の上位チャンネルのショートタブ（最大150本）を取得して tabs/ に保存する。"""
import json, subprocess, sys, os, concurrent.futures as cf, hashlib
C = [c for c in json.load(open("channels.json")) if c["hits"] >= int(sys.argv[1])][int(sys.argv[3]) if len(sys.argv) > 3 else 0:]
def run(c):
    f = "tabs/" + hashlib.md5(c["url"].encode()).hexdigest()[:12] + ".json"
    if os.path.exists(f): return c, "cached"
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", sys.argv[2] if len(sys.argv) > 2 else "150", c["url"] + "/shorts"], capture_output=True, text=True, timeout=400)
    if r.returncode or not r.stdout.strip(): return c, "fail"
    d = json.loads(r.stdout); d["_src"] = c
    json.dump(d, open(f, "w"), ensure_ascii=False); return c, len(d.get("entries", []))
print(len(C), "channels", flush=True)
with cf.ThreadPoolExecutor(10) as ex:
    for i, (c, s) in enumerate(ex.map(run, C)):
        if i % 25 == 0: print(i, c["name"], s, flush=True)
