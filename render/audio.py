"""BGMと効果音をその場で合成する (外部音源なし)。

- 低いドローン + ゆっくり動くパッド (Am系)
- flash カットに「ドン」(低音ヒット + ノイズ)
- 字幕のないキーワード/フックに軽い「シュッ」
ナレーションは別録り前提。ここでは仮の音だけを入れる。
"""
from __future__ import annotations

import wave

import numpy as np

SR = 48000


def _env(n, a, r):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    e[:ai] = np.linspace(0, 1, ai)
    e[-ri:] *= np.linspace(1, 0, ri)
    return e


def _pad(total):
    t = np.arange(int(total * SR)) / SR
    chords = [(110.0, 130.81, 164.81), (87.31, 110.0, 130.81), (98.0, 123.47, 146.83), (82.41, 103.83, 123.47)]
    out = np.zeros_like(t)
    seg = 8.0
    for i, ch in enumerate(chords * int(total / (seg * 4) + 1)):
        s = int(i * seg * SR)
        if s >= len(t):
            break
        e = min(len(t), s + int((seg + 2) * SR))
        tt = t[s:e] - t[s]
        env = np.clip(tt / 2.0, 0, 1) * np.clip((seg + 2 - tt) / 2.0, 0, 1)
        for f in ch:
            out[s:e] += env * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt)) / 6
    drone = 0.35 * np.sin(2 * np.pi * 55 * t) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t))
    return (out + drone) * 0.22


def _hit():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = 60 * np.exp(-t * 3) + 32
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    noise = np.random.default_rng(0).normal(0, 1, n) * np.exp(-t * 16) * 0.35
    return (boom + noise) * 0.9


def _whoosh():
    n = int(0.7 * SR)
    t = np.linspace(0, 1, n)
    noise = np.random.default_rng(1).normal(0, 1, n)
    k = np.ones(40) / 40
    noise = np.convolve(noise, k, mode="same")
    return noise * np.sin(np.pi * t) ** 2 * 1.4


def write(path, total, cues):
    """cues: [(開始秒, カット種別, [オーバーレイ種別...]), ...]"""
    mix = _pad(total)
    mix *= _env(len(mix), 2.5, 3.0)
    hit, wh = _hit(), _whoosh()
    for t0, cut, kinds in cues:
        s = int(t0 * SR)
        snd = hit if cut == "flash" else (wh * 0.5 if kinds else None)
        if snd is None:
            continue
        e = min(len(mix), s + len(snd))
        mix[s:e] += snd[: e - s] * 0.5
    mix = np.tanh(mix * 1.2) * 0.8
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
