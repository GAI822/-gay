# ハイのコント動画 — 台本とプロンプト

参考リール6本（2026-11-07 受領）の型:

| | 内容 | 長さ |
|---|---|---:|
| 1〜4 | グレーと黒の猫が立ち上がり、ステンレスのボウルを高速で回し合う「謎の遊び」。後ろのソファで白黒の猫が真顔で見ている | 8〜10秒 |
| 5・6 | ねじり鉢巻きの柴犬2匹がキッチンでコーヒーを入れて大惨事、最後に頭を抱える | 9〜12秒 |

**共通の作り**
- 固定カメラ・1か所・セリフなし。
- **2匹の掛け合い＋見ている1匹**、または**作業→失敗のオチ**。
- 1秒目から動いている。動きは人間そのもの（手つき・間・リアクション）で、顔は動物のまま。
- 音は効果音（金属音、こぼれる音）と軽いBGM。

## キャスト

| 役 | 見た目 | 性格づけ（演技でだけ出す） |
|---|---|---|
| ハイ | 柄なしブルーグレー短毛、黄色い目（`character/hai/`） | 真面目。いつも段取りをする側 |
| 相方 | 柄なしクリームホワイト短毛、黄色い目 | 雑。ハイの段取りを壊す側 |
| 見物 | 黒猫（ソファの上で座って見ているだけ） | 一切動かない。オチで少しだけ首を傾ける |

衣装や表情は付けない（「人間味の無い猫」）。小道具で場面を作る。

## 台本（各10秒）

| # | タイトル（字幕） | 0〜3秒 | 3〜8秒 | 8〜10秒（オチ） |
|---|---|---|---|---|
| 1 | 何この遊び？（ボウル回し） | 2匹が立ち、ボウルを1枚ずつ回してパス | 速度が上がり、ボウルが2枚、3枚に増える | 全部が見物の黒猫の頭にかぶさって止まる |
| 2 | コーヒー淹れてくれた | ハイがドリップポットで丁寧に注ぐ | 相方が砂糖をスプーンで山盛り10杯 | ハイが無言でカップを相方の前に押し出す |
| 3 | 洗濯物たたみ | 2匹が向かい合ってタオルを高速でたたむ | 積み上がるタオルの山 | 相方が山にダイブして全部崩れる。ハイが固まる |
| 4 | お寿司屋さん | ハイが真剣にシャリを握る | 握った端から相方が食べる、を繰り返す | ハイが握るのをやめ、相方が皿だけ見つめる。冒頭にループ |
| 5 | せっせっせ | 2匹が向かい合って手遊び（拍手→手合わせ） | だんだん高速になる | 相方の手が空振りして顔にパンチ。見物の黒猫がまばたき |
| 6 | 卓上ホッケー | テーブルの両端で鍋ぶたをラケットにして小皿を打ち合う | ラリーが高速化 | 小皿が見物の黒猫の前で止まり、黒猫が前足でそっと戻す |

## Kling 3.0 用プロンプト（10秒・9:16・1本20クレジット）

開始フレームに2匹の画像（`character/hai/05_duo_kitchen.png`、キッチンの場面のみ）を入れる場合は image-to-video、無い場合は text-to-video。リビングの開始フレームはローカルの画像モデルではうまく作れなかった（猫が小さい・数が合わない）ので、クレジットが入ったら Higgsfield で作る。どちらも共通の前置きを付ける。

**共通の前置き**
```
Fixed smartphone camera on a tripod, vertical 9:16, real home, photorealistic real cats with natural fur and cat faces,
no clothes, no accessories. Left: a plain solid blue-grey short-haired cat with yellow eyes. Right: a plain solid
cream-white short-haired cat with yellow eyes. Both stand upright on their hind legs and move their front legs exactly
like humans, with crisp human timing, while their faces stay completely expressionless. No talking, no text.
```

1. `In a plain living room with a beige wall, a black cat sits on a dark grey sofa in the background, watching without moving. The two cats face each other and pass a stainless steel bowl back and forth, spinning it with one paw like a juggling game. The rhythm speeds up and a second and third bowl join in, clanging metal sounds. At the end all three bowls land upside down on the black cat's head and everything stops.`
2. `At a home kitchen counter in the evening. The grey cat carefully pours hot water from a gooseneck kettle into a drip coffee cup, slow and precise. The white cat scoops sugar into the cup with a spoon again and again, ten heaping spoons, sugar spilling over. At the end the grey cat silently slides the cup in front of the white cat and stares at it.`
3. `On a living room floor, the two cats face each other and fold bath towels at high speed, stacking them into a tall neat pile. At the end the white cat jumps into the pile and all the towels collapse; the grey cat freezes holding a folded towel.`
4. `At a small sushi counter at home, the grey cat seriously shapes sushi rice with both front paws and places each piece on a plate. Each time, the white cat immediately picks it up and eats it. This repeats faster. At the end the grey cat stops and the white cat stares at the empty plate.`
5. `In a plain living room, a black cat watches from the sofa. The two cats face each other and play a hand-clapping game: clap, then press paws together, clap, then press paws together, getting faster and faster. At the end the white cat misses and its paw bops the grey cat on the nose. The black cat blinks once.`
6. `At a dining table, the two cats stand at opposite ends holding pot lids like paddles and hit a small saucer back and forth like air hockey, the rally getting faster with clacking sounds. At the end the saucer slides to a black cat sitting at the table, who calmly pushes it back with one paw.`

## 制作手順

1. 11月11日ごろの月額1,000クレジットを待つ（または追加購入）。
2. 1〜6を各1本（計120クレジット）作り、使える出来のものを選ぶ。
3. 上部に英語＋日本語の1行字幕を入れる（例: "What is this game? / 何この遊び？"）。
4. 出来の良かった型は、小道具だけ変えてシリーズ化する（ボウル→お玉、コーヒー→紅茶 など）。
5. AI生成の開示は必ず付ける。

## 人の演技を使う場合（より自然な動き）

2人で同じコントを演じてスマホで撮り、Higgsfield の motion control（`hf_mult_motion_control`）に「動画＝2人の演技 / 画像＝duo の開始フレーム」を渡す。Kling の文章だけで作るより、間や手つきが人間らしくなる。
