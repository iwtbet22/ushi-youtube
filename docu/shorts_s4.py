"""12本目（球場編）に合わせたショート (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_bp1

数字は script/ep12_narration.txt・ep12_research.md（確度つき）から取る。最後はチャンネル登録のお願いで締める。
"""
from functools import partial as P

import charts as C
import ep12
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, fog, head, pic
from shorts_s3 import photo, subscribe, END

BP1 = [
    S(["2025年、日本ハムの球団は、12億円あまりの赤字。",
       "ところが、本拠地の球場を運営する会社は、およそ71億円の営業利益を出しています。"],
      photo(ep12.ESCON, 1301, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("球団は赤字 球場は黒字"),
          E(P(C.note, "※エスコンフィールドHOKKAIDO", 30), CX, 940),
          big("球団 12億円の赤字", 1060, 120, RED, until=0, anim="slam", sfx="boom"),
          big("球場の会社 71億円の黒字", 1060, 100, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["札幌ドームを借りていたころ、使用料は、1試合800万円。",
       "球場の看板や、売店の売上は、球団には入りませんでした。"],
      photo(ep12.SAPPORO, 1302, BLUEF, (0.5, 0.5), 3), move="in", els=[
          head("借りていたころ"),
          E(P(C.note, "※札幌ドーム", 30), CX, 940),
          big("1試合 800万円", 1060, 140, WHITE, until=0, anim="slam", sfx="boom"),
          big("看板も売店も 入らない", 1060, 110, RED, at=1, anim="rise"),
      ]),
    S(["球団が値下げを求めると、返ってきたのは、逆に値上げでした。",
       "そこで日本ハムは、自分たちの球場を建てることにしたのです。"],
      pic(P(C.big_number, "値下げを求めたら", "値上げ", 160), 1303, REDF, 820, 460),
      move="in", els=[
          head("値下げを求めたら"),
          big("自分たちの球場へ", 1000, 130, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["2023年に開業したエスコンフィールド。",
       "球場の会社の売上は、2025年に277億円まで伸びました。"],
      photo(ep12.ESCON2, 1304, GOLDF, (0.5, 0.5), 3), move="in", els=[
          head("2023年 開業"),
          E(P(C.note, "※エスコンフィールドHOKKAIDO", 30), CX, 940),
          big("売上 277億円", 1060, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["球場を持てば、入場料も、看板も、売店も、そして球場の名前のお金も、自分たちのものになります。"],
      pic(P(C.bullet_list, ["入場料", "看板", "売店", "球場の名前（命名権）"], 64, 800), 1305, GOLDF, 840, 460), move="in",
      els=[
          head("球場を持つと"),
          big("収入が自分のものに", 1060, 110, GOLD, anim="rise"),
      ]),
    S(["一方、出ていかれた札幌ドームは、売上が29億円あまりから、12億円あまりに落ち込みました。"],
      pic(P(C.vbars, [("2022年度", 29.7, "29.7億円", False), ("2023年度", 12.7, "12.7億円", True)], "億円", 420, 190, 60),
          1306, REDF, 820, 460), move="in", els=[
          head("出ていかれた球場"),
          big("半分以下に", 1080, 150, RED, anim="slam", sfx="boom"),
      ]),
    subscribe(1307, END),
]

BP1 = ep12._fix_speech(BP1)

# ショートだけの読みの指定 (check_word で聞き比べて「微妙」だったもの)
for _sc in BP1:
    _sc["lines"] = [((ln[0] if isinstance(ln, tuple) else ln),
                     (ln[1] if isinstance(ln, tuple) else ln).replace("開業したエスコン", "開業した、エスコン"))
                    if "開業したエスコン" in (ln[1] if isinstance(ln, tuple) else ln) else ln for ln in _sc["lines"]]
