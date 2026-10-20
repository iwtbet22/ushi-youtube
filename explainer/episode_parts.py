"""episode.py / extra_scenes.py が共通で使う部品 (要素・シーンの定義用の関数)。"""
from __future__ import annotations

BLUE_CAP = (30, 70, 160)
GRAY_CAP = (110, 110, 124)
GREEN_CAP = (20, 120, 80)
TIE = (200, 40, 40)
TIE2 = (40, 90, 170)


def E(fn, x, y, at=0, until=None, anim="pop", scale=1.0, delay=0.15, over=False, full=False, count=None, name=None,
      dyn=None, dyn_dur=0.0):
    if name is None:
        name = getattr(fn, "func", fn).__name__ if fn else ("dyn" if dyn else "count")
        args = getattr(fn, "args", ())
        if args and isinstance(args[0], str):
            name += f"({args[0]})"
    return {"fn": fn, "x": x, "y": y, "at": at, "until": until, "anim": anim, "scale": scale, "delay": delay,
            "over": over, "full": full, "count": count, "name": name,
            "dyn": dyn, "dyn_dur": dyn_dur}


def C(end, fmt, x, y, at=0, until=None, color="red", size=130, dur=1.0, delay=0.2):
    """カウントアップする数字"""
    return E(None, x, y, at, until, "none", delay=delay, count=(end, fmt, color, size, dur), name=f"count({fmt(end)})")


def S(chapter, lines, els=(), bg="white", trans="cut", cam=None, hold=0):
    return {"chapter": chapter, "lines": list(lines), "els": list(els), "bg": bg, "trans": trans, "cam": cam,
            "hold": hold}


def man(v):
    """万円単位の数値を「1億円」「7,000万円」の形にする"""
    v = int(round(v))
    return "1億円" if v >= 10000 else f"{v:,}万円"


