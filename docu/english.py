"""公開済みの回に足す「英語の音声トラック」と英語字幕を作る (YouTube の多言語音声に上げる用)。

  python3 docu/english.py ep06          # script/ep06_en.txt (日本語の1文に英語1行) から作る

- 画面と字幕は日本語のままなので、英語の各文は、対応する日本語の文が始まる時刻に置く。
- 英語のほうが長くて次の文に食い込むときは、少しだけ速める (最大 MAX_TEMPO 倍)。
  それでも収まらない分は、後ろへずらす (章の扉などの間で追いつく)。
- BGM と効果音は、日本語版と同じ作りで混ぜる。音量は -14 LUFS にそろえる。
出力: output/upload/<回>_en_audio.mp3 と <回>_en.srt
"""
from __future__ import annotations

import importlib
import runpy
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import script_dir  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "render"))
sys.path.insert(0, str(ROOT / "docu"))
import tts  # noqa: E402

VOICE = "en-US-AndrewNeural"
MAX_TEMPO = 1.25
GAP = 0.15


def _read(path):
    with wave.open(str(path)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
    return a


def _tempo(wav, f, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-filter:a", f"atempo={f:.4f}",
                    "-ac", "1", "-ar", "48000", str(out)], check=True)
    return out


def _ts(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def main(ep):
    g = runpy.run_path(str(ROOT / "docu" / "film.py"), run_name="film_render")  # 書き出しと同じ時間割
    scenes = importlib.import_module(ep).SCENES
    items, total = g["timeline"](scenes)
    SR, LEAD = g["SR"], g["LEAD"]
    en = [ln.strip() for ln in (script_dir(ep) / f"{ep}_en.txt").read_text().splitlines() if ln.strip()]
    starts = [it["start"] + s["start"] + LEAD for it in items for s in it["sents"]]
    if len(en) != len(starts):
        raise SystemExit(f"英語 {len(en)} 行と日本語 {len(starts)} 文の数が合わない")

    tmp = ROOT / "output" / "voice_en_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    n = int(total * SR) + SR
    voice = np.zeros(n)
    srt, prev_end, fast, late = [], 0.0, [], []
    for k, (text, st) in enumerate(zip(en, starts)):
        wav = tts.ensure(text, voice=VOICE)
        d = tts.duration(wav)
        nxt = starts[k + 1] if k + 1 < len(starts) else total - 1.0
        avail = nxt - st - GAP
        if d > avail > 0:
            f = min(MAX_TEMPO, d / avail)
            if f > 1.01:
                wav = _tempo(wav, f, tmp / f"{k:04d}.wav")
                d /= f
                fast.append(f)
        at = max(st, prev_end + 0.12)
        if at - st > 0.05:
            late.append(at - st)
        a = _read(wav)
        i = int(at * SR)
        e = min(n, i + len(a))
        voice[i:e] += a[:e - i]
        prev_end = at + d
        srt.append(f"{k + 1}\n{_ts(at)} --> {_ts(prev_end)}\n{text}\n")

    # BGM と効果音 (film.write_audio と同じ作り)
    sfx = np.zeros(n)
    snd = {"boom": g["boom"](), "whoosh": g["whoosh"]()}

    def add(buf, at, a, gain=1.0):
        i = int(at * SR)
        e = min(len(buf), i + len(a))
        if i < e:
            buf[i:e] += a[:e - i] * gain

    for sc, it in zip(scenes, items):
        if sc["trans"] in ("fade", "flash") and it["start"] > 0:
            add(sfx, it["start"] - 0.25, snd["whoosh"], 0.8)
        for el in sc["els"]:
            if el["sfx"]:
                add(sfx, it["start"] + g["el_times"](el, it)[0], snd[el["sfx"]])
    music = g["bgm"](total)[:n]
    talking = g["_moving_avg"]((np.abs(voice) > 0.01).astype(np.float32), int(0.4 * SR))
    music *= 0.55 * (1 - 0.4 * np.clip(talking * 3, 0, 1))
    end, fade = int(total * SR), int(2.5 * SR)
    music[end - fade:end] *= np.linspace(1, 0, fade)
    music[end:] = 0
    mix = np.tanh((voice * 1.1 + music + sfx * 0.7) * 1.2) / 1.2
    raw = tmp / f"{ep}_en_mix.wav"
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    up = ROOT / "output" / "upload"
    up.mkdir(parents=True, exist_ok=True)
    out = up / f"{ep}_en_audio.mp3"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-t", f"{total:.3f}",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k",
                    str(out)], check=True)
    (up / f"{ep}_en.srt").write_text("\n".join(srt))
    raw.unlink()
    print(f"wrote {out} ({total:.1f}s)")
    print(f"速めた文 {len(fast)} / {len(en)}（最大 {max(fast, default=1):.2f} 倍）、"
          f"後ろへずれた文 {len(late)}（最大 {max(late, default=0):.1f} 秒）")


if __name__ == "__main__":
    main(sys.argv[1])
