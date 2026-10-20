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


# ---- YouTube の表示とかぶらないための配置 ------------------------------------
# 下: シークバーと操作ボタン (一時停止中・マウスを乗せたとき) は下端から約 5〜8% に出るので、字幕帯を浮かせる
# 右下: チャンネル透かし (ブランディング) が出るので、字幕の行幅を短くして右端に文字を置かない
# 上: タイトル表示・カードの i アイコンが出るので、章タイトルと帯を端から離す
SUB_H = 164
SUB_BOTTOM = 40
SUB_Y = H - SUB_BOTTOM - SUB_H              # 字幕帯の上端 (876)
CHAPTER_POS = (64, 44)                      # 左上の章タイトル
BANNER_MARGIN = (64, 40)                    # 右上の帯 (右端・上端からの距離)
CONTENT = (80, 150, W - 80, SUB_Y - 14)     # 画面要素を置いてよい範囲

# ---- 字幕 (画面下のグレー帯) -------------------------------------------------
SUB_MAX = 28  # 1行の最大文字数 (右下の透かしにかからない幅)

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
    f = font("sub", 52)
    lines = text.split("\n")
    lh = 68
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


# ---- バリエーション用の図解 ------------------------------------------------------
def staircase(rows, upto, w=1500, h=600):
    """順位別の相場を「下り階段」で見せる。rows=[(順位, 高さ0-1, 金額表示)]
    順位は段の下、金額は段の上に書く。"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = len(rows)
    sw = w / n
    base = h - 80
    for i, (lab, v, amt) in enumerate(rows[:upto]):
        x0, x1 = i * sw + 6, (i + 1) * sw - 6
        top = base - (base - 90) * v
        col = (255, 196, 40) if i == 0 else (120, 170, 235)
        d.rounded_rectangle((x0, top, x1, base), radius=12, fill=col, outline=INK, width=4)
        fl = font("label", 50)
        lw = d.textlength(lab, font=fl)
        d.text(((x0 + x1) / 2 - lw / 2, base + 8), lab, font=fl, fill=INK)
        fa = font("label", 40)
        aw = d.textlength(amt, font=fa)
        d.text(((x0 + x1) / 2 - aw / 2, top - 58), amt, font=fa, fill=RED if i == 0 else INK,
               stroke_width=6, stroke_fill=(255, 255, 255))
    return im


def timeline(marks, w=1500, h=300, upto=99):
    """左→右の時間軸。marks=[(位置0-1, 上の文字, 下の文字, 色)]"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = h / 2
    d.rounded_rectangle((20, y - 12, w - 70, y + 12), radius=12, fill=(150, 160, 180))
    d.polygon([(w - 80, y - 36), (w - 10, y), (w - 80, y + 36)], fill=(150, 160, 180))
    for k, (p, top, bottom, col) in enumerate(marks[:upto]):
        x = 40 + (w - 160) * p
        c = COLORS.get(col, col) if isinstance(col, str) else col
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=c, outline=(255, 255, 255), width=6)
        ft = font("label", 50)
        tw = d.textlength(top, font=ft)
        tx = min(max(x - tw / 2, 0), w - tw - 8)
        d.text((tx, y - 110), top, font=ft, fill=c, stroke_width=6, stroke_fill=(255, 255, 255))
        fb = font("body", 40)
        bw = d.textlength(bottom, font=fb)
        bx = min(max(x - bw / 2, 0), w - bw - 8)
        d.text((bx, y + 44), bottom, font=fb, fill=INK)
    return im


def flow_box(text, color="navy", w=420, h=130, size=50):
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = COLORS.get(color, color) if isinstance(color, str) else color
    d.rounded_rectangle((10, 10, w + 10, h + 10), radius=22, fill=(0, 0, 0, 50))
    d.rounded_rectangle((0, 0, w, h), radius=22, fill=c)
    f = font("label", size)
    lines = text.split("\n")
    lh = size * 1.25
    y = (h - lh * len(lines)) / 2 - 4
    for l in lines:
        tw = d.textlength(l, font=f)
        d.text(((w - tw) / 2, y), l, font=f, fill=(255, 255, 255))
        y += lh
    return im


def diamond(text, w=520, h=300, size=50):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w / 2, 6), (w - 6, h / 2), (w / 2, h - 6), (6, h / 2)], fill=(255, 246, 214), outline=INK)
    d.line([(w / 2, 6), (w - 6, h / 2), (w / 2, h - 6), (6, h / 2), (w / 2, 6)], fill=INK, width=6)
    f = font("label", size)
    lines = text.split("\n")
    lh = size * 1.25
    y = (h - lh * len(lines)) / 2 - 4
    for l in lines:
        tw = d.textlength(l, font=f)
        d.text(((w - tw) / 2, y), l, font=f, fill=INK)
        y += lh
    return im


def line_arrow(x0, y0, x1, y1, color=INK, width=8, label=None):
    """2点を結ぶ細い矢印 (フローチャート用)。返り値はスプライトと中心座標"""
    pad = 60
    l, t = min(x0, x1) - pad, min(y0, y1) - pad
    w, h = abs(x1 - x0) + pad * 2, abs(y1 - y0) + pad * 2
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a, b = (x0 - l, y0 - t), (x1 - l, y1 - t)
    d.line([a, b], fill=color, width=width)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    hd = 30
    d.polygon([b, (b[0] - hd * math.cos(ang - 0.45), b[1] - hd * math.sin(ang - 0.45)),
               (b[0] - hd * math.cos(ang + 0.45), b[1] - hd * math.sin(ang + 0.45))], fill=color)
    if label:
        f = font("label", 44)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        tw = d.textlength(label, font=f)
        d.text((mx - tw / 2 + 30, my - 30), label, font=f, fill=color, stroke_width=6, stroke_fill=(255, 255, 255))
    return im


def number(text, color="red", size=150):
    """大きな数字 (カウントアップ用)"""
    c = COLORS.get(color, color) if isinstance(color, str) else color
    return text_sprite(text, font("impact", size), c, stroke=12, stroke_fill=(255, 255, 255), shadow=True)


def gap_marker(w=270, h=135, color=RED):
    """2つの高さの差を示す: 上の高さから伸ばした点線 + 右端の上下矢印"""
    S2 = 2
    im = Image.new("RGBA", (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y0, y1 = 8 * S2, (h - 8) * S2
    x = (w - 24) * S2
    for xx in range(0, x, 28 * S2):
        d.line([(xx, y0), (min(x, xx + 16 * S2), y0)], fill=color, width=6 * S2)
    d.line([(x, y0 + 20 * S2), (x, y1 - 20 * S2)], fill=color, width=8 * S2)
    for yy, sgn in ((y0, 1), (y1, -1)):
        d.polygon([(x, yy), (x - 16 * S2, yy + sgn * 26 * S2), (x + 16 * S2, yy + sgn * 26 * S2)], fill=color)
    return im.resize((w, h), Image.LANCZOS)


def snake_order(rows=3, cols=12, upto=99, w=1560, h=470, labels=("2巡目", "3巡目", "4巡目")):
    """ウェーバー → 逆ウェーバー → ウェーバー … の順番。
    列は球団 (左が最下位、右が優勝)、丸の中の数字はその巡での指名の順番。"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lab_w = 190
    gap = (w - lab_w - 70) / cols
    head = 64
    rh = (h - head) / rows
    fl = font("label", 46)
    fn = font("label", 34)
    fh = font("label", 34)
    xs = [lab_w + gap * (c + 0.5) for c in range(cols)]
    for txt, x, col in (("最下位", xs[0], ORANGE), ("優勝", xs[-1], NAVY)):
        tw = d.textlength(txt, font=fh)
        d.text((x - tw / 2, 4), txt, font=fh, fill=col)
    for r in range(min(rows, upto)):
        y = head + rh * (r + 0.5)
        d.text((0, y - 30), labels[r], font=fl, fill=INK)
        fwd = r % 2 == 0
        x0, x1 = (xs[0], xs[-1]) if fwd else (xs[-1], xs[0])
        tip = x1 + (52 if fwd else -52)
        d.line([(x0, y), (tip, y)], fill=(170, 180, 200), width=8)
        d.polygon([(tip + (18 if fwd else -18), y), (tip, y - 18), (tip, y + 18)], fill=(170, 180, 200))
        for c in range(cols):
            k = c + 1 if fwd else cols - c
            col = ORANGE if k == 1 else NAVY
            x = xs[c]
            d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=col, outline=(255, 255, 255), width=4)
            t = str(k)
            tw = d.textlength(t, font=fn)
            d.text((x - tw / 2, y - 24), t, font=fn, fill=(255, 255, 255))
    return im


def vtimeline(items, upto=99, w=1300, row_h=104):
    """縦の年表。items=[(年, 出来事, 色)]"""
    h = row_h * len(items) + 10
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((176, 20, 188, h - 20), radius=6, fill=(200, 205, 215))
    fy = font("num", 62)
    fe = font("label", 56)
    for k, (year, text, col) in enumerate(items[:upto]):
        y = 10 + row_h * k + row_h / 2
        c = COLORS.get(col, col) if isinstance(col, str) else col
        d.rounded_rectangle((0, y - 40, 160, y + 40), radius=18, fill=c)
        yw = d.textlength(year, font=fy)
        d.text((80 - yw / 2, y - 46), year, font=fy, fill=(255, 255, 255))
        d.ellipse((168, y - 14, 196, y + 14), fill=c, outline=(255, 255, 255), width=4)
        d.text((226, y - 40), text, font=fe, fill=INK)
    return im


def month_bar(months, marks, w=1500, h=260):
    """月の帯。months=["10月",...], marks=[(index, 上の文字, 色)]"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = len(months)
    cw = w / n
    y0 = h - 110
    fm = font("label", 40)
    for i, m in enumerate(months):
        x0 = i * cw
        d.rounded_rectangle((x0 + 4, y0, x0 + cw - 4, y0 + 90), radius=12,
                            fill=(236, 240, 248), outline=(190, 196, 210), width=3)
        tw = d.textlength(m, font=fm)
        d.text((x0 + cw / 2 - tw / 2, y0 + 20), m, font=fm, fill=INK)
    ft = font("label", 42)
    for i, text, col in marks:
        c = COLORS.get(col, col) if isinstance(col, str) else col
        x = i * cw + cw / 2
        tw = d.textlength(text, font=ft)
        tx = min(max(x - tw / 2, 0), w - tw - 6)
        d.text((tx, 6), text, font=ft, fill=c, stroke_width=6, stroke_fill=(255, 255, 255))
        d.polygon([(x - 18, 70), (x + 18, 70), (x, 100)], fill=c)
        d.rounded_rectangle((i * cw + 4, y0, i * cw + cw - 4, y0 + 90), radius=12, outline=c, width=7)
    return im


def checklist(items, upto=99, w=1100, size=56):
    """チェックリスト (✓ 付き)"""
    row = int(size * 1.9)
    im = Image.new("RGBA", (w, row * len(items)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font("label", size)
    for k, (text, ok) in enumerate(items[:upto]):
        y = k * row
        d.rounded_rectangle((0, y + 8, row - 24, y + row - 16), radius=12, fill=(255, 255, 255),
                            outline=INK, width=5)
        if ok:
            d.line([(16, y + row / 2), (row / 2 - 12, y + row - 30), (row - 30, y + 20)], fill=GREEN, width=12)
        else:
            d.line([(20, y + 24), (row - 44, y + row - 40)], fill=RED, width=12)
            d.line([(row - 44, y + 24), (20, y + row - 40)], fill=RED, width=12)
        d.text((row + 6, y + (row - size) / 2 - 10), text, font=f, fill=INK)
    return im


# ---- チャンネル登録の呼びかけ (ボタンをクリックするアニメーション) ------------------
def _cursor(scale=1.0):
    """マウスカーソル (矢印)"""
    S2 = 2
    w, h = int(70 * scale), int(100 * scale)
    im = Image.new("RGBA", (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(0, 0), (0, 80), (20, 62), (34, 96), (48, 90), (34, 56), (60, 56)]
    pts = [(x * scale * S2 + 4, y * scale * S2 + 4) for x, y in pts]
    d.polygon(pts, fill=(255, 255, 255))
    d.line(pts + [pts[0]], fill=(20, 20, 20), width=int(5 * S2 * scale), joint="curve")
    return im.resize((w, h), Image.LANCZOS)


def _pill(text, fill, fg=(255, 255, 255), w=520, h=130, size=56, icon=None, press=1.0):
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 16, w + 14, h + 16), radius=h // 2, fill=(0, 0, 0, 60))
    d.rounded_rectangle((4, 4, w + 4, h + 4), radius=h // 2, fill=fill)
    f = font("label", size)
    tw = d.textlength(text, font=f)
    x0 = 4 + (w - tw) / 2 + (28 if icon else 0)
    if icon == "thumb":   # 上向きの矢印 (高評価)
        cx, cy = x0 - 52, 4 + h / 2
        d.polygon([(cx, cy - 30), (cx - 26, cy + 4), (cx - 10, cy + 4), (cx - 10, cy + 30), (cx + 10, cy + 30),
                   (cx + 10, cy + 4), (cx + 26, cy + 4)], fill=fg)
    elif icon == "check":
        cx, cy = x0 - 50, 4 + h / 2
        d.line([(cx - 22, cy), (cx - 6, cy + 18), (cx + 24, cy - 18)], fill=fg, width=10)
    d.text((x0, 4 + (h - size) / 2 - 10), text, font=f, fill=fg)
    if press < 1.0:
        im = im.resize((int(im.width * press), int(im.height * press)), Image.BILINEAR)
    return im


def _bell(ring=0.0, on=False):
    """通知ベル。ring は揺れの角度 (度)"""
    S2 = 2
    im = Image.new("RGBA", (130 * S2, 130 * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = ORANGE if on else (120, 120, 130)
    d.ellipse((5 * S2, 5 * S2, 125 * S2, 125 * S2), fill=(255, 255, 255), outline=col, width=6 * S2)
    d.pieslice((35 * S2, 28 * S2, 95 * S2, 100 * S2), 180, 360, fill=col)
    d.rectangle((35 * S2, 63 * S2, 95 * S2, 88 * S2), fill=col)
    d.rectangle((28 * S2, 86 * S2, 102 * S2, 94 * S2), fill=col)
    d.ellipse((57 * S2, 92 * S2, 73 * S2, 106 * S2), fill=col)
    im = im.resize((130, 130), Image.LANCZOS)
    return im.rotate(ring, resample=Image.BICUBIC) if ring else im


def cta_frame(t):
    """t 秒目の呼びかけアニメ: 高評価 → チャンネル登録 → 通知ベル の順にカーソルでクリック"""
    W2, H2 = 1500, 420
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    like_c, sub_c, bell_c = (260, 210), (850, 210), (1290, 210)
    t_like, t_sub, t_bell = 1.2, 2.6, 4.0

    def press_of(tc):
        return 0.92 if tc <= t < tc + 0.15 else 1.0

    liked, subbed, belled = t >= t_like, t >= t_sub, t >= t_bell
    like = _pill("高評価", BLUE if liked else (150, 160, 175), w=380, icon="thumb", press=press_of(t_like))
    sub = _pill("登録済み" if subbed else "チャンネル登録", (150, 150, 160) if subbed else RED, w=560,
                icon="check" if subbed else None, press=press_of(t_sub))
    ring = 18 * math.sin((t - t_bell) * 18) * max(0.0, 1 - (t - t_bell) / 1.2) if belled else 0
    bell = _bell(ring, belled)
    for spr, (cx, cy) in ((like, like_c), (sub, sub_c), (bell, bell_c)):
        im.alpha_composite(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)))
    if belled and t < t_bell + 2.0:
        lab = text_sprite("通知オン", font("label", 40), ORANGE, stroke=6, stroke_fill=(255, 255, 255))
        im.alpha_composite(lab, (bell_c[0] - lab.width // 2, bell_c[1] + 80))
    # カーソルの移動: 右下から 高評価 → 登録 → ベル
    path = [((W2 + 40, H2 + 60), 0.0), ((like_c[0] + 20, like_c[1] + 10), t_like - 0.15),
            ((sub_c[0] + 40, sub_c[1] + 10), t_sub - 0.15), ((bell_c[0] + 10, bell_c[1] + 10), t_bell - 0.15),
            ((bell_c[0] + 10, bell_c[1] + 10), 99.0)]
    for (p0, a), (p1, b) in zip(path, path[1:]):
        if a <= t <= b:
            k = min(1.0, (t - a) / max(0.01, min(0.8, b - a)))
            k = 1 - (1 - k) ** 3
            x, y = p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k
            break
    else:
        x, y = path[-1][0]
    if t < t_bell + 1.5:
        cur = _cursor(1.0 if not any(tc <= t < tc + 0.15 for tc in (t_like, t_sub, t_bell)) else 0.85)
        im.alpha_composite(cur, (int(min(W2 - cur.width, x)), int(min(H2 - cur.height, y))))
    return im
