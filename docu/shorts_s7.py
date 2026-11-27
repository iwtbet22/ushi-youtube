"""12/3 のショート (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_gd1

  short_gd1  12/3  現役ドラフトは救済か、厄介払いか（17本目 現役ドラフト。12/4 公開の前日）
  short_gd2  12/5  ソフトバンクが出した選手が、次々に活躍する（17本目の翌日。12/7 のソフトバンク編につなぐ）

台本の文と数字は、本編の台本 (script/ep17_narration.txt。出典と確度は script/ep17_research.md) から取っている。
置き方は shorts_s6 と同じ。
"""
from functools import partial as P

import charts as C
import ep17
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, head, pic
from shorts_s3 import photo, subscribe, END

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
       "年俸は、1040万円から、1億3000万円になりました。"],
      pic(P(C.vbars, [("移る前", 1040, "1040万円", False), ("今", 13000, "1億3000万円", True)], "万円", 420, 200, 120),
          1902, GOLDF, 820, 520), move="in", els=[
          head("現役ドラフト"),
          big("年俸 約12倍", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
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


# ---- 12/5：ソフトバンクが出した選手が、次々に活躍する (17本目の翌日) ------------------------------------
GD2 = [
    S(["現役ドラフトで出した選手が、次々にほかの球団で活躍している球団があります。",
       "ソフトバンクです。"],
      photo(ep17.PAYPAY, 2001, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("出した選手が活躍する球団"),
          E(P(C.note, "※みずほPayPayドーム福岡", 30), CX, 940),
          big("ソフトバンク", 1060, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["大竹耕太郎投手は、阪神に移って最初のシーズンに12勝。",
       "水谷瞬選手は、日本ハムで交流戦の最優秀選手に選ばれました。"],
      photo(ep17.OTAKE, 2002, GOLDF, (0.5, 0.3)), move="in", els=[
          head("出した選手のその後"),
          E(P(C.note, "※大竹耕太郎（阪神、2024年）", 30), CX, 940),
          big("阪神で12勝", 1060, 150, GOLD, until=0, anim="slam", sfx="boom"),
          big("交流戦の最優秀選手", 1060, 110, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["去年出した佐藤直樹選手は、その年、ソフトバンクで104試合に出ていた選手です。"],
      pic(P(C.big_number, "佐藤直樹（2025年 → 楽天）", "その年 104試合", 120), 2003, BLUEF, 860, 460), move="in", els=[
          head("去年は 佐藤直樹"),
      ]),
    S(["球団の幹部は、「本来はレギュラーをとれるだけの能力はある」と話しています。",
       "選手が多く、層が厚いからこそ、いい選手でも出すことになるのです。"],
      pic(P(C.quote, "本来はレギュラーを\nとれるだけの能力はある", 64), 2004, BLUEF, 860, 400), move="in", els=[
          head("球団の幹部（報道）"),
          big("層が厚すぎる", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    subscribe(2005, END),
]
GD2 = ep17._fix_speech(GD2)
