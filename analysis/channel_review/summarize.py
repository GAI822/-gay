"""peers/*.json からチャンネル別の再生数サマリーを出す。"""
import glob, json, statistics as st
for f in sorted(glob.glob("peers/*.json")):
    d = json.load(open(f))
    v = [e["view_count"] for e in d["entries"] if e.get("view_count") is not None]
    if not v: continue
    q = st.quantiles(v, n=4) if len(v) > 3 else [min(v), st.median(v), max(v)]
    print(f"{d.get('channel')[:28]:28s} subs={d.get('channel_follower_count'):>7} n={len(v):>3} "
          f"median={st.median(v):>9,.0f} p25={q[0]:>9,.0f} p75={q[2]:>9,.0f} max={max(v):>10,}")
