# ハイ自動投稿 手順書（定期実行のセッションはこの通りに進める）

持ち主の決定（2026-11-20）:
- **毎日2本**。Metricool の予約時刻は **18:00 と 19:00（日本時間）**。
- ~~公開前に持ち主が確認する~~ → **2026-11-24 に持ち主の指示で自動公開に変更。** Metricool には `draft: false`、`autoPublish: true` で予約する。
  そのぶん、品質の確認（手順3-4）で少しでも決まりに外れたら予約しない。
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

## 3. 1本の作り方（2026-11-24 から：前半は Kling、オチは人の動きをハイに移す。1本 約17クレジット）

持ち主の方針: ハイ独自の動きは人間くささが出ないので、**オチは実際の人の動きをハイに被せる**。
動きの見本は `drivers/drivers.json`（Mixkit の無料素材。Mixkit License で商用・加工可。元の動画は git に入れない）。
各見本は Higgsfield にアップ済みで `media_id` がある。足りない見本は `drivers/prep_driver.py` で作ってアップし、drivers.json に足す。

**参照画像（Higgsfield の ID）**

| 用途 | ID |
|---|---|
| ハイ（全身） | `339d4594-576f-4285-ba3b-a396514d003b` |
| ハイ（部屋で立つ） | `92f59334-395e-4f75-b24c-5e0d5a2fad1a` |
| ハイとミルク（キッチン） | `ea6f87bc-65c6-4ada-92e4-19515568902d` |
| リビングの部屋（ハイとクロ） | `158856ac-80a2-441d-a717-35bacc06cd3e` |

**手順**

1. **開始画像**（1クレジット）: `generate_image`、model `gpt_image_2_5`、quality `medium`、resolution `2k`、aspect_ratio `9:16`。
   参照画像を2つまで入れる。プロンプトは英語で、次を必ず含める:
   `the exact same plain solid blue-grey short-haired cat with yellow eyes from the reference images (Hai)`、
   `no clothes, no collar, natural fur, one tail each, anatomically correct real cats`、`amateur smartphone video frame, fixed phone camera`、
   `photorealistic, not cartoon, no people, no text, no watermark`。クロ＝plain black cat、ミルク＝plain solid cream-white cat。
2. **前半の動画**（約7.5クレジット）: `generate_video`、model `kling3_0`、mode `std`、sound `off`、**duration `5`**、`9:16`、medias に開始画像を `start_image`。
   `Fixed phone camera, no camera movement. From the very first frame, ...` で始め、企画の「動き」とオチの直前までを書く。
   最後は `Hai's face stays completely expressionless and deadpan the whole time. Hai keeps the same plain blue-grey fur color in every frame. Realistic real cats with natural fur, no clothes, no text, no talking.`
3. **オチ用のハイの立ち姿**（1クレジット）: `generate_image`（設定は1と同じ）。参照に「開始画像」と「ハイ（全身）」。
   `Same room, same lighting and same props as the first reference image. The exact same plain solid blue-grey short-haired cat (Hai) now stands upright on its hind legs like a human, facing the camera, front legs hanging relaxed at its sides, seen from the knees up, in the center of the frame.`
   ＋オチに必要なほかの猫や小物の位置。上半身だけの見本（拍手・力こぶ・サムズアップ・頭を抱える・肩をすくめる）は `seen from the waist up` にする。
4. **オチの動画**（約7〜10クレジット）: `generate_video`、model `hf_mult_motion_control_flash`、aspect_ratio `9:16`、
   medias = 3の画像を `image_references`、企画の見本の `media_id` を `video_references`（1本だけ）。
   プロンプト: `The standing blue-grey cat Hai copies exactly the person's movement in the video: <動きの説明>. Same room and fixed camera as the image. Hai keeps a deadpan cat face and the same plain blue-grey fur. No people, no text.`
5. **確認**: 前半・オチとも `fps=4` のコマ一覧を見る。人間が写る・文字が出る・毛色が紺や縞に変わる・体が崩れる・動きが移っていない、なら1回だけ作り直す（2回目もダメならその企画は飛ばす）。
   軽い青みは `python3 ../motion/fix_blue.py in.mp4 out.mp4 0.2 1.7`（紫まで直すなら末尾に 165）。
6. **仕上げ**: `bash assemble_mt.sh setup.mp4 punch.mp4 final.mp4 <前半の頭を切る秒> <オチの頭を切る秒> <オチの長さ> <オチの決めの瞬間（オチの中の秒）> "<秒>:<効果音>" ...`
   前半とオチをつなぎ、オチの決めの瞬間を冒頭0.9秒に先出しし、効果音を付ける（効果音の秒数はつないだ本編の秒数）。字幕は入れない。
7. 保存先: `content/autopilot/<YYYYMMDD>_<番号>/`（`start.png`、`subject.png`、`setup.mp4`、`punch.mp4`、`final.mp4`）。

**予算**: 1本 約17クレジット、1日2本で約34。月800に収まらない見込みの日は、その日は1本にして報告する（目安: 残り予算 ÷ 次の付与日までの日数 が 34 未満なら1本）。

## 4. Metricool に予約を入れる（自動公開）

1. `final.mp4` を Higgsfield の `media_upload` → curl PUT → `media_confirm` で上げ、返ってきた公開URLを使う。
2. `createScheduledPost`、blogId `7514409`、日時は今日の 18:00（1本目）と 19:00（2本目）、timezone `Asia/Tokyo`。
   info:
   - `"draft": false`、`"autoPublish": true`（予約時刻に自動で公開される）
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

- 決まりに外れた動画（人・文字が写る、毛色が変わる、オチの動きが起きない、動物が痛い目にあう）は予約しない。
- 他人の動画・実在の人物・ブランドを使わない。
- 動物が痛い・冷たい・怖い目にあうネタを作らない。
- 1日の作り直しは各企画1回まで。予算を超えそうなら止めて報告する。
