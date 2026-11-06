# ハイのコント動画 — オリジナル台本とプロンプト

## 参考リールの扱い

参考リール6本（2026-11-07 受領）は**型の研究にだけ使う**。ネタ・小道具・場面・キャラクターは借りない。

参考から学んだ「型」（どの動画にも共通する仕組み）:
- 固定カメラ・1か所・セリフなし、8〜12秒。
- 2匹の掛け合い、オチで反応する見物役。
- だんだん加速するか、作業が失敗して落ちる。
- 1秒目から動いている。動きは人間、顔は動物のまま。

**使わないもの:**
- 参考の具体的なネタ（ボウルを回し合う遊び、コーヒーを入れて失敗する）。
- 参考の配役（グレー＋黒＋白黒の3匹、鉢巻きの柴犬）と、その部屋の作り。

## キャスト（オリジナル）

| 役 | 見た目 | 演技でだけ出す性格 |
|---|---|---|
| ハイ | 柄なしブルーグレー短毛、黄色い目（`character/hai/`） | 真面目。段取りをする側 |
| ミルク | 柄なしクリームホワイト短毛、黄色い目 | 雑。段取りを壊す側 |
| クロ | 黒猫 | 毎回オチにだけ出てくる「先客」。表情は変えない |

衣装・表情は付けない（「人間味の無い猫」）。笑いは、人間くさい行動と無表情のズレだけで作る。

## 台本（各10秒・オリジナル）

| # | タイトル（字幕） | 流れ | オチ |
|---|---|---|---|
| 1 | POV: あなたは冷蔵庫 | 冷蔵庫の中から見た視点。2匹が開けて無言でのぞき、閉める。開けるたびに顔が近づく | 視点が切り替わると、冷蔵庫の中にクロが座っている |
| 2 | 体重計 | ハイが体重計に乗って数字を見る。乗り直す、片足で乗る、息を吐いて乗る | 後ろでミルクがずっと前足で踏んでいた。ハイが振り向いて固まる |
| 3 | 靴下合わせ選手権 | 2匹が洗濯物の山から靴下のペアを高速で見つけていく | 最後の1足の片方が見つからない。カメラが引くと、クロが履いている |
| 4 | ドミノ | ハイが息を止めて慎重にドミノを並べていく、長い列 | ミルクのくしゃみで全部倒れ、最後の1枚がクロの前で止まる。クロが前足で倒す |
| 5 | 電子レンジ待ち | 2匹がレンジの前に並び、残り時間を見つめる。同時に前足でトントン | 「チン」で2匹が同時に振り向くと、クロがもう食べている |
| 6 | 宅配便の受け取り | インターホンが鳴り、2匹が玄関まで競歩で競争、譲り合い、また競争 | ドアを開けると箱だけ。中からクロが出てくる |

クロが毎回オチにだけ出てくる「先客」の形式は、シリーズの決まりごとにする（同じオチ役がいると、2本目以降は視聴者が先を予想して見続ける）。

## Kling 3.0 用プロンプト（10秒・9:16・1本20クレジット）

**共通の前置き**
```
Fixed smartphone camera, vertical 9:16, small real Japanese apartment, photorealistic real cats with natural fur and
cat faces, no clothes, no accessories. Hai: a plain solid blue-grey short-haired cat with yellow eyes. Milk: a plain
solid cream-white short-haired cat with yellow eyes. Kuro: a plain black cat. Hai and Milk stand upright on their hind
legs and move their front legs exactly like humans, with crisp human timing, while their faces stay completely
expressionless. No talking, no text.
```

1. `The camera is inside a refrigerator looking out. The fridge door opens: Hai and Milk stand in the dark kitchen, lit by the cold fridge light, silently staring in. The door closes to darkness. It opens again and they are closer. Closed. Open, even closer, their faces filling the frame. Then the camera turns around inside the fridge to reveal Kuro sitting calmly on the middle shelf between the milk and eggs.`
2. `In a bathroom, Hai steps onto a digital bathroom scale and looks down at the number, steps off, steps on again, tries standing on one leg, exhales and steps on again, each time staring at the display. Behind Hai, Milk has been pressing one paw on the edge of the scale the whole time. At the end Hai slowly turns around and freezes, looking at Milk.`
3. `On a living room floor next to a big pile of laundry, Hai and Milk race to find matching pairs of socks, holding them up and tossing pairs into a basket faster and faster. At the end one sock has no partner. Both look around. The camera pulls back to show Kuro sitting nearby, wearing the missing sock on one front paw.`
4. `On a wooden floor, Hai holds its breath and carefully places dominoes one by one in a long curving line. Milk watches, then sneezes. All the dominoes fall in a chain. The last domino stops right in front of Kuro, who calmly pushes it over with one paw.`
5. `In a kitchen, Hai and Milk stand side by side in front of a running microwave, watching the countdown and tapping their front paws on the counter in sync. The microwave beeps. Both turn around at the same time: Kuro is behind them, already eating from the bowl.`
6. `The intercom rings. Hai and Milk race-walk side by side down a narrow hallway to the front door, bump shoulders, politely let each other go first, then race again. Hai opens the door: only a cardboard box is there. The box flaps open and Kuro climbs out.`

## 絵コンテ動画（クレジットが無い間の試作）

`fridge/` に台本1の試作がある。
- `fridge_animatic.mp4`: 10秒。静止画のズームと切り替え、合成した効果音（冷蔵庫の音・ドアの音）でできている。
- `make_animatic.py`: 作り直し用のスクリプト。

これで間（ま）とオチの効き方を確認してから、Kling の本番を作る。

## 制作手順

1. クレジット（11月11日ごろの月額1,000クレジット）が入ったら、1〜6を各1本作る（計120クレジット）。
2. 出来の良いものを選び、上部に英語＋日本語の1行字幕を入れる。
3. 投稿後の「視聴を継続」を記録し、50%を超えたネタの形をシリーズにする（小道具や場所だけ替える）。
4. AI生成の開示は必ず付ける。
