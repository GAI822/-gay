"""生成した動画を YouTube にアップロードし、多言語タイトル・字幕を付けて予約公開する。

必要な環境変数: YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN
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


def access_token():
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        sys.exit(f"環境変数が未設定です: {', '.join(missing)}")
    r = requests.post(TOKEN_URL, data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }, timeout=30)
    if r.status_code != 200:
        # invalid_grant = 鍵の期限切れ・取り消し（「テスト」状態のままだと7日で切れる）
        sys.exit(f"鍵の更新に失敗しました: {r.status_code} {r.text[:200]}")
    return r.json()["access_token"]


def video_body(meta, publish_at):
    title, desc = meta["title"], meta["description"]
    tags = [h.lstrip("#") for h in meta["hashtags"]]
    status = {
        "privacyStatus": "private" if publish_at else "public",
        "selfDeclaredMadeForKids": False,
        "embeddable": True,
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
            "defaultAudioLanguage": "zxx",  # 言語なしのコンテンツ
        },
        "localizations": {lang: {"title": title[lang][:100], "description": desc[lang]}
                          for lang in title if lang != "en"},
        "status": status,
    }


def upload(meta_path, publish_at, dry_run):
    meta_path = Path(meta_path)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    mp4 = meta_path.with_suffix(".mp4")
    body = video_body(meta, publish_at)
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
    a = ap.parse_args()
    if a.check:
        check()
    elif a.meta:
        upload(a.meta, a.publish_at, a.dry_run)
    else:
        ap.print_help()
