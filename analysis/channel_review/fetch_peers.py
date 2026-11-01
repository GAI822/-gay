"""比較対象チャンネルのショート一覧（タイトル・再生数）を yt-dlp --flat-playlist で取得する。"""
import json, subprocess, sys
CH = {
 "own_Cuttlefisher": "https://www.youtube.com/@Cuttlefisher-rehsifelttuC/shorts",
 "catboss_handle": "https://www.youtube.com/@catboss/shorts",
 "BossCatKitchen": "https://www.youtube.com/channel/UCZwBkqvEabpa5lk3Si9CcGg/shorts",
 "Shikineko": "https://www.youtube.com/channel/UCjwfXO-_BGW6fxzq6CfiOFw/shorts",
 "Nyankochin": "https://www.youtube.com/channel/UCNlkT_m_B6X8hndOMBUxvaw/shorts",
 "Marurin": "https://www.youtube.com/channel/UCo7f5QsqR67vb_WiBfLTnCA/shorts",
 "ShachikuMugi": "https://www.youtube.com/channel/UC5wXYrzQNelsmZmCxSBI69Q/shorts",
 "SoftCatVideo": "https://www.youtube.com/channel/UCKNBXLwSAaVKATafY18zGBA/shorts",
}
for k, url in (CH.items() if "--extra" not in sys.argv else []):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", "60", url], capture_output=True, text=True, timeout=180)
    if r.returncode or not r.stdout.strip():
        print(k, "FAILED", r.stderr.strip().splitlines()[-1:] ); continue
    json.dump(json.loads(r.stdout), open(f"peers/{k}.json", "w"), ensure_ascii=False)
    d = json.loads(r.stdout)
    print(k, d.get("channel"), d.get("channel_follower_count"), len(d.get("entries", [])))

# shorts タブが無い・少ないチャンネルは videos タブ（縦動画もここに入る）を取る
EXTRA = {
 "BossCatKitchen": "https://www.youtube.com/channel/UCZwBkqvEabpa5lk3Si9CcGg/videos",
 "Marurin": "https://www.youtube.com/channel/UCo7f5QsqR67vb_WiBfLTnCA/videos",
 "ShachikuMugi": "https://www.youtube.com/channel/UC5wXYrzQNelsmZmCxSBI69Q/videos",
}
if __name__ == "__main__" and "--extra" in sys.argv:
    for k, url in EXTRA.items():
        r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", "--playlist-end", "60", url], capture_output=True, text=True, timeout=180)
        if r.returncode or not r.stdout.strip():
            print(k, "FAILED", r.stderr.strip().splitlines()[-1:]); continue
        d = json.loads(r.stdout)
        json.dump(d, open(f"peers/{k}.json", "w"), ensure_ascii=False)
        print(k, d.get("channel"), d.get("channel_follower_count"), len(d.get("entries", [])))
