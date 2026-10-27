"""2本目の概要欄 (script/ep02_description.txt) を書き出す。チャプターは動画の時刻から、
画像のクレジットは assets/ep02/img/credits.json から作る (使っている画像だけ)。"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ep02  # noqa: E402
import film  # noqa: E402
import look  # noqa: E402

LIC = {"cc-by-2.0": "CC BY 2.0", "cc-by-sa-2.0": "CC BY-SA 2.0", "cc-by-sa-3.0": "CC BY-SA 3.0",
       "cc-by-4.0": "CC BY 4.0", "cc-by-sa-4.0": "CC BY-SA 4.0", "cc-zero": "CC0"}


def chapters():
    items, _ = film.timeline(ep02.SCENES)
    out = ["0:00 オープニング"]
    for sc, it in zip(ep02.SCENES, items):
        if not sc["lines"]:  # 章の扉
            t = int(it["start"])
            title = sc["els"][0]["fn"].args[1]
            out.append(f"{t // 60}:{t % 60:02d} {title}")
    end = items[-1]
    t = int(end["start"])
    out.append(f"{t // 60}:{t % 60:02d} エンディング")
    return out


def used_images():
    src = (HERE / "ep02.py").read_text() + (HERE / "ep02_open.py").read_text()
    names = set(re.findall(r'"([^"]+\.(?:jpg|JPG|jpeg|png))"', src))
    return [n for n in sorted(names) if (look.IMG / n).exists()]


def credit_lines():
    """作者ごとにまとめて「作者（ライセンス、枚数）」の形にする (URL まで並べると概要欄の5000字を超えるため)"""
    cred = json.loads((look.IMG / "credits.json").read_text())
    by = {}
    for n in used_images():
        c = cred.get(n)
        if not c:
            continue
        lic = next((LIC[l.lower()] for l in c["license"] if l.lower() in LIC), c["license"][0])
        by.setdefault((c["author"], lic), []).append(n)
    return [f"・{a}（{lic}{'、' + str(len(ns)) + '枚' if len(ns) > 1 else ''}）" for (a, lic), ns in sorted(by.items())]


def main():
    head = (ROOT := HERE.parent) / "script" / "ep02_description_head.txt"
    text = head.read_text().replace("{CHAPTERS}", "\n".join(chapters())).replace("{CREDITS}", "\n".join(credit_lines()))
    (ROOT / "script" / "ep02_description.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
