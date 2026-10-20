"""episode.py から本編のナレーション台本 (script/ep01_main.md) を書き出す。

文ごとに動画内の開始時刻を付ける。読み方を指定している文には「読み」も添える。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engine import LEAD, build_timeline  # noqa: E402
from episode import SCENES  # noqa: E402
from ui import ROOT  # noqa: E402


def tc(sec):
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


def main():
    items, total = build_timeline()
    n = sum(len(sc["lines"]) for sc in SCENES)
    out = ["# ナレーション台本：ドラフトのお金と制度 完全解説（本編）", "",
           f"全{n}文・約{total / 60:.0f}分（合成音声の速さでの目安）。時刻は動画内で読み始める位置です。",
           "事実関係と出典は `script/ep01_factcheck.md` にまとめています。",
           "`explainer/episode.py` から `python3 explainer/export_script.py` で生成しています。", ""]
    prev = None
    for it in items:
        if it["kind"] != "scene":
            continue
        sc = SCENES[it["index"]]
        if sc["chapter"] != prev:
            out += ["", f"## {tc(it['start'])} {sc['chapter']}", ""]
            prev = sc["chapter"]
        for line, s in zip(sc["lines"], it["sents"]):
            text = line[0] if isinstance(line, tuple) else line
            out.append(f"- `{tc(it['start'] + s['start'] + LEAD)}` {text}")
            if isinstance(line, tuple):
                out.append(f"  - 読み：{line[1]}")
    (ROOT / "script" / "ep01_main.md").write_text("\n".join(out).replace("\n\n\n", "\n\n") + "\n")


if __name__ == "__main__":
    main()
