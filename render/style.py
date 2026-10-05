"""デザインシステム: 色・フォント・テロップ部品。

参考動画から抽出した「型」(配置・配色・文字階層) を部品化したもの。
すべてのテロップは 1920x1080 の RGBA レイヤーとして返す。
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

# ---- カラートークン -------------------------------------------------------
SUB_FILL = (120, 22, 78, 215)        # 字幕ボックス: 深いマゼンタ
SUB_EDGE = (255, 236, 246, 235)      # 字幕ボックスの細い白枠
TEXT = (255, 255, 255, 255)
HIGHLIGHT = (255, 196, 40, 255)      # 強調語: 山吹
HIGHLIGHT_ALT = (120, 200, 255, 255)  # 強調語(サブ): 水色
TERM_LABEL = (92, 44, 20, 240)       # 用語ラベル: こげ茶
TERM_BOX = (8, 8, 10, 225)           # 用語説明: 墨
INK = (34, 28, 26, 255)              # 図解の墨色
RED = (214, 20, 28)


@lru_cache(maxsize=None)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    files = {
        "gothic": "NotoSansJP-Black.ttf",
        "gothic_bold": "NotoSansJP-Bold.ttf",
        "serif": "NotoSerifJP-Black.ttf",
        "kaku": "ZenKakuGothicNew-Black.ttf",
        "brush": "YujiSyuku-Regular.ttf",
        "num": "Oswald-Bold.ttf",
    }
    return ImageFont.truetype(str(FONT_DIR / files[name]), size)


def layer() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


# ---- リッチテキスト (【】で強調、《》で水色強調) -------------------------
def _runs(line: str):
    """'普通【強調】《別強調》' -> [(text, color), ...]"""
    out = []
    for tok in re.split(r"(【[^】]*】|《[^》]*》)", line):
        if not tok:
            continue
        if tok.startswith("【"):
            out.append((tok[1:-1], HIGHLIGHT))
        elif tok.startswith("《"):
            out.append((tok[1:-1], HIGHLIGHT_ALT))
        else:
            out.append((tok, TEXT))
    return out


def plain(line: str) -> str:
    return re.sub(r"[【】《》]", "", line)


def draw_rich(d: ImageDraw.ImageDraw, xy, line, f, stroke=3, stroke_fill=(0, 0, 0, 255)):
    x, y = xy
    for text, color in _runs(line):
        d.text((x, y), text, font=f, fill=color, stroke_width=stroke, stroke_fill=stroke_fill)
        x += d.textlength(text, font=f)


# ---- 部品1: 字幕ボックス (画面下部・マゼンタ) ----------------------------
def subtitle(text: str) -> Image.Image:
    im = layer()
    d = ImageDraw.Draw(im)
    f = font("gothic", 50)
    lines = text.split("\n")
    pad_x, pad_y, gap = 34, 18, 10
    lh = 62
    widths = [d.textlength(plain(l), font=f) for l in lines]
    bw = int(max(widths)) + pad_x * 2
    bh = lh * len(lines) + gap * (len(lines) - 1) + pad_y * 2
    x0 = 58
    y0 = H - 36 - bh
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=12, fill=SUB_FILL,
                        outline=SUB_EDGE, width=3)
    for i, l in enumerate(lines):
        draw_rich(d, (x0 + pad_x, y0 + pad_y - 8 + i * (lh + gap)), l, f, stroke=3)
    return im


# ---- 部品2: 用語ボックス (ラベル + 墨の説明帯) -----------------------------
def term(label: str, desc: str) -> Image.Image:
    im = layer()
    d = ImageDraw.Draw(im)
    fd = font("gothic_bold", 48)
    fl = font("gothic", 42)
    lines = desc.split("\n")
    lh = 60
    bw = max(int(max(d.textlength(plain(l), font=fd) for l in lines)) + 80, 1200)
    bh = lh * len(lines) + 50
    x0 = (W - bw) // 2
    y0 = H - 34 - bh
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=14, fill=TERM_BOX,
                        outline=(220, 220, 220, 200), width=2)
    for i, l in enumerate(lines):
        tw = d.textlength(plain(l), font=fd)
        draw_rich(d, ((W - tw) / 2, y0 + 22 + i * lh), l, fd, stroke=0)
    lw = int(d.textlength(label, font=fl)) + 70
    lx = (W - lw) // 2
    ly = y0 - 34
    d.rounded_rectangle((lx, ly, lx + lw, ly + 62), radius=31, fill=TERM_LABEL,
                        outline=(255, 230, 200, 230), width=3)
    d.text((lx + 35, ly + 3), label, font=fl, fill=TEXT)
    return im


# ---- 部品3: キーワードカード (中央に大きな単語) -----------------------------
def keyword(word: str, style: str = "white", pos: str = "center") -> Image.Image:
    """style='white': 白明朝+影 / 'fire': 橙グラデ+グロー"""
    im = layer()
    f = font("serif" if style == "white" else "kaku", 240 if len(word) <= 3 else 190)
    tmp = ImageDraw.Draw(im)
    tw = tmp.textlength(word, font=f)
    x = (W - tw) / 2 if pos == "center" else 120
    y = H / 2 - 170 if pos == "center" else H - 420

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((x, y), word, font=f, fill=255)

    if style == "white":
        shadow = mask.filter(ImageFilter.GaussianBlur(18)).point(lambda v: min(255, v * 2))
        im.paste((0, 0, 0, 230), (0, 0), shadow)
        im.paste((255, 255, 255, 255), (0, 0), mask)
        return im

    glow = mask.filter(ImageFilter.GaussianBlur(26))
    im.paste((255, 90, 0, 255), (0, 0), glow.point(lambda v: min(255, int(v * 1.6))))
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    top, bot = int(y), int(y + 300)
    for yy in range(H):
        t = min(1, max(0, (yy - top) / max(1, bot - top)))
        gd.line([(0, yy), (W, yy)], fill=(255, int(240 - 150 * t), int(170 - 170 * t), 255))
    edge = mask.filter(ImageFilter.MaxFilter(9))
    im.paste((40, 6, 0, 255), (0, 0), edge)
    im.paste(grad, (0, 0), mask)
    return im


# ---- 部品4: フック文字 (赤黒カード上の太ゴシック白文字) ---------------------
def hook(text: str, size: int = 118) -> Image.Image:
    im = layer()
    d = ImageDraw.Draw(im)
    f = font("gothic", size)
    lines = text.split("\n")
    y = H - 120 - len(lines) * (size + 24)
    for l in lines:
        draw_rich(d, (110, y), l, f, stroke=12)
        y += size + 24
    return im


# ---- 部品5: タイトルカード (サムネ風: 白銀+赤) -----------------------------
def title_card(top: str, bottom: str) -> Image.Image:
    im = layer()
    ft = font("gothic", 150)
    fb = font("gothic", 190)
    for text, f, y, colors in (
        (top, ft, 470, ((255, 255, 255), (150, 150, 160))),
        (bottom, fb, 680, ((255, 70, 70), (150, 0, 10))),
    ):
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).text((100, y), text, font=f, fill=255)
        outline = mask.filter(ImageFilter.MaxFilter(25))
        im.paste((0, 0, 0, 255), (0, 0), outline)
        if colors[0][0] == 255 and colors[0][1] == 70:
            im.paste((255, 255, 255, 255), (0, 0), mask.filter(ImageFilter.MaxFilter(9)))
        grad = Image.new("RGBA", (W, H))
        gd = ImageDraw.Draw(grad)
        h = f.size
        for yy in range(y, y + int(h * 1.4)):
            t = (yy - y) / (h * 1.4)
            c = tuple(int(colors[0][i] * (1 - t) + colors[1][i] * t) for i in range(3))
            gd.line([(0, yy), (W, yy)], fill=c + (255,))
        im.paste(grad, (0, 0), mask)
    return im
