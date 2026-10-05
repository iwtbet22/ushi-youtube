"""背景ビジュアルをコードで生成する。

実写/CG素材の代わりに、暗めのシネマティックな静止画を1枚ずつ作り、
render.py 側でゆっくりズーム(ケン・バーンズ)させて映像に見せる。
各関数は (BW, BH) の RGB 画像を返す。BW/BH は出力より少し大きい。
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from style import RED, font

BW, BH = 2112, 1188


def _rng(seed):
    return np.random.default_rng(seed)


def _noise(shape, scale, seed):
    """低周波ノイズ (粗い乱数を拡大)"""
    r = _rng(seed)
    small = r.random((max(2, shape[0] // scale), max(2, shape[1] // scale)))
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255


def _to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _glow(im, radius, gain=1.0):
    g = im.filter(ImageFilter.GaussianBlur(radius))
    a = np.asarray(im, dtype=np.float32) + np.asarray(g, dtype=np.float32) * gain
    return _to_img(a)


def _vgrad(top, bottom, h=BH, w=BW):
    t = np.linspace(0, 1, h)[:, None, None]
    return np.broadcast_to(np.array(top) * (1 - t) + np.array(bottom) * t, (h, w, 3)).copy()


# ---- 夜のスタジアム ------------------------------------------------------
def stadium(seed=1, warm=False):
    a = _vgrad((6, 10, 26), (2, 3, 8))
    yy, xx = np.mgrid[0:BH, 0:BW]
    # フィールド(楕円の芝)
    field = ((xx - BW / 2) / (BW * 0.75)) ** 2 + ((yy - BH * 1.25) / (BH * 0.62)) ** 2 < 1
    stripes = (np.sin(xx / 70.0) > 0) * 0.15 + 0.85
    a[field] = (np.array([14, 58, 24]) * stripes[field][:, None])
    # スタンド(観客のざらつき)
    stand = (yy > BH * 0.42) & ~field
    crowd = _noise((BH, BW), 3, seed) * 0.6 + _rng(seed).random((BH, BW)) * 0.4
    a[stand] = (np.array([28, 26, 34]) * crowd[stand][:, None] * 1.4)
    im = _to_img(a)
    d = ImageDraw.Draw(im)
    # 照明塔
    lights = Image.new("RGB", (BW, BH))
    ld = ImageDraw.Draw(lights)
    tint = (255, 210, 150) if warm else (210, 230, 255)
    for cx in (BW * 0.12, BW * 0.38, BW * 0.62, BW * 0.88):
        cy = BH * 0.16 + abs(cx - BW / 2) * 0.08
        d.line([(cx, cy + 60), (cx + (BW / 2 - cx) * 0.05, BH * 0.45)], fill=(20, 22, 30), width=12)
        for i in range(6):
            for j in range(3):
                x, y = cx - 75 + i * 30, cy + j * 26
                ld.ellipse((x - 9, y - 9, x + 9, y + 9), fill=tint)
    lights = lights.filter(ImageFilter.GaussianBlur(2))
    im = _to_img(np.asarray(im, np.float32) + np.asarray(lights, np.float32))
    im = _glow(im, 60, 1.6)
    # もや
    haze = _noise((BH, BW), 160, seed + 7)[..., None] * np.array(tint) * 0.12
    out = np.asarray(im, np.float32) * 0.62 + haze
    lum = out.mean(axis=2, keepdims=True)
    out = lum + (out - lum) * 0.55  # 彩度を落としてシネマ調に
    return _to_img(out)


# ---- 光る野球ボール --------------------------------------------------------
def baseball(seed=2, rim=(120, 190, 255)):
    a = np.zeros((BH, BW, 3), np.float32)
    cx, cy, r = BW * 0.56, BH * 0.52, 360
    yy, xx = np.mgrid[0:BH, 0:BW]
    dx, dy = (xx - cx) / r, (yy - cy) / r
    d2 = dx * dx + dy * dy
    inside = d2 < 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    light = np.clip(dx * -0.5 + dy * -0.55 + nz * 0.65, 0, 1)
    leather = np.array([235, 228, 214]) * (0.12 + 0.88 * light[..., None] ** 1.6)
    a[inside] = leather[inside]
    rimmask = np.clip((d2 - 0.75) / 0.25, 0, 1) * inside * np.clip(dx * 0.7 + 0.5, 0, 1)
    a += rimmask[..., None] * np.array(rim) * 1.2
    im = _to_img(a)
    d = ImageDraw.Draw(im)
    for sgn in (-1, 1):  # 縫い目
        pts = []
        for k in range(60):
            t = -1.25 + 2.5 * k / 59
            x = cx + sgn * r * (0.62 - 0.32 * math.cos(t * 1.25))
            y = cy + r * 0.78 * math.sin(t)
            if (x - cx) ** 2 + (y - cy) ** 2 < (r * 0.96) ** 2:
                pts.append((x, y))
        for i, (x, y) in enumerate(pts[::2]):
            ang = math.atan2(y - cy, x - cx)
            ox, oy = 14 * math.cos(ang + sgn * 0.9), 14 * math.sin(ang + sgn * 0.9)
            shade = max(0.25, 1 - ((x - cx + r * 0.4) ** 2 + (y - cy + r * 0.4) ** 2) / (2.4 * r * r))
            col = tuple(int(c * shade) for c in (200, 24, 30))
            d.line([(x - ox, y - oy), (x + ox, y + oy)], fill=col, width=7)
    im = _glow(im, 40, 0.5)
    # 粒子
    r_ = _rng(seed)
    d = ImageDraw.Draw(im)
    for _ in range(140):
        x, y, s = r_.random() * BW, r_.random() * BH, r_.random() * 3 + 1
        v = int(r_.random() * 120 + 40)
        d.ellipse((x - s, y - s, x + s, y + s), fill=(v, v, int(v * 1.1)))
    return im.filter(ImageFilter.GaussianBlur(0.6))


# ---- 木の机と札束 ---------------------------------------------------------
def _wood(seed, tone=(70, 42, 24)):
    n = _noise((BH, BW // 8), 4, seed)
    n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).resize((BW, BH), Image.BICUBIC), np.float32) / 255
    grain = np.sin(np.linspace(0, 1, BH)[:, None] * 900 + n * 18) * 0.5 + 0.5
    v = 0.55 + 0.3 * grain + 0.25 * n
    return np.array(tone)[None, None, :] * v[..., None]


def _spot(a, cx, cy, rx, ry, gain=1.0, floor=0.08):
    yy, xx = np.mgrid[0:BH, 0:BW]
    m = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
    return a * (floor + gain * m[..., None])


def _bundle(d, x, y, w, h, depth, band=True, label="", shade=1.0):
    top = tuple(int(c * shade) for c in (214, 206, 180))
    side = tuple(int(c * shade) for c in (150, 140, 118))
    front = tuple(int(c * shade) for c in (178, 168, 140))
    d.polygon([(x, y), (x + w, y), (x + w + depth, y - depth * 0.6), (x + depth, y - depth * 0.6)], fill=top)
    d.rectangle((x, y, x + w, y + h), fill=front)
    d.polygon([(x + w, y), (x + w + depth, y - depth * 0.6), (x + w + depth, y + h - depth * 0.6), (x + w, y + h)], fill=side)
    for k in range(1, int(h / 4)):
        yy = y + k * 4
        d.line([(x, yy), (x + w, yy)], fill=tuple(int(c * 0.85) for c in front), width=1)
    if band:
        bx = x + w * 0.42
        bc = tuple(int(c * shade) for c in (238, 236, 228))
        d.rectangle((bx, y, bx + w * 0.16, y + h), fill=bc)
        d.polygon([(bx, y), (bx + w * 0.16, y), (bx + w * 0.16 + depth, y - depth * 0.6), (bx + depth, y - depth * 0.6)], fill=bc)


def money(seed=3, tint=None, n_rows=3):
    a = _wood(seed)
    a = _spot(a, BW * 0.55, BH * 0.45, BW * 0.45, BH * 0.55, 1.1)
    im = _to_img(a)
    d = ImageDraw.Draw(im)
    w, h, dep = 300, 64, 90
    for row in range(n_rows):
        for col in range(5):
            stack = 4 + (col * 7 + row * 3) % 4
            x = 420 + col * 300 - row * 60
            base = 1040 - row * 120
            for s in range(stack):
                shade = 0.45 + 0.55 * math.exp(-((x - BW * 0.55) / 900) ** 2 - ((base - BH * 0.5) / 700) ** 2)
                _bundle(d, x, base - s * h, w * 0.86, h - 4, dep, shade=shade)
    im = _glow(im, 30, 0.25)
    if tint is not None:
        arr = np.asarray(im, np.float32)
        lum = arr.mean(axis=2, keepdims=True)
        im = _to_img(lum * np.array(tint) / 255 * 0.95)
    return im


# ---- 契約書 ---------------------------------------------------------------
def contract(seed=4):
    a = _wood(seed, (46, 30, 20))
    a = _spot(a, BW * 0.5, BH * 0.4, BW * 0.5, BH * 0.6, 1.0)
    im = _to_img(a)
    paper = Image.new("RGBA", (1100, 1500), (238, 232, 218, 255))
    pd = ImageDraw.Draw(paper)
    pd.text((300, 90), "選 手 契 約 書", font=font("serif", 80), fill=(30, 30, 30))
    r = _rng(seed)
    y = 280
    for _ in range(22):
        ln = r.integers(500, 900)
        pd.rectangle((110, y, 110 + ln, y + 14), fill=(120, 116, 108))
        y += 46
    pd.text((110, 1300), "契約金", font=font("gothic_bold", 46), fill=(30, 30, 30))
    pd.text((300, 1288), "¥100,000,000", font=font("num", 64), fill=(30, 30, 30))
    pd.ellipse((840, 1250, 990, 1400), outline=(200, 30, 30), width=10)
    pd.text((868, 1282), "球団", font=font("serif", 46), fill=(200, 30, 30))
    paper = paper.rotate(-8, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", paper.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 160), (0, 0), paper.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    im.paste(sh, (560, 20), sh)
    im.paste(paper, (520, -40), paper)
    d = ImageDraw.Draw(im)
    # 万年筆
    d.line([(1350, 1020), (1800, 640)], fill=(16, 16, 20), width=46)
    d.line([(1350, 1020), (1560, 842)], fill=(170, 140, 70), width=10)
    d.polygon([(1336, 1030), (1360, 1006), (1300, 1070)], fill=(200, 170, 90))
    return _to_img(_spot(np.asarray(im, np.float32), BW * 0.45, BH * 0.45, BW * 0.5, BH * 0.6, 1.0, 0.2))


# ---- 赤黒フックカード -----------------------------------------------------
def red_hook(seed=5):
    yy, xx = np.mgrid[0:BH, 0:BW]
    rr = np.sqrt(((xx - BW * 0.66) / BW) ** 2 + ((yy - BH * 0.35) / BH) ** 2)
    base = np.clip(1.25 - rr * 1.7, 0, 1)[..., None] * np.array(RED) * 1.05
    im = _to_img(base)
    ink = Image.new("L", (BW, BH), 0)
    d = ImageDraw.Draw(ink)
    r = _rng(seed)
    for _ in range(26):  # 墨のしぶき
        x, y, s = r.random() * BW, r.random() * BH, r.random() * 160 + 20
        if 0.35 * BW < x < 0.9 * BW and y < 0.6 * BH:
            continue
        d.ellipse((x - s, y - s * 0.6, x + s, y + s * 0.6), fill=255)
    for _ in range(400):
        x, y, s = r.random() * BW, r.random() * BH, r.random() * 8 + 1
        d.ellipse((x - s, y - s, x + s, y + s), fill=255)
    d.polygon([(0, BH * 0.55), (BW, BH * 0.95), (BW, BH), (0, BH)], fill=255)
    ink = ink.filter(ImageFilter.GaussianBlur(3)).point(lambda v: 255 if v > 110 else 0)
    im.paste((6, 2, 2), (0, 0), ink)
    # 巨大なバットのシルエット + 光るエッジ
    bat = Image.new("L", (BW, BH), 0)
    bd = ImageDraw.Draw(bat)
    p0, p1 = np.array([BW * 0.18, BH * 0.08]), np.array([BW * 0.95, BH * 0.78])
    v = (p1 - p0) / np.linalg.norm(p1 - p0)
    nrm = np.array([-v[1], v[0]])
    L = np.linalg.norm(p1 - p0)
    poly_l, poly_r = [], []
    for k in range(41):
        t = k / 40
        wdt = 16 + 70 * (t ** 1.6)
        c = p0 + v * L * t
        poly_l.append(tuple(c + nrm * wdt))
        poly_r.append(tuple(c - nrm * wdt))
    bd.polygon(poly_l + poly_r[::-1], fill=255)
    im.paste((4, 0, 0), (0, 0), bat)
    edge = Image.new("RGB", (BW, BH))
    ed = ImageDraw.Draw(edge)
    ed.line([poly_l[6], poly_l[-1]], fill=(255, 255, 255), width=10)
    im = _to_img(np.asarray(im, np.float32) + np.asarray(edge.filter(ImageFilter.GaussianBlur(14)), np.float32) * 3
                 + np.asarray(edge, np.float32))
    return im


# ---- 方眼紙 (図解の背景) ---------------------------------------------------
def grid_paper(seed=6):
    a = np.ones((BH, BW, 3), np.float32) * np.array([226, 224, 216])
    a *= (0.93 + 0.07 * _noise((BH, BW), 400, seed))[..., None]
    im = _to_img(a)
    d = ImageDraw.Draw(im)
    for x in range(0, BW, 44):
        d.line([(x, 0), (x, BH)], fill=(186, 188, 186), width=3 if x % 220 == 0 else 1)
    for y in range(0, BH, 44):
        d.line([(0, y), (BW, y)], fill=(186, 188, 186), width=3 if y % 220 == 0 else 1)
    return _to_img(_spot(np.asarray(im, np.float32), BW / 2, BH / 2, BW * 0.8, BH * 0.8, 0.75, 0.3))


# ---- お年玉のポチ袋が並ぶ机 (たとえ話) -------------------------------------
def envelopes(seed=7):
    a = _wood(seed, (52, 36, 26))
    im = _to_img(_spot(a, BW / 2, BH * 0.5, BW * 0.6, BH * 0.6, 1.0))
    d = ImageDraw.Draw(im)
    f = font("serif", 40)
    for row in range(3):
        for col in range(7):
            x, y = 150 + col * 270 + row * 40, 140 + row * 320
            hl = (row, col) == (1, 3)
            c = (236, 230, 220) if not hl else (255, 246, 214)
            d.rectangle((x + 10, y + 12, x + 210, y + 272), fill=(18, 12, 8))
            d.rectangle((x, y, x + 200, y + 260), fill=c)
            d.rectangle((x, y + 190, x + 200, y + 222), fill=(196, 30, 40))
            d.polygon([(x, y), (x + 200, y), (x + 100, y + 60)], fill=tuple(int(v * 0.9) for v in c))
            d.text((x + 42, y + 96), "お年玉", font=f, fill=(176, 24, 32))
    return _glow(im, 26, 0.2)


# ---- 無人のスタンド --------------------------------------------------------
def seats(seed=8):
    a = _vgrad((10, 12, 20), (2, 2, 4))
    im = _to_img(a)
    d = ImageDraw.Draw(im)
    for row in range(26):
        t = row / 25
        y = BH * 0.25 + (t ** 1.7) * BH * 0.8
        h = 6 + t * 46
        sp = 30 + t * 80
        x = -sp * (row % 2) / 2
        col = int(24 + 40 * t)
        while x < BW:
            d.rounded_rectangle((x, y, x + sp * 0.8, y + h), radius=int(h / 3), fill=(col, int(col * 0.4), int(col * 0.5)))
            x += sp
    a = _spot(np.asarray(im, np.float32), BW * 0.7, BH * 0.55, BW * 0.18, BH * 0.4, 2.2, 0.25)
    im = _to_img(a)
    beam = Image.new("RGB", (BW, BH))
    ImageDraw.Draw(beam).polygon([(BW * 0.66, 0), (BW * 0.74, 0), (BW * 0.86, BH), (BW * 0.54, BH)], fill=(60, 60, 70))
    return _to_img(np.asarray(im, np.float32) + np.asarray(beam.filter(ImageFilter.GaussianBlur(60)), np.float32))


# ---- 火花の散る暗い鉄骨 (キーワード「上限」用) ------------------------------
def sparks(seed=9):
    a = _vgrad((12, 14, 20), (4, 4, 6))
    im = _to_img(a)
    d = ImageDraw.Draw(im)
    for k in range(-3, 6):  # 鉄骨
        x = k * 420
        d.line([(x, 0), (x + 700, BH)], fill=(40, 44, 52), width=60)
        d.line([(x + 700, 0), (x, BH)], fill=(30, 33, 40), width=36)
    sp = Image.new("RGB", (BW, BH))
    sd = ImageDraw.Draw(sp)
    r = _rng(seed)
    for _ in range(260):
        x, y = r.random() * BW, BH * (0.3 + r.random() * 0.7)
        ang = r.random() * math.pi
        ln = r.random() * 50 + 10
        sd.line([(x, y), (x + math.cos(ang) * ln, y - math.sin(ang) * ln)], fill=(255, int(140 + r.random() * 100), 40), width=3)
    im = _to_img(np.asarray(im, np.float32) + np.asarray(sp, np.float32))
    return _glow(im, 16, 1.0)


def blackout():
    return Image.new("RGB", (BW, BH), (0, 0, 0))


GENERATORS = {
    "black": blackout,
    "stadium": stadium,
    "stadium_warm": lambda: stadium(11, warm=True),
    "baseball": baseball,
    "money": money,
    "money_red": lambda: money(13, tint=(255, 60, 50)),
    "money_dim": lambda: money(14, tint=(140, 150, 180)),
    "contract": contract,
    "red_hook": red_hook,
    "grid": grid_paper,
    "envelopes": envelopes,
    "seats": seats,
    "sparks": sparks,
}
