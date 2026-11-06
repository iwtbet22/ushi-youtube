"""メジャー契約の方法 (本編 ep05) へつなぐショート動画 2本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_ml1   (short_ml2)

台本の文と数字は本編 (script/ep05_narration.txt, ep05_factcheck.md で確認済み) から取っている。
置き方は shorts_ep04 と同じ (x=480 中心、幅 840 以内、絵は上半分、大きな文字はその下)。
"""
from functools import partial as P

import charts as C
import look as L
import props as R
from ep05 import PF
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, fit, fog, head, pic


def card(name, sub, y, delay=0.4, w=700, **k):
    return E(fit(PF(name, sub), w), CX, y, delay=delay, anim="rise", sfx="whoosh", **k)


def to_main(seed):
    """最後の「続きは本編で」"""
    return S(["メジャーと契約する4つの道は、関連動画の本編で。"], fog(seed, GOLDF, 0.9), move="in", hold=1.0, els=[
        E(fit(P(L.text, "続きは本編で", "NotoSerifJP-Black.ttf", 100, L.GOLD)), CX, 700, anim="slam", sfx="boom"),
        E(fit(P(C.name_plate, "メジャーと契約する方法", "下の関連動画から")), CX, 920, delay=0.6, anim="rise"),
        E(fit(P(L.text, "▼", "NotoSerifJP-Black.ttf", 90, L.GOLD)), 200, 1150, delay=1.2, anim="rise"),
    ])


# ---- 1本目：5111万1111ドルの理由 ---------------------------------------------
SHORT1 = [
    S(["5111万1111ドル。",
       "なぜ、こんな細かい数字になったのでしょうか。"],
      pic(P(R.scoreboard, [("入札額", "5111万1111ドル")], "2006年"), 911, GOLDF), move="in", trans="cut", els=[
          head("1が並んだ入札額"),
          big("なぜこの数字？", 980, 130, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["昔のポスティングは、入札制でした。",
       "メジャーの球団が、交渉する権利に値段をつけて入札し、最高額をつけた1球団だけが、選手と交渉できる。"],
      pic(P(R.envelope, "入札", 912), 912), move="in", els=[
          head("昔のポスティング"),
          big("入札制", 980, 170, GOLD, until=0, anim="slam", sfx="boom"),
          big("最高額の1球団だけ", 980, 110, WHITE, at=1, anim="rise"),
      ]),
    S(["2006年オフ、西武の松坂大輔投手。",
       "レッドソックスの入札額は、5111万1111ドル。",
       "1が並んだ、この細かい数字は、ライバルの入札をわずかでも上回るためだったと言われています。"],
      fog(913, REDF, 0.8), move="in", els=[
          head("2006年 松坂大輔"),
          card("松坂大輔", "2006年 西武→レッドソックス", 600),
          big("5111万1111ドル", 980, 120, GOLD, at=1, until=1, anim="slam", sfx="boom"),
          big("ライバルをわずかに上回る", 980, 90, WHITE, at=2, anim="rise"),
      ]),
    S(["2000年のイチロー選手は、1312万5000ドル。",
       "2011年のダルビッシュ有投手には、約5170万ドル。",
       "入札額は、どんどん高くなっていきました。"],
      fog(914, BLUEF, 0.8), move="in", els=[
          head("入札額の移り変わり"),
          card("イチロー", "2000年 1312万5000ドル", 600, until=0),
          card("ダルビッシュ有", "2011年 約5170万ドル", 600, at=1, until=1),
          E(P(R.fit, P(C.vbars, [("イチロー", 1312.5, "1312万ドル", False), ("松坂", 5111.1, "5111万ドル", False),
                                ("ダルビッシュ", 5170, "5170万ドル", True)], "万ドル", 470), 760, 440), CX, 640, at=2,
            anim="rise"),
          big("どんどん高く", 980, 150, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    S(["しかし、交渉できるのは1球団だけ。",
       "選手は、球団を選べませんでした。",
       "そこで2013年、制度が大きく変わり、選手が球団を選べるようになったのです。"],
      pic(P(R.timeline, "1998", "2013", "15年", "入札制 → 上限つき"), 915, GOLDF, 860, 420), move="in", els=[
          head("そして2013年"),
          big("交渉は1球団だけ", 980, 120, RED, until=0, anim="slam", sfx="boom"),
          big("球団を選べない", 980, 130, RED, at=1, until=1, anim="glitch"),
          big("選手が球団を選べる", 980, 110, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    to_main(916),
]

# ---- 2本目：12月1日で交渉が止まる？ -------------------------------------------
SHORT2 = [
    S(["12月1日。",
       "この日付が、佐藤輝明選手たちのメジャー挑戦を、大きく左右するかもしれません。"],
      pic(P(R.calendar, 2026, 12, 1, None), 921, REDF, 700, 460), move="in", trans="cut", els=[
          head("12月1日に何が？"),
          big("12月1日", 980, 190, RED, until=0, anim="slam", sfx="boom"),
          big("メジャー挑戦を左右", 980, 110, WHITE, at=1, anim="rise"),
      ]),
    S([("現地11月2日、阪神の佐藤輝明選手、西武の平良海馬投手、日本ハムの伊藤大海投手の3人が、ポスティングで公示されました。",
        "現地11月2日、阪神の佐藤輝明選手、西武のたいらかいま投手、日本ハムの伊藤ひろみ投手の3人が、ポスティングで公示されました。"),
       "本来なら、交渉の期限は12月中旬です。"],
      fog(922, BLUEF, 0.8), move="in", els=[
          head("ポスティングの3人"),
          card("佐藤輝明", "阪神", 470, 0.4, 480, until=0),
          card("平良海馬", "西武", 730, 1.2, 480, until=0),
          card("伊藤大海", "日本ハム", 990, 2.0, 480, until=0),
          big("期限は12月中旬", 980, 130, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["ところが今年は、メジャーの労使協定が、12月1日で切れます。",
       "新しい協定がまとまらず、オーナー側がロックアウト、つまり締め出しに踏み切れば、選手との交渉はすべて止まります。"],
      pic(P(R.calendar, 2026, 12, 1, "労使協定が切れる"), 923, REDF, 700, 460), move="in", els=[
          head("労使協定が切れる"),
          big("ロックアウト", 980, 160, RED, at=1, anim="glitch", sfx="boom"),
      ]),
    S(["2021年のオフにも、同じことがありました。",
       "このときは、ポスティング中の選手の交渉期間が、ロックアウトが終わるまで止められました。",
       "広島の鈴木誠也選手は、ロックアウトが終わった翌年の3月に、カブスと契約しています。"],
      fog(924, BLUEF, 0.8), move="in", els=[
          head("2021年にも"),
          big("2021年 ロックアウト", 980, 110, RED, until=0, anim="glitch", sfx="boom"),
          big("交渉期間を一時停止", 980, 110, GOLD, at=1, until=1, anim="slam", sfx="boom"),
          card("鈴木誠也", "2022年3月 カブスと契約", 600, at=2),
      ]),
    S(["しかし今年は、メジャー側が、交渉期間を止めることを拒否したと報じられています。",
       "12月1日までに契約がまとまらなければ、その時点で交渉は凍結。",
       "3人に残された時間は、実質で1か月ほどかもしれないのです。"],
      pic(P(R.timeline, "11月2日", "12月1日", "約1か月"), 925, REDF, 860, 420), move="in", els=[
          head("今年は止めない"),
          E(P(C.note, "※2026年11月3日時点の報道", 30), CX, 370),
          big("止めない", 980, 170, RED, until=0, anim="slam", sfx="boom"),
          big("交渉は凍結", 980, 150, RED, at=1, until=1, anim="glitch"),
          big("実質1か月", 980, 170, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    to_main(926),
]
