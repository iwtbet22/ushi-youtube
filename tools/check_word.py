"""文の中の1語が、合成音声で正しく読まれているかを、聞き比べで判定する。

実際に使う文の音声 (A) と、その語だけを「正しい読み」のかなにした文の音声 (正)、
「間違った読み」のかなにした文の音声 (誤) を作り、A がどちらに近いかを MFCC の DTW 距離で比べる。
文字起こし (check_kana.py) は雑音が多く、出→しゅつ のような聞き違いを出すので、怪しい語はこれで確かめる。

  python3 tools/check_word.py ep08 "来た日に" "きたひに" "きたにちに"
  (1つ目の語を含む文を、その回の台本から探して全部調べる)
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


def feat(wav):
    y, sr = librosa.load(str(wav), sr=16000)
    y, _ = librosa.effects.trim(y, top_db=35)
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=160)
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)


def dist(fa, fb):
    D, wp = librosa.sequence.dtw(X=fa, Y=fb, metric="euclidean")
    return float(D[-1, -1] / len(wp))


def judge(sp, word, good, bad):
    """sp (合成に渡す文) の中の word を good / bad に置き換えた音声と比べる。戻り値 (正の距離, 誤の距離)"""
    a = feat(tts.ensure(sp, **film.VOICE))
    g = feat(tts.ensure(sp.replace(word, good, 1), **film.VOICE))
    b = feat(tts.ensure(sp.replace(word, bad, 1), **film.VOICE))
    return dist(a, g), dist(a, b)


def main():
    ep, word, good, bad = sys.argv[1:5]
    mod = importlib.import_module(ep)
    for sc in mod.SCENES:
        for line in sc["lines"]:
            sp = film._speech(line)
            if word not in sp:
                continue
            dg, db = judge(sp, word, good, bad)
            verdict = "正しい" if dg < db * 0.9 else ("読み間違い" if db < dg * 0.9 else "微妙")
            print(f"{verdict}  正 {dg:.2f} / 誤 {db:.2f}  {word}→{good}?  {film._display(line)}", flush=True)


if __name__ == "__main__":
    main()
