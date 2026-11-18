"""チャンネル紹介動画（チャンネル登録していない人向け。チャンネルのホームのいちばん上に出る）。約75秒。

  python3 docu/film.py trailer --qa / bash tools/enc.sh trailer <場面の数>

数字は各回の台本・調査（確認済み）から取る：セ・リーグ編(ep06)、契約更改事件簿(ep03)、球場編(ep12)、MLB編(ep10)。
"""
from functools import partial as P

import charts as C
import look as L
import props as R
import ep05
import ep10
from ep04 import _arrange
from ep05 import FOG, A, W, SC, REDF, BLUEF, GOLDF
from ep06 import BIG, BULLETS, VB
from film import E, S

RED = (226, 52, 44)
WHITE = L.WHITE
GOLD = L.GOLD
NAME = "球界金融道"

TOKYODOME = "Tokyo_Dome_2007-12.jpg"
ESCON = "ES_CON_FIELD_HOKKAIDO_exterior_from_south_202607a.jpg"
CITI = "Citi_Field_from_the_south_2025.jpg"
KOSHIEN = ep05.KOSHIEN

SCENES = [
    SC(["巨人の決算書、見たことがありますか。",
        "実は、公表されていません。"],
       [(0, A(TOKYODOME, (0.5, 0.5))), (1, FOG(REDF, 0.85))], trans="cut", els=[
           W("巨人の決算書", 0, GOLD, 170, 760), W("公表されていない", 1, RED, 170),
       ], notes=[(0, "※東京ドーム")]),
    SC(["年俸6億円の投手に、球団が示したのは、1億円。"],
       [(0, VB([("前の年", 6, "6億円", False), ("球団の提示", 1, "1億円", True)], "億円"))], els=[
           W("5億円の減額提示", 0, RED, 150, 820),
       ]),
    SC(["球団は12億円の赤字。それなのに、球場の会社は71億円の黒字。"],
       [(0, A(ESCON, (0.5, 0.5)))], els=[
           W("球団は赤字 球場は黒字", 0, GOLD, 140, 760),
       ], notes=[(0, "※エスコンフィールドHOKKAIDO")]),
    SC(["メジャーで年俸総額1位の球団は、地区最下位でした。"],
       [(0, A(CITI, (0.5, 0.5)))], els=[
           W("年俸1位が最下位", 0, WHITE, 150, 760),
       ], notes=[(0, "※シティ・フィールド（メッツの本拠地）")]),
    SC(["球界金融道では、プロ野球のお金と制度のしくみを、数字で解説しています。",
        "球団は儲かってるのか、契約更改やトレードの事件簿、そしてメジャーのお金。"],
       [(0, P(L.bokeh, 1301)), (1, BULLETS(["球団は儲かってるのか", "契約更改・トレードの事件簿", "メジャーのお金"], 72))],
       els=[
           E(P(L.gold, NAME, size=130), 960, 360, until=0, anim="zoom", sfx="boom"),
           W("プロ野球のお金と制度を 数字で", 0, WHITE, 90, 560),
       ]),
    SC(["3日に1本、新しい動画を出しています。",
        "チャンネル登録をして、次の動画もお楽しみに。"],
       [(0, P(L.bokeh, 1302))], hold=1.5, els=[
           E(P(L.gold, NAME, size=110), 960, 260, anim="rise"),
           W("3日に1本 更新", 0, WHITE, 120, 440),
           E(ep05._cta, 960, 600, at=1, delay=0.3, anim="none", dyn=True),
       ]),
]

SPEECH_FIX = dict(ep10.SPEECH_FIX)
SPEECH_FIX.update({"球界金融道": "きゅうかいきんゆうどう", "1本": "いっぽん"})


def _fix_speech(scenes):
    import readings
    keys = sorted(SPEECH_FIX, key=len, reverse=True)
    for sc in scenes:
        out = []
        for line in sc["lines"]:
            text, sp = (line if isinstance(line, tuple) else (line, readings.speech(line)))
            for k in keys:
                sp = sp.replace(k, SPEECH_FIX[k])
            out.append((text, sp) if sp != text else text)
        sc["lines"] = out
    return scenes


SCENES = _arrange(ep05._finish(_fix_speech(SCENES)))
