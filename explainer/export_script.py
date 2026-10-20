"""episode.py から本編の台本 (script/ep01_main.md) を書き出す。"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from episode import SCENES  # noqa: E402
from ui import ROOT  # noqa: E402


def main():
    out = ["# 台本：ドラフトのお金と制度 完全解説（本編・約30分）", "",
           "対象：ニュースは見るけれど裏側までは知らない、ライト〜中級のファン。",
           "`explainer/episode.py` から `python3 explainer/export_script.py` で生成しています。", ""]
    prev = None
    for sc in SCENES:
        if sc["chapter"] != prev:
            out += [f"## {sc['chapter']}", ""]
            prev = sc["chapter"]
        for line in sc["lines"]:
            out.append(f"- {line[0] if isinstance(line, tuple) else line}")
        out.append("")
    out += ["## ファクトチェック", "", "事実関係と出典は `script/ep01_factcheck.md` にまとめています。"]
    (ROOT / "script" / "ep01_main.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
