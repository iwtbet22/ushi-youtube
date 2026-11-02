"""4本目の背景用の小道具 (同じ絵を使い回さないため、場面ごとに中身の違う絵を作る)。

どれも透明な RGBA の絵を返す。news.compose で背景 (暗い地・机・写真) の上に置く。
実在の紙面や番組の見た目はまねず、「当時の雰囲気の再現イメージ」にとどめる。
"""
from __future__ import annotations

import datetime
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import look as L
import news as N

SERIF, SANS = N.SERIF, N.SANS
RED, GOLD, WHITE = N.RED, N.GOLD, N.WHITE
INK = (24, 22, 20)
PAPER = (236, 230, 214)
WEEK = "月火水木金土日"


def _shadow(im, r=16, dx=16, dy=22, a=0.6):
    out = Image.new("RGBA", (im.width + dx + r * 2, im.height + dy + r * 2), (0, 0, 0, 0))
    s = Image.new("RGBA", im.size, (0, 0, 0, 255))
    s.putalpha(im.split()[3].point(lambda v: v * a))
    out.alpha_composite(s.filter(ImageFilter.GaussianBlur(r)), (r + dx, r + dy))
    out.alpha_composite(im, (r, r))
    return out


def _paper(w, h, seed=0, tone=PAPER):
    return N._grain(Image.new("RGB", (w, h), tone), 8, seed).convert("RGBA")


def fit(fn, w, h):
    """絵を w x h に収まるよう縮める (拡大はしない)"""
    im = fn()
    k = min(w / im.width, h / im.height, 1.0)
    return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS) if k < 1 else im


def print_photo(name, w=760, rot=-3, focus=(0.5, 0.4), aspect=0.75):
    """白い縁のついた古い焼き付け写真 (小さい写真を全画面に引き伸ばさず、写真のまま見せる)"""
    h = round(w * aspect)
    ph = L.cover(L.photo(name), w, h, focus).convert("L").convert("RGB")
    ph = N._grain(ph, 12, 3)
    b = 26
    im = Image.new("RGBA", (w + b * 2, h + b * 2 + 40), (238, 234, 222, 255))
    im.paste(ph, (b, b))
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    return _shadow(im)


def bills(n=1, seed=0):
    """札束だけ (金額の字なし)"""
    cnt = max(1, round(n))
    cols = min(cnt, 4)
    rows = (cnt + cols - 1) // cols
    bw, bh = 420, 236
    im = Image.new("RGBA", (cols * (bw - 70) + 140, rows * 120 + bh + 20), (0, 0, 0, 0))
    k = 0
    for r in range(rows):
        for c in range(cols):
            if k < cnt:
                im.alpha_composite(N._bill(bw, 210, seed + k), (c * (bw - 70) + (r % 2) * 50, im.height - bh - r * 120))
                k += 1
    return _shadow(im, 10, 8, 12, 0.7)


def envelope(label="", seed=0, opened=False):
    """茶封筒 (お金の受け渡し)。opened なら札がのぞく"""
    w, h = 820, 480
    im = Image.new("RGBA", (w, h + 120), (0, 0, 0, 0))
    if opened:
        b = N._bill(500, 220, seed).rotate(4, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(b, (150, 0))
    env = _paper(w, h, seed, (176, 140, 92))
    d = ImageDraw.Draw(env)
    d.polygon([(0, 0), (w, 0), (w // 2, h * 0.42)], fill=(160, 124, 80, 255), outline=(110, 84, 50, 255))
    if label:
        d.text((w // 2, h * 0.7), label, font=L.font(SERIF, 70), fill=INK + (255,), anchor="mm")
    im.alpha_composite(env, (0, 120))
    return _shadow(im.rotate(-4, expand=True, resample=Image.BICUBIC))


def calendar(y, m, d, note=None):
    """日めくりカレンダー (その日の曜日つき)"""
    w, h = 560, 640
    im = _paper(w, h, m * 31 + d, (244, 242, 234))
    dr = ImageDraw.Draw(im)
    wd = datetime.date(y, m, d).weekday()
    col = RED if wd == 6 else INK
    dr.rectangle((0, 0, w, 120), fill=(150, 26, 24, 255))
    dr.text((w // 2, 60), f"昭和{y - 1925}年  {y}" if y < 1989 else f"{y}年", font=L.font(SERIF, 48),
            fill=(255, 245, 230, 255), anchor="mm")
    dr.text((w // 2, 190), f"{m}月", font=L.font(SERIF, 70), fill=INK + (255,), anchor="mm")
    dr.text((w // 2, 380), str(d), font=L.font(SERIF, 280), fill=col + (255,), anchor="mm")
    dr.text((w // 2, 560), f"{WEEK[wd]}曜日", font=L.font(SERIF, 54), fill=col + (255,), anchor="mm")
    for x in range(40, w, 60):  # 綴じ穴
        dr.ellipse((x, 8, x + 16, 24), fill=(60, 20, 20, 255))
    im = _shadow(im.rotate(3, expand=True, resample=Image.BICUBIC))
    if note:
        t = N.tel(note, 60, WHITE, 6)
        out = Image.new("RGBA", (max(im.width, t.width), im.height + t.height), (0, 0, 0, 0))
        out.alpha_composite(im, ((out.width - im.width) // 2, 0))
        out.alpha_composite(t, ((out.width - t.width) // 2, im.height - 10))
        return out
    return im


def scoreboard(rows, title=None):
    """昔の手書きのスコアボード風の黒板 (rows = [(左の字, 右の字), ...])"""
    w = 1100
    h = 140 + 130 * len(rows) + (90 if title else 0)
    im = Image.new("RGBA", (w, h), (20, 46, 34, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=(200, 190, 150, 255), width=14)
    y = 70
    if title:
        d.text((w // 2, y + 10), title, font=L.font(SERIF, 56), fill=(240, 230, 200, 255), anchor="mm")
        y += 90
    for a, b in rows:
        d.text((80, y + 60), a, font=L.font(SERIF, 72), fill=(245, 245, 235, 255), anchor="lm")
        d.text((w - 80, y + 60), b, font=L.font(SERIF, 96), fill=(255, 214, 90, 255), anchor="rm")
        y += 130
    return _shadow(N._grain(im.convert("RGB"), 10, 5).convert("RGBA"))


def mics(n=7, seed=0):
    """会見の机に並んだマイク"""
    rng = random.Random(seed)
    w, h = 1500, 620
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, h - 120, w, h), fill=(70, 50, 36, 255))  # 机
    d.rectangle((0, h - 130, w, h - 118), fill=(120, 90, 60, 255))
    for k in range(n):
        x = 160 + k * (w - 320) / max(1, n - 1) + rng.randrange(-20, 20)
        top = 120 + rng.randrange(0, 160)
        ang = rng.uniform(-0.25, 0.25)
        bx, by = x, h - 125
        tx, ty = x + (by - top) * ang * 0.3, top
        d.line((bx, by, tx, ty + 60), fill=(30, 30, 32, 255), width=14)
        d.rounded_rectangle((tx - 32, ty - 40, tx + 32, ty + 70), radius=30, fill=(40, 40, 44, 255),
                            outline=(140, 140, 150, 255), width=4)
        c = rng.choice([(200, 40, 40), (40, 80, 180), (230, 200, 60), (60, 160, 90), (220, 220, 220)])
        d.rectangle((tx - 36, ty + 70, tx + 36, ty + 120), fill=c + (255,))
    return im


def notebook(lines, seed=0):
    """記者の取材ノート (手書き風の字)"""
    w = 980
    h = 180 + 92 * len(lines)
    im = _paper(w, h, seed, (240, 236, 220))
    d = ImageDraw.Draw(im)
    for y in range(120, h, 92):
        d.line((40, y + 70, w - 40, y + 70), fill=(150, 170, 200, 255), width=2)
    d.line((110, 0, 110, h), fill=(220, 120, 120, 255), width=3)
    f = L.font("YujiBoku-Regular.ttf", 58)
    for i, t in enumerate(lines):
        d.text((140, 120 + i * 92), t, font=f, fill=(30, 36, 80, 255))
    return _shadow(im.rotate(2, expand=True, resample=Image.BICUBIC))


def poster(title, name, sub=None):
    """「たずね人」の貼り紙 (顔は人影)"""
    w, h = 640, 860
    im = _paper(w, h, 7, (232, 224, 200))
    d = ImageDraw.Draw(im)
    d.text((w // 2, 90), title, font=L.font(SERIF, 96), fill=INK + (255,), anchor="mm")
    d.rectangle((120, 170, w - 120, 560), fill=(40, 38, 36, 255))
    d.ellipse((240, 220, 400, 380), fill=(12, 12, 12, 255))
    d.rounded_rectangle((180, 390, 460, 600), radius=90, fill=(12, 12, 12, 255))
    d.rectangle((120, 560, w - 120, 600), fill=(232, 224, 200, 255))
    d.text((w // 2, 680), name, font=L.font(SERIF, 80), fill=INK + (255,), anchor="mm")
    if sub:
        d.text((w // 2, 780), sub, font=L.font(SERIF, 40), fill=(80, 60, 50, 255), anchor="mm")
    return _shadow(im.rotate(-2, expand=True, resample=Image.BICUBIC))


def magazine(lines, seed=0):
    """週刊誌の表紙のような、大きな見出しの並ぶ紙 (特定の雑誌の見た目ではない)"""
    w, h = 760, 1000
    im = _paper(w, h, seed, (250, 248, 240))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 170), fill=(200, 30, 30, 255))
    d.text((w // 2, 85), "週刊誌", font=L.font(SERIF, 100), fill=(255, 255, 255, 255), anchor="mm")
    y = 220
    for i, t in enumerate(lines):
        col = RED if i == 0 else INK
        size = 116 if i == 0 else 88
        d.text((50, y), t, font=L.font(SERIF, size), fill=col + (255,))
        y += size + 40
    return _shadow(im.rotate(-3, expand=True, resample=Image.BICUBIC))


def fog(seed=0, tint=(1.0, 1.0, 1.0), dark=0.9):
    """黒い霧 (背景そのもの)。ゆっくり流れて見えるよう大きめの雲模様"""
    pw, ph = round(N.W * 1.18), round(N.H * 1.18)
    rng = np.random.default_rng(seed)
    acc = np.zeros((ph, pw), np.float32)
    for k, amp in [(8, 1.0), (16, 0.5), (32, 0.25), (64, 0.12)]:
        g = rng.random((k * ph // pw + 2, k + 2)).astype(np.float32)
        acc += amp * np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((pw, ph), Image.BICUBIC),
                                np.float32) / 255
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    v = 8 + acc ** 1.6 * 70 * dark
    rgb = np.stack([v * tint[0], v * tint[1], v * tint[2]], -1)
    return N._grain(Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)), 8, seed)


def snow(seed=0):
    """雪の夜 (札幌)"""
    im = fog(seed, (0.8, 0.9, 1.15), 0.7).convert("RGBA")
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    for _ in range(700):
        x, y, r = rng.randrange(im.width), rng.randrange(im.height), rng.choice([2, 3, 3, 4, 6])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 245, 255, rng.randrange(120, 230)))
    return im.filter(ImageFilter.GaussianBlur(0.8)).convert("RGB")


def tally(total=10, ok=2):
    """丸とバツの表 (試みた回数と、うまくいった回数)"""
    s, gap = 150, 30
    cols = 5
    rows = (total + cols - 1) // cols
    im = Image.new("RGBA", (cols * (s + gap) + 40, rows * (s + gap) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(total):
        x, y = 20 + (k % cols) * (s + gap), 20 + (k // cols) * (s + gap)
        d.rounded_rectangle((x, y, x + s, y + s), radius=20, fill=(20, 20, 22, 230), outline=(200, 200, 200, 255),
                            width=4)
        if k < ok:
            d.ellipse((x + 22, y + 22, x + s - 22, y + s - 22), outline=GOLD + (255,), width=18)
        else:
            d.line((x + 30, y + 30, x + s - 30, y + s - 30), fill=RED + (255,), width=18)
            d.line((x + s - 30, y + 30, x + 30, y + s - 30), fill=RED + (255,), width=18)
    return im


def ledger(rows, total, seed=0):
    """借金の帳簿 (rows = [(項目, 金額)]、最後に赤字の合計)"""
    w = 1000
    h = 200 + 80 * len(rows) + 120
    im = _paper(w, h, seed, (238, 232, 212))
    d = ImageDraw.Draw(im)
    d.text((w // 2, 70), "帳簿", font=L.font(SERIF, 64), fill=INK + (255,), anchor="mm")
    d.line((50, 130, w - 50, 130), fill=INK + (255,), width=3)
    f = L.font(SERIF, 46)
    y = 160
    for a, b in rows:
        d.text((70, y), a, font=f, fill=INK + (255,))
        d.text((w - 70, y), b, font=f, fill=INK + (255,), anchor="ra")
        y += 80
    d.line((50, y + 10, w - 50, y + 10), fill=INK + (255,), width=3)
    d.text((70, y + 40), "差し引き", font=L.font(SERIF, 56), fill=INK + (255,))
    d.text((w - 70, y + 40), total, font=L.font(SERIF, 64), fill=(190, 20, 20, 255), anchor="ra")
    return _shadow(im.rotate(-2, expand=True, resample=Image.BICUBIC))


def people(n=15, hi=6, cols=8, seed=0):
    """人のピクトグラムを並べる (hi 人を赤く)"""
    s = 130
    rows = (n + cols - 1) // cols
    im = Image.new("RGBA", (cols * s + 20, rows * (s + 40) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(n):
        x, y = 10 + (k % cols) * s, 10 + (k // cols) * (s + 40)
        c = RED if k < hi else (200, 200, 200)
        d.ellipse((x + 40, y, x + 90, y + 50), fill=c + (255,))
        d.rounded_rectangle((x + 20, y + 58, x + 110, y + 160), radius=34, fill=c + (255,))
    return im


def neon(s="BAR", color=(255, 70, 160)):
    """夜の店のネオン看板"""
    t = L.text(s, "DelaGothicOne-Regular.ttf", 260, (255, 235, 245), glow=False, pad=60)
    a = t.split()[3]
    glow = Image.new("RGBA", t.size, color + (0,))
    glow.putalpha(a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(26)))
    out = Image.new("RGBA", t.size, (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(glow)
    out.alpha_composite(t)
    return out


def wall_notes(lines, seed=0):
    """壁いっぱいの寄せ書き (ファンの励ましのイメージ)"""
    rng = random.Random(seed)
    w, h = 1600, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    f = L.font("YujiBoku-Regular.ttf", 44)
    for k in range(34):
        t = lines[k % len(lines)]
        c = rng.choice([(250, 240, 170), (240, 200, 210), (200, 230, 250), (230, 240, 210), (250, 250, 245)])
        pw, ph = rng.randrange(300, 420), rng.randrange(150, 210)
        pg = _paper(pw, ph, k, c)
        ImageDraw.Draw(pg).text((20, 30), t, font=f, fill=(30, 30, 60, 255))
        pg = pg.rotate(rng.uniform(-10, 10), expand=True, resample=Image.BICUBIC)
        im.alpha_composite(pg, (rng.randrange(-40, w - 260), rng.randrange(-30, h - 140)))
    return im


def timeline(a, b, label, note=None):
    """2つの年をつなぐ長い矢印 (a 年 → b 年、間に label)"""
    w, h = 1500, 360
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((150, 180, w - 190, 180), fill=(220, 220, 220, 255), width=10)
    d.polygon([(w - 190, 140), (w - 120, 180), (w - 190, 220)], fill=(220, 220, 220, 255))
    for x, t in [(150, a), (w - 190, b)]:
        d.ellipse((x - 26, 154, x + 26, 206), fill=GOLD + (255,), outline=(0, 0, 0, 255), width=4)
        d.text((x, 270), t, font=L.font(SERIF, 64), fill=(255, 255, 255, 255), anchor="mm", stroke_width=5,
               stroke_fill=(0, 0, 0, 255))
    lt = N.tel_gold(label, 110)
    im.alpha_composite(lt, ((w - lt.width) // 2, 0))
    if note:
        d.text((w // 2, 330), note, font=L.font(SERIF, 40), fill=(200, 200, 200, 255), anchor="mm")
    return im


def phone(lines):
    """スマートフォンの画面 (オンラインカジノのイメージ。実在のサイトではない)"""
    w, h = 520, 960
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w, h), radius=70, fill=(18, 18, 20, 255), outline=(120, 120, 130, 255), width=6)
    d.rounded_rectangle((26, 90, w - 26, h - 90), radius=30, fill=(40, 10, 60, 255))
    rng = random.Random(3)
    for k in range(3):  # スロットの窓
        x = 60 + k * 140
        d.rounded_rectangle((x, 330, x + 120, 500), radius=16, fill=(250, 240, 220, 255))
        d.text((x + 60, 415), rng.choice(["7", "♦", "★"]), font=L.font(SERIF, 90), fill=(200, 20, 40, 255),
               anchor="mm")
    for i, t in enumerate(lines):
        d.text((w // 2, 200 + i * 0 if i == 0 else 600 + i * 80), t, font=L.font(SERIF, 54 if i == 0 else 44),
               fill=(255, 220, 90, 255) if i == 0 else (240, 240, 240, 255), anchor="mm")
    return _shadow(im.rotate(-6, expand=True, resample=Image.BICUBIC))


def stamp_on(fn, s, color=RED, size=170, dx=120, dy=60):
    """絵の上に判子を押す"""
    im = fn().copy()
    st = N.stamp(s, color, size)
    im.alpha_composite(st, (max(0, im.width // 2 - st.width // 2 + dx), max(0, im.height // 2 - st.height // 2 + dy)))
    return im


def silhouette_name(name, sub=None, color=(150, 30, 30)):
    """人影 + 下に名前 (写真のない人物)"""
    s = N.silhouette(name, sub, color)
    t = N.tel(name, 80, WHITE, 7)
    out = Image.new("RGBA", (max(s.width, t.width), s.height + t.height - 40), (0, 0, 0, 0))
    out.alpha_composite(s, ((out.width - s.width) // 2, 0))
    out.alpha_composite(t, ((out.width - t.width) // 2, s.height - 40))
    if sub:
        u = N.tel(sub, 44, (220, 220, 220), 5)
        o2 = Image.new("RGBA", (max(out.width, u.width), out.height + u.height - 10), (0, 0, 0, 0))
        o2.alpha_composite(out, ((o2.width - out.width) // 2, 0))
        o2.alpha_composite(u, ((o2.width - u.width) // 2, out.height - 10))
        return o2
    return out


def profile(name, sub=None, photo=None, color=(200, 170, 90), rot=-2.0, focus=(0.5, 0.3), seed=0):
    """人物カード: 左に顔写真 (なければその人の色の人影)、右に名前と肩書き。名前だけの札より「誰か」が伝わる"""
    pw, ph_ = (330, 400) if photo is not False else (0, 220)
    if photo is False:
        face = None
    elif photo:
        face = L.cover(L.photo(photo), pw, ph_, focus).convert("L").convert("RGB")
        face = N._grain(face, 12, seed + 3).convert("RGBA")
    else:
        face = Image.new("RGBA", (pw, ph_), (0, 0, 0, 255))
        g = Image.new("RGB", (pw, ph_), tuple(int(c * 0.35) for c in color))
        m = Image.radial_gradient("L").resize((pw, ph_)).point(lambda v: 255 - v)
        face.paste(g, (0, 0), m)
        s = N.silhouette("", None, color, seed)
        s = s.resize((round(s.width * 0.56), round(s.height * 0.56)), Image.LANCZOS)
        face.alpha_composite(s, ((pw - s.width) // 2, ph_ - s.height + 40))
    nm = N.tel(name, 92 if len(name) <= 5 else 76, WHITE, 6)
    sb = N.tel(sub, 44, GOLD, 4) if sub else None
    tw = max(nm.width, sb.width if sb else 0)
    b = 18
    w, h = pw + b * 2 + 40 + tw + 30, ph_ + b * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=(14, 14, 16, 235))
    d.rectangle((0, 0, 9, h - 1), fill=color + (255,))
    if face is not None:
        d.rectangle((b - 4, b - 4, b + pw + 3, b + ph_ + 3), fill=(232, 226, 210, 255))
        im.alpha_composite(face, (b, b))
    x = b + pw + 40 if face is not None else 50
    y = h // 2 - (nm.height + (sb.height - 16 if sb else 0)) // 2
    im.alpha_composite(nm, (x, y))
    if sb:
        d.line((x + 10, y + nm.height - 4, x + tw - 10, y + nm.height - 4), fill=color + (200,), width=3)
        im.alpha_composite(sb, (x, y + nm.height + 4))
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    return _shadow(im)
