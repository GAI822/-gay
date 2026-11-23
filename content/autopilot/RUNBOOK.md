# ハイ自動投稿 手順書（定期実行のセッションはこの通りに進める）

持ち主の決定（2026-11-20）:
- **毎日2本**。Metricool の予約時刻は **18:00 と 19:00（日本時間）**。
- **公開前に持ち主が確認する**。Metricool には `draft: true`（下書き）で入れ、公開ボタンは持ち主が押す。**自分で公開しない。**
- Higgsfield のクレジットは **月800まで**（月額の付与日＝毎月11日ごろから数える）。

## 0. 準備

1. リポジトリ `gai822/-gay` のブランチ `claude/cat-character-design-3427im` を取得し、最新にする。
2. 必要なツール: Higgsfield と Metricool のコネクタ（ToolSearch で読み込む）。ffmpeg と python3（numpy）。
3. 今日の日付（日本時間）を確認する。`content/autopilot/log.jsonl` に今日の分が2本あれば、何もせず終える。

## 1. 予算の確認

1. Higgsfield `transactions` で、直近の「Subscription Credits」付与以降の spend 合計（refund を差し引く）を出す。
2. 合計 + 30 が 800 を超えるなら、**今日は作らない**。持ち主に「今月の上限に達したので止めた」と報告して終える。
3. `balance` が 30 未満でも同じく止める。

## 2. 企画を選ぶ

1. `content/autopilot/ideas.md` の `- [ ]` のうち、上から2つを使う。
2. 残りが10本を切っていたら、同じ決まりで10本書き足す。

## 3. 1本の作り方（1本 約10.5クレジット。作り直しは1回まで）

**参照画像（Higgsfield の ID。そのまま medias に入れられる）**

| 用途 | ID |
|---|---|
| ハイ（全身） | `339d4594-576f-4285-ba3b-a396514d003b` |
| ハイ（部屋で立つ） | `92f59334-395e-4f75-b24c-5e0d5a2fad1a` |
| ハイとミルク（キッチン） | `ea6f87bc-65c6-4ada-92e4-19515568902d` |
| リビングの部屋（ハイとクロ） | `158856ac-80a2-441d-a717-35bacc06cd3e` |

**手順**

1. **開始画像**: `generate_image`、model `gpt_image_2_5`、quality `medium`、resolution `2k`、aspect_ratio `9:16`。
   上の参照画像を2つまで入れる。プロンプトは英語で、次を必ず含める:
   `the exact same plain solid blue-grey short-haired cat with yellow eyes from the reference images (Hai)`、
   猫は `no clothes, no collar, natural fur, one tail each, anatomically correct real cats`、
   `amateur smartphone video frame, fixed phone camera`、`photorealistic, not cartoon, no people, no text, no watermark`。
   場面に必要な猫（クロ＝plain black cat、ミルク＝plain solid cream-white cat）と小道具を書く。
2. **画像の確認**: ダウンロードして目で見る。ハイがグレー単色で1匹、しっぽ1本、人間が写っていない、文字がない。ダメなら1回だけ作り直す。
3. **動画**: `generate_video`、model `kling3_0`、mode `std`、sound `off`、duration `7`、aspect_ratio `9:16`、
   medias に `start_image` として手順1の画像の job_id。
   プロンプトは英語で、`Fixed phone camera, no camera movement.` から始め、企画の「動き」と「オチ」を時間順に書き、
   **最後に企画の「オチの動き」を `PUNCHLINES.md` の英文で入れる**（`Then, as the punchline, <英文> and holds the final pose for one second, staring at the camera.`）。
   最初の動きは0秒から始める（静かに座っている時間を作らない）。
   `Hai's face stays completely expressionless and deadpan the whole time. Hai keeps the same plain blue-grey fur color in every frame.`
   `Realistic real cats with natural fur, no clothes, no text, no talking.` で終える。
   **提出前に `get_cost: true` で見積もり、12を超えたら設定を見直す。**
4. **動画の確認**: ダウンロードし、`fps=4` のコマ一覧を作って目で見る。次のどれかなら1回だけ作り直す（2回目もダメならその企画は飛ばして次へ）:
   - ハイの毛色が紺・黒に変わる（軽い青みなら `python3 content/motion/fix_blue.py in.mp4 out.mp4 0.2 1.7` で直してよい）
   - 人間や文字が出る、猫の体が崩れる、オチが起きない、**オチの動き（ポーズ）が分からない**
5. **仕上げ**: 冒頭の止まっている秒数を見て、
   `TEASER="<オチの動きの一番いい瞬間（切った後の秒数）>:0.9" bash content/autopilot/finish.sh take.mp4 final.mp4 <切る秒数> "<秒>:<効果音>" ...`
   **TEASER は必ず付ける。** オチの動きの決めの瞬間が冒頭0.9秒に先出しされ、巻き戻し音のあと本編が始まる。
   効果音は動きに合わせて3〜6個（種類は finish.sh の説明を参照）。字幕は入れない。
6. 保存先: `content/autopilot/<YYYYMMDD>_<番号>/`（`start.png`、`take.mp4`、`final.mp4`、`meta.json`）。

## 4. Metricool に下書きで入れる

1. `final.mp4` を Higgsfield の `media_upload` → curl PUT → `media_confirm` で上げ、返ってきた公開URLを使う。
2. `createScheduledPost`、blogId `7514409`、日時は今日の 18:00（1本目）と 19:00（2本目）、timezone `Asia/Tokyo`。
   info:
   - `"draft": true`、`"autoPublish": true`（持ち主が下書きを確定したら自動で出るように）
   - `providers`: youtube と instagram
   - `text`: `Hai's Daily Life: <英語タイトル> <絵文字1つ>\n\n<日本語タイトル>\nAI-generated video.\n\n#shorts #cat #catvideo #aicat #funnycat`
   - `youtubeData`: title `Hai's Daily Life: <英語タイトル> #shorts`、type `short`、privacy `public`、category `PETS_ANIMALS`、madeForKids `false`、**isAiGeneratedContent `true`**
   - `instagramData`: type `REEL`、showReelOnFeed `true`、**isAiGenerated `true`**
3. もう18:00を過ぎていたら、その日の 20:00 と 21:00 にずらす。それも過ぎていたら、今から1時間以内の次の正時と30分後にする。

## 5. 記録と報告

1. `content/autopilot/log.jsonl` に1本1行で追記: 日付、企画番号、タイトル、Higgsfield の job_id、使ったクレジット、Metricool の post id と plannerUrl、作り直した回数、気になった点。
2. `ideas.md` の使った企画を `- [x]` にする。
3. 前日以前に公開済みになった投稿は、Metricool の Instagram Reels の指標（IGRE23 再生、IGRE27 視聴率、IGRE30 3秒以内スワイプ率）を取り、`log.jsonl` の該当行の `metrics` に書き足す。
4. コミットしてブランチにプッシュする。
5. 最後の返答で持ち主に伝える: 作った2本の内容、Metricool の plannerUrl（下書きを開いて確認・公開する場所）、使ったクレジットと今月の合計、問題があればその内容。

## してはいけないこと

- 下書きを自分で公開・予約確定しない。
- 他人の動画・実在の人物・ブランドを使わない。
- 動物が痛い・冷たい・怖い目にあうネタを作らない。
- 1日の作り直しは各企画1回まで。予算を超えそうなら止めて報告する。
