"""2本目 (FA編) の見た目: 写真を全面に敷くドキュメンタリー調。

写真は暗めに色を整え (グレーディング)、周辺を落とし (ビネット)、粒子を足して、ゆっくり寄る/流す (Ken Burns)。
文字は、下の黒帯の字幕・縦書きの毛筆の名前・金色の大きな数字・ノイズの入る強調語・右上の章ラベル。
YouTube の表示 (下の再生バー、右下の透かし、右上のカード) にかからない位置に置く。
"""
from __future__ import annotations

import math
import os
import random
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "explainer"))
import ui  # noqa: E402  (字幕の改行ルールを共用)

# DOCU_VERTICAL=1 で縦長 (ショート動画 1080x1920)。右側のボタンと下側のタイトル欄を避けて文字を置く
VERTICAL = os.environ.get("DOCU_VERTICAL") == "1"
W, H = (1080, 1920) if VERTICAL else (1920, 1080)
SAFE_CX = 480 if VERTICAL else W // 2  # ショートは右のボタンを避けて、少し左を中心にする
IMG = ROOT / "assets" / "ep02" / "img"
GOLD = (232, 196, 110)
GOLD_DK = (150, 110, 40)
RED = (214, 40, 40)
WHITE = (255, 255, 255)

SUB_BOTTOM = 40          # 字幕帯の下端と画面下の距離 (再生バーにかからない)
SUB_SIZE = 58 if VERTICAL else 46
SUB_MAX = 13 if VERTICAL else 26
SUB_LOW = 1430           # 縦長のときの字幕帯の下端 (下のタイトル欄より上)


@lru_cache(maxsize=64)
def font(name, size):
    return ImageFont.truetype(str(ROOT / "assets" / "fonts" / name), size)


# ---- 写真 -------------------------------------------------------------------
@lru_cache(maxsize=32)
def photo(name):
    return Image.open(IMG / name).convert("RGB")


def cover(im, w, h, focus=(0.5, 0.5)):
    """w x h を埋めるように拡大して切り抜く。focus は残したい位置 (0〜1)"""
    s = max(w / im.width, h / im.height)
    r = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x = round((r.width - w) * focus[0])
    y = round((r.height - h) * focus[1])
    return r.crop((x, y, x + w, y + h))


def grade(im, mood="dark"):
    """色を整える。dark: 落ち着いた暗め / sepia: 昔の話 / cold: 冷たい / gold: お金の話"""
    im = ImageEnhance.Color(im).enhance({"sepia": 0.15, "cold": 0.55}.get(mood, 0.75))
    im = ImageEnhance.Contrast(im).enhance(1.18)
    im = ImageEnhance.Brightness(im).enhance({"dark": 0.62, "sepia": 0.72, "cold": 0.6, "gold": 0.66}[mood])
    a = np.asarray(im).astype(np.float32)
    tint = {"dark": (1.04, 1.0, 0.94), "sepia": (1.12, 1.0, 0.78), "cold": (0.9, 0.98, 1.1), "gold": (1.12, 1.02, 0.82)}
    a *= np.array(tint[mood], dtype=np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


@lru_cache(maxsize=4)
def vignette(strength=0.75):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    alpha = np.clip((d - 0.35) / 0.65, 0, 1) ** 1.6 * strength
    v = np.zeros((H, W, 4), np.uint8)
    v[..., 3] = (alpha * 255).astype(np.uint8)
    return Image.fromarray(v, "RGBA")


@lru_cache(maxsize=8)
def _grain_tile(seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    g = np.zeros((H // 2, W // 2, 4), np.uint8)
    g[..., :3] = np.where(n[..., None] > 0, 255, 0)
    g[..., 3] = np.clip(np.abs(n) * 9, 0, 40).astype(np.uint8)
    return Image.fromarray(g, "RGBA").resize((W, H), Image.NEAREST)


def grain(frame_no):
    return _grain_tile(frame_no % 6)


def plate(name, mood="dark", layout="full", focus=(0.5, 0.5), scale=1.18):
    """Ken Burns 用に、画面より少し大きい背景を作る (scale 倍)。
    layout=full: 全面 / left・right: 縦長の写真をぼかした背景の上の左右に置く"""
    pw, ph = round(W * scale), round(H * scale)
    im = photo(name)
    if layout == "full":
        return grade(cover(im, pw, ph, focus), mood)
    if layout == "blur":  # 図解の後ろに敷く、強くぼかして暗くした写真
        bg = grade(cover(im, pw, ph, focus).filter(ImageFilter.GaussianBlur(16)), mood)
        return ImageEnhance.Brightness(bg).enhance(0.6)
    bg = grade(cover(im, pw, ph, focus).filter(ImageFilter.GaussianBlur(28)), mood)
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    fh = round(ph * 0.94)
    fw = round(im.width * fh / im.height)
    if fw > pw * 0.6:  # 横長すぎるときは幅で合わせる
        fw = round(pw * 0.6)
        fh = round(im.height * fw / im.width)
    fg = grade(im.resize((fw, fh), Image.LANCZOS), mood)
    # 端をぼかして背景になじませる
    m = Image.new("L", (fw, fh), 0)
    ImageDraw.Draw(m).rectangle((30, 30, fw - 30, fh - 30), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    x = round(pw * (0.62 if layout == "right" else 0.38) - fw / 2)
    bg.paste(fg, (x, ph - fh), m)
    return bg


def plain(color=(10, 10, 12), scale=1.0):
    return Image.new("RGB", (round(W * scale), round(H * scale)), color)


def ken_burns(base, u, move="in"):
    """u (0〜1) の位置の 1920x1080 を切り出す。in: 寄る / out: 引く / left・right: 横に流す / up: 上へ"""
    bw, bh = base.size
    u = 0.5 - 0.5 * math.cos(math.pi * min(max(u, 0), 1))  # ゆっくり始まりゆっくり終わる
    if move in ("in", "out"):
        z = u if move == "in" else 1 - u
        cw = W + (bw - W) * (1 - z) * 0.999
        ch = cw * H / W
        x0, y0 = (bw - cw) / 2, (bh - ch) / 2
    else:
        cw, ch = W * 1.02, H * 1.02
        k = {"left": (1 - u, 0.5), "right": (u, 0.5), "up": (0.5, 1 - u), "down": (0.5, u)}[move]
        x0, y0 = (bw - cw) * k[0], (bh - ch) * k[1]
    cw, ch = min(cw, bw), min(ch, bh)
    x0, y0 = min(max(0.0, x0), bw - cw), min(max(0.0, y0), bh - ch)
    return base.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


# ---- 文字 -------------------------------------------------------------------
def _glow(sprite, radius=14, color=(0, 0, 0), alpha=200):
    a = sprite.split()[3].filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: min(255, v * alpha // 120))
    g = Image.new("RGBA", sprite.size, color + (0,))
    g.putalpha(a)
    g.alpha_composite(sprite)
    return g


def text(s, name="NotoSansJP-Black.ttf", size=80, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), glow=True, pad=40):
    f = font(name, size)
    box = ImageDraw.Draw(Image.new("L", (1, 1))).multiline_textbbox((0, 0), s, font=f, stroke_width=stroke,
                                                                     spacing=size // 5, align="center")
    im = Image.new("RGBA", (box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).multiline_text((pad - box[0], pad - box[1]), s, font=f, fill=fill, stroke_width=stroke,
                                      stroke_fill=stroke_fill, spacing=size // 5, align="center")
    return _glow(im) if glow else im


def gold(s, name="NotoSerifJP-Black.ttf", size=160):
    """金色のグラデーションの文字 (金額など)"""
    f = font(name, size)
    box = ImageDraw.Draw(Image.new("L", (1, 1))).multiline_textbbox((0, 0), s, font=f, spacing=size // 6,
                                                                     align="center")
    pad = 50
    w, h = box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).multiline_text((pad - box[0], pad - box[1]), s, font=f, fill=255, spacing=size // 6,
                                     align="center")
    yy = np.linspace(0, 1, h)[:, None]
    top, mid, bot = np.array((255, 240, 190)), np.array(GOLD), np.array(GOLD_DK)
    col = np.where(yy[..., None] < 0.5, top + (mid - top) * (yy[..., None] / 0.5),
                   mid + (bot - mid) * ((yy[..., None] - 0.5) / 0.5))
    rgb = np.broadcast_to(col, (h, w, 3)).astype(np.uint8)
    im = Image.fromarray(np.dstack([rgb, np.asarray(m)]), "RGBA")
    edge = m.filter(ImageFilter.MaxFilter(5))
    out = Image.new("RGBA", (w, h), (60, 35, 5, 0))
    out.putalpha(edge.point(lambda v: v * 230 // 255))
    out.alpha_composite(im)
    return _glow(out, 22, (0, 0, 0), 230)


def vertical(s, size=150, name="YujiSyuku-Regular.ttf", fill=WHITE):
    """縦書きの毛筆の名前 (人物の横に大きく出す)"""
    f = font(name, size)
    cells = []
    for ch in s:
        b = f.getbbox(ch)
        cells.append((ch, b))
    step = round(size * 1.02)
    w, h = size + 80, step * len(s) + 80
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (ch, b) in enumerate(cells):
        cx = (w - (b[2] - b[0])) / 2 - b[0]
        d.text((cx, 40 + i * step - b[1] + (size - (b[3] - b[1])) / 2), ch, font=f, fill=fill)
    return _glow(im, 16, (0, 0, 0), 240)


def caption_small(s, size=34):
    """写真の説明や「※推定」などの小さい注記"""
    return text(s, "NotoSansJP-Bold.ttf", size, (235, 235, 235), glow=True, pad=16)


def subtitle(s):
    """下の黒帯の字幕。帯は文字の幅に合わせ、半透明の黒"""
    lines = ui._hang(ui.wrap(s, SUB_MAX))
    f = font("NotoSansJP-Bold.ttf", SUB_SIZE)
    lh = round(SUB_SIZE * 1.42)
    tw = max(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(l, font=f) for l in lines)
    bw, bh = round(tw + 90), lh * len(lines) + 34
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, bw, bh), radius=8, fill=(0, 0, 0, 165))
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=f)
        d.text(((bw - lw) / 2, 17 + i * lh + 2), l, font=f, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0))
    return im


def subtitle_pos(sprite):
    if VERTICAL:
        return SAFE_CX - sprite.width // 2, SUB_LOW - sprite.height
    return (W - sprite.width) // 2, H - SUB_BOTTOM - sprite.height


def chapter_tag(s):
    """右上の小さな章ラベル (いま何の話か)"""
    f = font("NotoSerifJP-Black.ttf", 30)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = d.textlength(s, font=f)
    im = Image.new("RGBA", (round(tw) + 56, 64), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    dd.rectangle((0, 0, im.width, im.height), fill=(0, 0, 0, 120))
    dd.rectangle((0, 0, 6, im.height), fill=GOLD + (255,))
    dd.text((30, 12), s, font=f, fill=(240, 230, 210))
    return im


def bubble_v(s, size=56):
    """縦書きの白い吹き出し (人物のひとこと)"""
    f = font("NotoSerifJP-Black.ttf", size)
    cols = s.split("\n")
    step = round(size * 1.08)
    rows = max(len(c) for c in cols)
    w, h = len(cols) * round(size * 1.35) + 70, rows * step + 80
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((20, 20, w + 20, h + 20), fill=(250, 250, 248, 245), outline=(30, 30, 30, 255), width=4)
    for ci, col in enumerate(cols):
        x = 20 + w - 35 - (ci + 1) * round(size * 1.35) + round(size * 0.18)
        y0 = 20 + (h - len(col) * step) / 2
        for i, ch in enumerate(col):
            if ch in "ー":
                ch = "｜"
            d.text((x, y0 + i * step), ch, font=f, fill=(20, 20, 20))
    return im


def scroll(s, sub=None, w=None):
    """用語の巻物カード (ドラフトの「謀反」カードのようなもの)。縦長の画面では幅を狭める"""
    w, h = w or (820 if VERTICAL else 1100), 360
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((40, 20, w - 40, h - 20), fill=(232, 220, 190, 250))
    d.rectangle((40, 20, w - 40, h - 20), outline=(120, 40, 30, 255), width=10)
    d.rectangle((62, 42, w - 62, h - 42), outline=(170, 130, 60, 255), width=3)
    for x in (18, w - 40):
        d.rounded_rectangle((x, 0, x + 22, h), radius=10, fill=(90, 50, 30, 255))
    t = text(s, "YujiSyuku-Regular.ttf", 120, (40, 25, 20), glow=False, pad=0)
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 - (28 if sub else 0)))
    if sub:
        st = text(sub, "NotoSerifJP-Black.ttf", 40, (90, 40, 30), glow=False, pad=0)
        im.alpha_composite(st, ((w - st.width) // 2, h - 100))
    return im


def glitch(sprite, t, dur=0.35, seed=0):
    """出てすぐの dur 秒だけ、色ずれとノイズ線を入れる"""
    if t >= dur:
        return sprite
    rnd = random.Random(int(t * 60) + seed)
    k = 1 - t / dur
    r, g, b, a = sprite.split()
    dx = round(rnd.uniform(8, 26) * k)
    out = Image.new("RGBA", (sprite.width + 60, sprite.height), (0, 0, 0, 0))
    red = Image.merge("RGBA", (r, Image.new("L", r.size, 0), Image.new("L", r.size, 0), a.point(lambda v: v * 0.8)))
    cyan = Image.merge("RGBA", (Image.new("L", r.size, 0), g, b, a.point(lambda v: v * 0.8)))
    out.alpha_composite(red, (30 - dx, 0))
    out.alpha_composite(cyan, (30 + dx, 0))
    out.alpha_composite(sprite, (30, 0))
    # 横にずれる帯
    arr = np.asarray(out).copy()
    for _ in range(3):
        y = rnd.randrange(0, max(1, sprite.height - 20))
        hgt = rnd.randrange(6, 24)
        arr[y:y + hgt] = np.roll(arr[y:y + hgt], rnd.randrange(-40, 40) if k > 0.3 else 0, axis=1)
    return Image.fromarray(arr, "RGBA")


def bokeh(seed=0, color=GOLD, scale=1.18, n=46):
    """写真のないシーンの背景: 暗いグラデーションに、ぼけた光の粒"""
    pw, ph = round(W * scale), round(H * scale)
    yy = np.linspace(0, 1, ph)[:, None, None]
    base = (np.array((18, 14, 10)) * (1 - yy) + np.array((4, 4, 6)) * yy)
    im = Image.fromarray(np.broadcast_to(base, (ph, pw, 3)).astype(np.uint8)).convert("RGBA")
    rng = random.Random(seed)
    layer = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        r = rng.randrange(20, 110)
        x, y = rng.randrange(0, pw), rng.randrange(0, ph)
        a = rng.randrange(25, 90)
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(14))
    im.alpha_composite(layer)
    return im.convert("RGB")
