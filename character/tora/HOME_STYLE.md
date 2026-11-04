# 素のトラ（家撮り版）— 参考リールに合わせた設定

## 参考リール4本の共通点（2026-11-04 受領）

| | 内容 | 長さ |
|---|---|---:|
| 1 | シルバータビーが床で立ち上がり、カンフー／ボクシングの型をする（いいね46.2万） | 12秒 |
| 2 | 黒猫が立ち上がり、腕を振って踊る。手前に撮影者の足 | 9秒 |
| 3・4 | 白黒猫の顔アップ。口パクしながら人間の手振り（「今こんな気分」） | 8〜12秒 |

- **猫は服を着ていない、普通の飼い猫。** 作り込みゼロ。
- **背景は生活感のある自宅**（タイルの床、家電、ソファ）。
- **スマホの手持ち撮影っぽい画質**（少しブレる、明るさがまちまち）。
- **人の動きがそのまま入っている**（立ち上がり、腕の振り、口の動き）。
- **8〜12秒の1カット。** 文字はほぼなし。最初の1秒からもう動いている。

→ 前回の分析（「1本1出来事・15秒前後・冒頭から動く」）とも一致する。

## キャラクター

カーディガン版トラと**同じ猫**にする（毛柄・識別マークは README の固定ルールのまま）。服だけ脱いで、首輪とタグは残す。
- 茶トラ（サバ柄）、オス、大きめでぽっちゃり、頬がまるい
- 口まわり・あご・胸元・足先が白い
- 銅色がかったアンバーの目、れんがピンクの鼻
- **左耳の先に小さな切れ込み**
- 深緑の細い首輪＋丸い真鍮タグ（家撮り版でも外さない）

## 生成プロンプト（3枚、各1クレジット）

モデル `gpt_image_2_5`、medium、2k、9:16。参照画像にマスター `408f2252-eff6-4915-b886-2760deef5d78` を入れる。

### A. 全身・立ち上がり（カンフー／ダンス用の開始フレーム）

```
Vertical smartphone video frame, the exact same orange tabby cat from the reference image but wearing no clothes, only the thin forest-green collar with the small round brass tag, same face and fur pattern, white muzzle chin chest and paws, copper-amber eyes, small notch on the tip of his left ear, chunky adult tomcat. He is standing upright on his hind legs in the middle of a plain Japanese apartment floor with beige ceramic tiles, front paws raised loosely in front of his chest, looking at the camera, full body visible head to feet with some floor around him. Background: a cluttered real home corner with a fan, a laundry basket and a wall. Amateur handheld phone video look, slightly high camera angle, flat indoor ceiling light, mild noise and slight motion blur, no color grading. Photorealistic real cat with natural fur, not cartoon, not CGI, no clothes, no people, no other animals, no text, no watermark, no logos.
```

### B. 顔アップ（口パク・手振り用の開始フレーム）

```
Vertical smartphone video frame, extreme close-up of the exact same orange tabby cat from the reference image, no clothes, forest-green collar with round brass tag just visible, same face and fur pattern, white muzzle and chin, copper-amber eyes, notch on the tip of his left ear. He sits upright facing the camera very close, face filling the upper half of the frame, chest and both white front paws visible at the bottom of the frame, mouth closed, calm deadpan expression. Background: a blurred warm-brown living room wall and sofa. Amateur phone selfie-distance shot, soft indoor lamp light, slight noise, no color grading. Photorealistic real cat, natural whiskers, not cartoon, not CGI, no people, no hands, no text, no watermark, no logos.
```

### C. ソファでくつろぐ（日常ネタ・ループの開始フレーム）

```
Vertical smartphone video frame, the exact same orange tabby cat from the reference image, no clothes, forest-green collar with round brass tag, same face and fur pattern, notch on the tip of his left ear, sitting upright like a tired middle-aged man on a worn grey fabric sofa, back against the cushion, hind legs stretched forward, belly relaxed, front paws resting on his belly, half-closed eyes looking at the camera. Real lived-in living room, a TV remote and a crumpled blanket next to him, evening ceiling light. Amateur handheld phone video look, mild noise, no color grading. Photorealistic real cat, not cartoon, not CGI, no clothes, no people, no other animals, no text, no watermark, no logos.
```

## 動画化

1. 自分で同じ構図（全身 or 顔アップ）で演技して、スマホで8〜12秒撮る。手前に自分の足が映るのも参考リール2と同じで問題ない。
2. Higgsfield の motion control に「動画＝自分の演技 / 画像＝A か B」を渡す。
3. 画像の構図（全身か顔アップか、カメラの高さ）を演技動画と揃えると崩れにくい。
4. 口パクは B を使う。手の動きが大きいときは、画像側でも前足を画面に入れておく。

AI生成の開示は続ける。他人のリールの猫や映像を素材として使わない（参考は構図と撮り方のみ）。
