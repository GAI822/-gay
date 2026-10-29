# トラ（TORA）— ブランドキャラクター設定書

人の動きをそのまま投影した、実写リアルな猫。今後の投稿はこの1匹を主軸にする。

| ファイル | 用途 |
|---|---|
| `01_turnaround.png` | **マスター参照**（正面 / 3/4 / 横 / 背面）。生成時は必ずこれを参照画像に入れる |
| `02_expressions.png` | 表情シート（無表情・ドヤ・驚き・ため息・横目・胸張り） |
| `03_scene_kitchen.png` | 投稿イメージ（9:16、生活シーンに置いたときの見え方の確認） |

Higgsfield の job_id（参照画像としてそのまま使える）:
- マスター: `408f2252-eff6-4915-b886-2760deef5d78`
- 表情シート: `c1b80067-c2cd-43d2-8c31-b81d4fed1e98`

## ブランドの核

- **一言で:** 「人間より人間くさい、真顔の中年オス猫」
- **笑いの型:** 本人（猫）は真剣、やっていることは人間の日常。表情はほぼ変えず、**真顔のまま人間の動きをする**ギャップで笑わせる。
- **トーン:** ほのぼの・生活感・少しだけ哀愁。下品・攻撃的なネタはしない。
- **持ち場:** 一人暮らしの小さな部屋。料理、在宅ワーク、買い物、筋トレ、ため息。

## 見た目の固定ルール（毎回この通りに書く）

| 部位 | 固定値 |
|---|---|
| 種類 | オスの茶トラ（サバ柄の縞）、大きめでややぽっちゃり、頬がまるい |
| 毛色 | 明るいジンジャーオレンジ＋濃い赤茶の縞、額に「M」模様 |
| 白い部分 | 口まわり・あご・胸元（よだれかけ状）、四肢の先が白い靴下 |
| 目 | 銅色がかったアンバー、光らせない |
| 鼻 | れんがピンク |
| 識別マーク | **左耳（向かって右）の先に小さな切れ込み** |
| 服 | ネイビーの太編みカーディガン（少し大きめ、木のトグルボタン2つ、ポケット付き）＋オフホワイトのTシャツ |
| 小物 | 深緑の細い首輪＋丸い真鍮のネームタグ |
| 下半身 | 服なし、猫の脚と足のまま |
| 手 | 人間の手にしない。必ず猫の前足で物を持つ |

ブランドカラー: **オレンジ（毛） / ネイビー（カーディガン） / 深緑（首輪） / 真鍮ゴールド（タグ）**。サムネや文字の色もこの4色から選ぶ。

服を変える回（季節もの等）でも、**首輪と真鍮タグと耳の切れ込みは絶対に外さない**。この3つが「同じ猫」の目印になる。

## 生成プロンプトの雛形

モデル: `gpt_image_2_5`（medium / 2k で1クレジット）。参照画像に **マスターの job_id** を入れる。

```
[シーンの説明], the exact same orange tabby cat character from the reference image
(identical face and fur pattern, copper-amber eyes, white muzzle and bib, white paws,
notch on tip of left ear, navy chunky knit cardigan with wooden toggle buttons,
off-white t-shirt, forest-green collar with round brass tag) standing upright on hind
legs, [動作], deadpan serious expression, natural human-like posture,
shot on iPhone, casual handheld vlog framing, natural film grain,
photorealistic real cat with individual fur strands, not cartoon, not CGI,
no human hands, no people, no other animals, no text, no watermark, no logos.
```

縦動画は `aspect_ratio: 9:16`。

## 動画化（人の動きを投影する）

1. 人が演じた動画（mp4、3〜10秒、1人・全身が映る・背景は単純なほど良い）を撮る。
2. Higgsfield の motion control（Kling のモーション転写）に、**動画＝人の演技 / 画像＝`01_turnaround.png` か同じ構図のシーン画像** を渡す。
3. 出来た動画を `tools/analyze_short.py` で既存ショートと比べてテンポを確認する。

最初のフレームの構図（全身か上半身か）を、人の動画とシーン画像で揃えると崩れにくい。

## 生成時の注意

- 表情が大きく動くと、耳の切れ込みが両耳に出たり消えたりすることがある（表情シートの驚き顔で発生）。投稿前に耳を確認する。
- 実在のキャラクターや他チャンネルの猫に寄せた指示は入れない。トラは独自のキャラクター。
- AI生成であることは、これまでどおり概要欄で開示する。
