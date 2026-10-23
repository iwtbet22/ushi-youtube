"""episode.py を白背景の解説動画 (1920x1080 / 30fps) に書き出す。

  python3 explainer/engine.py               # 本番 -> output/ep01_main.mp4
  python3 explainer/engine.py --check       # 要素どうしの重なり・セーフエリアはみ出しを検査するだけ
  python3 explainer/engine.py --stills DIR  # 各文の終わりごろの静止画だけ
  python3 explainer/engine.py --only 3      # 3番目のシーンだけ (確認用)

タイミング: ナレーションを一文ずつ音声合成し、その長さで字幕と画面要素の出るタイミングを決める。

YouTube の表示とかぶらないための配置ルール (ui.py の定数):
  - 字幕帯は最下端から SUB_BOTTOM だけ浮かせる (シークバー・操作ボタンを避ける)
  - 字幕の1行は SUB_MAX 文字まで (右下のチャンネル透かしを避ける)
  - 章タイトルと右上の帯は端から離す (上部のタイトル表示・カードの i アイコンを避ける)
  - 画面要素は CONTENT 矩形の中だけに置く (--check で検査)
  - 最後に終了画面用の余白 (END_HOLD 秒) をとる
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
import rec_timing  # noqa: E402
import ui  # noqa: E402
from episode import SCENES  # noqa: E402

W, H, FPS = ui.W, ui.H, 30
OUT = ui.ROOT / "output"
LEAD, TAIL = 0.08, 0.2       # 文の前後の間
SKIP = 0.4                   # 録音で読まなかった文に置く間
CARD = 1.8                   # 章タイトルカードの長さ
TRANS = 0.45                 # シーン間トランジションの長さ
SR = 48000


# ---- タイムライン -----------------------------------------------------------
def _speech(line):
    return line[1] if isinstance(line, tuple) else line


def _display(line):
    return line[0] if isinstance(line, tuple) else line


REC_MAP = ui.ROOT / "output" / "voice_rec" / "map.json"
REC_SPEED = 1.1              # 録音を少し速めて読む (声の高さは変えない)


# 頭と終わりの無音を削る (字幕が出てから声が出るまでの間をそろえる)
TRIM = ("silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.03,areverse,"
        "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse")


def _prepare(wav):
    """録音を REC_SPEED 倍速にして前後の無音を削った wav (output/voice_rec/prep/ にキャッシュ)"""
    out = wav.parent / "prep" / wav.name
    if not out.exists() or out.stat().st_mtime < wav.stat().st_mtime:
        out.parent.mkdir(exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", f"atempo={REC_SPEED},{TRIM}",
                        str(out)], check=True)
    return out


def recorded():
    """本人の録音がある文 (tools/align_recording.py で作る) → wav のパス。録音で読まなかった文は None"""
    import json
    if not REC_MAP.exists():
        return {}
    rec = {k: _prepare(ui.ROOT / v) if v else None for k, v in json.loads(REC_MAP.read_text()).items()}
    rec_timing.ensure([w for w in rec.values() if w])
    return rec


def build_timeline():
    """[{kind: card|scene|trans, start, dur, ...}] を返す。文ごとの開始時刻と音声も入れる。"""
    items, t, prev = [], 0.0, None
    rec = recorded()
    for si, sc in enumerate(SCENES):
        new_chapter = sc["chapter"] != prev and sc["bg"] not in ("board", "end")
        if new_chapter:
            items.append({"kind": "card", "start": t, "dur": CARD, "chapter": sc["chapter"]})
            t += CARD
        elif items and sc.get("trans", "cut") != "cut":
            items.append({"kind": "trans", "start": t, "dur": TRANS, "style": sc["trans"],
                          "a": len(items) - 1, "b": len(items) + 1})
            t += TRANS
        prev = sc["chapter"]
        sents, st = [], 0.0
        for line in sc["lines"]:
            if _display(line) in rec and rec[_display(line)] is None:
                # 録音で読まなかった文は、字幕も音声も出さずに短い間だけ置く
                sents.append({"start": st, "dur": SKIP, "text": "", "wav": None})
                st += SKIP
                continue
            wav = rec.get(_display(line)) or tts.ensure(_speech(line))
            d = LEAD + tts.duration(wav) + TAIL
            sents.append({"start": st, "dur": d, "text": _display(line), "wav": wav, "rec": _display(line) in rec})
            st += d
        st += sc.get("hold", 0)
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


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def ease_bounce(x):
    x = min(1.0, max(0.0, x))
    if x < 1 / 2.75:
        return 7.5625 * x * x
    if x < 2 / 2.75:
        x -= 1.5 / 2.75
        return 7.5625 * x * x + 0.75
    if x < 2.5 / 2.75:
        x -= 2.25 / 2.75
        return 7.5625 * x * x + 0.9375
    x -= 2.625 / 2.75
    return 7.5625 * x * x + 0.984375


ANIM_LEN = {"pop": 0.32, "slide_l": 0.4, "slide_r": 0.4, "rise": 0.4, "drop": 0.6, "zoom": 0.4,
            "fade": 0.3, "wipe_up": 0.6, "wipe_right": 0.5, "none": 0.0}


def _scaled(sprite, s):
    if abs(s - 1) < 1e-3:
        return sprite
    w, h = max(1, int(sprite.width * s)), max(1, int(sprite.height * s))
    return sprite.resize((w, h), Image.BILINEAR)


def _alpha(sprite, k):
    if k >= 1:
        return sprite
    s = sprite.copy()
    s.putalpha(s.getchannel("A").point(lambda v: int(v * k)))
    return s


def draw_el(frame, spr, x, y, anim, t):
    """t = 要素が出てからの秒数"""
    L = ANIM_LEN.get(anim, 0)
    if t >= L or anim == "none":
        frame.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))
        return
    p = t / L
    if anim == "pop":
        s = _scaled(spr, max(0.05, ease_back(p)))
        frame.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))
    elif anim in ("slide_l", "slide_r"):
        k = ease_out(p)
        dx = (1 - k) * (-500 if anim == "slide_l" else 500)
        frame.alpha_composite(_alpha(spr, k), (int(x - spr.width / 2 + dx), int(y - spr.height / 2)))
    elif anim == "rise":
        k = ease_out(p)
        frame.alpha_composite(_alpha(spr, k), (int(x - spr.width / 2), int(y - spr.height / 2 + (1 - k) * 80)))
    elif anim == "drop":
        k = ease_bounce(p)
        frame.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2 - (1 - k) * 400)))
    elif anim == "zoom":
        k = ease_out(p)
        s = _scaled(_alpha(spr, k), 1.6 - 0.6 * k)
        frame.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))
    elif anim == "fade":
        frame.alpha_composite(_alpha(spr, p), (int(x - spr.width / 2), int(y - spr.height / 2)))
    elif anim == "wipe_up":
        k = ease_out(p)
        h = int(spr.height * k)
        if h > 0:
            part = spr.crop((0, spr.height - h, spr.width, spr.height))
            frame.alpha_composite(part, (int(x - spr.width / 2), int(y - spr.height / 2 + spr.height - h)))
    elif anim == "wipe_right":
        w = int(spr.width * ease_out(p))
        if w > 0:
            frame.alpha_composite(spr.crop((0, 0, w, spr.height)), (int(x - spr.width / 2), int(y - spr.height / 2)))


def background(kind):
    im = Image.new("RGBA", (W, H), ui.BG + (255,))
    d = ImageDraw.Draw(im)
    if kind == "dots":
        for y in range(30, H, 48):
            for x in range(30 + (24 if (y // 48) % 2 else 0), W, 48):
                d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(226, 232, 242))
    elif kind == "split":
        d.rectangle((0, 0, W // 2, H), fill=(255, 238, 232))
        d.rectangle((W // 2, 0, W, H), fill=(232, 240, 255))
    elif kind == "tint":
        for y in range(H):
            k = max(0.0, 1 - y / (H * 0.7))
            d.line([(0, y), (W, y)], fill=(int(255 - 10 * k), int(255 - 4 * k), int(255 - 26 * k)))
    elif kind == "end":
        d.rectangle((0, 0, W, H), fill=(246, 248, 252))
    return im


def chrome(chapter, bg):
    """背景 + 左上の章タイトル + 右上の帯"""
    im = background(bg)
    if bg == "board":
        return im
    if bg != "end":
        im.alpha_composite(ui.chapter_title(chapter), ui.CHAPTER_POS)
    b = ui.banner()
    im.alpha_composite(b, (W - b.width - ui.BANNER_MARGIN[0], ui.BANNER_MARGIN[1]))
    return im


def chapter_card(chapter):
    im = Image.new("RGBA", (W, H), ui.BG + (255,))
    b = ui.banner()
    im.alpha_composite(b, (W - b.width - ui.BANNER_MARGIN[0], ui.BANNER_MARGIN[1]))
    t = ui.text_sprite(chapter, ui.font("label", 110), ui.NAVY, stroke=12, stroke_fill=(255, 255, 255), shadow=True)
    im.alpha_composite(t, ((W - t.width) // 2, (H - t.height) // 2 - 40))
    d = ImageDraw.Draw(im)
    y = (H + t.height) // 2 - 10
    d.rounded_rectangle(((W - t.width) // 2 + 20, y, (W + t.width) // 2 - 20, y + 14), radius=7, fill=ui.ORANGE)
    return im


def subtitle_pages(sent):
    """文を2行ずつのページにして時間を割り振る。
    録音なら、各ページを読み始める時刻で切り替える。合成音声などで時刻が分からなければ文字数の比で割り振る。"""
    if not sent["text"]:
        return []
    pages = ui.pages(sent["text"])
    marks = sent.get("rec") and rec_timing.page_starts(sent["wav"], pages)
    if marks:
        # 1ページ目は文の頭から、2ページ目以降は読み始めの少し前に切り替える
        starts = [sent["start"]] + [sent["start"] + LEAD + m - 0.1 for m in marks[1:]]
    else:
        total = sum(len(p) for p in pages)
        starts, t = [], sent["start"]
        for p in pages:
            starts.append(t)
            t += sent["dur"] * len(p) / total
    ends = starts[1:] + [sent["start"] + sent["dur"]]
    return [(a, b, ui.subtitle(p)) for a, b, p in zip(starts, ends, pages)]


class Count:
    """カウントアップする数字。spec=(終値, 表示関数, 色, 大きさ, 秒数)"""

    def __init__(self, spec):
        self.end, self.fmt, self.color, self.size, self.dur = spec
        self.cache = {}

    def sprite(self, t):
        k = ease_out(t / self.dur)
        txt = self.fmt(self.end * k if k < 1 else self.end)
        if txt not in self.cache:
            self.cache[txt] = ui.number(txt, self.color, self.size)
        return self.cache[txt]

    def final(self):
        return self.sprite(1e9)


class Dyn:
    """時間で形が変わる要素 (呼びかけアニメなど)。fn(t) が t 秒目のスプライトを返す"""

    def __init__(self, fn, dur):
        self.fn, self.dur = fn, dur

    def sprite(self, t):
        return self.fn(t)

    def final(self):
        return self.fn(self.dur)


class SceneRenderer:
    """シーン1つ分。frame(t) で t 秒目の RGBA 画像を返す。"""

    def __init__(self, item):
        self.item = item
        self.sc = sc = SCENES[item["index"]]
        sents = item["sents"]
        self.base = chrome(sc["chapter"], sc["bg"])
        self.els = []
        for e in sc["els"]:
            if e.get("count"):
                obj = Count(e["count"])
                spr = obj.final()
            elif e.get("dyn"):
                obj = Dyn(e["dyn"], e["dyn_dur"])
                spr = obj.final()
            else:
                obj = None
                spr = _scaled(e["fn"](), e["scale"])
            t0 = sents[e["at"]]["start"] + e["delay"]
            u = e["until"]
            if u is None:
                t1 = 1e9
            elif isinstance(u, tuple):
                t1 = sents[u[0]]["start"] + u[1]
            else:
                t1 = sents[u]["start"]
            self.els.append((spr, e, t0, t1, obj))
        self.subs = [] if sc["bg"] == "board" else [p for s in sents for p in subtitle_pages(s)]
        self.cache_key, self.cache_img = None, None

    def _settle_time(self, e):
        if e.get("count"):
            return e["count"][4] + 0.1
        if e.get("dyn"):
            return e["dyn_dur"]
        return ANIM_LEN.get(e["anim"], 0) + 0.05

    def content(self, t):
        active = [(i, spr, e, t0, obj) for i, (spr, e, t0, t1, obj) in enumerate(self.els) if t0 <= t < t1]
        settled = tuple(i for i, spr, e, t0, obj in active if t - t0 >= self._settle_time(e))
        if settled != self.cache_key:
            im = self.base.copy()
            for i, spr, e, t0, obj in active:
                if i in settled:
                    draw_el(im, spr, e["x"], e["y"], "none", 99)
            self.cache_key, self.cache_img = settled, im
        frame = self.cache_img.copy()
        for i, spr, e, t0, obj in active:
            if i in settled:
                continue
            if obj is not None:
                s = obj.sprite(t - t0)
                draw_el(frame, s, e["x"], e["y"], "none", 99)
            else:
                draw_el(frame, spr, e["x"], e["y"], e["anim"], t - t0)
        return frame

    def frame(self, t):
        frame = self.content(t)
        cam = self.sc.get("cam")
        if cam:
            u = min(1.0, t / max(0.1, self.item["dur"]))
            z = 1 + 0.06 * (u if cam == "in" else 1 - u)
            cw, ch = W / z, H / z
            # 章タイトル・帯は動かさないよう、ズームした中身の上に描き直す
            frame = frame.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2 - 20 * (z - 1),
                                                              (W + cw) / 2, (H + ch) / 2 - 20 * (z - 1)))
            top = self.base.crop((0, 0, W, ui.CONTENT[1]))
            frame.paste(top, (0, 0))
        for a, b, sub in self.subs:
            if a <= t < b:
                frame.alpha_composite(sub, (0, ui.SUB_Y))
                break
        return frame


def item_frame(items, idx, t):
    it = items[idx]
    if it["kind"] == "card":
        card = chapter_card(it["chapter"])
        k = min(1, t / 0.25)
        return Image.blend(Image.new("RGBA", (W, H), (255, 255, 255, 255)), card, k) if k < 1 else card
    return SceneRenderer(it).frame(t)


def transition_frame(a, b, style, p):
    """a=前のシーンの最後, b=次のシーンの最初, p=0..1"""
    k = ease_out(p) if style != "fade" else p
    if style == "slide":
        out = Image.new("RGBA", (W, H))
        dx = int(W * k)
        out.alpha_composite(a, (-dx, 0))
        out.alpha_composite(b, (W - dx, 0))
        return out
    if style == "wipe":
        out = a.copy()
        w = int(W * k)
        if w > 0:
            out.alpha_composite(b.crop((0, 0, w, H)), (0, 0))
            ImageDraw.Draw(out).rectangle((w - 14, 0, w, H), fill=ui.ORANGE)
        return out
    if style == "zoom":
        z = 1 + 0.25 * k
        cw, ch = W / z, H / z
        za = a.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        return Image.blend(za, b, k)
    return Image.blend(a, b, k)


def render_item(args):
    idx, items, seg, stills = args
    item = items[idx]
    n = int(round(item["dur"] * FPS))
    proc = None
    if not stills:
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", str(seg)], stdin=subprocess.PIPE)

    def emit(img, name):
        if stills:
            img.convert("RGB").save(Path(stills) / name, quality=85)
        else:
            proc.stdin.write(img.convert("RGB").tobytes())

    if item["kind"] == "card":
        for fi in ([n // 2] if stills else range(n)):
            emit(item_frame(items, idx, fi / FPS), f"{idx:03d}_card.jpg")
    elif item["kind"] == "trans":
        a = item_frame(items, item["a"], items[item["a"]]["dur"] - 1 / FPS)
        b = item_frame(items, item["b"], 0)
        for fi in ([n // 2] if stills else range(n)):
            emit(transition_frame(a, b, item["style"], fi / max(1, n - 1)), f"{idx:03d}_trans.jpg")
    else:
        r = SceneRenderer(item)
        sents = item["sents"]
        frames = [int((s["start"] + s["dur"] * 0.8) * FPS) for s in sents] if stills else range(n)
        for fi in frames:
            emit(r.frame(fi / FPS), f"{idx:03d}_{fi:05d}.jpg")
    if proc:
        proc.stdin.close()
        proc.wait()
    print(f"item {idx} done", flush=True)


# ---- 重なりチェック -------------------------------------------------------------
def _bbox(spr, x, y):
    bb = spr.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    if not bb:
        return None
    ox, oy = x - spr.width / 2, y - spr.height / 2
    return (ox + bb[0], oy + bb[1], ox + bb[2], oy + bb[3])


def check(items):
    """同時に出ている要素どうしの重なりと、セーフエリアからのはみ出しを列挙する"""
    problems = []
    cx0, cy0, cx1, cy1 = ui.CONTENT
    for it in items:
        if it["kind"] != "scene":
            continue
        sc = SCENES[it["index"]]
        r = SceneRenderer(it)
        boxes = [(_bbox(spr, e["x"], e["y"]), e, t0, t1) for spr, e, t0, t1, obj in r.els]
        for k, s in enumerate(it["sents"]):
            t = s["start"] + s["dur"] - 0.05
            live = [(b, e) for b, e, t0, t1 in boxes if b and t0 <= t < t1]
            for b, e in live:
                if e.get("full"):
                    continue
                if b[0] < cx0 or b[1] < cy0 or b[2] > cx1 or b[3] > cy1:
                    problems.append(f"scene {it['index']} 文{k}: はみ出し {e['name']} {tuple(int(v) for v in b)}")
            for i in range(len(live)):
                for j in range(i + 1, len(live)):
                    (a, ea), (b, eb) = live[i], live[j]
                    if ea.get("over") or eb.get("over"):
                        continue
                    ix = min(a[2], b[2]) - max(a[0], b[0])
                    iy = min(a[3], b[3]) - max(a[1], b[1])
                    if ix > 6 and iy > 6:
                        problems.append(f"scene {it['index']} 文{k}: 重なり {ea['name']} × {eb['name']} ({int(ix)}x{int(iy)})")
    return problems


# ---- 音 ---------------------------------------------------------------------
def _read(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768


def _bgm(total):
    """明るめの軽いループ (マリンバ風のアルペジオ + ベース)。C-G-Am-F, 104bpm"""
    beat = 60 / 104
    chords = [(261.63, 329.63, 392.0), (196.0, 246.94, 293.66), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63)]
    n = round(total * SR)
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


def _whoosh():
    n = int(0.45 * SR)
    t = np.linspace(0, 1, n)
    noise = np.convolve(np.random.default_rng(2).normal(0, 1, n), np.ones(30) / 30, mode="same")
    return noise * np.sin(np.pi * t) ** 2 * 1.2


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
    pop, chime, whoosh = _pop(), _chime(), _whoosh()

    def add(buf, t0, snd, g=1.0):
        s = int(t0 * SR)
        e = min(n, s + len(snd))
        buf[s:e] += snd[: e - s] * g

    for it in items:
        if it["kind"] == "card":
            add(sfx, it["start"] + 0.05, chime)
            continue
        if it["kind"] == "trans":
            add(sfx, it["start"], whoosh, 0.6)
            continue
        sc = SCENES[it["index"]]
        for s in it["sents"]:
            if s["wav"] is None:
                continue
            add(voice, it["start"] + s["start"] + LEAD, _read(s["wav"]))
        for e in sc["els"]:
            if e["anim"] in ("pop", "drop", "zoom") or e.get("count"):
                add(sfx, it["start"] + it["sents"][e["at"]]["start"] + e["delay"], pop, 0.5)
    bgm = _bgm(n / SR)
    talking = np.convolve((np.abs(voice) > 0.01).astype(float), np.ones(int(0.4 * SR)) / (0.4 * SR), mode="same")
    bgm *= 0.22 * (1 - 0.45 * np.clip(talking * 3, 0, 1))
    fade = int(3 * SR)  # 最後の3秒でBGMをフェードアウト
    end = int(total * SR)
    bgm[end - fade:end] *= np.linspace(1, 0, fade)
    bgm[end:] = 0
    mix = np.clip(voice * 0.95 + bgm + sfx * 0.35, -1, 1)
    pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def write_chapters(items):
    """YouTube 概要欄に貼るチャプター (タイムスタンプ)。最初は必ず 0:00。"""
    lines, prev = [], None
    for it in items:
        ch = it.get("chapter") if it["kind"] == "card" else (SCENES[it["index"]]["chapter"] if it["kind"] == "scene" else None)
        if ch and ch != prev:
            t = 0 if not lines else int(it["start"])
            lines.append(f"{t // 60}:{t % 60:02d} {ch}")
            prev = ch
    (ui.ROOT / "script" / "ep01_chapters.txt").write_text("\n".join(lines) + "\n")


# ---- main -------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills")
    ap.add_argument("--only", type=int)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--upto", type=int, help="このシーン番号までだけ書き出す (試し書き出し用)")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()

    items, total = build_timeline()
    if args.upto is not None:
        last = max(i for i, it in enumerate(items) if it.get("index") == args.upto)
        items = items[:last + 1]
        total = items[-1]["start"] + items[-1]["dur"]
    print(f"total {total:.1f}s ({total / 60:.1f} min), {len(items)} items", flush=True)
    problems = check(items)
    for p in problems:
        print("CHECK", p)
    print(f"check: {len(problems)} problem(s)", flush=True)
    if args.check:
        return
    if args.upto is None:
        write_chapters(items)
    OUT.mkdir(exist_ok=True)
    seg_dir = OUT / "segments_main"
    seg_dir.mkdir(exist_ok=True)
    if args.stills:
        Path(args.stills).mkdir(parents=True, exist_ok=True)
    targets = [i for i, it in enumerate(items) if args.only is None or it.get("index") == args.only]
    tasks = [(i, items, seg_dir / f"{i:03d}.mp4", args.stills) for i in targets]
    tasks.sort(key=lambda a: -items[a[0]]["dur"])
    with Pool(args.jobs) as pool:
        list(pool.imap_unordered(render_item, tasks))
    if args.stills or args.only is not None:
        return
    wav = OUT / "ep01_main_audio.wav"
    write_audio(wav, items, total)
    lst = seg_dir / "list.txt"
    lst.write_text("".join(f"file '{i:03d}.mp4'\n" for i in range(len(items))))
    out = OUT / ("ep01_sample.mp4" if args.upto is not None else "ep01_main.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                    # AAC にしたあとも 0 dB を超えないよう、ピークを -3 dB ほどに抑える
                    "-af", "alimiter=limit=0.7:level=false",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)],
                   check=True)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
