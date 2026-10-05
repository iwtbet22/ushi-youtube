"""timeline.py から台本 (script/ep01_opening.md) を書き出す。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import durations  # noqa: E402
from style import ROOT, plain  # noqa: E402
from timeline import T  # noqa: E402


def overlay_text(o):
    if o[0] == "diagram":
        return f"［図解: {o[1]}］"
    if o[0] == "kw":
        return f"［キーワード］{o[1]}"
    return plain(" ".join(o[1:])).replace("\n", " ")


def main():
    lines = [
        "# 台本：ドラフト1位の契約金はなぜ1億円なのか（冒頭3分）", "",
        "対象：ニュースは見るけれど裏側までは知らない、ライト〜中級のファン。",
        "たとえ話の軸：新人契約の上限を、親戚同士の「お年玉は1万円まで」ルールにたとえる。",
        "`render/timeline.py` から `python3 render/export_script.py` で生成しています。", "",
        "| # | 時間 | 映像 | ナレーション | 画面テキスト |", "|---|---|---|---|---|",
    ]
    t = 0.0
    for i, ((_, bg, ovs, opt), d) in enumerate(zip(T, durations()), 1):
        nar = opt.get("nar", "（BGMのみ）")
        scr = " / ".join(overlay_text(o) for o in ovs) or "—"
        lines.append(f"| {i} | {int(t // 60)}:{t % 60:04.1f} | {bg} | {nar} | {scr} |")
        t += d
    lines += ["", f"合計 {t:.1f} 秒", "", "## ファクトメモ",
              "- 新人契約の上限（最高標準額）：契約金1億円＋出来高5000万円、年俸1600万円。12球団の申し合わせによるもの",
              "- 育成指名：契約金はなく、支度金（相場は約300万円）。1億円 ÷ 300万円 ≒ 33倍",
              "- 出来高の条件（新人王・規定投球回など）は選手ごとに違う。ナレーションでは「たとえば」と言っている",
              "- 本編に入る前に、NPBの公式資料・報道で最新の数字をもう一度確認すること"]
    (ROOT / "script" / "ep01_opening.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
