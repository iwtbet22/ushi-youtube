"""トレード事件簿 (本編 ep09) へつなぐショート動画 2本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_tr1   (short_tr2)

台本の文と数字は本編 (script/ep09_narration.txt と ep09_factcheck.md で確認済み) から取っている。
置き方は shorts_ep04 と同じ (x=480 中心、幅 840 以内、絵は上半分、大きな文字はその下)。
読み上げの速さと読み方の指定は本編 (ep09) と同じ。
"""
from functools import partial as P

import charts as C
import look as L
import news as N
import props as R
import ep09
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, fit, fog, head, pic


def photo(name, seed, tint=(1.0, 1.0, 1.0), focus=(0.5, 0.45), rot=-3):
    """霧の上に、白い縁の写真を1枚"""
    return pic(P(R.print_photo, name, 760, rot, focus), seed, tint, 840, 520, 640)


def swap(left, lp, right, rp, label=None):
    return P(ep09.swap, left, lp, right, rp, label, 640)


def to_main(seed):
    """最後の「続きは本編で」"""
    return S(["14件のトレード事件簿は、関連動画の本編で。"], fog(seed, GOLDF, 0.9), move="in", hold=1.0, els=[
        E(fit(P(L.text, "続きは本編で", "NotoSerifJP-Black.ttf", 100, L.GOLD)), CX, 700, anim="slam", sfx="boom"),
        E(fit(P(C.name_plate, "トレード事件簿", "下の関連動画から")), CX, 920, delay=0.6, anim="rise"),
        E(fit(P(L.text, "▼", "NotoSerifJP-Black.ttf", 90, L.GOLD)), 200, 1150, delay=1.2, anim="rise"),
    ])


# ---- 1本目：空白の一日 -------------------------------------------------------------
TR1 = [
    S(["キャンプへ向かう空港で、巨人のエースは呼び止められました。",
       "告げられたのは、ライバル球団、阪神へのトレードです。"],
      photo(ep09.HANEDA, 1101, BLUEF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("空港で告げられたトレード"),
          E(P(C.note, "※羽田空港（イメージ）", 30), CX, 940),
          big("空港で呼び止められた", 1060, 110, WHITE, until=0, anim="rise"),
          big("阪神へトレード", 1060, 150, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["始まりは、1978年のドラフトです。",
       "当時の野球協約では、交渉権を得た球団が交渉できるのは、翌年のドラフトの前々日まで、とされていました。"],
      pic(P(C.big_number, "交渉できるのは", "前々日まで", 150), 1102, GOLDF, 820, 460), move="in", els=[
          head("1978年のドラフト"),
          big("当時の野球協約", 1000, 130, GOLD, at=1, anim="rise"),
      ]),
    S(["では、ドラフトの前日は、どの球団の交渉権もない、空白の一日ではないか。",
       "巨人はこの盲点を突き、ドラフト前日の11月21日に、江川卓と契約を結びました。"],
      pic(P(R.calendar, 1978, 11, 21, "巨人が江川と契約"), 1103, REDF, 560, 460), move="in", els=[
          head("ドラフトの前日は？"),
          big("空白の一日", 1000, 160, GOLD, until=0, anim="slam", sfx="boom"),
          big("協約の盲点", 1000, 160, RED, at=1, anim="glitch", sfx="boom"),
      ]),
    S(["セ・リーグの会長は、この契約を無効と判断しました。",
       "そして、ドラフトで江川の交渉権を引き当てたのは、阪神でした。"],
      photo(ep09.KOSHIEN, 1104, GOLDF, (0.5, 0.5), 3), move="in", els=[
          head("契約は無効に"),
          E(P(C.note, "※阪神甲子園球場", 30), CX, 940),
          big("無効", 1060, 170, RED, until=0, anim="slam", sfx="boom"),
          big("交渉権は阪神に", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["混乱を収めるために、金子鋭コミッショナーが示したのが、「強い要望」です。",
       "江川はいったん阪神と契約し、そのあとすぐ、巨人へトレードする。",
       "その相手として阪神へ出されることになったのが、エースの小林繁でした。"],
      pic(swap("巨人へ", ["江川卓"], "阪神へ", ["小林繁"]), 1105, BLUEF, 840, 420), move="in", els=[
          head("コミッショナーの「強い要望」"),
          big("強い要望", 1000, 150, GOLD, until=0, anim="slam", sfx="boom"),
          big("阪神と契約→すぐ巨人へ", 1000, 100, WHITE, at=1, until=1, anim="rise"),
          big("相手は エース小林繁", 1000, 110, RED, at=2, anim="slam", sfx="boom"),
      ]),
    S(["1979年1月31日。",
       "小林は、空港から球団事務所へ連れて行かれ、トレードを告げられたのです。"],
      pic(P(R.calendar, 1979, 1, 31, "キャンプへ出発の日"), 1106, BLUEF, 560, 460), move="in", els=[
          head("1979年1月31日"),
          big("空港から球団事務所へ", 1000, 110, WHITE, at=1, anim="rise"),
      ]),
    S(["移籍1年目、小林は22勝を挙げて、最多勝と沢村賞。",
       "古巣の巨人に対しては、8戦全勝でした。"],
      pic(P(C.big_number, "移籍1年目", "22勝", 170), 1107, GOLDF, 820, 460), move="in", els=[
          head("阪神での1年目"),
          big("最多勝・沢村賞", 1000, 130, GOLD, until=0, anim="slam", sfx="boom", delay=1.2),
          big("巨人に8戦全勝", 1000, 150, RED, at=1, anim="slam", sfx="boom"),
      ]),
    to_main(1108),
]

# ---- 2本目：5年契約の2年目 ---------------------------------------------------------
TR2 = [
    S(["5年総額15億円とも報じられた契約の、まだ2年目。",
       "FAで迎えた捕手が、金銭トレードでチームを去りました。"],
      photo(ep09.KAI_HR, 1111, GOLDF, (0.5, 0.3)), move="in", trans="cut", els=[
          head("5年契約の2年目で"),
          E(P(C.note, "※甲斐拓也（2023年、ソフトバンク）", 30), CX, 940),
          big("5年 総額15億円（推定）", 1060, 100, GOLD, until=0, anim="slam", sfx="boom"),
          big("金銭トレード", 1060, 150, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["2026年10月30日。",
       "巨人の甲斐拓也が、楽天へ金銭トレードで移ることが発表されました。"],
      pic(swap("巨人", ["甲斐拓也"], "楽天", ["金銭"], "金銭"), 1112, BLUEF, 840, 420), move="in", els=[
          head("2026年10月30日"),
          big("巨人 → 楽天", 1000, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["甲斐は2024年のオフに、ソフトバンクからFAで巨人に移った捕手です。",
       "FAで選手を獲得したため、巨人は人的補償として、伊藤優輔投手をソフトバンクに譲っています。"],
      pic(P(C.move, "巨人", "ソフトバンク", "人的補償 伊藤優輔", 56, 560), 1113, BLUEF, 820, 420), move="in", els=[
          head("FAで巨人へ"),
          big("2024年オフ FA移籍", 1000, 110, WHITE, until=0, anim="rise"),
          big("人的補償も払った", 1000, 120, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["巨人1年目の2025年は、68試合に出場。",
       "しかし2026年は、出場が13試合にとどまりました。",
       "先発でマスクをかぶったのは、わずか3試合です。"],
      pic(P(C.vbars, [("2025年", 68, "68試合", False), ("2026年", 13, "13試合", True)], "試合", 420, 190, 60),
          1114, REDF, 820, 460), move="in", els=[
          head("出場試合数"),
          big("13試合", 1080, 150, RED, at=1, until=1, anim="slam", sfx="boom"),
          big("先発マスク 3試合", 1080, 120, WHITE, at=2, anim="rise"),
      ]),
    S(["FAで迎えた選手を、契約の途中で放出するのは、異例のことでした。",
       "楽天は、その前日に、捕手2人と来季の契約を結ばないと発表していました。"],
      pic(P(N.stamp, "異例", RED, 220), 1115, REDF, 700, 440), move="in", els=[
          head("契約の途中で放出"),
          big("異例のこと", 1000, 150, RED, until=0, anim="glitch", sfx="boom"),
          big("楽天は 捕手が足りない", 1000, 110, GOLD, at=1, anim="rise"),
      ]),
    S(["出場機会を失った捕手と、捕手が足りない球団。",
       "トレードは、そうした需要と供給を合わせる仕組みでもあるのです。"],
      pic(P(C.bullet_list, ["巨人：出場機会を失った捕手", "楽天：捕手が足りない"], 64, 800), 1116, GOLDF, 840, 420),
      move="in", els=[
          head("トレードの役目"),
          big("需要と供給を合わせる", 1000, 110, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    to_main(1117),
]

TR1, TR2 = (ep09._fix_speech(x) for x in (TR1, TR2))

# ショートだけの読みの指定 (check_word で聞き比べて「微妙」だったもの)
FIX = {"前々日": "ぜんぜんじつ"}
for _sc in TR1 + TR2:
    _out = []
    for _ln in _sc["lines"]:
        _text, _sp = _ln if isinstance(_ln, tuple) else (_ln, _ln)
        for _k, _v in FIX.items():
            _sp = _sp.replace(_k, _v)
        _out.append((_text, _sp) if _sp != _text else _text)
    _sc["lines"] = _out
