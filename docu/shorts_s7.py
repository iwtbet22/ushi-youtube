"""12/3 のショート (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_gd1

  short_gd1  12/3  現役ドラフトは救済か、厄介払いか（17本目 現役ドラフト。12/4 公開の前日）

台本の文と数字は、本編の台本 (script/ep17_narration.txt。出典と確度は script/ep17_research.md) から取っている。
置き方は shorts_s6 と同じ。
"""
from functools import partial as P

import charts as C
import ep17
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, head, pic
from shorts_s3 import photo, subscribe

GD_END = ["明日の夜6時、これまでに移った49人の結果から、現役ドラフトを検証します。",
          "チャンネル登録して、見逃さないでください。"]

GD1 = [
    S(["DeNAでは6年間で、ホームランが通算6本。その選手が、移った先で24本を打ちました。",
       "中日の細川成也選手です。"],
      photo(ep17.HOSOKAWA2, 1901, GOLDF, (0.5, 0.3)), move="in", trans="cut", els=[
          head("6年で6本 → 1年で24本"),
          E(P(C.note, "※細川成也（中日、2024年）", 30), CX, 940),
          big("通算6本", 1060, 150, WHITE, until=0, anim="slam", sfx="boom"),
          big("移って24本", 1060, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["移籍のきっかけは、現役ドラフト。",
       "年俸は、990万円から、1億3000万円になりました。"],
      pic(P(C.vbars, [("移る前", 990, "990万円", False), ("今", 13000, "1億3000万円", True)], "万円", 420, 200, 120),
          1902, GOLDF, 820, 520), move="in", els=[
          head("現役ドラフト"),
          big("年俸 約13倍", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["ところが、同じ年に移った12人のうち、半分近くは、1年で戦力外になりました。"],
      pic(P(C.big_number, "2022年に移った12人", "半分近くが戦力外", 120), 1903, REDF, 860, 460), move="in", els=[
          head("移った先で1年"),
          big("1年で戦力外", 1000, 140, RED, anim="slam", sfx="boom"),
      ]),
    S(["埋もれた選手を救う制度なのか。それとも、厄介払いなのか。"],
      pic(P(C.big_number, "現役ドラフトは", "救済か 厄介払いか", 120), 1904, BLUEF, 860, 460), move="in", els=[
          head("12月9日 第5回"),
      ]),
    subscribe(1905, GD_END),
]
GD1 = ep17._fix_speech(GD1)
