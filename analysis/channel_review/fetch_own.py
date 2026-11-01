"""自チャンネルの全アップロード動画の統計を YouTube Data API から取得して own_videos.json に保存する。"""
import json, sys
from pathlib import Path
import requests
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools/shorts_factory"))
from youtube_upload import access_token, scopes, API

tok = access_token()
H = {"Authorization": f"Bearer {tok}"}
print("scopes:", sorted(scopes(tok)))
ch = requests.get(f"{API}/channels", headers=H, params={"part": "snippet,statistics,contentDetails", "mine": "true"}, timeout=30).json()
c = ch["items"][0]
print("channel:", c["snippet"]["title"], c["statistics"])
up = c["contentDetails"]["relatedPlaylists"]["uploads"]
ids, page = [], None
while True:
    r = requests.get(f"{API}/playlistItems", headers=H, params={"part": "contentDetails", "playlistId": up, "maxResults": 50, **({"pageToken": page} if page else {})}, timeout=30).json()
    ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
    page = r.get("nextPageToken")
    if not page: break
vids = []
for i in range(0, len(ids), 50):
    r = requests.get(f"{API}/videos", headers=H, params={"part": "snippet,statistics,contentDetails,status", "id": ",".join(ids[i:i+50])}, timeout=30).json()
    vids += r.get("items", [])
json.dump({"channel": {"title": c["snippet"]["title"], "id": c["id"], "statistics": c["statistics"], "published": c["snippet"]["publishedAt"]}, "videos": vids}, open("own_videos.json", "w"), ensure_ascii=False, indent=1)
for v in vids:
    s = v["statistics"]
    print(v["id"], v["snippet"]["publishedAt"][:10], v["contentDetails"]["duration"], v["status"]["privacyStatus"], s.get("viewCount"), s.get("likeCount"), s.get("commentCount"), v["snippet"]["title"][:50])
