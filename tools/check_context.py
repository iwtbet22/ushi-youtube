"""文の中で、合成音声がある語をどちらの読みで言っているかを確かめる。

文をそのまま読ませた音声と、その語だけをひらがなの「正しい読み」「誤った読み」に置き換えた
音声を MFCC の DTW 距離で比べ、近い方をその文での実際の読みとみなす。
語を単独で読ませる check_readings2.py と違い、前後の言葉で読みが変わる語 (年、後、間 など) も分かる。

  python3 tools/check_context.py tools/context_ep03.txt
  (1行に「文の一部<TAB>語<TAB>正しい読み<TAB>誤った読み」)
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import librosa

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docu"))
sys.path.insert(0, str(ROOT / "render"))
import film  # noqa: E402
import tts  # noqa: E402


def feat(text):
    y, sr = librosa.load(str(tts.ensure(text, **film.VOICE)), sr=16000)
    y, _ = librosa.effects.trim(y, top_db=35)
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=160)
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)


def dist(fa, fb):
    D, wp = librosa.sequence.dtw(X=fa, Y=fb, metric="euclidean")
    return float(D[-1, -1] / len(wp))


def speeches(ep):
    mod = importlib.import_module(ep)
    return [film._speech(line) for sc in mod.SCENES for line in sc["lines"]]


def main():
    ep, path = sys.argv[1], sys.argv[2]
    all_sp = speeches(ep)
    for row in Path(path).read_text().splitlines():
        if not row.strip() or row.startswith("#"):
            continue
        part, word, good, bad = row.split("\t")
        sp = next((s for s in all_sp if part in s), None)
        if sp is None:
            print(f"?? 文が見つからない: {part}")
            continue
        f0 = feat(sp)
        dg = dist(f0, feat(sp.replace(word, good, 1)))
        db = dist(f0, feat(sp.replace(word, bad, 1)))
        verdict = "正しく読めている" if dg < db else "読み間違い"
        print(f"{verdict:8s} 正{dg:.3f} 誤{db:.3f}  {word}（{good}／{bad}） … {part}", flush=True)


if __name__ == "__main__":
    main()
