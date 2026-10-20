"""episode.py から本編の台本 (script/ep01_main.md) を書き出す。"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from episode import SCENES  # noqa: E402
from ui import ROOT  # noqa: E402


def main():
    out = ["# 台本：ドラフトの契約金はいくら？（本編）", "",
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
    out += ["## ファクトメモ",
            "- 新人契約の上限（最高標準額）：契約金1億円＋出来高5000万円、年俸1600万円（12球団の申し合わせ）",
            "- 順位別の契約金は決まった額がなく、報道ベースの目安：2位 7000万前後／3位 5000〜6000万／4位 4000万前後／5位 3000万前後／6位以下 2000万円台も",
            "- 年俸の目安：1位で大卒・社会人 1500万前後、高卒 1000万前後〜（目玉の高卒は上限1600万もある）",
            "- 社会人の指名解禁：高卒社会人は3年、大卒社会人は2年。社会人は慣例として育成指名されない",
            "- 指名縛り（順位縛り）：選手側が「○位以内でなければ進学・就職する」と事前に伝える慣行。2023年に高校生が3位縛りで指名漏れと報じられた例がある",
            "- 育成：契約金なし、支度金は200〜300万円ほど。育成契約は3年以内に支配下登録されないと、いったん自由契約",
            "- 2007年に球団がアマチュア選手へ金銭を渡していた問題が発覚",
            "- 数字は年・球団で変わる。公開前にNPBの資料や最新の報道で確認すること"]
    (ROOT / "script" / "ep01_main.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
