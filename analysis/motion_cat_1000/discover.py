"""検索で「人の動きを猫に被せた系」のショートを探し、動画IDとチャンネルを集める（discover.json）。"""
import json, subprocess, concurrent.futures as cf
Q = ["cat dancing like human shorts", "ai cat dance", "ai cat dance viral", "cat kung fu ai", "cat boxing ai shorts",
     "ai cat motion control", "cat doing human dance trend", "cat lip sync ai", "ai cat funny dance shorts",
     "cat standing dancing ai", "cat dance trend shorts", "ai animal dance shorts", "ai cat tiktok dance",
     "kling motion control cat", "cat dances like a human ai", "ai cat moves", "cat vibing dance ai",
     "猫 ダンス AI", "AI猫 ダンス", "猫 踊る shorts", "猫 カンフー AI", "AI猫 口パク", "猫 人間みたい 動き",
     "AI 猫 踊ってみた", "猫 ダンス バズ", "gato bailando ia", "猫咪跳舞 AI", "cat dance meme ai", "ai cat gym workout",
     "ai cat singing shorts", "cat human hands ai", "ai dog dance shorts", "ai cat cctv dance", "cat apt dance ai",
     "ai cat chipi chipi", "cat moonwalk ai", "ai cat breakdance", "ai cat hip hop dance", "funny ai cat moves shorts",
     "ai cat ballet", "ai cat twerk", "ai cat dancing in kitchen", "ai kitten dance"]
import sys
if "--extra" in sys.argv: Q = ['cat meme shorts', 'OIIA cat', 'funny cat shorts viral', 'cat dance meme', '猫ミーム', '猫 shorts バズ', 'cat vibing', 'cat dancing to music', 'cat singing meme', 'talking cat shorts', 'cat moonwalk', 'cat stands up like human', 'cat walking on two legs', 'cat waving hand', 'cat clapping hands meme', 'cat fight funny shorts', 'cat reaction meme', 'cat lip sync', 'ai cat', 'ai cat video', 'ai cat story shorts', 'ai cat cooking', 'ai cat cctv', 'ai giant cat', 'ai cat baby', 'ai cat sad story', 'ai kitten crying', 'ai animals dancing', 'ai dog dancing', 'ai monkey dance', 'ai cat apt', 'cat dance challenge', '猫 二足歩行', '猫 踊る', '猫 ダンス', 'AI 猫', 'AI猫 料理', 'AI猫 動画', 'AI 動物 ダンス', '고양이 춤', 'AI 고양이', '猫咪跳舞', 'AI猫咪', 'gato bailando', 'gato ia', 'kucing joget', 'kucing ai', 'gatto che balla', 'chat qui danse', 'cat edit dance', 'cat funny moves', 'happy cat dance', 'banana cat', 'sad cat dance', 'cat jumping dance', 'maxwell cat dance', 'cat chipi chipi chapa chapa', 'cat boxing', 'cat karate', 'cat kung fu', 'cat ninja', 'cat workout funny']
def run(q):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch100:{q}"], capture_output=True, text=True, timeout=300)
    try: return q, json.loads(r.stdout)["entries"]
    except Exception: return q, []
out = {v["id"]: v for v in json.load(open("discover.json"))} if "--extra" in sys.argv else {}
with cf.ThreadPoolExecutor(6) as ex:
    for q, E in ex.map(run, Q):
        print(q, len(E), flush=True)
        for e in E:
            v = out.setdefault(e["id"], {"id": e["id"], "title": e.get("title"), "duration": e.get("duration"),
                                         "channel_id": e.get("channel_id"), "channel": e.get("channel"), "views_search": e.get("view_count"), "queries": []})
            v["queries"].append(q)
json.dump(list(out.values()), open("discover.json", "w"), ensure_ascii=False)
print("unique", len(out))
