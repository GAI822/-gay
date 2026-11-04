"""100万回超えの猫動画を持つチャンネルは、ショートタブを最大400本まで深く取り直す（tabs_deep/）。"""
import json, glob, subprocess, os, hashlib, concurrent.futures as cf
R = json.load(open("dataset.json"))
ids = sorted({r["channel_id"] for r in R if r.get("channel_id")})
os.makedirs("tabs_deep", exist_ok=True)
def run(cid):
    f = f"tabs_deep/{cid}.json"
    if os.path.exists(f): return cid, "cached"
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", "400", f"https://www.youtube.com/channel/{cid}/shorts"], capture_output=True, text=True, timeout=600)
    if r.returncode or not r.stdout.strip(): return cid, "fail"
    open(f, "w").write(r.stdout); return cid, "ok"
with cf.ThreadPoolExecutor(8) as ex:
    for cid, s in ex.map(run, ids): print(cid, s, flush=True)
