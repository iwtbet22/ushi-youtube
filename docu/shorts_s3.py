"""長尺 (10本目 MLB編・8本目 マイナー編・11本目 球界再編) に合わせたショート 3本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_lt1   (short_mn1, short_st1)

台本の文と数字は、本編の台本 (script/ep10・ep08・ep11_narration.txt。出典は各回の factcheck) から取っている。
置き方は shorts_ep09 と同じ。最後は本編への誘導ではなく、チャンネル登録をお願いして締める
(本編への移動はほとんど起きていないため。2026-11 のアナリティクス)。
"""
from functools import partial as P

import charts as C
import look as L
import news as N
import props as R
import ep08
import ep10
import ep11
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, fit, fog, head, pic


def photo(name, seed, tint=(1.0, 1.0, 1.0), focus=(0.5, 0.45), rot=-3):
    """霧の上に、白い縁の写真を1枚"""
    return pic(P(R.print_photo, name, 760, rot, focus), seed, tint, 840, 520, 640)


def subscribe(seed, lines):
    """最後の「チャンネル登録をお願いします」"""
    return S(lines, fog(seed, GOLDF, 0.9), move="in", hold=1.2, els=[
        E(fit(P(L.text, "プロ野球 お金と制度のしくみ", "NotoSerifJP-Black.ttf", 76, L.GOLD)), CX, 560, anim="rise"),
        E(fit(P(L.text, "球団のお金を毎回解説", "NotoSerifJP-Black.ttf", 96, L.WHITE)), CX, 760, delay=0.4, anim="slam",
          sfx="boom"),
        E(fit(P(L.text, "チャンネル登録で 次も見逃さない", "NotoSerifJP-Black.ttf", 72, L.GOLD)), CX, 980, delay=1.0,
          anim="rise"),
    ])


END = ["球団のお金の仕組みを、毎回解説しています。",
       "チャンネル登録して、次も見逃さないでください。"]

# ---- 1本目：ぜいたく税 (10本目 MLB編) ------------------------------------------------
LT1 = [
    S(["税金のようなお金だけで、1年に、およそ268億円を払った球団があります。",
       "メジャーリーグの、ドジャースです。"],
      photo(ep10.DODGER_AIR, 1201, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("税金だけで 約268億円"),
          E(P(C.note, "※ドジャー・スタジアム", 30), CX, 940),
          big("約268億円", 1060, 170, GOLD, until=0, anim="slam", sfx="boom"),
          big("ドジャース", 1060, 150, WHITE, at=1, anim="slam", sfx="boom"),
      ]),
    S(["メジャーには、年俸の上限がありません。",
       "その代わりにあるのが、ぜいたく税です。"],
      pic(P(C.big_number, "年俸の上限", "なし", 170), 1202, BLUEF, 820, 460), move="in", els=[
          head("メジャーの決まり"),
          big("ぜいたく税", 1000, 160, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["年俸総額が基準額を超えると、超えた分に応じて、お金を払います。",
       "2026年の基準額は、2億4400万ドル。",
       "大きく超えると、超えた分の110%を払うこともあります。"],
      pic(P(C.big_number, "2026年の基準額", "2億4400万ドル", 120), 1203, GOLDF, 820, 460), move="in", els=[
          head("超えた分に応じて払う"),
          big("超えた分の110%も", 1000, 130, RED, at=2, anim="slam", sfx="boom"),
      ]),
    S(["2025年、ドジャースが払ったぜいたく税は、1億6937万ドル。過去最高の額でした。",
       "ソフトバンクの年俸総額の、3倍を超える額です。"],
      pic(P(C.big_number, "2025年 ドジャース", "1億6937万ドル", 120), 1204, REDF, 820, 460), move="in", els=[
          head("過去最高"),
          big("約268億円", 1000, 160, GOLD, until=0, anim="slam", sfx="boom", delay=1.0),
          big("ソフトバンクの年俸総額の3倍超", 1000, 90, WHITE, at=1, anim="rise"),
      ]),
    S(["大谷翔平の、10年7億ドルの契約にも、この仕組みが関係しています。",
       "そのうち6億8000万ドルは、2034年から受け取る後払いです。",
       "そのため、ぜいたく税の計算では、大谷の年俸は1年あたり、およそ4600万ドルとして扱われます。"],
      pic(P(C.vbars, [("額面", 7000, "7000万ドル", False), ("税の計算", 4600, "約4600万ドル", True)], "万ドル",
            420, 190, 60), 1205, GOLDF, 820, 460), move="in", els=[
          head("大谷の後払い契約"),
          big("10年7億ドル", 1080, 140, WHITE, until=0, anim="slam", sfx="boom"),
          big("6億8000万ドルは後払い", 1080, 100, GOLD, at=1, until=1, anim="rise"),
          big("小さく数えられる", 1080, 130, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    subscribe(1206, END),
]

# ---- 2本目：マイナーの週給 (8本目 マイナー編) ----------------------------------------
MN1 = [
    S(["メジャーを目指す選手の給料は、週710ドルから始まります。",
       "1ドル150円で、およそ10万6000円です。"],
      photo(ep08.STOCKTON_DUSK, 1211, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("メジャーの卵の給料"),
          E(P(C.note, "※1Aストックトンの球場", 30), CX, 940),
          big("週710ドル", 1060, 170, GOLD, until=0, anim="slam", sfx="boom"),
          big("約10万6000円", 1060, 150, WHITE, at=1, anim="slam", sfx="boom"),
      ]),
    S(["2026年の最低の給料は、週払いです。",
       "ルーキーリーグが週710ドル、1Aが885ドル、ハイAが935ドル、2Aが1040ドル、そして3Aが1250ドルです。"],
      pic(P(C.vbars, [("ルーキー", 710, "710", False), ("1A", 885, "885", False), ("ハイA", 935, "935", False),
                      ("2A", 1040, "1040", False), ("3A", 1250, "1250", True)], "ドル", 420, 110, 34),
          1212, BLUEF, 840, 460), move="in", els=[
          head("週の最低額（ドル）"),
          big("週払い", 1080, 150, GOLD, until=0, anim="slam", sfx="boom"),
      ]),
    S(["休みは、基本的に月曜日だけ。",
       "火曜から日曜まで、同じ相手と6連戦をして、月曜に移動します。",
       "下の段の移動は、主にバスです。"],
      pic(P(C.bullet_list, ["休みは月曜だけ", "6連戦して移動", "移動は主にバス"], 64, 800), 1213, REDF, 840, 420),
      move="in", els=[
          head("毎週の暮らし"),
          big("休みは月曜だけ", 1000, 130, RED, until=0, anim="slam", sfx="boom"),
      ]),
    S(["住まいは球団が用意しますが、1A以下では、1つの部屋を2人で使うこともあります。",
       "食事は、球場に来た日の、試合の前と後の2食です。"],
      photo(ep08.STOCKTON_NIGHT, 1214, BLUEF, (0.5, 0.5), 3), move="in", els=[
          head("住まいと食事"),
          E(P(C.note, "※ストックトン・ポーツの試合", 30), CX, 940),
          big("1部屋を2人で", 1060, 140, WHITE, until=0, anim="slam", sfx="boom"),
          big("食事は1日2食", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["メジャーに上がると、最低年俸は78万ドル。",
       "1Aの選手が1年で受け取る額の、30倍近くになります。"],
      pic(P(C.big_number, "メジャーの最低年俸", "78万ドル", 150), 1215, GOLDF, 820, 460), move="in", els=[
          head("メジャーに上がると"),
          big("1Aの30倍近く", 1000, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    subscribe(1216, END),
]

# ---- 3本目：史上初のストライキ (11本目 球界再編) -------------------------------------
ST1 = [
    S(["2004年9月18日。",
       "この日、日本のプロ野球の試合は、1つも行われませんでした。"],
      pic(P(R.calendar, 2004, 9, 18, "プロ野球の試合なし"), 1221, REDF, 560, 460), move="in", trans="cut", els=[
          head("試合が1つもなかった日"),
          big("試合は1つもなし", 1000, 140, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["選手たちが、プロ野球の歴史で初めての、ストライキに踏み切ったのです。",
       "きっかけは、近鉄とオリックスの合併。",
       "その先には、12球団を10球団に減らし、リーグを1つにする構想がありました。"],
      pic(P(N.stamp, "ストライキ", RED, 200), 1222, REDF, 760, 440), move="in", els=[
          head("史上初"),
          big("近鉄とオリックスの合併", 1000, 100, WHITE, at=1, until=1, anim="rise"),
          big("12球団 → 10球団", 1000, 140, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    S(["話し合いを求めた選手会に対して、巨人のオーナーが記者団に語った言葉が、大きく報じられます。",
       "「たかが選手が」。"],
      fog(1223, (1.0, 1.0, 1.0), 0.95), move="in", els=[
          head("2004年7月"),
          big("選手会は話し合いを求めた", 900, 100, WHITE, until=0, anim="rise"),
          big("「たかが選手が」", 900, 150, WHITE, at=1, anim="slam", sfx="boom"),
          E(P(C.note, "※発言は報道による", 30), CX, 1100, at=1),
      ]),
    S(["8月12日、選手会は、ストライキを行う権利を確立します。",
       "投票の結果は、賛成648、反対7でした。"],
      pic(P(C.vbars, [("賛成", 648, "648", True), ("反対", 7, "7", False)], "票", 420, 190, 60),
          1224, GOLDF, 820, 460), move="in", els=[
          head("スト権の投票"),
          big("賛成648・反対7", 1080, 130, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["9月18日と19日、一軍の6試合と、二軍の3試合が中止に。",
       "選手とファンは、何を守ろうとしたのか。2004年の球界再編は、本編で、お金の流れから解説します。"],
      photo(ep11.KOSHIEN, 1225, BLUEF, (0.5, 0.5)), move="in", els=[
          head("何を守ろうとした？"),
          E(P(C.note, "※イメージ（阪神甲子園球場）", 30), CX, 940),
          big("一軍6試合・二軍3試合 中止", 1060, 90, RED, until=0, anim="slam", sfx="boom"),
          big("お金の流れで解説", 1060, 130, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    subscribe(1226, END),
]

LT1 = ep10._fix_speech(LT1)
MN1 = ep08._fix_speech(MN1)
ST1 = ep11._fix_speech(ST1)

# ショートだけの読みの指定 (check_word で聞き比べて「微妙」だったもの)
FIX = {"ぜいたく税": "ぜいたくぜい"}
for _sc in LT1:
    _out = []
    for _ln in _sc["lines"]:
        _text, _sp = _ln if isinstance(_ln, tuple) else (_ln, _ln)
        for _k, _v in FIX.items():
            _sp = _sp.replace(_k, _v)
        _out.append((_text, _sp) if _sp != _text else _text)
    _sc["lines"] = _out
