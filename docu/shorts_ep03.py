"""契約更改事件簿へつなぐショート動画 3本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_kk1   (short_kk2 / short_kk3)

どれも本編の事件簿の1件を切り出し、最後に「続きは関連動画で」と本編へ誘導する。
台本の文と数字は本編 (script/ep03_narration.txt, ep03_factcheck.md で確認済み) から取っている。
文字は右側のボタン (x > 900) と下側のタイトル欄 (y > 1450) を避け、x=480 を中心に、幅 840 以内に収める。
"""
from functools import partial as P

import charts as C
import look as L
from ep02 import NAGOYA, SENGA, ph
from ep03 import KANEKO, NAKAMURA_N, _shrink
from film import E, S

CX = L.SAFE_CX
MAXW = 840


def fit(fn):
    return P(_shrink, fn, MAXW)


def head(s, size=84):
    """画面上の見出し (ずっと出しておく問いかけ)"""
    return fit(P(L.text, s, "NotoSerifJP-Black.ttf", size, L.GOLD))


def big(s, size=96, color=L.WHITE):
    return fit(P(L.text, s, "NotoSerifJP-Black.ttf", size, color))


def gold(s, size=130):
    return fit(P(L.gold, s, size=size))


def name_v(s, at=0, until=None, delay=0.3):
    return E(P(L.vertical, s, 110), 150, 450, at=at, until=until, delay=delay, anim="wipe", anchor="t")


def note(s="※金額は報道による推定", y=1360):
    return E(P(C.note, s, 32), CX, y)


def to_main():
    """最後の「続きは関連動画で」"""
    return [
        E(big("続きは本編で", 100, L.GOLD), CX, 700, anim="slam", sfx="boom"),
        E(fit(P(C.name_plate, "契約更改 事件簿", "下の関連動画から")), CX, 920, delay=0.6, anim="rise"),
        E(big("▼", 90, L.GOLD), 200, 1150, delay=1.2, anim="rise"),
    ]


# ---- 1本目：年俸6億円のエースに、提示は1億円 ---------------------------------
SHORT1 = [
    S(["年俸6億円とも報じられたエースに、球団が示した金額は、1億円でした。"],
      ph(KANEKO, "dark", focus=(0.5, 0.25)), move="in", trans="cut", els=[
          E(head("6億円のエースに…"), CX, 300),
          E(gold("提示 1億円", 150), CX, 800, delay=2.6, anim="slam", sfx="boom"),
          note(),
      ]),
    S(["2018年のオフ、オリックスのエース、金子千尋投手。",
       "年俸は5億円とも6億円とも報じられていました。",
       "しかし、このシーズンの成績は4勝7敗でした。"],
      ph(KANEKO, "dark", focus=(0.5, 0.25)), move="in", els=[
          E(head("2018年オフ"), CX, 300),
          name_v("金子千尋", until=0),
          E(gold("年俸 5億〜6億円", 110), CX, 800, at=1, until=1, anim="rise"),
          E(gold("4勝7敗", 170), CX, 800, at=2, anim="slam", sfx="boom"),
          note(),
      ]),
    S(["5億円という減額の提示は、プロ野球の歴史で最も大きなものです。",
       "減額のルールでは、1億円を超える年俸は、40%までしか下げられません。",
       "それを大きく超える提示でした。"],
      P(L.bokeh, 311), move="in", els=[
          E(head("史上最大の減額提示"), CX, 300),
          E(gold("5億円減", 180), CX, 760, until=0, anim="slam", sfx="boom"),
          E(fit(P(L.scroll, "減額制限", "1億円超は40%まで")), CX, 780, at=1, until=1, anim="zoom"),
          E(big("大きく超える提示", 100, L.GOLD), CX, 780, at=2, anim="rise"),
      ]),
    S(["金子投手は同意せず、自由契約となって、日本ハムへ移籍しました。"],
      ph(KANEKO, "dark", focus=(0.5, 0.25)), move="in", els=[
          E(head("その結末"), CX, 300),
          E(fit(P(C.move, "オリックス", "日本ハム", "自由契約", 56, 820)), CX, 900, delay=1.0, anim="rise",
            sfx="whoosh"),
      ]),
    S(["契約更改の歴史に残る事件は、関連動画の契約更改事件簿で。"],
      P(L.bokeh, 312), move="in", hold=1.0, els=to_main()),
]

# ---- 2本目：年俸2億円から400万円、そして日本シリーズMVP ----------------------
SHORT2 = [
    S(["年俸2億円から、400万円になった強打者がいます。"],
      ph(NAKAMURA_N, "dark", focus=(0.5, 0.25)), move="in", trans="cut", els=[
          E(head("2億円から…"), CX, 300),
          E(fit(P(C.big_number, "2億円", "400万円", 150)), CX, 820, delay=1.2, anim="rise", sfx="boom"),
          E(P(C.note, "※写真は横浜時代", 30), CX, 1360),
      ]),
    S(["2006年のオフ、オリックスの中村紀洋選手は、60%減の提示を受けたと報じられました。",
       "中村選手はこれを受け入れず、自由契約になります。"],
      ph(NAKAMURA_N, "dark", focus=(0.5, 0.25)), move="in", els=[
          E(head("2006年オフ"), CX, 300),
          name_v("中村紀洋", until=0, delay=1.5),
          E(gold("60%減の提示", 130), CX, 1080, delay=2.5, until=0, anim="slam", sfx="boom"),
          E(P(C.note, "減額制限は40%まで", 34), CX, 1200, delay=3.0, until=0),
          E(big("自由契約に", 120, L.GOLD), CX, 800, at=1, anim="rise"),
          E(P(C.note, "※写真は横浜時代", 30), CX, 1360),
      ]),
    S(["手を差し伸べたのは、中日でした。",
       "入団テストを経て結んだのは、育成選手としての契約。",
       "背番号は205、年俸は400万円でした。"],
      ph(NAGOYA, "dark"), move="in", els=[
          E(head("拾ったのは中日"), CX, 300),
          E(fit(P(L.scroll, "育成選手", "入団テストを経て")), CX, 780, at=1, until=1, anim="zoom"),
          E(gold("背番号205", 140), CX, 720, at=2, anim="slam", sfx="boom"),
          E(gold("年俸400万円", 140), CX, 900, at=2, delay=1.2, anim="slam", sfx="boom"),
      ]),
    S(["しかし中村選手は、ここから這い上がります。",
       "そのシーズン、中日は日本一に。",
       "日本シリーズのMVPに選ばれたのは、中村紀洋選手でした。"],
      ph(NAGOYA, "gold", layout="blur", seed=313), move="in", els=[
          E(head("その年"), CX, 300),
          E(big("ここから、這い上がる", 100), CX, 780, until=0, anim="rise"),
          E(gold("2007年 中日 日本一", 110), CX, 780, at=1, until=1, anim="slam", sfx="boom"),
          E(gold("日本シリーズ MVP", 120), CX, 780, at=2, anim="slam", sfx="boom"),
      ]),
    S(["契約更改の歴史に残る事件は、関連動画の契約更改事件簿で。"],
      P(L.bokeh, 314), move="in", hold=1.0, els=to_main()),
]

# ---- 3本目：年俸270万円から6億円へ -----------------------------------------
SHORT3 = [
    S(["年俸270万円から、6億円へ。"],
      ph(SENGA, "dark", focus=(0.5, 0.25)), move="in", trans="cut", els=[
          E(head("およそ220倍"), CX, 300),
          E(fit(P(C.big_number, "270万円", "6億円", 160)), CX, 820, anim="rise", sfx="boom"),
          note(),
      ]),
    S(["2010年、育成ドラフトの4位でソフトバンクに入った、千賀滉大投手。",
       "育成選手としての年俸は、270万円と報じられています。"],
      ph(SENGA, "dark", focus=(0.5, 0.25)), move="in", els=[
          E(head("2010年 育成4位"), CX, 300),
          name_v("千賀滉大", until=0, delay=2.0),
          E(gold("年俸270万円", 140), CX, 800, at=1, anim="slam", sfx="boom"),
          E(P(C.note, "※写真はメッツ時代", 30), CX, 1360),
      ]),
    S(["2年目に支配下の選手になると、毎年の契約更改で、年俸を積み上げていきます。",
       "そして2022年、年俸は6億円に。",
       "およそ220倍です。"],
      P(L.bokeh, 315), move="in", els=[
          E(head("契約更改のたびに"), CX, 300),
          E(fit(P(C.flow, ["育成", "支配下", "年俸\n6億円"], 2, 240, 140, 60)), CX, 780, until=0, anim="rise"),
          E(gold("2022年 6億円", 130), CX, 780, at=1, until=1, anim="slam", sfx="boom"),
          E(gold("約220倍", 200), CX, 780, at=2, anim="slam", sfx="boom"),
          note(),
      ]),
    S(["このオフ、千賀投手は海外FA権を使い、メッツと5年総額7500万ドルの契約を結びました。"],
      ph(SENGA, "gold", focus=(0.5, 0.25)), move="in", els=[
          E(head("そして世界へ"), CX, 300),
          E(fit(P(C.move, "ソフトバンク", "メッツ", "5年 7500万ドル", 56, 820)), CX, 900, delay=1.5, anim="rise",
            sfx="whoosh"),
          E(P(C.note, "※写真はメッツ時代", 30), CX, 1360),
      ]),
    S(["契約更改の歴史に残る事件は、関連動画の契約更改事件簿で。"],
      P(L.bokeh, 316), move="in", hold=1.0, els=to_main()),
]
