"""Mixkit（無料・商用可の素材サイト。Mixkit License）から、オチの動きに使えそうな「1人の人が全身で動く」動画を探す。
タグのページを2ページずつ見て、題名（URLの文字列）で絞り込む。結果は mixkit_candidates.json。"""
import json, re, subprocess, concurrent.futures as cf
TAGS = ["celebration", "victory", "winner", "clapping", "applause", "karate", "kung-fu", "jumping", "surprised", "shocked",
        "thumbs-up", "sunglasses", "hip-hop", "dance", "dancing", "running", "slow-motion", "gym", "workout", "yoga",
        "happy", "excited", "fitness", "boxing", "martial-arts", "street-dance", "party", "success", "goal", "football",
        "soccer", "basketball", "athlete", "silly", "funny", "crazy", "strong", "muscle", "man-dancing", "woman-dancing"]
def get(tag, page):
    url = f"https://mixkit.co/free-stock-video/{tag}/" + (f"?page={page}" if page > 1 else "")
    h = subprocess.run(["curl", "-s", "-m", "25", "-A", "Mozilla/5.0", url], capture_output=True, text=True).stdout
    return tag, set(re.findall(r'href="/free-stock-video/([a-z0-9-]+)-(\d+)/"', h))
out = {}
with cf.ThreadPoolExecutor(8) as ex:
    for tag, items in ex.map(lambda a: get(*a), [(t, p) for t in TAGS for p in (1, 2)]):
        for slug, i in items:
            out.setdefault(i, {"id": i, "slug": slug, "tags": set()})["tags"].add(tag)
SOLO = re.compile(r"\b(man|woman|boy|girl|guy|athlete|dancer|person|kid|teen|young|senior|player|boxer|fighter)\b")
GROUP = re.compile(r"couple|group|friends|people|crowd|team|family|dancers|together|two|three|four|five|audience|fans|kids|players|women|men\b")
ACT = re.compile(r"danc|celebrat|jump|clap|cheer|win|victor|punch|kick|karate|martial|box|flex|muscle|strong|pose|spin|surpris|shock|"
                 r"thumb|sunglass|happy|excit|fun|silly|crazy|move|groov|shuffl|break|hip-hop|run|slow-motion|walk|bow|salut|stretch|yoga")
rows = []
for v in out.values():
    s = v["slug"].replace("-", " ")
    if SOLO.search(s) and not GROUP.search(s) and ACT.search(s):
        rows.append({"id": v["id"], "slug": v["slug"], "tags": sorted(v["tags"]),
                     "url": f"https://mixkit.co/free-stock-video/{v['slug']}-{v['id']}/",
                     "mp4": f"https://assets.mixkit.co/videos/{v['id']}/{v['id']}-720.mp4"})
json.dump(rows, open("mixkit_candidates.json", "w"), ensure_ascii=False, indent=1)
print("all", len(out), "| solo+action", len(rows))
for r in rows: print(r["id"], r["slug"])
