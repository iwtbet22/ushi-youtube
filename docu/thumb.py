"""サムネイル (1280x720) を作る。

  python3 docu/thumb.py c2ep01      # 回のモジュールの THUMB (dict) から作る → output/upload/<回>_thumb.png

THUMB = {
    "bg": "写真のファイル名" (assets/ep02/img、なければ黒),
    "title": "上の大きな文字",
    "left": ("見出し", "数字", (r, g, b)),   # 左右の数字の札
    "right": ("見出し", "数字", (r, g, b)),
    "bottom": "下の一言",
}
字が小さい画面 (スマホのおすすめ欄) でも読めるよう、文字は太く大きく、縁取りをつける。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts"
IMG = ROOT / "assets" / "ep02" / "img"
W, H = 1280, 720


def font(name, size):
    return ImageFont.truetype(str(FONT / name), size)


def fit(d, s, name, size, max_w):
    while size > 20 and d.textlength(s, font=font(name, size)) > max_w:
        size -= 4
    return font(name, size)


def outlined(d, xy, s, f, fill, stroke=10, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def background(name):
    p = IMG / name if name else None
    if not p or not p.exists():
        return Image.new("RGB", (W, H), (12, 12, 14))
    im = Image.open(p).convert("RGB")
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(2))
    return ImageEnhance.Brightness(im).enhance(0.45)


def card(d, cx, label, value, color):
    """数字の札: 上に見出し、下に大きな数字"""
    bw, top, bot = 560, 190, 560
    d.rounded_rectangle((cx - bw // 2, top, cx + bw // 2, bot), radius=28, fill=(0, 0, 0, 170),
                        outline=color, width=8)
    outlined(d, (cx, top + 85), label, fit(d, label, "DelaGothicOne-Regular.ttf", 80, bw - 60), (255, 255, 255), 6)
    outlined(d, (cx, top + 250), value, fit(d, value, "DelaGothicOne-Regular.ttf", 150, bw - 40), color, 10)


def make(t, out):
    im = background(t.get("bg")).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    outlined(d, (W // 2, 95), t["title"], fit(d, t["title"], "DelaGothicOne-Regular.ttf", 120, W - 80), (255, 255, 255), 12)
    card(d, 330, *t["left"])
    card(d, 950, *t["right"])
    d.rectangle((0, 590, W, H), fill=(200, 30, 30, 235))
    outlined(d, (W // 2, 655), t["bottom"], fit(d, t["bottom"], "DelaGothicOne-Regular.ttf", 92, W - 60), (255, 236, 120), 8)
    im.alpha_composite(layer)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(out)
    return out


if __name__ == "__main__":
    ep = sys.argv[1]
    sys.path.insert(0, str(ROOT / "docu"))
    mod = importlib.import_module(ep)
    print(make(mod.THUMB, ROOT / "output" / "upload" / f"{ep}_thumb.png"))
