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
