"""黒い霧事件 (本編 ep04) へつなぐショート動画 2本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_kw1   (short_kw2)

台本の文と数字は本編 (script/ep04_narration.txt, ep04_factcheck.md で確認済み) から取っている。
文字は右側のボタン (x > 900) と下側のタイトル欄 (y > 1450) を避け、x=480 を中心に、幅 840 以内に収める。
絵は上半分 (y 450〜1000) に置き、大きな文字はその下に出す。
"""
from functools import partial as P

import charts as C
import look as L
import news as N
import props as R
from ep03 import _shrink
from ep04 import IKENAGA, kw
from film import E, S

CX = L.SAFE_CX
MAXW = 840
RED, GOLD, WHITE = N.RED, N.GOLD, N.WHITE
REDF, GOLDF, BLUEF = (1.25, 0.75, 0.7), (1.2, 1.05, 0.75), (0.75, 0.9, 1.25)


def fit(fn, w=MAXW):
    return P(_shrink, fn, w)


def head(s, size=84):
    """画面上の見出し (ずっと出しておく問いかけ)"""
    return E(fit(P(L.text, s, "NotoSerifJP-Black.ttf", size, L.GOLD)), CX, 280)


def big(s, y=980, size=120, color=WHITE, **k):
    return E(fit(kw(s, size, color)), CX, y, **k)


def fog(seed, tint=(1.0, 1.0, 1.0), dark=0.8):
    return P(R.fog, seed, tint, dark)


def pic(fn, seed, tint=(1.0, 1.0, 1.0), w=820, h=460, y=640):
    """霧の上に絵を1枚 (画面の上半分)"""
    return P(N.compose, fog(seed, tint, 0.55), (P(R.fit, fn, w, h), CX, y))


def to_main(seed):
    """最後の「続きは本編で」"""
    return S(["黒い霧事件の全体は、関連動画の本編で。"], fog(seed, GOLDF, 0.9), move="in", hold=1.0, els=[
        E(fit(P(L.text, "続きは本編で", "NotoSerifJP-Black.ttf", 100, L.GOLD)), CX, 700, anim="slam", sfx="boom"),
        E(fit(P(C.name_plate, "黒い霧事件", "下の関連動画から")), CX, 920, delay=0.6, anim="rise"),
        E(fit(P(L.text, "▼", "NotoSerifJP-Black.ttf", 90, L.GOLD)), 200, 1150, delay=1.2, anim="rise"),
    ])


# ---- 1本目：100万円を返さなかっただけで、永久追放 -------------------------------
SHORT1 = [
    S(["受け取った100万円を、返さなかった。",
       "それだけで、プロ野球から永久追放されたエースがいます。"],
      pic(P(R.envelope, "", 811, True), 811), move="in", trans="cut", els=[
          head("100万円で永久追放"),
          big("100万円", 980, 170, GOLD, until=0, anim="slam", sfx="boom"),
          big("永久追放", 980, 170, RED, at=1, anim="glitch", sfx="boom"),
      ]),
    S([("池永正明。1965年に西鉄に入り、1年目から20勝を挙げて新人王。", "池永正明。1965年に西鉄に入り、1年目から20しょうを挙げて新人王。"),
       "入団から5年で99勝。",
       "西鉄の大エース、稲尾和久さんの後継者と言われた投手でした。"],
      pic(P(R.print_photo, IKENAGA, 760, -3, (0.5, 0.3)), 812, BLUEF, 820, 480, 640), move="in", els=[
          head("西鉄のエース 池永正明"),
          E(P(C.note, "※池永正明（1965年）", 30), CX, 370),
          big("1年目 20勝・新人王", 980, 100, GOLD, until=0, anim="rise", delay=1.5),
          big("5年で99勝", 980, 150, GOLD, at=1, until=1, anim="slam", sfx="boom"),
          big("稲尾の後継者", 980, 120, WHITE, at=2, anim="rise"),
      ]),
    S(["1969年から、プロ野球は八百長事件、黒い霧事件に揺れます。",
       "池永投手は、中日の田中勉投手から、100万円を渡されました。",
       "お金を受け取ったことは認めましたが、八百長はしていないと言い続けました。"],
      pic(P(R.bills, 4, 813), 813, REDF), move="in", els=[
          head("黒い霧事件"),
          big("八百長事件", 980, 140, RED, until=0, anim="glitch", sfx="boom"),
          big("100万円", 980, 160, GOLD, at=1, until=1, anim="slam", sfx="boom"),
          big("八百長はしていない", 980, 100, WHITE, at=2, anim="rise"),
      ]),
    S(["1970年5月25日。池永投手は、永久追放になります。",
       "理由は、受け取った100万円を返さなかったこと。",
       "そして、八百長に誘われたことを報告しなかったこと。",
       "このとき、まだ23歳でした。"],
      pic(P(R.calendar, 1970, 5, 25, "永久追放"), 814, REDF, 700, 460), move="in", els=[
          head("処分の理由"),
          big("永久追放", 980, 170, RED, until=0, anim="glitch", sfx="boom"),
          big("返さなかった", 980, 140, GOLD, at=1, until=1, anim="slam"),
          big("報告しなかった", 980, 130, GOLD, at=2, until=2, anim="slam"),
          big("まだ23歳", 980, 160, WHITE, at=3, anim="rise"),
      ]),
    S(["処分が解かれたのは、2005年。",
       "追放から、35年がたっていました。"],
      pic(P(R.timeline, "1970", "2005", "35年", "永久追放 → 復権"), 815, GOLDF, 860, 420), move="in", els=[
          head("そして"),
          big("2005年 復権", 980, 140, GOLD, until=0, anim="rise"),
          big("35年後", 980, 190, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    to_main(816),
]

# ---- 2本目：オーナーが渡した550万円 -------------------------------------------
SHORT2 = [
    S(["球団のオーナーが、八百長をした選手に、550万円を渡していました。"],
      pic(P(R.bills, 5, 821), 821, GOLDF), move="in", trans="cut", els=[
          head("オーナーが渡したお金"),
          big("550万円", 980, 190, GOLD, delay=2.2, anim="slam", sfx="boom"),
      ]),
    S([("1969年、西鉄ライオンズの永易将之投手は、八百長を報じられたその日から、姿を消します。",
        "1969年、西鉄ライオンズの永易まさゆき投手は、八百長を報じられたその日から、姿を消します。"),
       "本人がいないまま、わざと負けたことを理由にした、プロ野球で初めての永久追放となりました。"],
      pic(P(R.magazine, ["西鉄・永易投手", "八百長か", "本人は行方不明"], 822), 822), move="in", els=[
          head("消えた投手"),
          E(P(C.note, "※イメージ", 30), CX, 370),
          big("姿を消す", 980, 160, WHITE, until=0, anim="glitch", delay=3.0, sfx="whoosh"),
          big("史上初の永久追放", 980, 110, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["国会では、暴力団に監禁されているのでは、とまで言われました。",
       "ところが本人は、恋人と札幌で、ひっそりと暮らしていました。"],
      fog(823, BLUEF, 0.8), move="in", els=[
          head("行方不明のまま"),
          big("監禁説まで", 980, 150, RED, until=0, anim="glitch", sfx="boom"),
          big("札幌で暮らしていた", 980, 110, WHITE, at=1, anim="rise"),
      ]),
    S(["翌年の春、永易投手は告白します。",
       "八百長は、やった。そして、西鉄の球団から、550万円を受け取っていた。",
       "オーナーからは、何も言うな、一生面倒を見る、と言われていたといいます。"],
      pic(P(R.envelope, "", 824, True), 824, GOLDF), move="in", els=[
          head("永易投手の告白"),
          E(P(C.note, "※永易投手の主張", 30), CX, 370),
          big("八百長は、やった", 980, 120, RED, at=1, until=1, anim="slam", sfx="boom"),
          big("「一生面倒を見る」", 980, 110, GOLD, at=2, anim="rise"),
      ]),
    S(["オーナーは、はじめは全面否定でした。",
       "しかし4月末、お金を渡していたことを認めます。",
       "その額は、550万円。永易投手の言った金額と、ぴたりと一致していました。",
       "5月、オーナーは辞任しました。"],
      pic(P(R.scoreboard, [("永易の告白", "550万円"), ("オーナー", "550万円")], "ぴたり一致"), 825), move="in", els=[
          head("否定から一転"),
          big("全面否定", 980, 150, WHITE, until=0, anim="rise"),
          big("認めた", 980, 170, RED, at=1, until=1, anim="slam", sfx="boom"),
          big("ぴたり一致", 980, 150, GOLD, at=2, until=2, anim="slam", sfx="boom"),
          big("オーナー辞任", 980, 140, RED, at=3, anim="glitch"),
      ]),
    to_main(826),
]
