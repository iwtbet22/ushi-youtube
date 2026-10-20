"""episode.py を白背景の解説動画 (1920x1080 / 30fps) に書き出す。

  python3 explainer/engine.py               # 本番 -> output/ep01_main.mp4
  python3 explainer/engine.py --stills DIR  # 各文の中ほどの静止画だけ
  python3 explainer/engine.py --only 3      # 3番目のシーンだけ (確認用)

タイミング: ナレーションを一文ずつ音声合成し、その長さで字幕と画面要素の出るタイミングを決める。
"""
from __future__ import annotations

import argparse
import math
import subprocess
import sys
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "render"))
import tts  # noqa: E402  (render/tts.py を共用)
import ui  # noqa: E402
from episode import SCENES  # noqa: E402

W, H, FPS = ui.W, ui.H, 30
OUT = ui.ROOT / "output"
LEAD, TAIL = 0.15, 0.4       # 文の前後の間
CARD = 1.8                   # 章タイトルカードの長さ
SR = 48000


# ---- タイムライン -----------------------------------------------------------
def _speech(line):
    return line[1] if isinstance(line, tuple) else line


def _display(line):
    return line[0] if isinstance(line, tuple) else line


def build_timeline():
    """[{kind: card|scene, start, dur, ...}] を返す。文ごとの開始時刻と音声も入れる。"""
    items, t, prev = [], 0.0, None
    for si, sc in enumerate(SCENES):
        if sc["chapter"] != prev and sc["bg"] == "white":
            items.append({"kind": "card", "start": t, "dur": CARD, "chapter": sc["chapter"]})
            t += CARD
        prev = sc["chapter"]
        sents, st = [], 0.0
        for line in sc["lines"]:
            wav = tts.ensure(_speech(line))
            d = LEAD + tts.duration(wav) + TAIL
            sents.append({"start": st, "dur": d, "text": _display(line), "wav": wav})
            st += d
        dur = math.ceil(st * FPS) / FPS
        items.append({"kind": "scene", "index": si, "start": t, "dur": dur, "sents": sents})
        t += dur
    return items, t


# ---- 描画 -------------------------------------------------------------------
def ease_back(x):
    """少し行き過ぎて戻るイージング (ポンと出る感じ)"""
    x = min(1.0, max(0.0, x))
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def _scaled(sprite, s):
    if abs(s - 1) < 1e-3:
        return sprite
    w, h = max(1, int(sprite.width * s)), max(1, int(sprite.height * s))
    return sprite.resize((w, h), Image.BILINEAR)


def draw_el(frame, spr, x, y, anim, t):
    """t = 要素が出てからの秒数"""
    if anim == "pop" and t < 0.32:
        k = ease_back(t / 0.32)
        s = _scaled(spr, max(0.05, k))
        frame.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))
        return
    if anim == "fade" and t < 0.3:
        s = spr.copy()
        s.putalpha(s.getchannel("A").point(lambda v: int(v * t / 0.3)))
        spr = s
    elif anim == "wipe_up" and t < 0.6:
        k = 1 - (1 - t / 0.6) ** 2
        h = int(spr.height * k)
        if h <= 0:
            return
        part = spr.crop((0, spr.height - h, spr.width, spr.height))
        frame.alpha_composite(part, (int(x - spr.width / 2), int(y - spr.height / 2 + spr.height - h)))
        return
    elif anim == "wipe_right" and t < 0.5:
        w = int(spr.width * (t / 0.5))
        if w <= 0:
            return
        frame.alpha_composite(spr.crop((0, 0, w, spr.height)), (int(x - spr.width / 2), int(y - spr.height / 2)))
        return
    frame.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))


def chrome(chapter):
    """背景 + 左上の章タイトル + 右上の帯"""
    im = Image.new("RGBA", (W, H), ui.BG + (255,))
    im.alpha_composite(ui.chapter_title(chapter), (22, 14))
    b = ui.banner()
    im.alpha_composite(b, (W - b.width - 22, 18))
    return im


def chapter_card(chapter):
    im = Image.new("RGBA", (W, H), ui.BG + (255,))
    b = ui.banner()
    im.alpha_composite(b, (W - b.width - 22, 18))
    t = ui.text_sprite(chapter, ui.font("label", 110), ui.NAVY, stroke=12, stroke_fill=(255, 255, 255), shadow=True)
    im.alpha_composite(t, ((W - t.width) // 2, (H - t.height) // 2 - 40))
    d = ImageDraw.Draw(im)
    y = (H + t.height) // 2 - 10
    d.rounded_rectangle(((W - t.width) // 2 + 20, y, (W + t.width) // 2 - 20, y + 14), radius=7, fill=ui.ORANGE)
    return im


def subtitle_pages(sent):
    """文を2行ずつのページにし、文字数に比例して時間を割り振る"""
    pages = ui.pages(sent["text"])
    total = sum(len(p) for p in pages)
    out, t = [], sent["start"]
    for p in pages:
        d = sent["dur"] * len(p) / total
        out.append((t, t + d, ui.subtitle(p)))
        t += d
    return out


def render_item(args):
    idx, item, seg, stills = args
    n = int(round(item["dur"] * FPS))
    proc = None
    if not stills:
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", str(seg)], stdin=subprocess.PIPE)

    if item["kind"] == "card":
        card = chapter_card(item["chapter"])
        frames = [n // 2] if stills else range(n)
        for fi in frames:
            t = fi / FPS
            k = min(1, t / 0.25)
            img = Image.blend(Image.new("RGBA", (W, H), (255, 255, 255, 255)), card, k) if k < 1 else card
            if stills:
                img.convert("RGB").save(Path(stills) / f"{idx:03d}_card.jpg", quality=85)
            else:
                proc.stdin.write(img.convert("RGB").tobytes())
    else:
        sc = SCENES[item["index"]]
        sents = item["sents"]
        if sc["bg"] == "board":
            base = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        else:
            base = chrome(sc["chapter"])
        els = []
        for e in sc["els"]:
            spr = _scaled(e["fn"](), e["scale"])
            t0 = sents[e["at"]]["start"] + e["delay"]
            t1 = sents[e["until"]]["start"] if e["until"] is not None else 1e9
            els.append((spr, e, t0, t1))
        subs = [p for s in sents for p in subtitle_pages(s)]
        settled_cache = {}
        if stills:
            frames = [int((s["start"] + s["dur"] * 0.7) * FPS) for s in sents]
        else:
            frames = range(n)
        for fi in frames:
            t = fi / FPS
            active = [(i, spr, e, t0) for i, (spr, e, t0, t1) in enumerate(els) if t0 <= t < t1]
            settled = tuple(i for i, spr, e, t0 in active if t - t0 >= 0.65)
            if settled not in settled_cache:
                im = base.copy()
                for i, spr, e, t0 in active:
                    if i in settled:
                        draw_el(im, spr, e["x"], e["y"], "none", 99)
                settled_cache = {settled: im}
            frame = settled_cache[settled].copy()
            for i, spr, e, t0 in active:
                if i not in settled:
                    draw_el(frame, spr, e["x"], e["y"], e["anim"], t - t0)
            if sc["bg"] != "board":
                for a, b, sub in subs:
                    if a <= t < b:
                        frame.alpha_composite(sub, (0, H - ui.SUB_H))
                        break
            if stills:
                frame.convert("RGB").save(Path(stills) / f"{idx:03d}_{fi:05d}.jpg", quality=85)
            else:
                proc.stdin.write(frame.convert("RGB").tobytes())
    if proc:
        proc.stdin.close()
        proc.wait()
    print(f"item {idx} done", flush=True)


# ---- 音 ---------------------------------------------------------------------
def _read(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768


def _bgm(total):
    """明るめの軽いループ (マリンバ風のアルペジオ + ベース)。C-G-Am-F, 104bpm"""
    beat = 60 / 104
    chords = [(261.63, 329.63, 392.0), (196.0, 246.94, 293.66), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63)]
    n = int(total * SR)
    out = np.zeros(n)
    note_len = int(0.5 * SR)
    tt = np.arange(note_len) / SR
    env = np.exp(-tt * 9)

    def pluck(f):
        return (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt * 20)) * env

    step, i = beat / 2, 0
    while True:
        s = int(i * step * SR)
        if s >= n:
            break
        ch = chords[(i // 8) % 4]
        pattern = [0, 1, 2, 1, 0, 2, 1, 2]
        f = ch[pattern[i % 8]] * (2 if i % 8 in (2, 5) else 1)
        e = min(n, s + note_len)
        out[s:e] += pluck(f)[: e - s] * 0.22
        if i % 4 == 0:  # ベース
            bl = min(n - s, int(beat * 2 * SR))
            bt = np.arange(bl) / SR
            out[s:s + bl] += np.sin(2 * np.pi * ch[0] / 2 * bt) * np.exp(-bt * 2.5) * 0.35
        i += 1
    return out


def _pop():
    t = np.arange(int(0.09 * SR)) / SR
    f = 520 + 900 * t / t[-1]
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.5


def _chime():
    t = np.arange(int(1.2 * SR)) / SR
    out = np.zeros_like(t)
    for k, f in enumerate((783.99, 1046.5)):
        s = int(k * 0.12 * SR)
        tt = t[: len(t) - s]
        out[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 4) * 0.35
    return out


def write_audio(path, items, total):
    n = int(total * SR) + SR
    voice = np.zeros(n)
    sfx = np.zeros(n)
    pop, chime = _pop(), _chime()

    def add(buf, t0, snd, g=1.0):
        s = int(t0 * SR)
        e = min(n, s + len(snd))
        buf[s:e] += snd[: e - s] * g

    for it in items:
        if it["kind"] == "card":
            add(sfx, it["start"] + 0.05, chime)
            continue
        sc = SCENES[it["index"]]
        for s in it["sents"]:
            add(voice, it["start"] + s["start"] + LEAD, _read(s["wav"]))
        for e in sc["els"]:
            if e["anim"] == "pop":
                add(sfx, it["start"] + it["sents"][e["at"]]["start"] + e["delay"], pop, 0.5)
    bgm = _bgm(n / SR)
    talking = np.convolve((np.abs(voice) > 0.01).astype(float), np.ones(int(0.4 * SR)) / (0.4 * SR), mode="same")
    bgm *= 0.22 * (1 - 0.45 * np.clip(talking * 3, 0, 1))
    mix = voice * 0.95 + bgm + sfx * 0.35
    mix = np.clip(mix, -1, 1)
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---- main -------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--only", type=int)
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    items, total = build_timeline()
    print(f"total {total:.1f}s ({total / 60:.1f} min), {len(items)} items", flush=True)
    OUT.mkdir(exist_ok=True)
    seg_dir = OUT / "segments_main"
    seg_dir.mkdir(exist_ok=True)
    if args.stills:
        Path(args.stills).mkdir(parents=True, exist_ok=True)
    targets = [i for i, it in enumerate(items) if args.only is None or it.get("index") == args.only]
    tasks = [(i, items[i], seg_dir / f"{i:03d}.mp4", args.stills) for i in targets]
    tasks.sort(key=lambda a: -a[1]["dur"])
    with Pool(args.jobs) as pool:
        list(pool.imap_unordered(render_item, tasks))
    if args.stills or args.only is not None:
        return
    wav = OUT / "ep01_main_audio.wav"
    write_audio(wav, items, total)
    lst = seg_dir / "list.txt"
    lst.write_text("".join(f"file '{i:03d}.mp4'\n" for i in range(len(items))))
    out = OUT / "ep01_main.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)],
                   check=True)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
