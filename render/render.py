"""タイムラインを 1920x1080 / 30fps の mp4 に書き出す。

  python3 render/render.py               # 本番 (output/ep01_opening.mp4)
  python3 render/render.py --preview     # 960x540 / 15fps の確認用
  python3 render/render.py --stills DIR  # 各シーン中央の静止画だけ書き出す
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio  # noqa: E402
import style  # noqa: E402
from diagrams import DIAGRAMS  # noqa: E402
from scenes import BH, BW, GENERATORS  # noqa: E402
from timeline import T  # noqa: E402

W, H = style.W, style.H
OUT = style.ROOT / "output"


def build_overlay(item):
    kind = item[0]
    if kind == "sub":
        return style.subtitle(item[1]), "slide"
    if kind == "term":
        return style.term(item[1], item[2]), "slide"
    if kind == "kw":
        return style.keyword(item[1], item[2]), "punch"
    if kind == "hook":
        return style.hook(item[1]), "punch"
    if kind == "title":
        return style.title_card(item[1], item[2]), "punch"
    if kind == "diagram":
        return DIAGRAMS[item[1]](), "fade"
    raise ValueError(kind)


def vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip(1.08 - 0.42 * r ** 2.2, 0.35, 1)[..., None].astype(np.float32)


def grade_lut():
    """シネマ調: 軽いコントラスト + シャドウを青緑、ハイライトを暖色に (チャンネル別LUT)"""
    v = np.arange(256) / 255.0
    v = np.clip((v - 0.5) * 1.08 + 0.5, 0, 1)
    lut = []
    for sh, hi in ((-0.012, 0.02), (0.004, 0.006), (0.02, -0.02)):
        lut += list(np.clip((v + (1 - v) * sh + v * hi) * 255, 0, 255).astype(np.uint8))
    return lut


class Dust:
    """ゆっくり漂う塵の粒子"""

    def __init__(self, seed=0, n=70):
        r = np.random.default_rng(seed)
        self.p = r.random((n, 2)) * [W, H]
        self.v = (r.random((n, 2)) - 0.5) * [18, 10] + [6, -4]
        self.s = r.random(n) * 2.4 + 0.8
        self.a = r.random(n) * 70 + 30

    def draw(self, t):
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        pos = (self.p + self.v * t) % [W, H]
        for (x, y), s, a in zip(pos, self.s, self.a):
            d.ellipse((x - s, y - s, x + s, y + s), fill=int(a))
        return np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)), np.float32)[..., None]


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def place(ov, mode, t):
    """登場アニメ: slide=下から / punch=拡大から / fade"""
    k = ease(t / (0.35 if mode != "fade" else 0.5))
    if k >= 1:
        return ov
    if mode == "slide":
        out = Image.new("RGBA", (W, H))
        out.alpha_composite(ov, (0, int((1 - k) * 40)))
    elif mode == "punch":
        s = 1.12 - 0.12 * k
        sw, sh = int(W * s), int(H * s)
        big = ov.resize((sw, sh), Image.BILINEAR)
        out = big.crop(((sw - W) // 2, (sh - H) // 2, (sw - W) // 2 + W, (sh - H) // 2 + H))
    else:
        out = ov.copy()
    a = out.getchannel("A").point(lambda v: int(v * k))
    out.putalpha(a)
    return out


def kenburns(bg, z0, z1, pan, u):
    z = z0 + (z1 - z0) * u
    cw, ch = BW / z, BW / z * H / W
    cx = min(max(BW / 2 + pan[0] * u, cw / 2), BW - cw / 2)
    cy = min(max(BH / 2 + pan[1] * u, ch / 2), BH - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return bg.resize((W, H), Image.BILINEAR, box=box)


def scene_starts():
    starts, t0 = [], 0.0
    for dur, *_ in T:
        starts.append(t0)
        t0 += dur
    return starts, t0


def render_scene(args):
    """1シーンを書き出す。stills_dir があれば中央フレームの静止画だけ。"""
    si, fps, size, stills_dir, seg_path = args
    dur, bgname, ovs, opt = T[si]
    starts, _ = scene_starts()
    vig = vignette()
    lut = grade_lut()
    dust = Dust()
    rng = np.random.default_rng(si)
    grains = [rng.normal(0, 5, (H, W, 1)).astype(np.float32) for _ in range(4)]
    bg = GENERATORS[bgname]()
    layers = [build_overlay(o) for o in ovs]
    z0, z1 = opt.get("zoom", (1.0, 1.0))
    pan = opt.get("pan", (0, 0))
    cut = opt.get("cut", "cut")
    fade_out = si + 1 < len(T) and T[si + 1][3].get("cut") == "fade"
    n = int(round(dur * fps))
    proc = None
    if not stills_dir:
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{size[0]}x{size[1]}", "-r", str(fps), "-i", "-",
             "-c:v", "libx264", "-preset", "medium", "-b:v", "3200k", "-maxrate", "4500k",
             "-bufsize", "8000k", "-pix_fmt", "yuv420p",
             str(seg_path)], stdin=subprocess.PIPE)
    for fi in ([n // 2] if stills_dir else range(n)):
        t = fi / fps
        u = fi / max(1, n - 1)
        frame = kenburns(bg, z0, z1, pan, u).convert("RGBA")
        for ov, mode in layers:
            frame.alpha_composite(place(ov, mode, t))
        a = np.asarray(frame.convert("RGB").point(lut), np.float32)
        if bgname != "grid":
            a += dust.draw(starts[si] + t) * 0.9
        a *= vig
        a += grains[fi % len(grains)]
        if cut == "flash" and t < 0.25:
            a += (1 - t / 0.25) * 255
        if cut == "fade" and t < 0.6:
            a *= t / 0.6
        if fade_out and dur - t < 0.6:
            a *= max(0.0, (dur - t) / 0.6)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        if stills_dir:
            img.save(Path(stills_dir) / f"{si:02d}_{bgname}.jpg", quality=88)
            continue
        if size != (W, H):
            img = img.resize(size, Image.BILINEAR)
        proc.stdin.write(img.tobytes())
    if proc:
        proc.stdin.close()
        proc.wait()
    print(f"scene {si + 1}/{len(T)} done", flush=True)
    return si


def render(preview=False, stills_dir=None, jobs=4):
    fps = 15 if preview else 30
    size = (960, 540) if preview else (W, H)
    starts, total = scene_starts()
    print(f"total {total:.1f}s, {len(T)} scenes", flush=True)
    OUT.mkdir(exist_ok=True)
    seg_dir = OUT / "segments"
    seg_dir.mkdir(exist_ok=True)
    tasks = [(si, fps, size, stills_dir, seg_dir / f"{si:02d}.mp4") for si in range(len(T))]
    # 長いシーンから先に投げて並列の偏りを減らす
    tasks.sort(key=lambda a: -T[a[0]][0])
    with Pool(jobs) as pool:
        list(pool.imap_unordered(render_scene, tasks))
    if stills_dir:
        return

    cues = [(starts[i], opt.get("cut", "cut"), [o[0] for o in ovs]) for i, (_, _, ovs, opt) in enumerate(T)]
    wav = OUT / "ep01_opening_audio.wav"
    audio.write(wav, total, cues)
    lst = seg_dir / "list.txt"
    lst.write_text("".join(f"file '{si:02d}.mp4'\n" for si in range(len(T))))
    name = "ep01_opening_preview.mp4" if preview else "ep01_opening.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", str(OUT / name)], check=True)
    print("wrote", OUT / name, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--stills")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    if args.stills:
        Path(args.stills).mkdir(parents=True, exist_ok=True)
    render(args.preview, args.stills, args.jobs)
