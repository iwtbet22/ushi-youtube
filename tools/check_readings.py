"""読みの辞書 (docu/readings.py) のうち、本当に置き換えが必要な語を調べる。

漢字のまま読ませた音声と、指定した読み (ひらがな) で読ませた音声を、MFCC の DTW 距離で比べる。
近ければ合成音声は漢字のままでも正しく読めているので、置き換えない方がアクセントが自然になる。
しきい値は、同じ読みの組 (東京/とうきょう など) と違う読みの組 (東京/おおさか など) の距離から決める。

  python3 tools/check_readings.py            # 結果を表で出す
"""
from __future__ import annotations

import sys
from pathlib import Path

import librosa
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docu"))
sys.path.insert(0, str(ROOT / "render"))
import film  # noqa: E402
import readings  # noqa: E402
import tts  # noqa: E402

CARRIER = "これは、{}です。"


def feat(text):
    wav = tts.ensure(CARRIER.format(text), **film.VOICE)
    y, sr = librosa.load(str(wav), sr=16000)
    y, _ = librosa.effects.trim(y, top_db=35)
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=160)
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)


def dist(a, b):
    fa, fb = feat(a), feat(b)
    D, wp = librosa.sequence.dtw(X=fa, Y=fb, metric="euclidean")
    return float(D[-1, -1] / len(wp))


def main():
    same = [("東京", "とうきょう"), ("野球", "やきゅう"), ("選手", "せんしゅ"), ("球団", "きゅうだん")]
    diff = [("東京", "おおさか"), ("野球", "すいえい"), ("選手", "かんとく"), ("球団", "せんしゅ")]
    ds = [dist(a, b) for a, b in same]
    dd = [dist(a, b) for a, b in diff]
    th = (max(ds) + min(dd)) / 2
    print(f"same {np.round(ds, 2)}  diff {np.round(dd, 2)}  threshold {th:.2f}")
    for k, v in readings.READ.items():
        d = dist(k, v)
        print(f"{'不要' if d < th else '必要'}  {d:5.2f}  {k} → {v}", flush=True)


if __name__ == "__main__":
    main()
