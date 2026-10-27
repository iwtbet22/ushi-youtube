"""ドキュメンタリー調の動画を書き出す (2本目 FA編)。

  python3 docu/film.py ep02_open            # 冒頭を output/ep02_open.mp4 に
  python3 docu/film.py ep02_open --stills   # 各シーンの代表フレームだけ output/stills_ep02/ に
  python3 docu/film.py ep02_open --check    # 字幕と画面要素の重なり・はみ出しを確認

シーンの定義は docu/<名前>.py の SCENES。ナレーションは edge-tts (render/tts.py) で文ごとに作り、
文の長さに合わせて字幕と画面要素を出す。
"""
from __future__ import annotations

import argparse
import importlib
import math
import subprocess
import sys
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "render"))
import look  # noqa: E402
import readings  # noqa: E402
import tts  # noqa: E402
import ui  # noqa: E402

W, H, FPS = look.W, look.H, 30
SR = 48000
OUT = ROOT / "output"
LEAD, TAIL = 0.12, 0.32      # 文の前後の間
FADE = 0.5                   # シーン間のクロスフェード
VOICE = {"rate": "+0%", "pitch": "-4Hz"}  # 落ち着いた低めの語り


def E(fn, x, y, at=0, delay=0.0, until=None, anim="fade", anchor="c", sfx=None, dyn=False):
    """画面要素。fn() が RGBA 画像を返す。(x, y) は anchor の位置 (c: 中心 / tl: 左上 / tr: 右上 ...)。
    at 番目の文の頭から delay 秒後に出て、until 番目の文の終わりで消える (None ならシーンの終わりまで)"""
    return dict(fn=fn, x=x, y=y, at=at, delay=delay, until=until, anim=anim, anchor=anchor, sfx=sfx, dyn=dyn)


def S(lines, bg, move="in", tag=None, els=(), trans="fade", hold=0.0):
    """シーン。bg() が Ken Burns 用の背景 (画面より大きい RGB) を返す"""
    return dict(lines=lines, bg=bg, move=move, tag=tag, els=list(els), trans=trans, hold=hold)


# ---- タイムライン -----------------------------------------------------------
def _speech(line):
    return line[1] if isinstance(line, tuple) else readings.speech(line)


def _display(line):
    return line[0] if isinstance(line, tuple) else line


def timeline(scenes):
    out, t = [], 0.0
    for sc in scenes:
        sents, st = [], 0.0
        for line in sc["lines"]:
            wav = tts.ensure(_speech(line), **VOICE)
            d = LEAD + tts.duration(wav) + TAIL
            sents.append({"start": st, "dur": d, "text": _display(line), "wav": wav})
            st += d
        dur = math.ceil((st + sc["hold"]) * FPS) / FPS
        out.append({"start": t, "dur": dur, "sents": sents})
        t += dur
    return out, t


def pages(text):
    """字幕を2行ずつのページに分ける"""
    lines = ui._hang(ui.wrap(text, look.SUB_MAX))
    if len(lines) <= 2:
        return ["".join(lines)]
    cands = [i + 1 for i, c in enumerate(text[:-1]) if c in "、。"]
    best = min(cands, key=lambda i: abs(i - len(text) / 2)) if cands else len(text) // 2
    return pages(text[:best]) + pages(text[best:])


def sub_pages(sent):
    ps = pages(sent["text"])
    total = sum(len(p) for p in ps)
    out, t = [], sent["start"]
    for p in ps:
        d = sent["dur"] * len(p) / total
        out.append((t, t + d, p))
        t += d
    return out


# ---- 描画 -------------------------------------------------------------------
def el_times(e, item):
    """要素が出ている時間 (シーンの頭からの秒)。ナレーションのないシーン (章の扉) は頭から数える"""
    sents = item["sents"]
    t0 = (sents[e["at"]]["start"] if sents else 0.0) + e["delay"]
    t1 = item["dur"] if e["until"] is None else sents[e["until"]]["start"] + sents[e["until"]]["dur"]
    return t0, t1


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def _place(e, im):
    ax = {"c": 0.5, "tl": 0, "bl": 0, "tr": 1, "br": 1, "t": 0.5, "b": 0.5, "l": 0, "r": 1}[e["anchor"]]
    ay = {"c": 0.5, "tl": 0, "tr": 0, "t": 0, "bl": 1, "br": 1, "b": 1, "l": 0.5, "r": 0.5}[e["anchor"]]
    return round(e["x"] - im.width * ax), round(e["y"] - im.height * ay)


class SceneRenderer:
    def __init__(self, sc, item, index):
        self.sc, self.item, self.index = sc, item, index
        self.base = sc["bg"]()
        # dyn=True の要素は、毎フレーム fn(出てからの秒数) で描き直す
        self.sprites = [None if e["dyn"] else e["fn"]() for e in sc["els"]]
        self.subs = [(a, b, look.subtitle(p)) for s in item["sents"] for a, b, p in sub_pages(s)]
        self.tag = look.chapter_tag(sc["tag"]) if sc["tag"] else None
        self.times = [el_times(e, item) for e in sc["els"]]

    def frame(self, t, no):
        u = t / self.item["dur"]
        im = look.ken_burns(self.base, u, self.sc["move"]).convert("RGBA")
        im.alpha_composite(look.vignette())
        for e, sp, (t0, t1) in zip(self.sc["els"], self.sprites, self.times):
            if not t0 <= t < t1:
                continue
            k = ease_out((t - t0) / 0.35)
            out = min(1.0, (t1 - t) / 0.25)
            alpha = min(k, out)
            if e["dyn"]:
                sp = e["fn"](t - t0)
            s = sp
            x, y = _place(e, sp)
            if e["anim"] == "rise":
                y += round((1 - k) * 60)
            elif e["anim"] == "zoom":
                z = 1.18 - 0.18 * k
                s = sp.resize((round(sp.width * z), round(sp.height * z)), Image.BILINEAR)
                x, y = x - (s.width - sp.width) // 2, y - (s.height - sp.height) // 2
            elif e["anim"] == "glitch":
                s = look.glitch(sp, t - t0, seed=no)
                x -= 30
                alpha = out
            elif e["anim"] == "slam":  # 大きく出て一瞬で収まる
                z = 1 + 0.6 * (1 - ease_out((t - t0) / 0.18))
                s = sp.resize((round(sp.width * z), round(sp.height * z)), Image.BILINEAR)
                x, y = x - (s.width - sp.width) // 2, y - (s.height - sp.height) // 2
                alpha = min(out, ease_out((t - t0) / 0.1))
            elif e["anim"] == "wipe":  # 上から下へ書き出す (縦書きの名前)
                h = max(1, round(sp.height * ease_out((t - t0) / 0.8)))
                s = sp.crop((0, 0, sp.width, h))
                alpha = out
            if alpha < 1:
                s = s.copy()
                s.putalpha(s.split()[3].point(lambda v, a=alpha: round(v * a)))
            im.alpha_composite(s, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))
        if self.tag:
            im.alpha_composite(self.tag, (W - self.tag.width - 60, 40))
        for a, b, sp in self.subs:
            if a <= t < b:
                im.alpha_composite(sp, look.subtitle_pos(sp))
        im.alpha_composite(look.grain(no))
        return im.convert("RGB")


def render_scene(args):
    i, mod_name, items, out_path, stills = args
    scenes = importlib.import_module(mod_name).SCENES
    sc, item = scenes[i], items[i]
    r = SceneRenderer(sc, item, i)
    n = round(item["dur"] * FPS)
    if stills:
        mid = item["sents"][-1]["start"] + 0.9 if item["sents"] else item["dur"] / 2
        r.frame(min(mid, item["dur"] - 0.05), 0).save(out_path)
        return
    prev = None
    if i > 0 and sc["trans"] in ("fade",):
        pr = SceneRenderer(scenes[i - 1], items[i - 1], i - 1)
        prev = pr.frame(items[i - 1]["dur"] - 1 / FPS, 0)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "18", "-pix_fmt", "yuv420p", str(out_path)], stdin=subprocess.PIPE)
    start_no = round(item["start"] * FPS)
    for f in range(n):
        t = f / FPS
        img = r.frame(t, start_no + f)
        if t < FADE and sc["trans"] == "fade" and prev is not None:
            img = Image.blend(prev, img, ease_out(t / FADE))
        elif t < FADE and sc["trans"] == "black":
            img = Image.blend(Image.new("RGB", (W, H)), img, ease_out(t / FADE))
        elif t < 0.18 and sc["trans"] == "flash":
            img = Image.blend(Image.new("RGB", (W, H), (255, 255, 255)), img, t / 0.18)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()


# ---- 音 ---------------------------------------------------------------------
def _read(wav):
    with wave.open(str(wav)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
        if w.getframerate() != SR:
            a = np.interp(np.arange(0, len(a), w.getframerate() / SR), np.arange(len(a)), a)
    return a


def _lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def _moving_avg(x, n):
    """長さ n の移動平均 (中心合わせ)。累積和で計算するので長い音でも速い"""
    c = np.concatenate([[0.0], np.cumsum(x, dtype=np.float64)])
    i = np.arange(len(x))
    lo, hi = np.clip(i - n // 2, 0, len(x)), np.clip(i + n // 2, 0, len(x))
    return ((c[hi] - c[lo]) / n).astype(np.float32)


def bgm(total):
    """暗めの持続音 (Dm - B♭ - F - C) と、低い鼓動のようなキック"""
    n = int(total * SR) + SR
    t = np.arange(n) / SR
    out = np.zeros(n)
    chords = [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (87.31, 130.81, 174.61), (130.81, 164.81, 196.0)]
    bar = 8.0
    for k in range(int(total / bar) + 2):
        s, e = int(k * bar * SR), min(n, int((k + 1) * bar * SR + SR))
        if s >= n:
            break
        tt = t[s:e] - k * bar
        env = np.minimum(1, tt / 2.5) * np.minimum(1, np.maximum(0, (bar + 1 - tt)) / 2.0)
        seg = np.zeros(e - s)
        for f in chords[k % 4]:
            for det in (-0.6, 0.6):
                ph = 2 * np.pi * (f + det) * tt
                seg += (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)) * env * 0.05
            seg += np.sin(2 * np.pi * f / 2 * tt) * env * 0.05
        out[s:e] += _lowpass(seg, 900)  # 1小節ずつ削る (全体を一度に FFT するとメモリが足りない)
    beat = 60 / 64
    kick_t = np.arange(int(0.45 * SR)) / SR
    kick = np.sin(2 * np.pi * (55 * kick_t + 40 * (1 - np.exp(-kick_t * 18)) / 18)) * np.exp(-kick_t * 7) * 0.22
    for b in np.arange(0, total, beat * 2):
        i = int(b * SR)
        e = min(n, i + len(kick))
        out[i:e] += kick[:e - i]
    return out


def boom():
    t = np.arange(int(1.6 * SR)) / SR
    low = np.sin(2 * np.pi * (48 * t + 60 * (1 - np.exp(-t * 6)) / 6)) * np.exp(-t * 2.6)
    noise = _lowpass(np.random.default_rng(1).normal(0, 1, len(t)), 400) * np.exp(-t * 5) * 0.4
    return (low + noise) * 0.75


def whoosh():
    t = np.arange(int(0.7 * SR)) / SR
    noise = np.random.default_rng(2).normal(0, 1, len(t))
    env = np.sin(np.pi * t / 0.7) ** 2
    return _lowpass(noise, 2500) * env * 0.25


def write_audio(path, scenes, items, total):
    n = int(total * SR) + SR
    voice, sfx = np.zeros(n), np.zeros(n)

    def add(buf, at, a, g=1.0):
        i = int(at * SR)
        e = min(len(buf), i + len(a))
        if i < e:
            buf[i:e] += a[:e - i] * g

    snd = {"boom": boom(), "whoosh": whoosh()}
    for sc, it in zip(scenes, items):
        for s in it["sents"]:
            add(voice, it["start"] + s["start"] + LEAD, _read(s["wav"]))
        if sc["trans"] in ("fade", "flash") and it["start"] > 0:
            add(sfx, it["start"] - 0.25, snd["whoosh"], 0.8)
        for e in sc["els"]:
            if e["sfx"]:
                add(sfx, it["start"] + el_times(e, it)[0], snd[e["sfx"]])
    music = bgm(total)[:n]
    talking = _moving_avg((np.abs(voice) > 0.01).astype(np.float32), int(0.4 * SR))
    music *= 0.55 * (1 - 0.4 * np.clip(talking * 3, 0, 1))
    end = int(total * SR)
    fade = int(2.5 * SR)
    music[end - fade:end] *= np.linspace(1, 0, fade)
    music[end:] = 0
    mix = np.tanh((voice * 1.1 + music + sfx * 0.7) * 1.2) / 1.2
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---- 確認 -------------------------------------------------------------------
def check(scenes, items):
    """字幕帯と画面要素が重ならないか、要素が画面からはみ出さないかを調べる"""
    problems = 0
    for i, (sc, it) in enumerate(zip(scenes, items)):
        subs = [(a, b, look.subtitle(p)) for s in it["sents"] for a, b, p in sub_pages(s)]
        for e in sc["els"]:
            sp = e["fn"](9.0) if e["dyn"] else e["fn"]()
            x, y = _place(e, sp)
            box = (x, y, x + sp.width, y + sp.height)
            if box[0] < -40 or box[1] < -40 or box[2] > W + 40 or box[3] > H + 40:
                print(f"scene {i}: element off screen {box}")
                problems += 1
            for a, b, ss in subs:
                sx, sy = look.subtitle_pos(ss)
                # 要素の見える部分 (文字のある範囲) が字幕帯に重なるか
                bb = sp.split()[3].point(lambda v: 255 if v > 60 else 0).getbbox()
                if not bb:
                    continue
                vb = (x + bb[0], y + bb[1], x + bb[2], y + bb[3])
                if vb[3] > sy and vb[2] > sx and vb[0] < sx + ss.width:
                    print(f"scene {i}: element overlaps subtitle {vb}")
                    problems += 1
                    break
    print(f"check: {problems} problem(s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", help="この番号のシーンだけ描き直してつなぎ直す (例: 3,7,12)。ほかは前回の書き出しを使う")
    args = ap.parse_args()
    scenes = importlib.import_module(args.module).SCENES
    items, total = timeline(scenes)
    print(f"total {total:.1f}s, {len(scenes)} scenes", flush=True)
    if args.check:
        check(scenes, items)
        return
    seg = OUT / f"segments_{args.module}"
    seg.mkdir(parents=True, exist_ok=True)
    if args.stills:
        st = OUT / f"stills_{args.module}"
        st.mkdir(parents=True, exist_ok=True)
        tasks = [(i, args.module, items, st / f"{i:02d}.png", True) for i in range(len(scenes))]
    else:
        only = {int(x) for x in args.only.split(",")} if args.only else set(range(len(scenes)))
        tasks = [(i, args.module, items, seg / f"{i:03d}.mp4", False) for i in range(len(scenes)) if i in only]
    with Pool(args.jobs) as p:
        list(p.imap_unordered(render_scene, tasks))
    if args.stills:
        return
    wav = OUT / f"{args.module}_audio.wav"
    write_audio(wav, scenes, items, total)
    lst = seg / "list.txt"
    lst.write_text("".join(f"file '{i:03d}.mp4'\n" for i in range(len(scenes))))
    out = OUT / f"{args.module}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(out)], check=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
