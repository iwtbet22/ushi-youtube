"""2本目「FAのお金と歴史 完全解説」の冒頭 (約1分)。

最初に大きな金額で引きつけ、FA の始まり (1993年・落合博満) を見せ、
本編で答える問い (なぜ生まれたか・権利の条件・補償・歴代の大型契約) を並べてからタイトルへ。
金額は球団発表ではなく報道による推定なので、画面にも「※報道による推定」を出す。
"""
from functools import partial as P

import look as L
from film import E, S

KONDO = "Kensuke_Kondoh_Hawks_20230405.jpg"
OCHIAI = "Hiromitsu_Ochiai.jpg"
MARU = "丸佳浩-20240310.jpg"
DOME = "Tokyo_Dome_2007-12.jpg"
KOSHIEN = "Hanshin_Koshien_Stadium_2009.jpg"


def question(s):
    return L.text(s, "NotoSerifJP-Black.ttf", 76, (245, 238, 225))


def rank_teaser():
    """「1位 ？」「2位 ？」「3位 ？」の札"""
    from PIL import Image, ImageDraw
    w, h = 720, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = L.font("NotoSerifJP-Black.ttf", 64)
    for i, (rank, col) in enumerate((("1位", L.GOLD), ("2位", (200, 200, 210)), ("3位", (196, 130, 80)))):
        y = 20 + i * 165
        d.rectangle((0, y, w, y + 140), fill=(0, 0, 0, 150), outline=col + (255,), width=4)
        d.text((40, y + 30), rank, font=f, fill=col)
        d.text((w - 140, y + 30), "？", font=f, fill=(255, 255, 255))
        d.line((220, y + 70, w - 180, y + 70), fill=(255, 255, 255, 90), width=3)
    return im


SCENES = [
    # 0 掴み: 金額
    S(["7年で、総額50億円。"],
      P(L.plate, DOME, "gold", focus=(0.5, 0.4)), move="in", trans="black", hold=0.6, els=[
          E(P(L.gold, "総額50億円", size=210), 960, 470, anim="slam", sfx="boom"),
          E(P(L.caption_small, "※金額は報道による推定"), 960, 680, delay=0.6),
      ]),
    # 1 近藤健介
    S(["2022年のオフ、近藤健介選手は、日本ハムからソフトバンクへ移籍しました。",
       "その契約は、7年で総額50億円規模とも報じられました。"],
      P(L.plate, KONDO, "dark", layout="right", focus=(0.5, 0.3)), move="in", els=[
          E(P(L.vertical, "近藤健介", 120), 470, 60, anim="wipe", anchor="t", delay=0.4),
          E(P(L.caption_small, "日本ハム → ソフトバンク（2022年オフ）", 38), 470, 860, anim="rise", anchor="b",
            delay=1.6, until=0),
          E(P(L.gold, "7年 総額50億円規模", size=90), 560, 870, anim="rise", at=1, anchor="b"),
      ]),
    # 2 FAとは
    S(["選手が、自分の意思で、次の球団を選ぶ。",
       "それを可能にしたのが、FA、フリーエージェントという制度です。"],
      P(L.bokeh, 3), move="in", els=[
          E(P(L.text, "自分で、次の球団を選ぶ", "NotoSerifJP-Black.ttf", 80, (245, 238, 225)), 960, 470,
            anim="fade", until=0),
          E(P(L.text, "FA", "NotoSerifJP-Black.ttf", 300, L.WHITE), 960, 400, at=1, delay=0.9, anim="glitch",
            sfx="boom"),
          E(P(L.text, "フリーエージェント", "NotoSerifJP-Black.ttf", 64, L.GOLD), 960, 640, at=1, delay=1.6,
            anim="rise"),
      ]),
    # 3 1993年
    S(["今のような形のFA制度が、日本のプロ野球に生まれたのは、1993年のことです。"],
      P(L.plate, KOSHIEN, "sepia"), move="left", els=[
          E(P(L.gold, "1993年", size=230), 960, 450, delay=2.2, anim="slam", sfx="boom"),
      ]),
    # 4 落合博満
    S(["その最初のオフに、球界を代表する大打者が動きます。",
       "落合博満選手。中日から、巨人への移籍でした。"],
      P(L.plate, OCHIAI, "sepia", layout="right", focus=(0.5, 0.3)), move="in", els=[
          E(P(L.vertical, "落合博満", 150), 470, 90, at=1, anim="wipe", anchor="t"),
          E(P(L.caption_small, "中日 → 巨人（1993年オフ）", 40), 470, 860, at=1, delay=1.4, anim="rise",
            anchor="b"),
          E(P(L.caption_small, "※写真は中日監督時代", 28), 1860, 860, anchor="br"),
      ]),
    # 5 本編の問い
    S(["なぜ、FAは生まれたのか。",
       "権利は、どうすれば手に入るのか。",
       "そして、選手が出ていくとき、元の球団には何が残るのか。"],
      P(L.plate, DOME, "cold", focus=(0.5, 0.6)), move="right", els=[
          E(P(question, "なぜ、FAは生まれたのか"), 960, 260, anim="rise"),
          E(P(question, "権利は、どうすれば手に入るのか"), 960, 450, at=1, anim="rise"),
          E(P(question, "元の球団には、何が残るのか"), 960, 640, at=2, anim="rise"),
      ]),
    # 6 ランキング予告
    S(["さらに、歴代のFA大型契約で、いちばんの大金を手にしたのは、誰なのか。"],
      P(L.plate, MARU, "dark", layout="left", focus=(0.5, 0.3)), move="in", els=[
          E(P(L.gold, "歴代 大型契約ランキング", size=78), 1350, 170, anim="fade"),
          E(rank_teaser, 1350, 560, delay=1.2, anim="rise"),
      ]),
    # 7 タイトル
    S(["今回は、プロ野球のFAの仕組みと歴史、そして歴代の大型契約まで、まとめて解説します。"],
      P(L.bokeh, 7), move="in", trans="flash", hold=1.6, els=[
          E(P(L.gold, "FA", size=300), 960, 330, anim="slam", sfx="boom"),
          E(P(L.gold, "フリーエージェント 完全解説", size=96), 960, 560, delay=0.5, anim="rise"),
          E(P(L.caption_small, "仕組み・歴史・歴代大型契約ランキング", 44), 960, 700, delay=1.0, anim="fade"),
      ]),
]
