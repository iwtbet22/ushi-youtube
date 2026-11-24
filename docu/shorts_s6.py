"""12/2・12/3 のショート 2本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_hs1   (short_sb1)

  short_hs1  12/2  阪神タイガースの利益（15本目 阪神編。12/1 公開の翌日）
  short_sb1  12/3  日本一でも75億円の赤字（16本目 ソフトバンク編。12/4 公開の前日）

台本の文と数字は、本編の台本 (script/ep15・ep16_narration.txt。出典と確度は各回の research.md) から取っている。
置き方は shorts_s3 と同じ。
"""
from functools import partial as P

import charts as C
import ep15
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, head, pic
from shorts_s3 import photo, subscribe, END

_PL = [("20年3月", 3.84, "3.8億", False), ("21年3月", -14.07, "▲14.1億", False), ("23年3月", 13.58, "13.6億", False),
       ("24年3月", 26.59, "26.6億", True), ("25年3月", 22.03, "22.0億", False), ("26年3月", 27.54, "27.5億", True)]


def pl(seed, upto, tint=GOLDF):
    return pic(P(C.plbars, _PL, "億円", 420, 120, 40, upto), seed, tint, 840, 520)


# ---- 12/2：阪神タイガースの利益 (15本目 阪神編) ------------------------------------------
HS1 = [
    S(["コロナのとき、14億円の赤字だった阪神タイガース。",
       "それが5年後には、27億円を超える黒字になりました。"],
      photo(ep15.KOSHIEN_STA, 1701, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("阪神タイガースの利益"),
          E(P(C.note, "※阪神甲子園駅", 30), CX, 940),
          big("14億円の赤字", 1060, 150, RED, until=0, anim="slam", sfx="boom"),
          big("27億円の黒字へ", 1060, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["球団の阪神タイガースは、毎年、官報に決算を載せています。",
       "2021年3月期は、14億700万円の赤字でした。",
       "2020年のシーズンは、はじめは無観客。満員の甲子園という強みが、消えたのです。"],
      pl(1702, 1, REDF), move="in", els=[
          head("球団の純利益"),
          big("コロナで赤字", 1060, 140, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["2023年、岡田監督のもとで、38年ぶりの日本一。",
       "その年をふくむ2024年3月期は、26億5900万円。前の年の、およそ2倍です。"],
      pl(1703, 3), move="in", els=[
          head("日本一の年"),
          big("前の年の約2倍", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["そして、ふたたびリーグ優勝した2025年をふくむ2026年3月期は、27億5400万円。",
       "確かめられた中で、最も大きい数字です。"],
      pl(1704, 5), move="in", els=[
          head("ふたたび優勝"),
          big("27億5400万円", 1060, 140, GOLD, at=0, anim="slam", sfx="boom"),
      ]),
    S(["勝つと、お金は親会社にも広がります。",
       "阪急阪神ホールディングスは、連覇を理由の1つに、今年度の営業利益の見通しを、60億円引き上げました。"],
      photo(ep15.HANKYU2, 1705, BLUEF, (0.5, 0.5), 3), move="in", els=[
          head("親会社の見通しも"),
          E(P(C.note, "※大阪梅田駅（阪急）", 30), CX, 940),
          big("1217億円 → 1277億円", 1060, 110, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    subscribe(1706, END),
]
HS1 = ep15._fix_speech(HS1)


def _say(scenes, fix):
    """ショートだけの読みの指定 (check_kana で 年→ねん だったもの)"""
    for sc in scenes:
        out = []
        for ln in sc["lines"]:
            text, sp = ln if isinstance(ln, tuple) else (ln, ln)
            for k, v in fix.items():
                sp = sp.replace(k, v)
            out.append((text, sp) if sp != text else text)
        sc["lines"] = out
    return scenes


_say(HS1, {"その年をふくむ": "そのとしをふくむ", "前の年の": "まえのとしの"})
