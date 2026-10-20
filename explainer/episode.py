"""第1回 本編: ドラフトの契約金はいくら？ (順位別・高卒/大卒/社会人・指名縛り・育成)

シーン = 章タイトル + ナレーション(一文ずつ) + 画面要素。
画面要素は E(スプライト関数, x, y, at=何文目で出すか, until=何文目で消すか, anim=出し方)
  x, y は要素の中心 (1920x1080)。at/until はそのシーン内の文の番号 (0始まり)。
ナレーションの文は ("字幕", "読み") のタプルにすると、字幕と読み上げを分けられる。
"""
from __future__ import annotations

from functools import partial as P

import illust as il
import ui

BLUE_CAP = (30, 70, 160)
GRAY_CAP = (110, 110, 124)
GREEN_CAP = (20, 120, 80)
TIE = (200, 40, 40)


def E(fn, x, y, at=0, until=None, anim="pop", scale=1.0, delay=0.15):
    return {"fn": fn, "x": x, "y": y, "at": at, "until": until, "anim": anim, "scale": scale, "delay": delay}


def S(chapter, lines, els=(), bg="white"):
    return {"chapter": chapter, "lines": list(lines), "els": list(els), "bg": bg}


def chart(upto, highlight=None):
    rows = [("1位", 10000, "1億"), ("2位", 7000, "7000万"), ("3位", 5500, "5〜6000万"),
            ("4位", 4000, "4000万"), ("5位", 3000, "3000万"), ("6位〜", 2500, "2000万台")]
    shown = [(l, v if i < upto else 0.0001, t if i < upto else "") for i, (l, v, t) in enumerate(rows)]
    return ui.bar_chart(shown, w=1500, h=600, vmax=10000, highlight=highlight)


def board(k):
    pts = ["①上限は契約金1億＋出来高5000万",
           "②2位以下は順位ごとに相場が下がる",
           "③出身の差は契約金より年俸に出る",
           "④指名縛りは将来を見すえた条件",
           "⑤育成は契約金なし、支度金のみ"]
    return ui.chalkboard(pts[:k], title="まとめ")


CH1 = "新人契約の3点セット"
CH2 = "ドラフト順位別の契約金の相場"
CH3 = "高卒・大卒・社会人で何が違う？"
CH4 = "指名縛り（順位縛り）とは"
CH5 = "育成指名との差"
CH6 = "なぜ契約金に上限があるのか"
CH7 = "まとめ"

SCENES = [
    # ===== 1. 新人契約の3点セット =====
    S(CH1, [
        "今回は、ドラフトで指名された選手が、実際にいくらもらえるのかを解説します。",
        "新人の契約は、大きく分けて三つのお金でできています。",
        "入団するときに一度だけもらう、契約金。",
        "毎年もらう給料である、年俸。",
        ("そして、成績に応じて上乗せされる、出来高です。", "そして、成績に応じて上乗せされる、できだかです。"),
    ], [
        E(P(il.person, "player", "happy", BLUE_CAP, ""), 960, 470, at=0, until=1),
        E(P(ui.label, "ドラフト指名", "red", 80), 960, 180, at=0, until=1),
        E(P(ui.big_word, "3つのお金", "yellow", 150), 960, 200, at=1, until=2),
        E(P(il.contract, amount="契約金"), 420, 520, at=2),
        E(P(ui.label, "契約金", "orange"), 420, 290, at=2),
        E(P(il.money, 3), 960, 560, at=3),
        E(P(ui.label, "年俸", "navy"), 960, 290, at=3),
        E(P(il.ball, 90), 1500, 540, at=4),
        E(P(ui.label, "出来高", "green"), 1500, 290, at=4),
    ]),
    S(CH1, [
        "この三つには、12球団の申し合わせで、上限が決められています。",
        "契約金は1億円、出来高は5000万円、年俸は1600万円までです。",
        "これを、最高標準額と呼びます。",
        "ドラフト1位の契約金が、毎年のように1億円で並ぶのは、このためです。",
    ], [
        E(P(il.building, "office"), 960, 470, at=0, until=1),
        E(P(ui.label, "12球団の申し合わせ", "navy", 76), 960, 200, at=0, until=1),
        E(P(ui.table, ["", "上限"], [["契約金", "1億円"], ["出来高", "5000万円"], ["年俸", "1600万円"]], [380, 520], 104, 1),
          960, 500, at=1, until=3),
        E(P(ui.big_word, "最高標準額", "red_brush", 150), 960, 190, at=2, until=3),
        E(P(il.person, "player", "happy", BLUE_CAP, "1"), 640, 500, at=3),
        E(P(ui.big_word, "1億円", "yellow", 190), 1240, 470, at=3),
    ]),

    # ===== 2. 順位別の相場 =====
    S(CH2, [
        "では、2位以下の選手は、いくらもらっているのでしょうか。",
        "実は、上限のほかに決まった金額はなく、球団と選手の交渉で決まります。",
        "ただ、これまでの報道をもとにすると、だいたいの相場が見えてきます。",
    ], [
        E(P(il.person, "player", "worried", GRAY_CAP, "2"), 760, 500, at=0),
        E(P(il.mark, "q", 200), 1060, 300, at=0, until=1),
        E(P(il.person, "staff", "normal", TIE), 1260, 500, at=1),
        E(P(ui.bubble, "条件は\nこのくらいで…", 46, "right"), 1420, 200, at=1),
        E(P(ui.label, "球団と選手の交渉", "navy", 76), 960, 160, at=2),
    ]),
    S(CH2, [
        "1位は、ほぼ上限の1億円。",
        "2位は、7000万円前後。",
        "3位は、5000万円から6000万円ほど。",
        "4位は4000万円前後、5位は3000万円前後が目安です。",
        "6位以下になると、2000万円台という例も珍しくありません。",
        "つまり、1位と2位の間だけで、いきなり3000万円ほどの差がつくのです。",
        "同じ日に名前を呼ばれても、順位ひとつで、受け取る額が大きく変わります。",
    ], [
        E(P(chart, 1, 0), 960, 470, at=0, until=1, anim="none"),
        E(P(chart, 2, 0), 960, 470, at=1, until=2, anim="none"),
        E(P(chart, 3, 0), 960, 470, at=2, until=3, anim="none"),
        E(P(chart, 5, 0), 960, 470, at=3, until=4, anim="none"),
        E(P(chart, 6, 0), 960, 470, at=4, anim="none"),
        E(P(ui.red_circle, 470, 560), 506, 450, at=5, until=6, anim="wipe_right"),
        E(P(ui.label, "差 約3000万円", "red", 80), 1000, 190, at=5, until=6),
        E(P(ui.big_word, "順位ひとつで大差", "red", 120), 960, 180, at=6),
    ]),

    # ===== 3. 高卒・大卒・社会人 =====
    S(CH3, [
        "次に、同じ順位でも、高卒・大卒・社会人で違いはあるのでしょうか。",
        "結論から言うと、契約金は順位でほぼ決まり、出身による差は小さめです。",
        "差が出やすいのは、年俸のほうです。",
    ], [
        E(P(il.person, "player", "normal", BLUE_CAP, "高"), 480, 520, at=0),
        E(P(il.person, "player", "normal", GRAY_CAP, "大"), 960, 520, at=0, delay=0.5),
        E(P(il.person, "player", "normal", GREEN_CAP, "社"), 1440, 520, at=0, delay=0.85),
        E(P(ui.label, "高卒", "orange"), 480, 210, at=0, until=1),
        E(P(ui.label, "大卒", "navy"), 960, 210, at=0, until=1, delay=0.5),
        E(P(ui.label, "社会人", "green"), 1440, 210, at=0, until=1, delay=0.85),
        E(P(ui.panel, 1100, 150, (255, 248, 230)), 960, 140, at=1, until=2),
        E(P(ui.label, "契約金 ＝ 順位でほぼ決まる", "red", 64, 8), 960, 140, at=1, until=2),
        E(P(ui.big_word, "差が出るのは年俸", "yellow", 120), 960, 150, at=2),
    ]),
    S(CH3, [
        "すぐに一軍で戦える即戦力として見られる大卒や社会人は、年俸が高めに設定されがちです。",
        "一方で高卒の選手は、数年かけて育てる前提なので、年俸は低めからのスタートが多くなります。",
        "例えば同じ1位でも、大卒や社会人は上限に近い1500万円前後、高卒は1000万円前後から、というケースがよく見られます。",
        "もちろん、高卒でも目玉の選手なら、上限の1600万円で契約することもあります。",
    ], [
        E(P(il.person, "player", "happy", GRAY_CAP, "大"), 560, 520, at=0, until=1),
        E(P(il.person, "player", "happy", GREEN_CAP, "社"), 900, 520, at=0, until=1),
        E(P(ui.label, "即戦力", "red", 96), 730, 200, at=0, until=1),
        E(P(il.money, 3), 1400, 560, at=0, until=1),
        E(P(il.person, "player", "normal", BLUE_CAP, "高"), 640, 520, at=1, until=2),
        E(P(il.calendar, "数年"), 1060, 520, at=1, until=2),
        E(P(ui.label, "じっくり育てる", "orange", 84), 860, 200, at=1, until=2),
        E(P(ui.table, ["1位の年俸の例", "金額"], [["大卒・社会人", "1500万円前後"], ["高卒", "1000万円前後〜"]], [560, 560], 110, 1),
          960, 480, at=2),
        E(P(ui.label, "※目玉の高卒選手は上限もあり", "ink", 52, 8), 960, 760, at=3),
    ]),
    S(CH3, [
        "社会人の選手には、独特のルールもあります。",
        "高校を出て社会人チームに入った選手は3年、大学を出て入った選手は2年たたないと、ドラフトで指名できません。",
        "さらに社会人の選手は、慣例として、育成ドラフトでは指名されません。",
        "会社にとって選手は社員でもあるので、送り出すなら、きちんとした条件で、という事情があるのです。",
    ], [
        E(P(il.building, "company"), 600, 500, at=0, until=1),
        E(P(il.person, "player", "normal", GREEN_CAP, "社"), 1100, 520, at=0, until=1),
        E(P(ui.label, "社会人のルール", "green", 84), 860, 180, at=0, until=1),
        E(P(il.calendar, "3年"), 620, 520, at=1, until=2),
        E(P(il.calendar, "2年"), 1300, 520, at=1, until=2, delay=1.6),
        E(P(ui.label, "高卒→社会人", "orange", 70), 620, 260, at=1, until=2),
        E(P(ui.label, "大卒→社会人", "navy", 70), 1300, 260, at=1, until=2, delay=1.6),
        E(P(ui.label, "育成ドラフト", "navy", 90), 960, 300, at=2, until=3),
        E(P(il.mark, "ng", 300), 960, 520, at=2, until=3),
        E(P(il.building, "company"), 560, 500, at=3),
        E(P(il.person, "staff", "normal", (40, 90, 170)), 1000, 520, at=3),
        E(P(ui.bubble, "送り出すなら\n上位指名で！", 48, "left"), 1390, 260, at=3),
    ]),

    # ===== 4. 指名縛り =====
    S(CH4, [
        "ここで出てくるのが、指名縛りと呼ばれるものです。",
        "これは選手の側が、何位以内に指名されなければプロには行かない、と事前に球団へ伝えておくものです。",
        "3位以内でなければ進学する3位縛りや、育成なら行かない支配下縛りなどがあります。",
    ], [
        E(P(ui.big_word, "指名縛り", "red_brush", 220), 960, 430, at=0, until=1),
        E(P(il.person, "gakuran", "normal"), 640, 540, at=1),
        E(P(ui.bubble, "3位以内じゃなければ\n大学に行きます", 50, "left"), 1180, 300, at=1, until=2),
        E(P(ui.label, "3位縛り", "red", 90), 1220, 300, at=2),
        E(P(ui.label, "支配下縛り", "navy", 90), 1260, 520, at=2, delay=1.8),
    ]),
    S(CH4, [
        "なぜ、こんな条件をつけるのでしょうか。",
        "理由のひとつは、お金と将来のバランスです。",
        "下位指名だと契約金も年俸も低く、もしプロで結果が出なければ、数年で戦力外になることもあります。",
        "それなら大学や社会人で力をつけて、数年後に上位指名を目指したほうがいい、という考え方です。",
    ], [
        E(P(il.person, "gakuran", "worried"), 760, 540, at=0, until=2),
        E(P(il.mark, "q", 220), 1120, 320, at=0, until=1),
        E(P(ui.label, "お金 と 将来", "orange", 100), 1260, 360, at=1, until=2),
        E(P(il.money, 1), 700, 600, at=2, until=3),
        E(P(ui.label, "契約金も年俸も低め", "navy", 72), 700, 330, at=2, until=3),
        E(P(ui.stamp, "数年で戦力外も", ui.RED, 84, -8), 1290, 520, at=2, until=3),
        E(P(il.building, "highschool"), 380, 540, at=3),
        E(P(ui.arrow, 220), 700, 560, at=3, delay=0.6),
        E(P(il.building, "university"), 1020, 540, at=3, delay=1.0),
        E(P(ui.arrow, 220), 1340, 560, at=3, delay=1.6),
        E(P(ui.label, "上位指名", "red", 96), 1650, 540, at=3, delay=2.0),
    ]),
    S(CH4, [
        "また、進学先や就職先の枠を確保するために、大学や会社の側から、縛りをつけてほしいと求めることもあります。",
        "ただし、縛りが厳しいと、球団が指名を見送り、指名漏れになるリスクもあります。",
        "実際に、甲子園で注目された高校生が、3位縛りで指名漏れになったと報じられた例もあります。",
    ], [
        E(P(il.building, "university"), 560, 500, at=0, until=1),
        E(P(il.building, "company"), 1000, 500, at=0, until=1, delay=0.4),
        E(P(ui.bubble, "枠を空けて\n待ってるよ", 48, "left"), 1440, 300, at=0, until=1),
        E(P(il.person, "gakuran", "worried"), 960, 520, at=1),
        E(P(ui.stamp, "指名漏れ！", ui.RED, 120, -10), 1400, 400, at=1),
        E(P(ui.label, "縛りはリスクと隣り合わせ", "navy", 66, 8), 960, 170, at=2),
    ]),

    # ===== 5. 育成 =====
    S(CH5, [
        "最後に、育成指名との差を見ておきましょう。",
        "育成選手には、契約金がありません。",
        ("代わりに支払われるのが支度金で、相場は200万円から300万円ほどです。", "代わりに支払われるのが、したくきんで、相場は200万円から300万円ほどです。"),
        "年俸も、数百万円台からのスタートです。",
    ], [
        E(P(ui.big_word, "育成指名", "yellow", 170), 960, 430, at=0, until=1),
        E(P(il.contract, amount="契約金"), 760, 520, at=1, until=2),
        E(P(il.mark, "ng", 320), 760, 520, at=1, until=2, delay=0.5),
        E(P(il.envelope, "支度金"), 760, 540, at=2),
        E(P(ui.label, "200〜300万円", "red", 90), 1300, 460, at=2),
        E(P(ui.label, "年俸も数百万円台〜", "navy", 70), 1300, 640, at=3),
    ]),
    S(CH5, [
        "1位の契約金1億円と比べると、その差は30倍以上です。",
        "さらに育成契約は、3年以内に支配下登録されなければ、いったん自由契約になります。",
        "同じドラフトで指名されても、スタートラインはまったく違うのです。",
    ], [
        E(P(ui.bar_chart, [("ドラフト1位", 10000, "1億円"), ("育成", 300, "約300万円")], 1000, 600, "万円", 10000, 0),
          760, 470, at=0, until=1, anim="wipe_up"),
        E(P(ui.big_word, "30倍以上", "red", 150), 1500, 330, at=0, until=1, delay=1.2),
        E(P(il.calendar, "3年"), 700, 520, at=1, until=2),
        E(P(ui.label, "支配下登録されないと", "navy", 70), 1260, 420, at=1, until=2),
        E(P(ui.label, "いったん自由契約", "red", 84), 1260, 580, at=1, until=2, delay=1.8),
        E(P(il.person, "player", "happy", BLUE_CAP, "1"), 640, 520, at=2),
        E(P(il.person, "player", "worried", GRAY_CAP, "育"), 1280, 520, at=2, delay=0.4),
        E(P(ui.label, "スタートラインが違う", "red", 80), 960, 180, at=2),
    ]),

    # ===== 6. なぜ上限があるのか =====
    S(CH6, [
        "では、なぜ契約金に上限があるのでしょうか。",
        "上限がないと、人気の選手を獲るために、球団どうしで契約金がどんどんつり上がってしまいます。",
        "そうなると、お金のある球団ばかりに有力な選手が集まり、戦力のバランスが崩れてしまいます。",
        "また2007年には、球団がアマチュア選手に金銭を渡していた問題が発覚し、大きな批判を浴びました。",
        "こうした反省もあって、上限を守り、ドラフトを公平に保とうという流れが強まったのです。",
    ], [
        E(P(il.mark, "q", 240), 960, 450, at=0, until=1),
        E(P(il.person, "staff", "normal", TIE), 560, 540, at=1, until=3),
        E(P(il.person, "staff", "surprised", (40, 90, 170)), 1360, 540, at=1, until=3),
        E(P(ui.bubble, "1億5千万！", 50, "right"), 400, 220, at=1, until=2),
        E(P(ui.bubble, "なら2億！", 50, "left"), 1540, 220, at=1, until=2, delay=1.4),
        E(P(ui.arrow, 260, ui.RED, 90), 960, 470, at=1, until=2, delay=2.0),
        E(P(ui.label, "戦力バランスが崩れる", "red", 76), 960, 200, at=2, until=3),
        E(P(ui.stamp, "問題発覚", ui.RED, 130, -8), 960, 420, at=3, until=4),
        E(P(ui.label, "ドラフトを公平に", "navy", 100), 960, 300, at=4),
        E(P(il.mark, "ok", 260), 960, 560, at=4, delay=0.5),
    ]),

    # ===== 7. まとめ =====
    S(CH7, [
        "最後に、今回のまとめです。",
        "新人契約の上限は、契約金1億円と出来高5000万円、年俸1600万円。",
        "2位以下は決まった額がなく、順位が下がるごとに相場も下がります。",
        "高卒・大卒・社会人の差は、契約金よりも年俸に出やすくなります。",
        "指名縛りは、選手が将来を見すえてつける条件です。",
        "そして育成指名には契約金がなく、支度金だけ。スタートラインは大きく違います。",
    ], [
        E(P(board, 0), 960, 540, at=0, until=1, anim="none", delay=0),
        E(P(board, 1), 960, 540, at=1, until=2, anim="none", delay=0),
        E(P(board, 2), 960, 540, at=2, until=3, anim="none", delay=0),
        E(P(board, 3), 960, 540, at=3, until=4, anim="none", delay=0),
        E(P(board, 4), 960, 540, at=4, until=5, anim="none", delay=0),
        E(P(board, 5), 960, 540, at=5, anim="none", delay=0),
    ], bg="board"),
]
