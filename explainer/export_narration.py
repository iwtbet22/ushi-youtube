"""episode.py から本編のナレーション台本 (script/ep01_narration.txt) を書き出す。

時刻は付けず、章見出しと文だけを並べたプレーンテキスト。読み方を指定している文は（読み：…）を添える。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from episode import SCENES  # noqa: E402
from ui import ROOT  # noqa: E402


def main():
    n = sum(len(sc["lines"]) for sc in SCENES)
    out = ["ドラフトのお金と制度 完全解説（本編）ナレーション台本", "", f"全{n}文", ""]
    prev = None
    for sc in SCENES:
        if sc["chapter"] != prev:
            out += ["", f"【{sc['chapter']}】", ""]
            prev = sc["chapter"]
        out += [f"{l[0]}（読み：{l[1]}）" if isinstance(l, tuple) else l for l in sc["lines"]]
    (ROOT / "script" / "ep01_narration.txt").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
