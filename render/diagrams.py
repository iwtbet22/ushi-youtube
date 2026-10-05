"""方眼紙の上に描く図解レイヤー (墨・筆文字スタイル)。"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from style import H, INK, W, font, layer


def _brush_label(d, cx, y, text, size=88):
    f = font("brush", size)
    tw = d.textlength(text, font=f)
    d.text((cx - tw / 2, y), text, font=f, fill=INK)


def _ink_card(im, box, fill=(250, 248, 240, 255)):
    x0, y0, x1, y1 = box
    sh = layer()
    ImageDraw.Draw(sh).rectangle((x0 + 14, y0 + 16, x1 + 14, y1 + 16), fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im)
    d.rectangle(box, fill=fill, outline=INK, width=5)
    return d


def three_parts(with_amounts: bool) -> Image.Image:
    """新人契約 = 契約金 / 出来高 / 年俸"""
    im = layer()
    items = [("契約金", "1億円", "入団時に一度"),
             ("出来高", "5000万円", "成績しだい"),
             ("年俸", "1600万円", "毎年の給料")]
    for i, (name, amt, note) in enumerate(items):
        cx = 400 + i * 560
        d = _ink_card(im, (cx - 230, 170, cx + 230, 690))
        _brush_label(d, cx, 200, name, 104)
        d.line([(cx - 160, 360), (cx + 160, 360)], fill=INK, width=4)
        if with_amounts:
            f = font("gothic", 76)
            tw = d.textlength(amt, font=f)
            d.text((cx - tw / 2, 400), amt, font=f, fill=(176, 18, 30))
            f2 = font("gothic_bold", 40)
            tw = d.textlength(note, font=f2)
            d.text((cx - tw / 2, 540), note, font=f2, fill=INK)
            d.rounded_rectangle((cx + 100, 596, cx + 216, 648), radius=8, fill=(176, 18, 30))
            d.text((cx + 122, 594), "上限", font=font("gothic", 36), fill=(255, 255, 255))
        else:
            f = font("gothic", 120)
            d.text((cx - 36, 420), "？", font=f, fill=(150, 150, 150))
    for i in range(2):
        x = 400 + i * 560 + 280
        ImageDraw.Draw(im).text((x - 22, 380), "+", font=font("gothic", 90), fill=INK)
    return im


def gap_bars(show_ratio: bool) -> Image.Image:
    """ドラフト1位 1億円 vs 育成 支度金 約300万円"""
    im = layer()
    d = ImageDraw.Draw(im)
    base_y = 690
    bars = [("ドラフト1位", "契約金", 100_000_000, "1億円", (176, 18, 30)),
            ("育成指名", "支度金", 3_000_000, "約300万円", (60, 60, 64))]
    max_h = 470
    for i, (who, kind, v, label, col) in enumerate(bars):
        cx = 620 + i * 680
        h = max(14, int(max_h * v / 100_000_000))
        d.rectangle((cx - 150 + 12, base_y - h + 12, cx + 150 + 12, base_y + 12), fill=(0, 0, 0, 70))
        d.rectangle((cx - 150, base_y - h, cx + 150, base_y), fill=col + (255,), outline=INK, width=4)
        f = font("gothic", 72)
        tw = d.textlength(label, font=f)
        d.text((cx - tw / 2, base_y - h - 104), label, font=f, fill=col + (255,))
        _brush_label(d, cx, base_y + 20, who, 76)
        fk = font("gothic_bold", 38)
        tw = d.textlength(kind, font=fk)
        d.text((cx - tw / 2, base_y + 120), kind, font=fk, fill=INK)
    d.line([(300, base_y), (1640, base_y)], fill=INK, width=6)
    if show_ratio:
        f = font("gothic", 96)
        txt = "約33倍"
        tw = d.textlength(txt, font=f)
        top = base_y - max_h
        # 1億円の高さまで点線を引き、差をブラケットで示す
        for x in range(780, 1520, 36):
            d.line([(x, top), (x + 18, top)], fill=(176, 18, 30), width=5)
        d.line([(1540, top), (1540, base_y - 20)], fill=(176, 18, 30), width=8)
        d.polygon([(1540, base_y - 14), (1522, base_y - 50), (1558, base_y - 50)], fill=(176, 18, 30))
        d.text((1566, top + 150), txt, font=f, fill=(176, 18, 30), stroke_width=10, stroke_fill=(255, 255, 255))
    return im


DIAGRAMS = {
    "three_parts_q": lambda: three_parts(False),
    "three_parts": lambda: three_parts(True),
    "gap": lambda: gap_bars(False),
    "gap_ratio": lambda: gap_bars(True),
}
