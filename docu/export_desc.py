"""概要欄 (script/<名前>_description.txt) を書き出す。チャプターは動画の時刻から、
画像のクレジットは assets/ep02/img/credits.json から作る (実際に場面で使っている画像だけ)。

  python3 docu/export_desc.py [ep02|ep03]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import importlib  # noqa: E402
from functools import partial  # noqa: E402

import charts  # noqa: E402
import film  # noqa: E402
import look  # noqa: E402

LIC = {"cc-by-2.0": "CC BY 2.0", "cc-by-2.5": "CC BY 2.5", "cc-by-sa-2.0": "CC BY-SA 2.0", "cc-by-sa-3.0": "CC BY-SA 3.0",
       "cc-by-sa-3.0,2.5,2.0,1.0": "CC BY-SA 3.0", "cc-by-sa-all": "CC BY-SA 4.0", "cc-by-sa-3.0-migrated": "CC BY-SA 3.0",
       "cc-by-4.0": "CC BY 4.0", "cc-by-sa-4.0": "CC BY-SA 4.0", "cc-zero": "CC0"}


def chapters(mod):
    items, _ = film.timeline(mod.SCENES)
    out = ["0:00 オープニング"]
    for sc, it in zip(mod.SCENES, items):
        if sc["lines"]:
            continue
        fn = sc["els"][0]["fn"]  # 章の扉 / 事件簿の扉
        t = int(it["start"])
        if fn.func is charts.case_card:
            title = f"事件簿{fn.args[0]:02d} {fn.args[2]}"
        else:
            title = fn.args[1]
        out.append(f"{t // 60}:{t % 60:02d} {title}")
    t = int(items[-1]["start"])
    out.append(f"{t // 60}:{t % 60:02d} エンディング")
    # YouTube はチャプターの間隔が10秒未満だとチャプター全体を無効にするので、すぐ次が来るものは外す
    sec = [int(x.split()[0].split(":")[0]) * 60 + int(x.split()[0].split(":")[1]) for x in out]
    return [x for k, x in enumerate(out) if k == len(out) - 1 or sec[k + 1] - sec[k] >= 10]


def _files(obj, found):
    """partial の引数をたどって、画像ファイル名を集める"""
    if isinstance(obj, partial):
        _files(obj.func, found)
        for a in list(obj.args) + list(obj.keywords.values()):
            _files(a, found)
    elif isinstance(obj, str) and re.search(r"\.(jpe?g|png)$", obj, re.I):
        found.add(obj)
    elif isinstance(obj, (list, tuple)):
        for a in obj:
            _files(a, found)


def used_images(mod):
    found = set()
    for sc in mod.SCENES:
        _files(sc["bg"], found)
        for e in sc["els"]:
            _files(e["fn"], found)
    return [n for n in sorted(found) if (look.IMG / n).exists()]


def credit_lines(mod):
    """作者ごとにまとめて「作者（ライセンス、枚数）」の形にする (URL まで並べると概要欄の5000字を超えるため)"""
    cred = json.loads((look.IMG / "credits.json").read_text())
    by = {}
    for n in used_images(mod):
        c = cred.get(n)
        if not c:
            continue
        lic = next((LIC[l.lower()] for l in c["license"] if l.lower() in LIC), c["license"][0])
        author = re.sub(r"^User:", "", c["author"]).replace(" on Flickr", " (Flickr)")
        by.setdefault((author, lic), []).append(n)
    return [f"・{a}（{lic}{'、' + str(len(ns)) + '枚' if len(ns) > 1 else ''}）" for (a, lic), ns in sorted(by.items())]


def main():
    ep = sys.argv[1] if len(sys.argv) > 1 else "ep02"
    mod = importlib.import_module(ep)
    root = HERE.parent
    head = root / "script" / f"{ep}_description_head.txt"
    text = head.read_text().replace("{CHAPTERS}", "\n".join(chapters(mod))).replace(
        "{CREDITS}", "\n".join(credit_lines(mod)))
    (root / "script" / f"{ep}_description.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
