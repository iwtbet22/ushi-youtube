"""人物カード用に、受け取った写真から上半身を切り出す (縦横比 330:400)。
  python3 tools/face_crops.py <元写真のフォルダ>
出力は assets/ep02/img/face_<元の名前>.jpg
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

OUT = Path(__file__).resolve().parent.parent / "assets/ep02/img"
# 元のファイル名: (中心x, 中心y, 高さの割合)  ※向きを直した後の画像に対する割合
BOX = {
    "20110928-0441_Junichi_Tazawa.jpg": (0.5, 0.3, 0.6),
    "202306041702_DSCN7591.jpg": (0.52, 0.33, 0.4),
    "Daisuke_Matsuzaka_on_March_25,_2008.jpg": (0.55, 0.25, 0.5),
    "Hiromi_Ito_Fighters2026.jpg": (0.45, 0.25, 0.45),
    "Ichiro_Suzuki_(51007139682)_(cropped).jpg": (0.5, 0.27, 0.4),
    "Kenta_Maeda_Los_Angeles_Dodgers_(26686442045)_(cropped).jpg": (0.4, 0.3, 0.6),
    "Konatakahashi.jpg": (0.38, 0.3, 0.5),
    "Masataka_Yoshida_April14,_2026_(cropped).jpg": (0.7, 0.3, 0.6),
    "Rahm_Emanuel_with_Rintaro_Sasaki_-_01.jpg": (0.72, 0.45, 0.6),
    "Roki-Sasaki-20240430-Kobe_(cropped).jpg": (0.6, 0.2, 0.4),
    "Seiya_Suzuki_at_bat.jpg": (0.5, 0.3, 0.45),
    "Teruaki-Sato-20240310-Koshien.jpg": (0.55, 0.32, 0.45),
    "YS-Munetaka_MUrakami20220812-2.jpg": (0.5, 0.38, 0.42),
    "今井達也_2023年5月16日エスコンフィールドHOKKAIDO.jpg": (0.4, 0.42, 0.85),
    "鎌ヶ谷スタジアム_0320_平良海馬2.jpg": (0.5, 0.4, 0.6),
    "960px-Shota_Imanaga_pitching_form1.jpg": (0.53, 0.27, 0.45),
    "960px-Yu_Darvish_on_March_13,_2012_(3).jpg": (0.55, 0.25, 0.4),
}


def crop(src, cx, cy, hf, ratio=330 / 400):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    W, H = im.size
    h = hf * H
    w = min(h * ratio, W)
    h = w / ratio
    x0 = min(max(cx * W - w / 2, 0), W - w)
    y0 = min(max(cy * H - h / 2, 0), H - h)
    out = im.crop((round(x0), round(y0), round(x0 + w), round(y0 + h)))
    if out.height > 1000:
        out = out.resize((round(1000 * ratio), 1000), Image.LANCZOS)
    return out


if __name__ == "__main__":
    src = Path(sys.argv[1])
    for name, b in BOX.items():
        if (src / name).exists():
            crop(src / name, *b).save(OUT / f"face_{Path(name).stem}.jpg", quality=92)
            print("ok", name)
