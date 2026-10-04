"""ショート動画の構造を数値化する解析スクリプト。

使い方: python3 tools/analyze_short.py video1.mp4 [video2.mp4 ...]
必要: pip install scenedetect opencv-python-headless librosa / ffmpeg
"""
import json
import subprocess
import sys

import librosa
import numpy as np
from scenedetect import ContentDetector, detect


def analyze(path):
    scenes = detect(path, ContentDetector(threshold=27))
    cuts = [s[0].seconds for s in scenes[1:]]
    probe = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path]))
    duration = float(probe["format"]["duration"])

    result = {
        "file": path,
        "duration_s": round(duration, 1),
        "cuts": len(cuts),
        "avg_shot_len_s": round(duration / (len(cuts) + 1), 2),
        "cuts_in_first_3s": sum(c < 3 for c in cuts),
        "first_cut_s": round(cuts[0], 2) if cuts else None,
    }

    try:
        y, sr = librosa.load(path, sr=22050, mono=True)
        rms = librosa.feature.rms(y=y)[0]
        times = librosa.times_like(rms, sr=sr)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        loud = lambda a, b: float(np.mean(rms[(times >= a) & (times < b)]) + 1e-9)
        result.update({
            "bpm": round(float(np.atleast_1d(tempo)[0]), 1),
            "sound_events_per_s": round(len(onsets) / duration, 2),
            # >1 なら冒頭が平均より大きい音 = 音でのフックがある
            "hook_loudness_ratio": round(loud(0, 3) / float(np.mean(rms) + 1e-9), 2),
            # <1 なら終盤が静か = 余韻型、>1 ならラストで盛り上げる型
            "ending_loudness_ratio": round(loud(duration - 3, duration) / float(np.mean(rms) + 1e-9), 2),
        })
    except Exception as e:  # 無音動画など
        result["audio_error"] = str(e)
    return result


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(json.dumps(analyze(p), ensure_ascii=False))
