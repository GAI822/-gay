# オチの動き一覧（自動制作で使う）

元データ: `analysis/punchline_moves/REPORT.md`（YouTube の人の動画 7,585本をタイトルで分類）。
上から順に「再生100万回以上の本数が多い」もの。猫（ハイ・クロ・ミルク）が無理なくできる形に直してある。

## 使い方

1. 企画の「オチ」のあと（動画の 4.5〜6.5秒あたり）に、下の動きを1つ入れる。動きは画面の真ん中で、全身が見える大きさにする。
2. Kling のプロンプトには、下の「プロンプト」の英文をそのまま入れ、その前に `Then, as the punchline,` を付ける。
   そのあとに `and holds the final pose for one second, staring at the camera.` を続ける（決めの静止が冒頭の先出しに使える）。
3. コマ一覧で、動きが起きているか（ポーズが分かるか）を確認する。起きていなければ「オチが起きない」として作り直し対象。
4. 仕上げで、その動きの一番いい瞬間を冒頭に先出しする:
   `TEASER="<切った後の秒数>:0.9" bash finish.sh take.mp4 final.mp4 <切る秒数> "<秒>:<効果音>" ...`
5. 字幕は入れない。曲名・作品名・選手名・ゲーム名はタイトルにも説明にも書かない。

## 一覧

| # | 動き | 100万回以上（本） | プロンプト（英語） | 効果音 |
|---|---|---:|---|---|
| 1 | シャッフル高速ステップ | 22 | `does a super fast human shuffle dance on its hind legs, feet sliding in and out rapidly` | beat |
| 2 | ゴールパフォーマンス（ひざスライディング・両腕を広げる） | 21 | `slides across the floor on its knees with both front legs spread wide like a soccer goal celebration` | cheer |
| 3 | スローモーション | 19 | `moves in dramatic slow motion, fur and ears flowing` | （無音にして steps を遅く） |
| 4 | ジャンプ回転して着地（決め） | 19 | `jumps, spins in the air, lands facing the camera with both front legs spread down and out, chest puffed` | jump, thud, cheer |
| 5 | カンフーの構え | 13 | `strikes a dramatic kung fu stance on its hind legs, one front paw forward, one raised` | pop |
| 6 | ムーンウォーク | 13 | `glides backwards on its hind legs in a smooth human moonwalk` | beat |
| 7 | アニメ風の決めポーズ | 12 | `strikes an exaggerated dramatic anime-style pose, body twisted, one paw over its face` | pop |
| 8 | 力こぶポーズ | 9 | `stands on its hind legs and flexes both front legs in a bodybuilder double biceps pose` | cheer |
| 9 | ポーズのまま固まる | 7 | `suddenly freezes completely still mid-motion like a mannequin` | （音を止める） |
| 10 | 馬乗りダンス | 5 | `does a bouncy horse-riding dance, front paws crossed as if holding reins` | beat |
| 11 | 深々とお辞儀 | 5 | `bows deeply and slowly like a polite human` | pop |
| 12 | ガッツポーズ | 3 | `pumps one front paw down hard in a human fist-pump of victory` | cheer |
| 13 | ダブ | 3 | `does a quick human dab pose, head tucked into one bent front leg, other leg stretched out` | pop |
| 14 | 四股を踏む | 3 | `raises one hind leg high to the side and stomps down like a sumo wrestler, then the other` | thud, thud |
| 15 | 忍者走り | 3 | `runs away on its hind legs leaning forward with both front legs stretched straight back` | steps |
| 16 | マイクドロップ | 2 | `holds a small object out at arm's length and drops it straight down, deadpan` | thud |
| 17 | ゆっくり拍手 | 2 | `claps its front paws together slowly three times` | pop, pop, pop |
| 18 | 横目でチラ見 | 2 | `slowly slides its eyes sideways to look at the other cat without moving its head` | （無音） |
| 19 | 指鉄砲 | 2 | `points both front paws at the camera like finger guns` | pop |
| 20 | かっこつけて歩き去る | 0〜1 | `turns and walks away coolly without looking back` | steps |

## 使わない動き

- ゲームのエモートそのまま（権利の心配。ボトルフリップのダンス版と同じ理由）
- 腰振り・おしりのダンス（性的に見えやすい）
- 猫が落ちる・ぶつかる・痛そうに見える宙返りや転倒（動物が痛い目にあう型）
- 実在の歌手・選手と分かる衣装や小物
