"""2本目の図解パーツ (暗い背景に金の線で描く)。

どれも RGBA の画像を返す。配置とアニメは film.E で決める。
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import look as L

INK = (240, 234, 220)
DIM = (170, 165, 155)
PANEL = (8, 8, 10, 190)


def _f(size, name="NotoSerifJP-Black.ttf"):
    return L.font(name, size)


def _tw(d, s, f):
    return d.textlength(s, font=f)


def panel(w, h, border=L.GOLD, fill=PANEL, width=3):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=fill, outline=border + (255,), width=width)
    d.rectangle((10, 10, w - 11, h - 11), outline=border + (90,), width=1)
    return im


def chapter_card(no, title):
    """章の扉: 「第◯章」と章タイトル、間に金の線"""
    kanji = "〇一二三四五六七八九十"
    n = kanji[no] if no <= 10 else str(no)
    head = L.text(f"第{n}章", "NotoSerifJP-Black.ttf", 54, L.GOLD, pad=10)
    t = L.text(title, "NotoSerifJP-Black.ttf", 104, L.WHITE, pad=10)
    w = max(head.width, t.width) + 80
    im = Image.new("RGBA", (w, head.height + t.height + 60), (0, 0, 0, 0))
    im.alpha_composite(head, ((w - head.width) // 2, 0))
    d = ImageDraw.Draw(im)
    y = head.height + 18
    d.line((40, y, w - 40, y), fill=L.GOLD + (220,), width=3)
    im.alpha_composite(t, ((w - t.width) // 2, y + 26))
    return im


def move(src, dst, year=None, size=56, max_w=900):
    """「中日 → 巨人（1993年オフ）」のような移籍の札。max_w より広くなるときは縮める"""
    f = _f(size)
    fs = _f(round(size * 0.6), "NotoSansJP-Bold.ttf")
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    a, b = _tw(d, src, f), _tw(d, dst, f)
    arrow = 110
    yr = f"（{year}）" if year else ""
    yw = _tw(d, yr, fs) if yr else 0
    w = round(a + b + arrow + yw + 120)
    h = round(size * 1.9)
    im = panel(w, h)
    d = ImageDraw.Draw(im)
    x = 40
    cy = h // 2
    d.text((x, cy), src, font=f, fill=INK, anchor="lm")
    x += a + 20
    d.line((x, cy, x + arrow - 30, cy), fill=L.GOLD, width=6)
    d.polygon([(x + arrow - 34, cy - 16), (x + arrow - 6, cy), (x + arrow - 34, cy + 16)], fill=L.GOLD)
    x += arrow
    d.text((x, cy), dst, font=f, fill=L.WHITE, anchor="lm")
    if yr:
        d.text((x + b + 10, cy + 4), yr, font=fs, fill=DIM, anchor="lm")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    return im


def note(s="※金額は報道による推定", size=30):
    return L.caption_small(s, size)


def bullet_list(items, size=60, width=None, gap=34, mark="◆"):
    """箇条書き (左に金のしるし)"""
    f = _f(size)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = max(_tw(d, s, f) for s in items)
    w = width or round(tw + size * 2.4 + 80)
    lh = round(size * 1.25) + gap
    h = lh * len(items) + 70
    im = panel(w, h)
    d = ImageDraw.Draw(im)
    for i, s in enumerate(items):
        y = 45 + i * lh + size // 2 + 4
        d.text((50, y), mark, font=_f(round(size * 0.6)), fill=L.GOLD, anchor="lm")
        d.text((50 + size * 1.2, y), s, font=f, fill=INK, anchor="lm")
    return im


def timeline(marks, upto=99, w=1640, h=330):
    """横の年表。marks = [(年, ラベル), ...]。upto 番目までを明るく、upto 番目を金で強調"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 150
    d.line((40, y, w - 40, y), fill=(200, 190, 170, 200), width=5)
    n = len(marks)
    fy, fl = _f(50), _f(34, "NotoSansJP-Bold.ttf")
    # 端のラベルがはみ出さないよう、いちばん広い文字の半分だけ内側から並べる
    half = max(max(_tw(d, yr, fy), *(_tw(d, p, fl) for p in lab.split("\n"))) for yr, lab in marks) / 2
    m = max(120, half + 20)
    for i, (yr, lab) in enumerate(marks):
        x = m + (w - 2 * m) * i / max(1, n - 1)
        on = i <= upto
        col = L.GOLD if i == upto else (INK if on else (110, 105, 100))
        r = 18 if i == upto else 12
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)
        d.text((x, y - 40), yr, font=fy, fill=col, anchor="ms")
        for k, part in enumerate(lab.split("\n")):
            d.text((x, y + 62 + k * 44), part, font=fl, fill=col, anchor="ms")
    return im


def table(header, rows, col_w, row_h=96, highlight=None, size=44):
    """表。highlight は強調する行番号"""
    w = sum(col_w)
    h = row_h * (len(rows) + 1)
    im = Image.new("RGBA", (w + 6, h + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w + 5, h + 5), fill=PANEL)
    fh, fb = _f(size), _f(size, "NotoSansJP-Bold.ttf")
    d.rectangle((3, 3, w + 2, row_h), fill=(70, 52, 20, 230))
    x = 3
    for c, cw in zip(header, col_w):
        d.text((x + cw / 2, row_h / 2 + 3), c, font=fh, fill=L.GOLD, anchor="mm")
        x += cw
    for r, row in enumerate(rows):
        y0 = 3 + row_h * (r + 1)
        if highlight == r:
            d.rectangle((3, y0, w + 2, y0 + row_h), fill=(232, 196, 110, 60))
        x = 3
        for c, cw in zip(row, col_w):
            for k, part in enumerate(str(c).split("\n")):
                n = len(str(c).split("\n"))
                yy = y0 + row_h / 2 + (k - (n - 1) / 2) * (size * 1.1)
                d.text((x + cw / 2, yy), part, font=fb, fill=INK, anchor="mm")
            x += cw
        d.line((3, y0, w + 2, y0), fill=L.GOLD + (110,), width=2)
    d.rectangle((0, 0, w + 5, h + 5), outline=L.GOLD + (255,), width=3)
    return im


def days_bar(days, total=145, w=1300, h=220, label=None):
    """一軍登録日数のゲージ (145日で1年)"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = 40, w - 40, 80, 150
    d.rectangle((x0, y0, x1, y1), fill=(30, 30, 34, 220), outline=L.GOLD, width=3)
    fx = x0 + (x1 - x0) * min(days, total) / total
    d.rectangle((x0 + 4, y0 + 4, fx - 4, y1 - 4), fill=L.GOLD + (230,))
    f = _f(52)
    d.text((x0, 50), label or f"一軍登録 {days}日", font=f, fill=INK, anchor="ls")
    d.text((x1, 50), f"{total}日 ＝ 1年", font=f, fill=L.GOLD, anchor="rs")
    return im


def protect_grid(protected=28, total=70, cols=14, highlight=None):
    """支配下70人のうち28人を守る図。highlight は指名される1人の番号"""
    cell = 70
    rows = (total + cols - 1) // cols
    w, h = cols * cell + 40, rows * cell + 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=PANEL, outline=L.GOLD + (255,), width=3)
    for i in range(total):
        r, c = divmod(i, cols)
        cx, cy = 20 + c * cell + cell // 2, 20 + r * cell + cell // 2
        if i < protected:
            d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill=L.GOLD)
        elif i == highlight:
            d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=L.RED, outline=L.WHITE, width=4)
        else:
            d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), outline=(220, 220, 220), width=4)
    f = _f(44)
    y = 20 + rows * cell + 50
    d.ellipse((40, y - 18, 76, y + 18), fill=L.GOLD)
    d.text((90, y), f"プロテクト {protected}人", font=f, fill=L.GOLD, anchor="lm")
    d.ellipse((w // 2 + 30, y - 18, w // 2 + 66, y + 18), outline=(220, 220, 220), width=4)
    d.text((w // 2 + 80, y), "名簿に載る選手", font=f, fill=INK, anchor="lm")
    return im


def option_cards(left, right, title=None, w=700, gap=120):
    """「AかBか」の2択カード。left/right = (見出し, 中身)。w は1枚の幅"""
    h = 330
    th = 110 if title else 0
    im = Image.new("RGBA", (w * 2 + gap, h + th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if title:
        d.text(((w * 2 + gap) / 2, 50), title, font=_f(64), fill=L.GOLD, anchor="mm")
    for i, (head, body) in enumerate((left, right)):
        x = i * (w + gap)
        p = panel(w, h)
        im.alpha_composite(p, (x, th))
        d.text((x + w / 2, th + 80), head, font=_f(48, "NotoSansJP-Bold.ttf"), fill=DIM, anchor="mm")
        for k, part in enumerate(body.split("\n")):
            d.text((x + w / 2, th + 175 + k * 80), part, font=_f(70), fill=L.WHITE, anchor="mm")
    d.text((w + gap / 2, th + h / 2), "or", font=_f(60), fill=L.GOLD, anchor="mm")
    return im


def money_bars(rows, unit="億円", w=1400, vmax=None):
    """横棒で金額を比べる。rows = [(ラベル, 値, 金色か)]"""
    vmax = vmax or max(v for _, v, _ in rows)
    lh = 120
    im = Image.new("RGBA", (w, lh * len(rows) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f, fv = _f(46, "NotoSansJP-Bold.ttf"), _f(56)
    lab_w = 420 if w >= 1200 else 230  # 狭い画面 (ショート) ではラベル欄を詰める
    for i, (lab, v, hi) in enumerate(rows):
        y = 10 + i * lh
        d.text((lab_w - 20, y + 45), lab, font=f, fill=INK, anchor="rm")
        bw = (w - lab_w - 260) * v / vmax
        col = L.GOLD if hi else (150, 150, 155)
        d.rectangle((lab_w, y + 10, lab_w + bw, y + 80), fill=col + (235,))
        vs = f"{v:g}{unit}"
        d.text((lab_w + bw + 20, y + 45), vs, font=fv, fill=col, anchor="lm")
    return im


def rank_card(rank, name, lines, amount, photo=None, focus=(0.5, 0.25), h=430, w=1180):
    """ランキングの札: 順位・写真・名前・移籍・金額。2枚並べるときは h を小さく"""
    im = panel(w, h, width=4)
    d = ImageDraw.Draw(im)
    x = 40
    if photo:
        pw = round((h - 80) * 300 / 350)
        ph = L.grade(L.cover(L.photo(photo), pw, h - 80, focus), "dark")
        im.paste(ph, (40, 40))
        d.rectangle((40, 40, 40 + pw, h - 40), outline=L.GOLD, width=3)
        x = 80 + pw
    top = 95 if h >= 430 else 80
    d.text((x, top), f"第{rank}位", font=_f(64), fill=L.GOLD, anchor="ls")
    d.text((x, top + 105), name, font=_f(86), fill=L.WHITE, anchor="ls")
    for k, s in enumerate(lines):
        d.text((x, top + 165 + k * 50), s, font=_f(38, "NotoSansJP-Bold.ttf"), fill=DIM, anchor="ls")
    g = L.gold(amount, size=78)
    im.alpha_composite(g, (w - g.width + 30, h - g.height + 30))
    return im


def portrait(name, focus=(0.5, 0.3), w=420, h=520, mood="dark"):
    """小さめの人物写真 (枠つき)"""
    ph = L.grade(L.cover(L.photo(name), w, h, focus), mood).convert("RGBA")
    d = ImageDraw.Draw(ph)
    d.rectangle((0, 0, w - 1, h - 1), outline=L.GOLD, width=4)
    return ph


def name_plate(name, sub=None):
    """写真のない人物の名札"""
    f = _f(72)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    w = round(max(_tw(d, name, f), _tw(d, sub or "", _f(38, "NotoSansJP-Bold.ttf"))) + 120)
    h = 200 if sub else 140
    im = panel(w, h)
    d = ImageDraw.Draw(im)
    d.text((w / 2, 75), name, font=f, fill=L.WHITE, anchor="mm")
    if sub:
        d.text((w / 2, 150), sub, font=_f(38, "NotoSansJP-Bold.ttf"), fill=DIM, anchor="mm")
    return im


def quote(s, size=58):
    """「」つきの引用 (白い文字に金のかぎかっこ)"""
    return L.text(f"「{s}」", "NotoSerifJP-Black.ttf", size, L.WHITE)
