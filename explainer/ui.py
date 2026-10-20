"""白背景の解説動画用テロップ部品。

参考にした「型」:
  - 画面下: 横いっぱいの半透明グレー帯に、ナレーション全文を白文字2行で出す (一文ごとに切り替え)
  - 左上: 今の章のタイトルを小さく常時表示
  - 右上: 赤い帯にシリーズ名を2行で常時表示
  - 画面中: イラストの上に色付きの太ラベル、吹き出し、大きな強調ワード、赤い手書き丸
部品はすべて RGBA のスプライト (必要な大きさだけ) として返し、配置は engine 側で行う。
"""
from __future__ import annotations

import math
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# ---- カラートークン ---------------------------------------------------------
BG = (255, 255, 255)
INK = (40, 40, 48)
NAVY = (28, 52, 130)
ORANGE = (236, 108, 28)
GREEN = (36, 150, 72)
RED = (214, 32, 40)
BLUE = (40, 110, 220)
YELLOW = (255, 214, 0)
BANNER = (226, 56, 36)
SUB_BAND = (40, 40, 40, 175)

COLORS = {"navy": NAVY, "orange": ORANGE, "green": GREEN, "red": RED, "blue": BLUE,
          "ink": INK, "yellow": YELLOW, "white": (255, 255, 255)}


@lru_cache(maxsize=None)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    files = {
        "sub": "MPLUSRounded1c-Black.ttf",       # 字幕
        "label": "MPLUSRounded1c-Black.ttf",     # ラベル
        "body": "MPLUSRounded1c-ExtraBold.ttf",  # 吹き出し・図中の文字
        "impact": "DelaGothicOne-Regular.ttf",   # 強調ワード
        "brush": "YujiBoku-Regular.ttf",         # 筆の強調ワード
        "chalk": "YuseiMagic-Regular.ttf",       # 黒板
        "num": "Oswald-Bold.ttf",
        "gothic": "NotoSansJP-Black.ttf",
    }
    return ImageFont.truetype(str(FONT_DIR / files[name]), size)


def _measure(text, f, stroke=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), text, font=f, stroke_width=stroke)
    return l, t, r, b


def text_sprite(text, f, fill, stroke=0, stroke_fill=(255, 255, 255), shadow=False, pad=8):
    """1行のテキストをぴったりのRGBAスプライトにする"""
    l, t, r, b = _measure(text, f, stroke)
    w, h = r - l + pad * 2, b - t + pad * 2
    im = Image.new("RGBA", (w + (6 if shadow else 0), h + (6 if shadow else 0)), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 5, pad - t + 5), text, font=f, fill=(0, 0, 0, 90),
                                stroke_width=stroke, stroke_fill=(0, 0, 0, 90))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(im).text((pad - l, pad - t), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def stack(sprites, gap=0, align="center"):
    w = max(s.width for s in sprites)
    h = sum(s.height for s in sprites) + gap * (len(sprites) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for s in sprites:
        x = (w - s.width) // 2 if align == "center" else 0
        out.alpha_composite(s, (x, y))
        y += s.height + gap
    return out


# ---- 字幕 (画面下のグレー帯) -------------------------------------------------
SUB_H = 176
SUB_MAX = 30  # 1行の最大文字数

_NO_HEAD = set("、。，．・：；？！ゃゅょっャュョッァィゥェォー）」』】々〜")
_PARTICLES = set("はがをにでともへのてや")
_HIRA = lambda c: "ぁ" <= c <= "ゖ"


def _cut_cost(text, i, ideal):
    """text[:i] / text[i:] で切るときのコスト (小さいほど自然)"""
    a, b = text[i - 1], text[i]
    cost = abs(i - ideal) * 1.0
    if a in "、。":
        cost -= 14
    elif a in _PARTICLES and not _HIRA(b):
        cost -= 7          # 「〜は|契約金」のように助詞の後ろで漢字・カタカナに切り替わる所
    elif a in _PARTICLES:
        cost -= 2
    if b in _NO_HEAD:
        cost += 100        # 行頭禁則
    if (a.isdigit() or a in "〜") and (b.isdigit() or b in "万億円位年倍〜%"):
        cost += 100        # 数字や「1億円」を割らない
    if _HIRA(a) and _HIRA(b) and a not in _PARTICLES:
        cost += 6          # 「でしょ|うか」のような語の途中
    if not _HIRA(a) and not _HIRA(b) and a not in "、。" and b not in "、。":
        cost += 8          # 漢字・カタカナ語の途中
    return cost


def wrap(text: str, n: int = SUB_MAX):
    """日本語を自然な位置で折り返す (各行 n 文字以内、行数は最小)"""
    if "\n" in text:
        return text.split("\n")
    if len(text) <= n:
        return [text]
    k = -(-len(text) // n)
    ideal = len(text) / k
    lo, hi = max(1, len(text) - n * (k - 1)), min(n, len(text) - 1)
    best = min(range(lo, hi + 1), key=lambda i: _cut_cost(text, i, ideal))
    return [text[:best]] + wrap(text[best:], n)


def _hang(lines):
    """行頭に来た句読点などを前の行の末尾にぶら下げる"""
    out = []
    for l in lines:
        while out and l and l[0] in _NO_HEAD:
            out[-1] += l[0]
            l = l[1:]
        if l:
            out.append(l)
    return out


def pages(text: str):
    """字幕を2行ずつのページに分ける。3行以上になる文は句読点でページを区切る。"""
    lines = _hang(wrap(text))
    if len(lines) <= 2:
        return ["\n".join(lines)]
    # 2行に収まる塊になるよう、読点・句点の位置で前後に分ける
    cands = [i + 1 for i, c in enumerate(text[:-1]) if c in "、。"]
    best = min(cands, key=lambda i: abs(i - len(text) / 2)) if cands else len(text) // 2
    return pages(text[:best]) + pages(text[best:])


def subtitle(text: str) -> Image.Image:
    """横幅いっぱいの帯 (W x SUB_H)。白文字・黒縁の2行を中央揃え。"""
    im = Image.new("RGBA", (W, SUB_H), SUB_BAND)
    d = ImageDraw.Draw(im)
    f = font("sub", 54)
    lines = text.split("\n")
    lh = 72
    y0 = (SUB_H - lh * len(lines)) // 2 - 6
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f)
        d.text(((W - tw) / 2, y0 + i * lh), l, font=f, fill=(255, 255, 255), stroke_width=5,
               stroke_fill=(20, 20, 20))
    return im


# ---- 左上の章タイトル / 右上のシリーズ帯 --------------------------------------
def chapter_title(text: str) -> Image.Image:
    return text_sprite(text, font("label", 40), NAVY, stroke=6, stroke_fill=(255, 255, 255))


def banner(lines=("プロ野球 お金と制度のしくみ", "ドラフト契約金の相場まとめ")) -> Image.Image:
    f = font("label", 30)
    sp = [text_sprite(l, f, (255, 255, 255)) for l in lines]
    w = max(s.width for s in sp) + 36
    h = sum(s.height for s in sp) + 14
    im = Image.new("RGBA", (w, h), BANNER + (255,))
    ImageDraw.Draw(im).rectangle((3, 3, w - 4, h - 4), outline=(255, 255, 255, 230), width=3)
    y = 7
    for s in sp:
        im.alpha_composite(s, ((w - s.width) // 2, y))
        y += s.height
    return im


# ---- 画面中の部品 -------------------------------------------------------------
def label(text, color="navy", size=72, stroke=10):
    """イラストの上に乗せる色付きの太ラベル (白フチ)"""
    return text_sprite(text, font("label", size), COLORS.get(color, color) if isinstance(color, str) else color,
                       stroke=stroke, stroke_fill=(255, 255, 255), shadow=True)


def big_word(text, style="yellow", size=200):
    """強調ワード。yellow=黄色+黒フチ / red_brush=赤の筆 / ink_brush=黒の筆 / red=赤ゴシック"""
    if style == "yellow":
        return text_sprite(text, font("impact", size), YELLOW, stroke=14, stroke_fill=(30, 30, 30), shadow=True)
    if style == "red":
        return text_sprite(text, font("impact", size), RED, stroke=12, stroke_fill=(255, 255, 255), shadow=True)
    if style == "red_brush":
        return text_sprite(text, font("brush", size), RED, stroke=8, stroke_fill=(255, 255, 255), shadow=True)
    if style == "ink_brush":
        return text_sprite(text, font("brush", size), (20, 20, 20), stroke=8, stroke_fill=(255, 255, 255), shadow=True)
    raise ValueError(style)


def stamp(text, color=RED, size=90, angle=-12):
    """斜めのスタンプ文字 (例: 指名漏れ！)"""
    s = text_sprite(text, font("impact", size), color, stroke=8, stroke_fill=(255, 255, 255))
    return s.rotate(angle, expand=True, resample=Image.BICUBIC)


def bubble(text, size=52, tail="left", w=None):
    """白い吹き出し (黒フチ)。tail は尻尾の向き: left/right/down"""
    f = font("body", size)
    lines = text.split("\n")
    tw = max(int(_measure(l, f)[2]) for l in lines)
    lh = int(size * 1.3)
    bw = w or tw + 100
    bh = lh * len(lines) + 70
    m = 30
    cw, ch = bw + m * 2, bh + m * 2 + 60
    mask = Image.new("L", (cw * 2, ch * 2), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((m * 2, m * 2, (m + bw) * 2, (m + bh) * 2), fill=255)
    bx = {"left": 0.3, "right": 0.7, "down": 0.5}[tail]
    tipx = {"left": m + 6, "right": m + bw - 6, "down": m + bw * 0.5}[tail]
    base_l, base_r = m + bw * (bx - 0.09), m + bw * (bx + 0.09)
    d.polygon([(base_l * 2, (m + bh * 0.8) * 2), (base_r * 2, (m + bh * 0.8) * 2), (tipx * 2, (m + bh + 52) * 2)], fill=255)
    mask = mask.resize((cw, ch), Image.LANCZOS)
    edge = mask.filter(ImageFilter.MaxFilter(9))
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    im.paste((30, 30, 30, 255), (0, 0), edge)
    im.paste((255, 255, 255, 255), (0, 0), mask)
    d = ImageDraw.Draw(im)
    y = m + (bh - lh * len(lines)) // 2 - 6
    for l in lines:
        lw = d.textlength(l, font=f)
        d.text((m + (bw - lw) / 2, y), l, font=f, fill=INK)
        y += lh
    return im


def red_circle(w, h, width=12, color=RED):
    """手書き風の赤丸 (少しずれた楕円を2周)"""
    S = 2
    im = Image.new("RGBA", ((w + 40) * S, (h + 40) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = []
    for k in range(0, 400):
        t = k / 360 * 2 * math.pi
        rx = w / 2 * (1 + 0.03 * math.sin(3 * t))
        ry = h / 2 * (1 + 0.04 * math.cos(2 * t))
        jitter = 1 + 0.05 * (k / 400)
        pts.append(((w / 2 + 20 + rx * math.cos(t - 0.4) * jitter) * S, (h / 2 + 20 + ry * math.sin(t - 0.4)) * S))
    d.line(pts, fill=color + (255,), width=width * S, joint="curve")
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


def arrow(length=200, color=BLUE, angle=0, width=46):
    """太い矢印。angle は度 (0=右向き、90=上向き)"""
    S = 2
    L, Wd = length * S, width * S
    im = Image.new("RGBA", (L + 20 * S, int(Wd * 2.4) + 20 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cy = im.height / 2
    head = Wd * 1.4
    body = [(10 * S, cy - Wd / 2), (10 * S + L - head, cy - Wd / 2), (10 * S + L - head, cy - Wd * 1.1),
            (10 * S + L, cy), (10 * S + L - head, cy + Wd * 1.1), (10 * S + L - head, cy + Wd / 2), (10 * S, cy + Wd / 2)]
    d.polygon(body, fill=(255, 255, 255), outline=None)
    d.line(body + [body[0]], fill=(255, 255, 255), width=10 * S)
    d.polygon(body, fill=color)
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    return im.rotate(angle, expand=True, resample=Image.BICUBIC)


def panel(w, h, fill=(255, 255, 255), outline=(60, 60, 70), radius=24, width=5):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((2, 2, w - 3, h - 3), radius=radius, fill=fill, outline=outline, width=width)
    return im


def bar_chart(rows, w=1300, h=560, unit="万円", vmax=None, highlight=None, show_values=True):
    """横軸ラベル付きの棒グラフ。rows=[(ラベル, 値, 値の表示)]"""
    vmax = vmax or max(v for _, v, _ in rows)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base = h - 90
    top = 90
    d.line((40, base, w - 20, base), fill=INK, width=5)
    n = len(rows)
    slot = (w - 80) / n
    bw = slot * 0.56
    fl = font("label", 46)
    fv = font("label", 44)
    for i, (lab, v, vt) in enumerate(rows):
        cx = 60 + slot * (i + 0.5)
        bh = (base - top) * v / vmax
        col = RED if highlight == i else (88, 140, 220)
        d.rounded_rectangle((cx - bw / 2, base - bh, cx + bw / 2, base), radius=10, fill=col)
        lw = d.textlength(lab, font=fl)
        d.text((cx - lw / 2, base + 14), lab, font=fl, fill=INK)
        if show_values:
            vw = d.textlength(vt, font=fv)
            d.text((cx - vw / 2, base - bh - 62), vt, font=fv, fill=RED if highlight == i else INK,
                   stroke_width=6, stroke_fill=(255, 255, 255))
    return im


def table(header, rows, col_w, row_h=96, highlight_col=None):
    """シンプルな表。header=[...], rows=[[...]]"""
    w = sum(col_w)
    h = row_h * (len(rows) + 1)
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fh = font("label", 46)
    fb = font("body", 46)
    d.rounded_rectangle((4, 4, w + 4, h + 4), radius=18, fill=(255, 255, 255), outline=INK, width=5)
    d.rounded_rectangle((4, 4, w + 4, row_h + 4), radius=18, fill=NAVY)
    d.rectangle((4, row_h - 14, w + 4, row_h + 4), fill=NAVY)
    x = 4
    for ci, cw in enumerate(col_w):
        if highlight_col == ci:
            d.rectangle((x, row_h + 4, x + cw, h + 4), fill=(255, 238, 232))
        x += cw
    for ri, row in enumerate([header] + rows):
        x = 4
        y = 4 + ri * row_h
        if ri > 0:
            d.line((4, y, w + 4, y), fill=(190, 190, 200), width=3)
        for ci, (cell, cw) in enumerate(zip(row, col_w)):
            f = fh if ri == 0 or ci == 0 else fb
            col = (255, 255, 255) if ri == 0 else (RED if (highlight_col == ci and ri > 0) else INK)
            tw = d.textlength(cell, font=f)
            d.text((x + (cw - tw) / 2, y + (row_h - f.size) / 2 - 8), cell, font=f, fill=col)
            x += cw
    return im


def chalkboard(lines, title=None):
    """まとめ用の黒板 (全面)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 50, W - 70, H - 50), radius=18, fill=(156, 104, 58))
    d.rectangle((100, 80, W - 100, H - 80), fill=(34, 84, 58))
    d.rectangle((100, H - 112, W - 100, H - 80), fill=(120, 80, 44))
    fc = font("chalk", 64)
    y = 130
    if title:
        ft = font("chalk", 78)
        d.text((170, y), title, font=ft, fill=(255, 238, 120))
        y += 130
    for l in lines:
        first, rest = l[0], l[1:]
        d.text((170, y), first, font=font("chalk", 84), fill=(255, 238, 120))
        d.text((170 + d.textlength(first, font=font("chalk", 84)) + 6, y + 14), rest, font=fc, fill=(250, 250, 245))
        y += 128
    return im


def strip_markup(s: str) -> str:
    return re.sub(r"[【】《》]", "", s)
