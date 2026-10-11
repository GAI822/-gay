"""生成した動画を YouTube にアップロードし、多言語タイトル・字幕を付けて予約公開する。

必要な環境変数: YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN（YT_* でも可）
使い方:
  python3 tools/shorts_factory/youtube_upload.py out/oddone_1.json --publish-at 2026-10-09T06:00+09:00
  python3 tools/shorts_factory/youtube_upload.py out/oddone_1.json --dry-run   # 送信せず内容だけ表示
  python3 tools/shorts_factory/youtube_upload.py --check                        # 鍵が有効か確認

注意: Google の監査(Audit)を通過していないプロジェクトからの動画は、YouTube 側で強制的に非公開になる。
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3"
CATEGORY_ENTERTAINMENT = "24"


def env(name):
    # YT_* と YOUTUBE_* のどちらの名前で登録されていても読む
    return os.environ.get(f"YT_{name}") or os.environ.get(f"YOUTUBE_{name}")


def access_token():
    names = ("CLIENT_ID", "CLIENT_SECRET", "REFRESH_TOKEN")
    missing = [f"YOUTUBE_{n}" for n in names if not env(n)]
    if missing:
        sys.exit(f"環境変数が未設定です: {', '.join(missing)}")
    r = requests.post(TOKEN_URL, data={
        "client_id": env("CLIENT_ID"),
        "client_secret": env("CLIENT_SECRET"),
        "refresh_token": env("REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }, timeout=30)
    if r.status_code != 200:
        # invalid_grant = 鍵の期限切れ・取り消し（「テスト」状態のままだと7日で切れる）
        sys.exit(f"鍵の更新に失敗しました: {r.status_code} {r.text[:200]}")
    return r.json()["access_token"]


def scopes(tok):
    info = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": tok}, timeout=30).json()
    return set(info.get("scope", "").split())


def video_body(meta, publish_at, privacy="public"):
    title, desc = meta["title"], meta["description"]
    tags = [h.lstrip("#") for h in meta["hashtags"]]
    status = {
        "privacyStatus": "private" if publish_at else privacy,
        "selfDeclaredMadeForKids": False,
        "embeddable": True,
        # リアルに見えるAI生成映像は「改変・合成コンテンツ」の申告が必要
        "containsSyntheticMedia": bool(meta.get("synthetic_disclosure")),
    }
    if publish_at:
        # 予約公開: 非公開でアップロードし、指定時刻に YouTube 側が公開する
        status["publishAt"] = datetime.fromisoformat(publish_at).isoformat()
    return {
        "snippet": {
            "title": title["en"][:100],
            "description": desc["en"] + "\n\n" + " ".join(meta["hashtags"]),
            "tags": tags,
            "categoryId": CATEGORY_ENTERTAINMENT,
            "defaultLanguage": "en",
        },
        "localizations": {lang: {"title": title[lang][:100], "description": desc[lang]}
                          for lang in title if lang != "en"},
        "status": status,
    }


def upload(meta_path, publish_at, dry_run, privacy="public", title_prefix=""):
    meta_path = Path(meta_path)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    mp4 = meta_path.with_suffix(".mp4")
    body = video_body(meta, publish_at, privacy)
    if title_prefix:
        body["snippet"]["title"] = (title_prefix + body["snippet"]["title"])[:100]
    srts = sorted(meta_path.parent.glob(f"{meta['id']}.*.srt"))
    if dry_run:
        print(json.dumps(body, ensure_ascii=False, indent=2))
        print("字幕:", [s.name for s in srts], "| 動画:", mp4.name, f"{mp4.stat().st_size // 1024}KB")
        return
    tok = access_token()
    h = {"Authorization": f"Bearer {tok}"}
    # レジューム可能アップロード: まずセッションを作り、そこへ動画本体を送る
    r = requests.post(f"{UPLOAD}/videos", params={"uploadType": "resumable", "part": "snippet,status,localizations"},
                      headers={**h, "Content-Type": "application/json; charset=UTF-8",
                               "X-Upload-Content-Type": "video/mp4"},
                      data=json.dumps(body), timeout=60)
    r.raise_for_status()
    with open(mp4, "rb") as f:
        r = requests.put(r.headers["Location"], headers={**h, "Content-Type": "video/mp4"}, data=f, timeout=600)
    r.raise_for_status()
    vid = r.json()["id"]
    print("uploaded:", f"https://youtube.com/shorts/{vid}", r.json()["status"].get("privacyStatus"))
    if "https://www.googleapis.com/auth/youtube.force-ssl" not in scopes(tok):
        # 字幕の追加には youtube.force-ssl の権限が必要
        print("字幕: 鍵に字幕の権限がないため省略（YouTube Studioで手動追加、または鍵を取り直す）")
        srts = []
    for srt in srts:
        lang = srt.suffixes[-2].lstrip(".")
        snippet = {"snippet": {"videoId": vid, "language": lang, "name": lang}}
        files = {"metadata": (None, json.dumps(snippet), "application/json; charset=UTF-8"),
                 "media": (srt.name, srt.read_bytes(), "application/octet-stream")}
        cr = requests.post(f"{UPLOAD}/captions", params={"uploadType": "multipart", "part": "snippet"},
                           headers=h, files=files, timeout=60)
        print("caption", lang, cr.status_code)
    log = meta_path.parent / "uploaded.jsonl"
    with open(log, "a") as f:
        f.write(json.dumps({"id": meta["id"], "youtube_id": vid, "publish_at": publish_at}) + "\n")


def check():
    tok = access_token()
    sc = scopes(tok)
    print("鍵の更新: OK | 権限:", " ".join(x.rsplit("/", 1)[-1] for x in sorted(sc)))
    if "https://www.googleapis.com/auth/youtube.upload" not in sc and "https://www.googleapis.com/auth/youtube" not in sc:
        sys.exit("アップロード権限がありません")
    if not sc & {"https://www.googleapis.com/auth/youtube.force-ssl", "https://www.googleapis.com/auth/youtube.readonly",
                 "https://www.googleapis.com/auth/youtube"}:
        print("アップロードは可能。チャンネル情報・字幕・再生数の取得には youtube.force-ssl の権限が追加で必要")
        return
    r = requests.get(f"{API}/channels", params={"part": "snippet,statistics", "mine": "true"},
                     headers={"Authorization": f"Bearer {tok}"}, timeout=30)
    r.raise_for_status()
    for c in r.json().get("items", []):
        print("接続OK:", c["snippet"]["title"], "| 登録者", c["statistics"].get("subscriberCount"),
              "| 動画数", c["statistics"].get("videoCount"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("meta", nargs="?")
    ap.add_argument("--publish-at", help="予約公開時刻 例: 2026-10-09T06:00+09:00")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--privacy", choices=["public", "unlisted", "private"], default="public")
    ap.add_argument("--title-prefix", default="", help="例: '[TEST] '")
    a = ap.parse_args()
    if a.check:
        check()
    elif a.meta:
        upload(a.meta, a.publish_at, a.dry_run, a.privacy, a.title_prefix)
    else:
        ap.print_help()
