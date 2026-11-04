"""discover.json の動画のチャンネルを oEmbed で特定し、出現回数の多いチャンネル順に channels.json に保存する。"""
import json, requests, collections, concurrent.futures as cf
V = json.load(open("discover.json"))
def oe(v):
    if v.get("channel_url"): return v["id"], v["channel"], v["channel_url"]
    if v.get("channel_id"): return v["id"], v.get("channel"), f"https://www.youtube.com/channel/{v['channel_id']}"
    try:
        j = requests.get("https://www.youtube.com/oembed", params={"url": f"https://www.youtube.com/watch?v={v['id']}", "format": "json"}, timeout=20).json()
        return v["id"], j.get("author_name"), j.get("author_url")
    except Exception: return v["id"], None, None
res = {}
with cf.ThreadPoolExecutor(16) as ex:
    for vid, name, url in ex.map(oe, V): res[vid] = (name, url)
for v in V: v["channel"], v["channel_url"] = res[v["id"]]
json.dump(V, open("discover.json", "w"), ensure_ascii=False)
c = collections.Counter(v["channel_url"] for v in V if v["channel_url"])
json.dump([{"url": u, "name": next(v["channel"] for v in V if v["channel_url"] == u), "hits": n} for u, n in c.most_common()], open("channels.json", "w"), ensure_ascii=False, indent=0)
print(len(c), "channels; resolved", sum(1 for v in V if v["channel_url"]), "/", len(V))
for u, n in c.most_common(25): print(n, u)
