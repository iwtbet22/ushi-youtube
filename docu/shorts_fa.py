"""FA編へつなぐショート動画 3本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_fa1   (short_fa2 / short_fa3)

どれも本編の一部を切り出し、最後に「続きは関連動画で」と本編へ誘導する。
アップロードのときに、ショートの「関連動画」に本編を設定する前提。
文字は右側のボタン (x > 900) と下側のタイトル欄 (y > 1450) を避け、x=480 を中心に置く。
"""
from functools import partial as P

import charts as C
import look as L
from ep02 import DOME, KAINO, KONDO, MARU, MORI, VICTORY, WADA, YAMAKAWA, has, ph
from film import E, S

SUGIUCHI_G = "Toshiya_Sugiuchi_on_March_24__2012.jpg"
ASAMURA = "Hideto_Asamura_2023.jpg"

CX = L.SAFE_CX


def head(s, size=84):
    """画面上の見出し (ずっと出しておく問いかけ)"""
    return P(L.text, s, "NotoSerifJP-Black.ttf", size, L.GOLD)


def big(s, size=96, color=L.WHITE):
    return P(L.text, s, "NotoSerifJP-Black.ttf", size, color)


def to_main():
    """最後の「続きは関連動画で」"""
    return [
        E(big("続きは本編で", 100, L.GOLD), CX, 700, anim="slam", sfx="boom"),
        E(P(C.name_plate, "FA完全解説", "下の関連動画から"), CX, 920, delay=0.6, anim="rise"),
        E(big("▼", 90, L.GOLD), 200, 1150, delay=1.2, anim="rise"),
    ]


# ---- 1本目：4年18億円なのに、1年目は2億1000万円？ -------------------------
SHORT1 = [
    S(["4年総額18億円。",
       "2022年のオフ、森友哉選手が、FAで西武からオリックスへ移ったときの契約です。"],
      ph(MORI, "dark", focus=(0.5, 0.3)), move="in", trans="cut", els=[
          E(head("4年18億円なのに…"), CX, 300, until=1),
          E(P(L.gold, "4年 18億円", size=150), CX, 760, until=0, anim="slam", sfx="boom"),
          E(P(C.note), CX, 900, until=0, delay=0.6),
          E(P(C.move, "西武", "オリックス", "2022年オフ", 56, 820), CX, 1100, at=1, anim="rise"),
      ]),
    S(["ところが、移籍1年目の年俸は、2億1000万円。",
       "前の年と、まったく同じでした。"],
      ph(MORI, "dark", focus=(0.5, 0.3)), move="in", trans="cut", els=[
          E(head("1年目の年俸は？"), CX, 300),
          E(P(C.money_bars, [("1年目", 2.1, False), ("4年総額", 18, True)], "億円", 840), CX, 760, anim="rise"),
          E(big("前の年と同じ", 100, L.GOLD), CX, 1050, at=1, anim="slam", sfx="boom"),
      ]),
    S(["実はFAには、移籍1年目の年俸は、前の年を超えてはいけない、というルールがあります。",
       "球団どうしが、年俸をつり上げ合うのを防ぐためです。"],
      ph(DOME, "dark"), move="in", els=[
          E(head("FAの決まり"), CX, 300),
          E(P(L.scroll, "現状維持", "1年目は前の年まで"), CX, 760, anim="zoom", sfx="boom"),
          E(P(C.note, "FA規約 第7条", 34), CX, 1000, delay=1.0),
      ]),
    S(["でも、2年目以降の年俸や、出来高には、制限がありません。",
       "だからFAの契約は、何年で総額いくら、と語られるのです。"],
      P(L.bokeh, 201), move="in", els=[
          E(head("抜け道"), CX, 300),
          E(P(C.bullet_list, ["2年目以降の年俸", "出来高", "契約年数"], 64, 760), CX, 760, anim="rise"),
          E(big("→ 総額で大きくなる", 80, L.GOLD), CX, 1080, at=1, anim="rise"),
      ]),
    S(["FAには、ほかにもお金のルールがたくさんあります。続きは、関連動画のFA完全解説で。"],
      P(L.bokeh, 202), move="in", hold=1.0, els=to_main()),
]

# ---- 2本目：人的補償、42歳の大ベテランが指名される？ ------------------------
SHORT2 = [
    S(["2024年の1月、プロ野球の補償をめぐって、大きな騒ぎが起きました。",
       "西武の山川穂高選手が、FAでソフトバンクへ移籍。",
       "西武は補償として、ソフトバンクから選手を1人選べることになります。"],
      ph(YAMAKAWA, "dark", focus=(0.5, 0.3)), move="in", trans="cut", els=[
          E(head("人的補償の大騒動"), CX, 300),
          E(P(L.gold, "2024年1月", size=140), CX, 760, until=0, anim="slam", sfx="boom"),
          E(P(C.move, "西武", "ソフトバンク", "FA", 56, 820), CX, 1100, at=1, until=1, anim="rise"),
          E(P(L.scroll, "人的補償", "選手を1人もらえる"), CX, 800, at=2, anim="zoom"),
      ]),
    S(["1月11日、一部のスポーツ紙が、西武は42歳の大ベテラン、和田毅投手を指名する方針と報じます。",
       "ファンは騒然。"],
      ph(WADA, "dark", focus=(0.5, 0.3)), move="in", els=[
          E(head("指名されたのは…"), CX, 300),
          E(P(L.vertical, "和田毅", 120), 160, 450, anim="wipe", anchor="t", delay=1.5),
          E(P(L.gold, "42歳の大ベテラン", size=84), CX, 1100, delay=3.0, until=0, anim="rise"),
          E(big("騒然", 170, L.GOLD), CX, 1080, at=1, anim="glitch", sfx="boom"),
      ]),
    S(["しかし、その日に西武が発表したのは、別の選手、甲斐野央投手でした。",
       "指名が変わった理由は、説明されていません。"],
      ph(KAINO, "dark", focus=(0.5, 0.3)), move="in", els=[
          E(head("発表されたのは"), CX, 300),
          E(P(L.vertical, "甲斐野央", 120), 160, 450, anim="wipe", anchor="t", delay=2.0),
          E(big("理由は説明されず", 84, L.GOLD), CX, 1100, at=1, anim="rise"),
      ]),
    S(["この騒動もきっかけに、人的補償をなくす議論が動き出し、今も話し合いが続いています。"],
      ph(VICTORY, "cold", layout="blur", seed=203), move="in", els=[
          E(head("その後"), CX, 300),
          E(P(L.gold, "人的補償の撤廃論", size=96), CX, 760, anim="slam", sfx="boom"),
          E(P(C.name_plate, "2026年 今も協議中", "今オフは今の制度のまま"), CX, 1000, delay=1.2, anim="rise"),
      ]),
    S(["人的補償のルールと、これまでのドラマは、関連動画のFA完全解説で。"],
      P(L.bokeh, 204), move="in", hold=1.0, els=to_main()),
]

# ---- 3本目：FA大型契約 歴代トップ3 -----------------------------------------
def card(rank, name, line, amount, photo=None):
    return P(C.rank_card, rank, name, [line], amount, photo if photo and has(photo) else None, (0.5, 0.25), 360, 840)


SHORT3 = [
    S(["プロ野球のFA、歴代の大型契約トップ3です。"],
      P(L.bokeh, 205), move="in", trans="cut", els=[
          E(head("FA大型契約"), CX, 300),
          E(P(L.gold, "歴代 TOP3", size=170), CX, 800, anim="slam", sfx="boom"),
          E(P(C.note), CX, 1000, delay=1.0),
      ]),
    S(["第3位は、同じ金額で2人。",
       "ソフトバンクから巨人へ移った、杉内俊哉投手。",
       "西武から楽天へ移った、浅村栄斗選手。",
       "どちらも、4年総額20億円です。"],
      ph(DOME, "dark"), move="in", els=[
          E(head("第3位"), CX, 300),
          E(card(3, "杉内俊哉", "ソフトバンク → 巨人（2011年）", "4年 20億円", SUGIUCHI_G), CX, 620, at=1,
            anim="rise", sfx="whoosh"),
          E(card(3, "浅村栄斗", "西武 → 楽天（2018年）", "4年 20億円", ASAMURA), CX, 1010, at=2, anim="rise",
            sfx="whoosh"),
      ]),
    S(["第2位、丸佳浩選手。広島から巨人へ、5年総額25億5000万円。"],
      ph(MARU, "dark", focus=(0.5, 0.3)), move="in", els=[
          E(head("第2位"), CX, 300),
          E(card(2, "丸佳浩", "広島 → 巨人（2018年）", "5年 25.5億円"), CX, 1000, anim="rise", sfx="whoosh"),
      ]),
    S(["そして第1位。",
       "近藤健介選手。日本ハムからソフトバンクへ、7年総額50億円規模。",
       "2位の、およそ2倍です。"],
      ph(KONDO, "gold", focus=(0.5, 0.3)), move="in", els=[
          E(head("第1位"), CX, 300),
          E(P(L.gold, "第1位", size=200), CX, 800, until=0, anim="slam", sfx="boom"),
          E(card(1, "近藤健介", "日本ハム → ソフトバンク（2022年）", "7年 50億円規模"), CX, 1000, at=1, anim="rise",
            sfx="whoosh"),
          E(big("2位の約2倍", 100, L.GOLD), CX, 700, at=2, anim="slam", sfx="boom"),
      ]),
    S(["金額は報道による推定です。続きのランキングは、関連動画のFA完全解説で。"],
      P(L.bokeh, 206), move="in", hold=1.0, els=to_main()),
]
