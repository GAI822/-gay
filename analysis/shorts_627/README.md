# YouTube Shorts 627本 解析（2026-10-04）

- 対象: 27チャンネルのShortsタブから各最大25本（MrBeast, Zach King, NileRed, Fischer's, はじめしゃちょー 等）
- 取得できたもの: タイトル・再生数・カバー画像。動画本体はYouTubeのボット確認で取得不可。
- 指標: 「チャンネル内中央値に対する再生数の倍率（log10）」。各チャンネル最新3本は除外（n=550）。
- 特徴量: タイトル（長さ・絵文字・?・!・数字・ハッシュタグ等）、カバー画像（明るさ・彩度・色彩度・コントラスト・顔検出YuNet・文字OCR tesseract）
- 実行: `python3 feat.py`（yunet.onnx と th/ にカバー画像が必要）→ `python3 stats.py`
- 結果: stats_output.txt
