"""episode.py から録音用の台本 (script/ep01_recording.md) を書き出す。

1章 = 1ファイルで録音してもらい、文と文の間の無音で切り分けて各文に対応させる前提。
各文には「章番号-文番号」を振る (例: 03-05)。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "render"))
import tts  # noqa: E402
from episode import SCENES  # noqa: E402
from ui import ROOT  # noqa: E402

# 読み間違えやすい語と数字の読み方
READINGS = [
    ("出来高", "できだか"), ("支度金", "したくきん"), ("年俸", "ねんぽう"), ("最高標準額", "さいこうひょうじゅんがく"),
    ("支配下", "しはいか"), ("指名縛り", "しめいしばり"), ("順位縛り", "じゅんいしばり"), ("一軍", "いちぐん"),
    ("12球団", "じゅうにきゅうだん"), ("1億円", "いちおくえん"), ("1億5千万", "いちおくごせんまん"), ("2億", "におく"),
    ("5000万円", "ごせんまんえん"), ("1600万円", "せんろっぴゃくまんえん"), ("1500万円", "せんごひゃくまんえん"),
    ("1000万円", "いっせんまんえん"), ("7000万円", "ななせんまんえん"), ("6000万円", "ろくせんまんえん"),
    ("4000万円", "よんせんまんえん"), ("3000万円", "さんぜんまんえん"), ("2000万円台", "にせんまんえんだい"),
    ("200万円", "にひゃくまんえん"), ("300万円", "さんびゃくまんえん"), ("30倍", "さんじゅうばい"),
    ("2007年", "にせんななねん"), ("1位", "いちい"), ("2位", "にい"), ("3位", "さんい"), ("4位", "よんい"),
    ("5位", "ごい"), ("6位", "ろくい"), ("3年", "さんねん"), ("2年", "にねん"), ("FA", "エフエー"), ("江川卓", "えがわすぐる"), ("小林繁", "こばやししげる"), ("山崎裕之", "やまざきひろゆき"),
    ("上尾", "あげお"), ("西鉄", "にしてつ"), ("田澤純一", "たざわじゅんいち"), ("新日本石油ENEOS", "しんにほんせきゆエネオス"),
    ("都市対抗", "としたいこう"), ("倫理行動宣言", "りんりこうどうせんげん"), ("公正取引委員会", "こうせいとりひきいいんかい"), ("交渉権", "こうしょうけん"), ("1巡目", "いちじゅんめ"), ("2巡目", "にじゅんめ"),
    ("3巡目", "さんじゅんめ"), ("4巡目", "よんじゅんめ"), ("田澤", "たざわ"), ("1965年", "せんきゅうひゃくろくじゅうごねん"),
    ("3000万円", "さんぜんまんえん"), ("12.5", "じゅうにてんご"), ("4月1日", "しがつついたち"), ("7月31日", "しちがつさんじゅういちにち"),
]


def hints(text):
    """文に含まれる読み注意の語。長い語に含まれる短い語 (例: 1億5千万 の中の 1億) は出さない"""
    found = [(w, y) for w, y in READINGS if w in text]
    keep = [(w, y) for w, y in found if not any(w != o and w in o for o, _ in found)]
    return [f"{w}={y}" for w, y in keep]


def main():
    chapters = []
    for sc in SCENES:
        key = "終わりのあいさつ" if sc["bg"] == "end" else sc["chapter"]
        if not chapters or chapters[-1][0] != key:
            chapters.append((key, []))
        for line in sc["lines"]:
            chapters[-1][1].append(line[0] if isinstance(line, tuple) else line)

    total = sum(tts.duration(tts.ensure(l if not isinstance(l, tuple) else l[1]))
                for sc in SCENES for l in sc["lines"])
    out = [
        "# 録音用台本：ドラフトのお金と制度 完全解説（本編・約30分）", "",
        f"全{sum(len(c[1]) for c in chapters)}文（1ファイル通しでも、{len(chapters)}章に分けても可）。"
        f"読み上げだけで約{total / 60:.0f}分（合成音声の速さでの目安）。",
        "`python3 explainer/export_recording.py` で `explainer/episode.py` から生成しています。", "",
        "## 録音のしかた",
        "- **全部を1ファイルで通して録音してOK**です（`ep01_all.wav` など）。章ごとに分けたい場合は、各章にある名前（`ch01.wav` など）で保存してください",
        "- **1文読むごとに2秒ほど間を空けてください**。この無音で文を切り分けて、画面のタイミングに合わせます",
        "- 噛んだときは、**5秒ほど長めに空けてから、その文を頭から読み直して**ください。長い無音を目印に、読み直した方を使います",
        "- 途中で休憩するときは、録音を止めずに黙っていれば大丈夫です。止めて複数ファイルになっても、順番どおりにつなげて使います",
        "- 番号（`01-03` など）は読まなくて大丈夫です",
        "- 解説動画のテンションで、はっきり・やや明るめに。章ごとに日をまたいでもいいので、声の調子はなるべくそろえてください",
        "- 静かな部屋で、マイクとの距離（15〜20cm）を一定に。WAV（44.1kHzか48kHz）で保存してください",
        "- 「読み」欄は読み間違えやすい語です。迷ったらこの読み方で", "",
    ]
    for ci, (title, lines) in enumerate(chapters, 1):
        out += [f"## {ci:02d}. {title}　（分ける場合は `ch{ci:02d}.wav`）", "", "| 番号 | 読む文 | 読み |", "|---|---|---|"]
        for li, text in enumerate(lines, 1):
            h = "、".join(hints(text)) or ""
            out.append(f"| {ci:02d}-{li:02d} | {text} | {h} |")
        out.append("")
    (ROOT / "script" / "ep01_recording.md").write_text("\n".join(out) + "\n")
    print(len(chapters), "files,", sum(len(c[1]) for c in chapters), "lines,", f"{total / 60:.1f} min")


if __name__ == "__main__":
    main()
