"""報道ドキュメンタリー風の部品 (4本目から)。

参考にした政治解説チャンネルの画づくりに寄せる:
- 背景は写真を白黒寄りにして粒子を足した「資料映像」風 (archive)。抽象的な光の粒は減らす
- 文字は太い明朝に黒い太縁と影 (tel)。金・赤は強調だけ
- 人物や用語は、左下の「名前」札と小さな説明 (card)
- 仕組みの説明は、白黒写真の上に黒いピクトグラム (pict)
- 冒頭の登場人物紹介は、文字が流れる背景 (code_rain) にネオン色の名前
- 当時の新聞の見出しを再現した切り抜き (paper)
"""
from __future__ import annotations

import random

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import look as L

W, H = L.W, L.H
SERIF = "NotoSerifJP-Black.ttf"
SANS = "NotoSansJP-Black.ttf"
RED = (214, 38, 32)
GOLD = L.GOLD
WHITE = L.WHITE


# ---- 文字 --------------------------------------------------------------------
def _outline(im, px=10, shadow=True):
    """文字の外側に黒い太縁と、右下へ落ちる影をつける"""
    a = im.split()[3]
    pad = px * 2 + 16
    big = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
    big.paste(a, (pad, pad))
    edge = big.filter(ImageFilter.MaxFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", big.size, (0, 0, 0, 0))
    if shadow:
        sh = big.filter(ImageFilter.MaxFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(10))
        layer = Image.new("RGBA", big.size, (0, 0, 0, 0))
        layer.putalpha(sh.point(lambda v: v * 0.85))
        out.alpha_composite(layer, (8, 10))
    black = Image.new("RGBA", big.size, (0, 0, 0, 0))
    black.putalpha(edge)
    out.alpha_composite(black)
    out.alpha_composite(im, (pad, pad))
    return out


def tel(s, size=120, color=WHITE, px=10):
    """テロップ: 太い明朝 + 黒い太縁 + 影"""
    return _outline(L.text(s, SERIF, size, color, glow=False, pad=10), px)


def tel_gold(s, size=140, px=10):
    """金のグラデーションの明朝 + 黒い太縁 (数字や大事な言葉)"""
    return _outline(L.gold(s, SERIF, size), px)


def tel_red(s, size=140, px=10):
    """赤い明朝 + 黒い太縁 (事件・処分など強い言葉)。少し暗い赤を下に重ねて立体的に"""
    base = L.text(s, SERIF, size, (120, 10, 10), glow=False, pad=10)
    top = L.text(s, SERIF, size, RED, glow=False, pad=10)
    im = Image.new("RGBA", (base.width + 6, base.height + 6), (0, 0, 0, 0))
    im.alpha_composite(base, (5, 5))
    im.alpha_composite(top, (0, 0))
    return _outline(im, px)


def caption(s, size=64):
    """「小泉内閣」のようなかぎかっこつきの白い明朝 (名前や用語の見出し)"""
    return tel(f"「{s}」", size, WHITE, 7)


def card(name, lines=(), sub=None, w=None):
    """左下に置く「名前」札と説明。sub は名前の上の小さな字 (年や肩書き)"""
    head = tel(f"「{name}」", 64, WHITE, 6)
    small = L.font(SANS, 30)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    lw = max([d0.textlength(x, font=small) for x in lines] + [0])
    subim = tel(sub, 34, GOLD, 4) if sub else None
    bw = round(lw + 50) if lines else 0
    w = w or head.width + (bw + 20 if lines else 0)
    hh = head.height + (subim.height - 24 if subim else 0)
    im = Image.new("RGBA", (w, max(hh, 60 + 42 * len(lines))), (0, 0, 0, 0))
    y0 = 0
    if subim:
        im.alpha_composite(subim, (max(0, (head.width - subim.width) // 2), 0))
        y0 = subim.height - 30
    im.alpha_composite(head, (0, y0))
    if lines:
        x = head.width + 4
        bh = 34 + 42 * len(lines)
        by = y0 + (head.height - bh) // 2
        box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        d.rectangle((0, 0, bw - 1, bh - 1), fill=(10, 10, 12, 190), outline=(200, 200, 200, 160), width=2)
        for i, t in enumerate(lines):
            d.text((24, 17 + i * 42), t, font=small, fill=WHITE)
        im.alpha_composite(box, (x, max(0, by)))
    return im


# ---- 背景 --------------------------------------------------------------------
def _grain(im, amount=18, seed=0):
    rng = np.random.default_rng(seed)
    a = np.asarray(im).astype(np.int16)
    n = rng.normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))


def archive(name, focus=(0.5, 0.4), tint=(1.0, 0.97, 0.9), bright=0.62, seed=0, color=0.0):
    """資料映像風の写真背景: ほぼ白黒、強めのコントラスト、粒子"""
    pw, ph = round(W * 1.18), round(H * 1.18)
    im = L.cover(L.photo(name), pw, ph, focus)
    im = ImageEnhance.Color(im).enhance(color)
    im = ImageEnhance.Contrast(im).enhance(1.35)
    im = ImageEnhance.Brightness(im).enhance(bright)
    a = np.asarray(im).astype(np.float32) * np.array(tint, dtype=np.float32)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return _grain(im, 16, seed)


def archive_or(name, fallback_seed, **kw):
    """写真があれば資料映像風、なければ文字の流れる暗い背景"""
    if L.has(name) if hasattr(L, "has") else (L.IMG / name).exists():
        return archive(name, seed=fallback_seed, **kw)
    return code_rain(fallback_seed, (90, 90, 96))


KANJI = "八百長賭博敗退行為永久追放球団選手金円万告白国会逮捕霧黒契約協約処分口止料野球西鉄投手"


def code_rain(seed=0, color=(60, 230, 120), dim=0.55):
    """文字が縦に流れる背景 (登場人物紹介用)。動きは Ken Burns に任せる"""
    pw, ph = round(W * 1.18), round(H * 1.18)
    rng = random.Random(seed)
    im = Image.new("RGB", (pw, ph), (6, 6, 8))
    d = ImageDraw.Draw(im)
    f = L.font(SERIF, 30)
    for x in range(10, pw, 36):
        y = rng.randrange(-400, 0)
        n = rng.randrange(8, 34)
        for k in range(n):
            a = (k + 1) / n
            c = tuple(round(v * a * dim * rng.uniform(0.6, 1.0)) for v in color)
            d.text((x, y + k * 36), rng.choice(KANJI), font=f, fill=c)
    return im.filter(ImageFilter.GaussianBlur(0.6))


def dark(seed=0):
    """写真を使わない場面の背景: 粒子の入った暗い紙のような地"""
    pw, ph = round(W * 1.18), round(H * 1.18)
    yy = np.linspace(0, 1, ph)[:, None]
    xx = np.linspace(-1, 1, pw)[None, :]
    v = 30 - 18 * (xx ** 2) - 10 * yy
    im = Image.fromarray(np.clip(np.stack([v * 1.05, v, v * 0.95], -1), 0, 255).astype(np.uint8))
    return _grain(im, 10, seed)


# ---- 図 ----------------------------------------------------------------------
def _icon(kind, s=190):
    """黒いピクトグラム (白い縁つき)。kind: person / group / money / ball / paper / cuffs"""
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = (12, 12, 14, 255)

    def person(cx, sc=1.0):
        u = s / 150
        r = 22 * sc * u
        cy = (38 * sc) * u
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=k)
        d.rounded_rectangle((cx - 38 * sc * u, 66 * sc * u, cx + 38 * sc * u, 150 * sc * u), radius=int(24 * sc * u), fill=k)

    if kind == "person":
        person(s / 2)
    elif kind == "group":
        for cx, sc in ((s * 0.25, 0.8), (s * 0.75, 0.8), (s / 2, 0.95)):
            person(cx, sc)
    elif kind == "money":
        d.ellipse((18, 40, s - 18, s - 6), fill=k)
        d.polygon([(s / 2 - 26, 44), (s / 2 + 26, 44), (s / 2 + 40, 14), (s / 2 - 40, 14)], fill=k)
        f = L.font(SERIF, 64)
        d.text((s / 2, s * 0.64), "¥", font=f, fill=(240, 240, 240, 255), anchor="mm")
    elif kind == "ball":
        d.ellipse((10, 10, s - 10, s - 10), fill=k)
        d.arc((-40, 20, 60, s - 20), -50, 50, fill=(240, 240, 240, 255), width=5)
        d.arc((s - 60, 20, s + 40, s - 20), 130, 230, fill=(240, 240, 240, 255), width=5)
    elif kind == "paper":
        d.rectangle((30, 10, s - 30, s - 10), fill=k)
        for y in range(40, s - 30, 22):
            d.line((48, y, s - 48, y), fill=(220, 220, 220, 255), width=6)
    elif kind == "cuffs":
        d.ellipse((10, 40, 80, 110), outline=k, width=16)
        d.ellipse((s - 80, 40, s - 10, 110), outline=k, width=16)
        d.line((78, 75, s - 78, 75), fill=k, width=12)
    a = im.split()[3]
    edge = a.filter(ImageFilter.MaxFilter(9))
    out = Image.new("RGBA", (s + 10, s + 10), (0, 0, 0, 0))
    white = Image.new("RGBA", (s, s), (235, 235, 235, 0))
    white.putalpha(edge)
    out.alpha_composite(white, (5, 5))
    out.alpha_composite(im, (5, 5))
    return out


def pict(steps, hi=None, gap=110):
    """ピクトグラムの流れ図。steps = [(kind, 文字), ...]。hi 番目の文字を赤く"""
    icons = [_icon(k) for k, _ in steps]
    labels = [tel(t, 46, RED if i == hi else WHITE, 5) for i, (_, t) in enumerate(steps)]
    cw = max(max(i.width for i in icons), max(lb.width for lb in labels))
    w = cw * len(steps) + gap * (len(steps) - 1)
    h = icons[0].height + max(lb.height for lb in labels) - 10
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    arrow = tel("→", 90, WHITE, 6)
    for i, (ic, lb) in enumerate(zip(icons, labels)):
        x = i * (cw + gap)
        im.alpha_composite(ic, (x + (cw - ic.width) // 2, 0))
        im.alpha_composite(lb, (x + (cw - lb.width) // 2, ic.height - 20))
        if i < len(steps) - 1:
            im.alpha_composite(arrow, (x + cw + (gap - arrow.width) // 2, ic.height // 2 - arrow.height // 2))
    return im


def paper(headline, sub=None, date=None, w=560):
    """当時の新聞の見出しを再現した切り抜き (縦書きの太い見出し)"""
    f = L.font(SERIF, 80)
    fs = L.font(SERIF, 38)
    cols = [headline[i:i + 7] for i in range(0, len(headline), 7)]  # 7字ずつ右から縦に並べる
    rows = len(headline)
    w = max(w, 110 * len(cols) + (90 if sub else 0) + 120)
    h = 90 * min(7, rows) + 150
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    paper_ = Image.new("RGB", (w, h), (226, 218, 196))
    paper_ = _grain(paper_, 9, len(headline))
    d = ImageDraw.Draw(paper_)
    x = w - 90
    for col in cols:
        for i, c in enumerate(col):
            d.text((x, 50 + i * 90), c, font=f, fill=(20, 18, 16), anchor="mt")
        x -= 110
    if sub:
        for i, c in enumerate(sub[:14]):
            d.text((x - 10, 60 + i * 44), c, font=fs, fill=(40, 36, 32), anchor="mt")
    if date:
        d.text((30, h - 50), date, font=L.font(SERIF, 30), fill=(60, 56, 50))
    # 縁を少し不揃いにして切り抜きらしく
    m = Image.new("L", (w, h), 255)
    md = ImageDraw.Draw(m)
    rng = random.Random(rows)
    for y in range(0, h, 12):
        md.rectangle((0, y, rng.randrange(0, 8), y + 12), fill=0)
        md.rectangle((w - rng.randrange(0, 8), y, w, y + 12), fill=0)
    im.paste(paper_.convert("RGBA"), (0, 0), m)
    im = im.rotate(2.5, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
    s2 = Image.new("RGBA", im.size, (0, 0, 0, 0))
    s2.putalpha(im.split()[3].point(lambda v: v * 0.6))
    sh.alpha_composite(s2.filter(ImageFilter.GaussianBlur(12)), (18, 22))
    sh.alpha_composite(im, (0, 0))
    return sh


# ---- 写真の代わりに場面ごとに描く絵 (同じ写真を何度も使わないため) -------------------
def _table(seed=0, tone=(38, 30, 24)):
    """木の机のような暗い地 (札束や書類を置く)"""
    pw, ph = round(W * 1.18), round(H * 1.18)
    rng = np.random.default_rng(seed)
    y = np.arange(ph)[:, None]
    x = np.arange(pw)[None, :]
    grain = (np.sin(y / 5.0 + np.sin(x / 260.0) * 2 + seed) * 0.5 + 0.5) * 5
    base = np.stack([tone[0] + grain, tone[1] + grain * 0.8, tone[2] + grain * 0.6], -1)
    base += rng.normal(0, 4, base.shape[:2])[..., None]
    vign = 1 - 0.55 * (((x - pw / 2) / (pw / 2)) ** 2 + ((y - ph / 2) / (ph / 2)) ** 2)
    return Image.fromarray(np.clip(base * vign[..., None], 0, 255).astype(np.uint8))


def _bill(w=300, h=150, seed=0):
    """札束の1つ (実在の紙幣の図柄は使わず、色と帯だけの札)"""
    im = Image.new("RGBA", (w, h + 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    for k in range(9, -1, -1):  # 横から見た札の重なり
        c = 196 + rng.randrange(-8, 8)
        d.rectangle((k * 1.2, 26 - k * 2.4, w - 1 - k * 1.2, h + 26 - k * 2.4), fill=(c, c - 8, c - 34, 255),
                    outline=(120, 110, 80, 255))
    d.rectangle((0, 2, w - 1, h + 2), fill=(206, 198, 160, 255), outline=(110, 100, 70, 255), width=2)
    d.ellipse((w * 0.62, h * 0.25 + 2, w * 0.9, h * 0.8 + 2), outline=(150, 140, 100, 255), width=3)
    d.rectangle((w * 0.42, 2, w * 0.56, h + 2), fill=(250, 248, 240, 255), outline=(150, 140, 100, 255))  # 帯
    return im


def money(label="100万円", n=1, sub=None, seed=0):
    """札束を積んだ絵 + 金額。n は束の数 (半端は 0.5 束)"""
    full, half = int(n), n - int(n) >= 0.5
    cnt = full + (1 if half else 0)
    cols = min(cnt, 3)
    rows = (cnt + cols - 1) // cols
    bw, bh = 420, 246
    im = Image.new("RGBA", (cols * (bw - 60) + 120, rows * (bh - 110) + 160 + 230), (0, 0, 0, 0))
    k = 0
    for r in range(rows):
        for c in range(cols):
            if k >= cnt:
                break
            b = _bill(bw, 210, seed + k)
            if half and k == cnt - 1:
                b = b.crop((0, 0, bw, bh)).resize((bw, bh))
                b.putalpha(b.split()[3].point(lambda v: v * 0.55))
            im.alpha_composite(b, (c * (bw - 60) + (r % 2) * 60, im.height - 230 - bh - r * (bh - 110)))
            k += 1
    t = tel_gold(label, 130)
    im2 = Image.new("RGBA", (max(im.width, t.width), im.height), (0, 0, 0, 0))
    im2.alpha_composite(im, ((im2.width - im.width) // 2, 0))
    im2.alpha_composite(t, ((im2.width - t.width) // 2, im.height - t.height + 10))
    if sub:
        s = tel(sub, 44, WHITE, 5)
        out = Image.new("RGBA", (max(im2.width, s.width), im2.height + s.height - 20), (0, 0, 0, 0))
        out.alpha_composite(im2, ((out.width - im2.width) // 2, 0))
        out.alpha_composite(s, ((out.width - s.width) // 2, im2.height - 30))
        return out
    return im2


def document(title, body, mark=None, w=1000, h=620):
    """書類の1ページ (協約の条文など)。mark に含まれる文を赤い線で強調"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pg = _grain(Image.new("RGB", (w, h), (236, 232, 220)), 7, 3)
    d = ImageDraw.Draw(pg)
    ft = L.font(SERIF, 46)
    fb = L.font(SERIF, 34)
    d.text((60, 50), title, font=ft, fill=(20, 20, 20))
    d.line((60, 115, w - 60, 115), fill=(60, 60, 60), width=2)
    y = 150
    import textwrap
    for para in body:
        for line in textwrap.wrap(para, 26):
            if mark and any(m in para for m in mark):
                d.rectangle((52, y - 4, w - 52, y + 44), fill=(244, 206, 200))
            d.text((60, y), line, font=fb, fill=(25, 25, 25))
            y += 52
        y += 14
    im.paste(pg.convert("RGBA"), (0, 0))
    im = im.rotate(-1.5, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", (im.width + 40, im.height + 40), (0, 0, 0, 0))
    s2 = Image.new("RGBA", im.size, (0, 0, 0, 0))
    s2.putalpha(im.split()[3].point(lambda v: v * 0.6))
    sh.alpha_composite(s2.filter(ImageFilter.GaussianBlur(14)), (20, 24))
    sh.alpha_composite(im, (0, 0))
    return sh


# 日本のおおまかな形 (地図の絵用、緯度経度の粗い輪郭)
_JP = {
    "hokkaido": [(141.0, 41.4), (140.0, 42.5), (139.9, 43.2), (141.4, 43.3), (141.7, 45.4), (142.3, 45.3), (143.8, 44.2),
                 (145.3, 44.3), (145.6, 43.3), (144.0, 42.9), (143.2, 42.0), (141.8, 42.6)],
    "honshu": [(141.4, 41.5), (141.5, 40.5), (142.0, 39.5), (141.0, 38.3), (140.9, 37.0), (140.6, 36.0), (140.8, 35.7),
               (139.8, 34.9), (139.0, 34.7), (138.2, 34.6), (137.0, 34.6), (136.8, 34.3), (135.8, 33.4), (135.1, 33.9),
               (135.2, 34.6), (134.0, 34.6), (132.5, 34.2), (131.0, 33.9), (130.9, 34.4), (132.0, 35.4), (133.5, 35.5),
               (135.3, 35.6), (136.0, 35.8), (136.7, 36.9), (137.3, 36.8), (138.4, 37.4), (139.4, 38.2), (139.9, 39.9),
               (140.0, 40.7), (140.3, 41.3)],
    "shikoku": [(132.5, 33.0), (133.0, 32.8), (134.2, 33.3), (134.7, 33.8), (134.5, 34.2), (133.6, 34.4), (132.7, 34.0)],
    "kyushu": [(130.9, 33.9), (131.9, 33.4), (131.7, 32.5), (131.3, 31.4), (130.7, 31.0), (130.2, 31.3), (130.6, 32.0),
               (130.0, 32.6), (129.6, 33.2), (130.1, 33.7)],
}
CITY = {"福岡": (130.4, 33.6), "大阪": (135.5, 34.7), "東京": (139.7, 35.7), "札幌": (141.35, 43.06), "所沢": (139.47, 35.8),
        "名古屋": (136.9, 35.2), "下関": (130.94, 33.96)}


def japan(points=(), route=None, w=900, h=1000, hi=None):
    """日本の地図の絵。points に都市名、route に (出発, 到着) を渡すと線を引く"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lon0, lon1, lat0, lat1 = 128.8, 146.2, 30.5, 45.8

    def xy(p):
        return ((p[0] - lon0) / (lon1 - lon0) * w, (lat1 - p[1]) / (lat1 - lat0) * h)

    for poly in _JP.values():
        d.polygon([xy(p) for p in poly], fill=(70, 70, 74, 230), outline=(200, 200, 200, 255))
    if route:
        a, b = xy(CITY[route[0]]), xy(CITY[route[1]])
        for k in range(0, 40, 2):  # 点線
            t0, t1 = k / 40, (k + 1) / 40
            d.line((a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0, a[0] + (b[0] - a[0]) * t1,
                    a[1] + (b[1] - a[1]) * t1), fill=RED + (255,), width=7)
    f = L.font(SERIF, 44)
    for name in points:
        x, y = xy(CITY[name])
        col = RED if name == hi else GOLD
        d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=col + (255,), outline=(0, 0, 0, 255), width=3)
        d.text((x + 22, y - 30), name, font=f, fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0, 255))
    return im


def standings(rows, w=1300, h=560, title=None):
    """順位の推移 (rows = [(年, 順位, 強調)]、6球団)。下に行くほど悪い"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = L.font(SERIF, 40)
    top, bot = 70, h - 80
    for r in range(1, 7):
        y = top + (r - 1) * (bot - top) / 5
        d.line((120, y, w - 40, y), fill=(255, 255, 255, 60), width=2)
        d.text((40, y - 24), f"{r}位", font=f, fill=(200, 200, 200, 255))
    pts = []
    for i, (yr, rank, hi) in enumerate(rows):
        x = 200 + i * (w - 300) / max(1, len(rows) - 1)
        y = top + (rank - 1) * (bot - top) / 5
        pts.append((x, y))
        d.text((x, h - 50), yr, font=f, fill=(230, 230, 230, 255), anchor="mm")
    d.line(pts, fill=RED + (255,), width=8, joint="curve")
    for (x, y), (_, rank, hi) in zip(pts, rows):
        d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(RED if hi else GOLD) + (255,), outline=(0, 0, 0, 255), width=3)
    if title:
        d.text((w // 2, 20), title, font=L.font(SERIF, 44), fill=(255, 255, 255, 255), anchor="mt")
    return im


def signatures(count="18万7787人", seed=0, w=1100, h=640):
    """署名用紙が重なった絵 + 人数"""
    rng = random.Random(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for k in range(5):
        pg = Image.new("RGBA", (520, 640), (232, 228, 214, 255))
        d = ImageDraw.Draw(pg)
        d.text((30, 24), "署名用紙", font=L.font(SERIF, 34), fill=(30, 30, 30, 255))
        for r in range(14):
            y = 90 + r * 38
            d.line((30, y + 30, 490, y + 30), fill=(150, 150, 150, 255), width=1)
            x = 40
            while x < 440:  # 手書きの名前のような線
                n = rng.randrange(3, 8)
                pts = [(x + i * 9, y + 14 + rng.randrange(-9, 9)) for i in range(n)]
                d.line(pts, fill=(30, 40, 90, 255), width=2)
                x += n * 9 + rng.randrange(20, 60)
        pg = pg.rotate(rng.uniform(-8, 8), expand=True, resample=Image.BICUBIC)
        im.alpha_composite(pg.resize((round(pg.width * 0.75), round(pg.height * 0.75))),
                           (60 + k * 110, rng.randrange(0, 60)))
    t = tel_gold(count, 120)
    im.alpha_composite(t, ((w - t.width) // 2, h - t.height))
    return im


def silhouette(name, sub=None, color=(150, 30, 30), seed=0):
    """写真のない人物: 黒い人影に名前 (人物紹介用)"""
    im = Image.new("RGBA", (620, 760), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((210, 60, 410, 290), fill=(8, 8, 10, 255))
    d.rounded_rectangle((90, 300, 530, 760), radius=160, fill=(8, 8, 10, 255))
    glow = im.split()[3].filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(18))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    g = Image.new("RGBA", im.size, color + (0,))
    g.putalpha(glow.point(lambda v: v * 0.9))
    out.alpha_composite(g)
    out.alpha_composite(im)
    q = tel("?", 220, (200, 200, 200), 6)
    out.alpha_composite(q, ((out.width - q.width) // 2, 70))
    return out


def tv(lines, w=900, h=640):
    """昭和のブラウン管テレビの絵。画面に lines の文字"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w, h - 60), radius=40, fill=(70, 52, 36, 255), outline=(20, 14, 10, 255), width=6)
    d.rounded_rectangle((50, 50, w - 220, h - 110), radius=60, fill=(20, 30, 28, 255))
    rng = np.random.default_rng(1)
    noise = Image.fromarray((rng.random((h - 160, w - 270)) * 60).astype(np.uint8))
    im.paste(Image.merge("RGBA", (noise, noise, noise, noise.point(lambda v: 90))), (50, 50),
             Image.new("L", noise.size, 0).point(lambda v: 255))
    sm = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sm).rounded_rectangle((50, 50, w - 220, h - 110), radius=60, fill=255)
    f = L.font(SERIF, 54)
    for i, t in enumerate(lines):
        d.text(((w - 170) // 2, 160 + i * 80), t, font=f, fill=(235, 240, 230, 255), anchor="mm")
    for k in range(2):
        d.ellipse((w - 170, 120 + k * 120, w - 70, 220 + k * 120), fill=(40, 30, 22, 255), outline=(15, 10, 8, 255), width=5)
    d.rectangle((140, h - 60, 220, h), fill=(40, 30, 22, 255))
    d.rectangle((w - 300, h - 60, w - 220, h), fill=(40, 30, 22, 255))
    return im


def stamp(s, color=RED, size=150):
    """判子のような四角い印 (処分・却下など)"""
    t = L.text(s, SERIF, size, color, glow=False, pad=20)
    im = Image.new("RGBA", (t.width + 40, t.height + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, im.width - 6, im.height - 6), radius=18, outline=color + (255,), width=12)
    im.alpha_composite(t, (20, 10))
    im = im.rotate(-8, expand=True, resample=Image.BICUBIC)
    a = np.asarray(im).copy()
    rng = np.random.default_rng(2)
    a[..., 3] = (a[..., 3] * (rng.random(a.shape[:2]) > 0.12)).astype(np.uint8)  # かすれ
    return Image.fromarray(a, "RGBA")


def compose(base, *items):
    """背景 base() の上に絵を置いた、Ken Burns 用の背景を作る。
    items = (fn, x, y): (x, y) は画面 (1920x1080) での中心の位置。背景は 1.18 倍なので位置を合わせる"""
    im = base().convert("RGBA")
    ox, oy = (im.width - W) / 2, (im.height - H) / 2
    for fn, x, y in items:
        sp = fn()
        im.alpha_composite(sp, (round(ox + x - sp.width / 2), round(oy + y - sp.height / 2)))
    return im.convert("RGB")
