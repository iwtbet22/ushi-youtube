"""オリジナルのフラットイラスト (すべてコードで描画)。

画風: こげ茶の線(太め) + ベタ塗り + 丸いパーツ。2倍で描いて縮小しアンチエイリアス。
各関数は RGBA スプライトを返す。
"""
from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

from ui import INK, RED, font

LINE = (60, 44, 36)
SKIN = (255, 222, 196)
CHEEK = (250, 170, 160)
S = 2  # スーパーサンプリング倍率


def _canvas(w, h):
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _done(im):
    return im.resize((im.width // S, im.height // S), Image.LANCZOS)


def _p(*v):
    return [x * S for x in v]


def _ell(d, box, fill, lw=5):
    d.ellipse(_p(*box), fill=fill, outline=LINE, width=lw * S)


def _rr(d, box, r, fill, lw=5):
    d.rounded_rectangle(_p(*box), radius=r * S, fill=fill, outline=LINE, width=lw * S)


def _poly(d, pts, fill, lw=5):
    pts = [(x * S, y * S) for x, y in pts]
    d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=LINE, width=lw * S, joint="curve")


def _line(d, pts, w=5, fill=LINE):
    d.line([(x * S, y * S) for x, y in pts], fill=fill, width=w * S, joint="curve")


# ---- 顔 -----------------------------------------------------------------------
def _face(d, cx, cy, r, mood="normal", hair=(50, 40, 36), cap=None, hair_style="short"):
    if hair_style == "long":
        _rr(d, (cx - r * 1.05, cy - r * 0.6, cx + r * 1.05, cy + r * 1.25), int(r * 0.5), hair)
    _ell(d, (cx - r, cy - r, cx + r, cy + r), SKIN)
    if cap:
        # 野球帽: つば + 帽子本体
        _poly(d, [(cx - r * 0.2, cy - r * 0.35), (cx + r * 1.35, cy - r * 0.25), (cx + r * 1.3, cy - r * 0.05), (cx - r * 0.1, cy - r * 0.1)], cap, 4)
        d.chord(_p(cx - r * 1.02, cy - r * 1.08, cx + r * 1.02, cy + r * 0.5), 180, 360, fill=cap, outline=LINE, width=4 * S)
    elif hair_style in ("short", "long"):
        d.chord(_p(cx - r * 1.03, cy - r * 1.06, cx + r * 1.03, cy + r * 0.45), 180, 360, fill=hair, outline=LINE, width=4 * S)
        _poly(d, [(cx - r * 0.95, cy - r * 0.2), (cx - r * 0.3, cy - r * 0.55), (cx + r * 0.2, cy - r * 0.25), (cx + r * 0.95, cy - r * 0.3),
                  (cx + r * 0.8, cy - r * 0.8), (cx - r * 0.8, cy - r * 0.8)], hair, 0)
    elif hair_style == "buzz":
        d.chord(_p(cx - r * 1.0, cy - r * 1.02, cx + r * 1.0, cy + r * 0.2), 180, 360, fill=(90, 80, 76), outline=LINE, width=4 * S)
    ey = cy + r * 0.1
    ex = r * 0.38
    if mood == "happy":
        for sx in (-1, 1):
            d.arc(_p(cx + sx * ex - 10, ey - 6, cx + sx * ex + 10, ey + 10), 200, 340, fill=LINE, width=4 * S)
    else:
        for sx in (-1, 1):
            d.ellipse(_p(cx + sx * ex - 6, ey - 8, cx + sx * ex + 6, ey + 8), fill=LINE)
    if mood == "worried":
        for sx in (-1, 1):
            _line(d, [(cx + sx * (ex - 12), ey - 26), (cx + sx * (ex + 12), ey - 18 - (6 if sx > 0 else -6) * 0 - 10)], 4)
    for sx in (-1, 1):
        d.ellipse(_p(cx + sx * r * 0.62 - 12, cy + r * 0.38 - 7, cx + sx * r * 0.62 + 12, cy + r * 0.38 + 7), fill=CHEEK)
    my = cy + r * 0.5
    if mood == "happy":
        d.chord(_p(cx - 16, my - 12, cx + 16, my + 14), 0, 180, fill=(200, 70, 70), outline=LINE, width=3 * S)
    elif mood == "surprised":
        _ell(d, (cx - 9, my - 6, cx + 9, my + 16), (200, 70, 70), 3)
    elif mood == "worried":
        d.arc(_p(cx - 14, my, cx + 14, my + 20), 200, 340, fill=LINE, width=4 * S)
    else:
        d.arc(_p(cx - 13, my - 10, cx + 13, my + 8), 20, 160, fill=LINE, width=4 * S)


# ---- 人物 ---------------------------------------------------------------------
@lru_cache(maxsize=None)
def person(kind="player", mood="normal", color=(30, 70, 160), letter="", w=300, h=520, pose="normal"):
    """kind: player(ユニフォーム) / suit(スーツ) / gakuran(学ラン) / staff(スーツ+バインダー)
    pose: normal / point(右を指す) / cheer(両手を上げる) / think(あごに手)"""
    im, d = _canvas(w, h)
    cx = w / 2
    head_r = 74
    hy = 100
    # 脚
    leg = (235, 235, 238) if kind == "player" else (50, 54, 70)
    _rr(d, (cx - 52, 330, cx - 8, 470), 14, leg)
    _rr(d, (cx + 8, 330, cx + 52, 470), 14, leg)
    if kind == "player":  # ストッキング
        _rr(d, (cx - 52, 410, cx - 8, 470), 10, color)
        _rr(d, (cx + 8, 410, cx + 52, 470), 10, color)
    _rr(d, (cx - 62, 455, cx - 4, 492), 16, (40, 40, 46))
    _rr(d, (cx + 4, 455, cx + 62, 492), 16, (40, 40, 46))
    # 胴体
    body = {"player": (246, 246, 248), "suit": (54, 62, 86), "staff": (54, 62, 86), "gakuran": (34, 34, 44)}[kind]
    _rr(d, (cx - 82, 168, cx + 82, 350), 46, body)
    # 腕
    for sx in (-1, 1):
        ax = cx + sx * 82
        if pose == "cheer":
            _line(d, [(ax, 200), (ax + sx * 40, 110)], 44, LINE)
            _line(d, [(ax, 200), (ax + sx * 40, 110)], 34, body)
            _ell(d, (ax + sx * 40 - 22, 70, ax + sx * 40 + 22, 114), SKIN, 4)
        elif pose == "point" and sx > 0:
            _line(d, [(ax - 10, 210), (ax + 100, 200)], 44, LINE)
            _line(d, [(ax - 10, 210), (ax + 100, 200)], 34, body)
            _ell(d, (ax + 92, 182, ax + 132, 218), SKIN, 4)
        elif pose == "think" and sx > 0:
            _line(d, [(ax, 200), (ax - 30, 290), (cx + 20, 196)], 40, LINE)
            _line(d, [(ax, 200), (ax - 30, 290), (cx + 20, 196)], 30, body)
            _ell(d, (cx, 160, cx + 40, 200), SKIN, 4)
        else:
            _rr(d, (ax - 24, 182, ax + 24, 320), 22, body)
            _ell(d, (ax - 20, 300, ax + 20, 340), SKIN, 4)
    if kind == "player":
        _line(d, [(cx, 172), (cx, 346)], 3, (200, 200, 205))
        if letter:
            tx = ImageDraw.Draw(im)
            fl = font("label", 64 * S)
            lw = tx.textlength(letter, font=fl)
            tx.text(((cx * S) - lw / 2, 205 * S), letter, font=fl, fill=color)
        for sx in (-1, 1):
            _line(d, [(cx + sx * 82 - 22, 230), (cx + sx * 82 + 22, 230)], 6, color)
    elif kind in ("suit", "staff"):
        _poly(d, [(cx - 30, 172), (cx, 230), (cx + 30, 172)], (250, 250, 250), 3)
        _poly(d, [(cx - 9, 182), (cx + 9, 182), (cx + 12, 262), (cx, 276), (cx - 12, 262)], color, 3)
    elif kind == "gakuran":
        for k in range(4):
            d.ellipse(_p(cx - 7, 200 + k * 36, cx + 7, 214 + k * 36), fill=(230, 190, 60))
        _rr(d, (cx - 40, 164, cx + 40, 186), 6, (34, 34, 44), 4)
    if kind == "staff" and pose == "normal":  # バインダー
        _rr(d, (cx + 40, 230, cx + 124, 340), 8, (250, 246, 230), 4)
        for k in range(4):
            _line(d, [(cx + 54, 256 + k * 20), (cx + 110, 256 + k * 20)], 3, (150, 150, 160))
    cap = color if kind == "player" else None
    style = "buzz" if kind == "gakuran" else "short"
    _face(d, cx, hy, head_r, mood, cap=cap, hair_style=style)
    return _done(im)


# ---- 建物 ---------------------------------------------------------------------
def _windows(d, x0, y0, cols, rows, ww, wh, gx, gy, col=(170, 210, 240)):
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * (ww + gx), y0 + r * (wh + gy)
            d.rectangle(_p(x, y, x + ww, y + wh), fill=col, outline=LINE, width=3 * S)


@lru_cache(maxsize=None)
def building(kind="company", w=360, h=420):
    """company(会社) / highschool(高校) / university(大学) / office(球団事務所)"""
    im, d = _canvas(w, h)
    if kind == "company":
        _rr(d, (60, 30, w - 60, h - 10), 10, (120, 170, 220))
        _windows(d, 90, 60, 4, 7, 34, 30, 20, 18)
        _rr(d, (w / 2 - 34, h - 80, w / 2 + 34, h - 10), 6, (80, 110, 150), 4)
    elif kind == "highschool":
        _rr(d, (20, 140, w - 20, h - 10), 8, (246, 236, 214))
        _rr(d, (w / 2 - 60, 60, w / 2 + 60, 160), 8, (246, 236, 214))
        _ell(d, (w / 2 - 34, 76, w / 2 + 34, 144), (255, 255, 255), 4)
        _line(d, [(w / 2, 110), (w / 2, 88)], 4)
        _line(d, [(w / 2, 110), (w / 2 + 16, 118)], 4)
        _windows(d, 44, 176, 6, 3, 34, 34, 13, 26, (180, 220, 245))
        _rr(d, (w / 2 - 30, h - 70, w / 2 + 30, h - 10), 6, (150, 120, 90), 4)
    elif kind == "university":
        _poly(d, [(w / 2, 20), (w - 30, 120), (30, 120)], (170, 70, 60))
        _rr(d, (40, 120, w - 40, h - 10), 6, (214, 120, 96))
        for k in range(5):
            x = 70 + k * ((w - 140) / 4)
            _rr(d, (x - 12, 150, x + 12, h - 40), 4, (250, 240, 228), 3)
        _rr(d, (30, h - 40, w - 30, h - 10), 4, (240, 226, 210), 4)
    elif kind == "office":
        _rr(d, (50, 120, w - 50, h - 10), 8, (236, 236, 240))
        _windows(d, 80, 150, 5, 4, 30, 34, 14, 22, (180, 210, 240))
        _line(d, [(w / 2, 120), (w / 2, 20)], 5)
        _poly(d, [(w / 2, 22), (w / 2 + 90, 44), (w / 2, 66)], RED, 4)
    return _done(im)


@lru_cache(maxsize=None)
def stadium(w=560, h=300):
    im, d = _canvas(w, h)
    _ell(d, (20, 90, w - 20, h - 10), (110, 180, 90))
    d.chord(_p(20, 90, w - 20, h - 10), 180, 360, fill=(150, 156, 170), outline=LINE, width=5 * S)
    _ell(d, (w / 2 - 60, 170, w / 2 + 60, 250), (210, 170, 110), 4)
    for x in (70, w - 70):
        _line(d, [(x, 110), (x, 20)], 6)
        _rr(d, (x - 32, 6, x + 32, 40), 6, (255, 246, 190), 4)
    return _done(im)


# ---- 小物 ---------------------------------------------------------------------
@lru_cache(maxsize=None)
def money(n=3, w=320, h=260):
    """札束を n 段積んだもの (実在の紙幣は描かない)"""
    im, d = _canvas(w, h)
    for k in range(n):
        y = h - 70 - k * 46
        _rr(d, (30, y, w - 30, y + 60), 8, (226, 214, 170), 4)
        _rr(d, (w / 2 - 26, y - 2, w / 2 + 26, y + 62), 4, (250, 250, 246), 3)
        f = font("label", 30 * S)
        ImageDraw.Draw(im).text(((w / 2 - 9) * S, (y + 10) * S), "¥", font=f, fill=(120, 100, 60))
    return _done(im)


@lru_cache(maxsize=None)
def contract(w=280, h=340, amount=""):
    im, d = _canvas(w, h)
    _rr(d, (20, 10, w - 20, h - 10), 8, (255, 255, 250))
    f = font("label", 34 * S)
    ImageDraw.Draw(im).text((70 * S, 30 * S), "契約書", font=f, fill=INK)
    for k in range(5):
        _line(d, [(50, 100 + k * 32), (w - 50, 100 + k * 32)], 4, (180, 180, 190))
    if amount:
        fa = font("label", 30 * S)
        ImageDraw.Draw(im).text((50 * S, 262 * S), amount, font=fa, fill=RED)
    _ell(d, (w - 96, h - 96, w - 36, h - 36), (255, 255, 255), 4)
    ImageDraw.Draw(im).ellipse(_p(w - 92, h - 92, w - 40, h - 40), outline=RED, width=5 * S)
    return _done(im)


@lru_cache(maxsize=None)
def envelope(text="支度金", w=260, h=320):
    im, d = _canvas(w, h)
    _rr(d, (20, 10, w - 20, h - 10), 6, (255, 255, 255))
    _poly(d, [(20, 10), (w - 20, 10), (w / 2, 90)], (240, 240, 236), 4)
    d.rectangle(_p(20, h - 64, w - 20, h - 42), fill=RED)
    f = font("label", 40 * S)
    dd = ImageDraw.Draw(im)
    for i, ch in enumerate(text):
        dd.text(((w / 2 - 20) * S, (104 + i * 44) * S), ch, font=f, fill=INK)
    return _done(im)


@lru_cache(maxsize=None)
def ball(r=60):
    im, d = _canvas(r * 2 + 10, r * 2 + 10)
    _ell(d, (5, 5, r * 2 + 5, r * 2 + 5), (255, 255, 255))
    for sx in (-1, 1):
        cx = r + 5 + sx * r * 1.25
        d.arc(_p(cx - r, 5, cx + r, r * 2 + 5), 120 if sx > 0 else -60, 240 if sx > 0 else 60, fill=RED, width=4 * S)
    return _done(im)


@lru_cache(maxsize=None)
def mark(kind="ok", size=200):
    """ok=赤丸 / ng=青バツ / q=はてな / ex=びっくり"""
    im, d = _canvas(size, size)
    if kind == "ok":
        d.ellipse(_p(20, 20, size - 20, size - 20), outline=RED, width=26 * S)
    elif kind == "ng":
        for a, b in (((30, 30), (size - 30, size - 30)), ((size - 30, 30), (30, size - 30))):
            _line(d, [a, b], 28, (40, 100, 210))
    else:
        f = font("impact", int(size * 0.9) * S)
        ch = "？" if kind == "q" else "！"
        ImageDraw.Draw(im).text((size * 0.12 * S, -size * 0.08 * S), ch, font=f, fill=(240, 150, 30) if kind == "q" else RED,
                                stroke_width=8 * S, stroke_fill=(255, 255, 255))
    return _done(im)


@lru_cache(maxsize=None)
def calendar(text="3年", w=260, h=260):
    im, d = _canvas(w, h)
    _rr(d, (20, 30, w - 20, h - 10), 14, (255, 255, 255))
    d.rounded_rectangle(_p(20, 30, w - 20, 92), radius=14 * S, fill=RED)
    d.rectangle(_p(20, 70, w - 20, 92), fill=RED)
    d.rounded_rectangle(_p(20, 30, w - 20, h - 10), radius=14 * S, outline=LINE, width=5 * S)
    for x in (80, w - 80):
        _rr(d, (x - 10, 12, x + 10, 54), 8, (200, 200, 205), 4)
    f = font("label", 82 * S)
    dd = ImageDraw.Draw(im)
    tw = dd.textlength(text, font=f)
    dd.text((w / 2 * S - tw / 2, 108 * S), text, font=f, fill=INK)
    return _done(im)


@lru_cache(maxsize=None)
def gate(w=420, h=300):
    """「入口」を表すゲート (順位縛りの説明用)"""
    im, d = _canvas(w, h)
    _rr(d, (20, 40, 70, h - 10), 6, (200, 70, 60))
    _rr(d, (w - 70, 40, w - 20, h - 10), 6, (200, 70, 60))
    _rr(d, (0, 20, w, 70), 8, (230, 90, 70))
    return _done(im)


# ---- 図解用の小物 --------------------------------------------------------------
@lru_cache(maxsize=None)
def newspaper(head="スポーツ報", w=360, h=300):
    """新聞 (見出しは架空)"""
    im, d = _canvas(w, h)
    _rr(d, (16, 16, w - 16, h - 16), 6, (250, 248, 240))
    dd = ImageDraw.Draw(im)
    dd.text((40 * S, 30 * S), head, font=font("label", 44 * S), fill=INK)
    _line(d, [(36, 92), (w - 36, 92)], 4)
    _rr(d, (36, 108, 170, 250), 4, (200, 200, 205), 3)
    for k in range(6):
        _line(d, [(190, 116 + k * 24), (w - 40, 116 + k * 24)], 4, (170, 170, 178))
    return _done(im)


@lru_cache(maxsize=None)
def scale_balance(w=420, h=340):
    """天秤 (公平のイメージ)"""
    im, d = _canvas(w, h)
    _rr(d, (w / 2 - 70, h - 40, w / 2 + 70, h - 14), 8, (200, 160, 80))
    _rr(d, (w / 2 - 12, 70, w / 2 + 12, h - 36), 6, (220, 180, 90))
    _rr(d, (40, 60, w - 40, 84), 8, (220, 180, 90))
    for x in (70, w - 70):
        _line(d, [(x, 84), (x - 40, 190)], 4)
        _line(d, [(x, 84), (x + 40, 190)], 4)
        d.chord(_p(x - 60, 160, x + 60, 220), 0, 180, fill=(240, 210, 120), outline=LINE, width=5 * S)
    _ell(d, (w / 2 - 22, 40, w / 2 + 22, 84), (240, 200, 100))
    return _done(im)


@lru_cache(maxsize=None)
def lottery_box(w=360, h=320):
    """抽選箱 (上に手を入れる穴)"""
    im, d = _canvas(w, h)
    _rr(d, (30, 80, w - 30, h - 14), 10, (232, 60, 52))
    _poly(d, [(30, 80), (w - 30, 80), (w - 60, 40), (60, 40)], (250, 110, 96))
    _ell(d, (w / 2 - 70, 46, w / 2 + 70, 74), (60, 30, 30), 4)
    dd = ImageDraw.Draw(im)
    f = font("label", 54 * S)
    tw = dd.textlength("抽選", font=f)
    dd.text((w / 2 * S - tw / 2, 150 * S), "抽選", font=f, fill=(255, 255, 255))
    return _done(im)


@lru_cache(maxsize=None)
def lottery_card(text="交渉権確定", w=300, h=170):
    """抽選で引くカード"""
    im, d = _canvas(w, h)
    _rr(d, (10, 10, w - 10, h - 10), 10, (255, 255, 252))
    d.rectangle(_p(10, 10, w - 10, 44), fill=(214, 32, 40))
    dd = ImageDraw.Draw(im)
    f = font("label", 44 * S)
    tw = dd.textlength(text, font=f)
    dd.text((w / 2 * S - tw / 2, 70 * S), text, font=f, fill=(214, 32, 40))
    return _done(im)


@lru_cache(maxsize=None)
def form_paper(title="プロ野球志望届", w=320, h=400):
    """届出の用紙 (枠と記入欄だけの架空の書式)"""
    im, d = _canvas(w, h)
    _rr(d, (16, 10, w - 16, h - 10), 6, (255, 255, 250))
    dd = ImageDraw.Draw(im)
    f = font("label", 32 * S)
    tw = dd.textlength(title, font=f)
    dd.text((w / 2 * S - tw / 2, 30 * S), title, font=f, fill=INK)
    for k in range(5):
        y = 100 + k * 52
        d.rectangle(_p(40, y, w - 40, y + 38), outline=(150, 150, 160), width=3 * S)
    _ell(d, (w - 100, h - 90, w - 40, h - 30), (255, 255, 255), 4)
    dd.ellipse(_p(w - 96, h - 86, w - 44, h - 34), outline=RED, width=5 * S)
    return _done(im)


@lru_cache(maxsize=None)
def plane(w=300, h=160):
    """飛行機 (海外へ行くイメージ)"""
    im, d = _canvas(w, h)
    _rr(d, (30, 60, w - 20, 100), 20, (235, 240, 250))
    _poly(d, [(120, 70), (180, 70), (120, 10), (96, 10)], (120, 160, 220))
    _poly(d, [(120, 90), (180, 90), (120, 150), (96, 150)], (120, 160, 220))
    _poly(d, [(36, 70), (60, 70), (40, 30), (24, 30)], (120, 160, 220))
    for k in range(5):
        d.ellipse(_p(150 + k * 22, 72, 162 + k * 22, 84), fill=(120, 160, 220))
    return _done(im)


@lru_cache(maxsize=None)
def house(w=300, h=280):
    """家 (自由競争時代に契約金のほかに用意されたもののイメージ)"""
    im, d = _canvas(w, h)
    _poly(d, [(20, 130), (w / 2, 20), (w - 20, 130)], (200, 80, 60))
    _rr(d, (50, 120, w - 50, h - 14), 6, (250, 236, 210))
    _rr(d, (w / 2 - 30, h - 110, w / 2 + 30, h - 14), 4, (150, 100, 60), 4)
    d.rectangle(_p(76, 150, 126, 196), fill=(170, 210, 240), outline=LINE, width=3 * S)
    d.rectangle(_p(w - 126, 150, w - 76, 196), fill=(170, 210, 240), outline=LINE, width=3 * S)
    return _done(im)


@lru_cache(maxsize=None)
def letter(title="お願い", w=320, h=240):
    """封筒から出した手紙"""
    im, d = _canvas(w, h)
    _rr(d, (20, 60, w - 20, h - 10), 6, (245, 236, 214))
    _rr(d, (50, 10, w - 50, h - 60), 4, (255, 255, 252))
    dd = ImageDraw.Draw(im)
    f = font("label", 34 * S)
    tw = dd.textlength(title, font=f)
    dd.text((w / 2 * S - tw / 2, 30 * S), title, font=f, fill=INK)
    for k in range(3):
        _line(d, [(80, 100 + k * 24), (w - 80, 100 + k * 24)], 4, (170, 170, 178))
    return _done(im)
