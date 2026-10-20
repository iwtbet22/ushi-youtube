"""第1回 本編: ドラフトの契約金はいくら？ (順位別・高卒/大卒/社会人・指名縛り・育成)

シーン = 章タイトル + ナレーション(一文ずつ) + 画面要素。
画面要素は E(スプライト関数, x, y, at=何文目で出すか, until=何文目で消すか, anim=出し方)
  x, y は要素の中心 (1920x1080)。at/until はそのシーン内の文の番号 (0始まり)。
  anim: pop / slide_l / slide_r / rise / drop / zoom / fade / wipe_up / wipe_right / none
  until=(文番号, 秒) … その文が始まって何秒後に消すか (図を段階的に差し替えるとき)
  over=True … 他の要素に重ねる前提のもの (赤丸・バツ印・矢印など)。重なりチェックの対象外
  count=(終値, 表示関数, 色, 大きさ, 秒数) … 数字をカウントアップで出す
ナレーションの文は ("字幕", "読み") のタプルにすると、字幕と読み上げを分けられる。

同じ見せ方の繰り返しにならないよう、シーンごとに 構図・背景(bg)・出し方・トランジション(trans)・
カメラ(cam) を変えている。
"""
from __future__ import annotations

from functools import partial as P

import illust as il
import ui

BLUE_CAP = (30, 70, 160)
GRAY_CAP = (110, 110, 124)
GREEN_CAP = (20, 120, 80)
TIE = (200, 40, 40)
TIE2 = (40, 90, 170)


def E(fn, x, y, at=0, until=None, anim="pop", scale=1.0, delay=0.15, over=False, full=False, count=None, name=None):
    if name is None:
        name = getattr(fn, "func", fn).__name__ if fn else "count"
        args = getattr(fn, "args", ())
        if args and isinstance(args[0], str):
            name += f"({args[0]})"
    return {"fn": fn, "x": x, "y": y, "at": at, "until": until, "anim": anim, "scale": scale, "delay": delay,
            "over": over, "full": full, "count": count, "name": name}


def C(end, fmt, x, y, at=0, until=None, color="red", size=130, dur=1.0, delay=0.2):
    """カウントアップする数字"""
    return E(None, x, y, at, until, "none", delay=delay, count=(end, fmt, color, size, dur), name=f"count({fmt(end)})")


def S(chapter, lines, els=(), bg="white", trans="cut", cam=None, hold=0):
    return {"chapter": chapter, "lines": list(lines), "els": list(els), "bg": bg, "trans": trans, "cam": cam,
            "hold": hold}


def man(v):
    """万円単位の数値を「1億円」「7,000万円」の形にする"""
    v = int(round(v))
    return "1億円" if v >= 10000 else f"{v:,}万円"


STEPS = [("1位", 1.0, "1億"), ("2位", 0.7, "7000万"), ("3位", 0.55, "5〜6000万"),
         ("4位", 0.4, "4000万"), ("5位", 0.3, "3000万"), ("6位〜", 0.22, "2000万台")]


def stairs(k):
    return ui.staircase(STEPS, k, w=1500, h=560)


def board(k):
    pts = ["①上限は契約金1億＋出来高5000万",
           "②2位以下は順位ごとに相場が下がる",
           "③出身の差は契約金より年俸に出る",
           "④指名縛りは将来を見すえた条件",
           "⑤育成は契約金なし、支度金のみ"]
    return ui.chalkboard(pts[:k], title="まとめ")


def tl(k):
    marks = [(0.02, "入社", "社会人1年目", "ink"), (0.5, "2年", "大卒は指名OK", "navy"),
             (0.98, "3年", "高卒も指名OK", "orange")]
    return ui.timeline(marks, w=1500, h=300, upto=k)


CH1 = "新人契約の3点セット"
CH2 = "ドラフト順位別の契約金の相場"
CH3 = "高卒・大卒・社会人で何が違う？"
CH4 = "指名縛り（順位縛り）とは"
CH5 = "育成指名との差"
CH6 = "なぜ契約金に上限があるのか"
CH7 = "まとめ"

SCENES = [
    # ===== 1. 新人契約の3点セット: 小物を3方向から並べる =====
    S(CH1, [
        "今回は、ドラフトで指名された選手が、実際にいくらもらえるのかを解説します。",
        "新人の契約は、大きく分けて三つのお金でできています。",
        "入団するときに一度だけもらう、契約金。",
        "毎年もらう給料である、年俸。",
        ("そして、成績に応じて上乗せされる、出来高です。", "そして、成績に応じて上乗せされる、できだかです。"),
    ], [
        E(P(il.person, "player", "happy", BLUE_CAP, "", pose="cheer"), 960, 590, at=0, until=1, anim="drop"),
        E(P(ui.label, "ドラフト指名！", "red", 84), 960, 240, at=0, until=1, delay=0.6),
        E(P(ui.big_word, "3つのお金", "yellow", 150), 960, 480, at=1, until=2, anim="zoom"),
        E(P(il.contract, amount="契約金"), 420, 610, at=2, anim="slide_l"),
        E(P(ui.label, "契約金", "orange"), 420, 330, at=2, delay=0.4),
        E(P(il.money, 3), 960, 640, at=3, anim="rise"),
        E(P(ui.label, "年俸", "navy"), 960, 330, at=3, delay=0.4),
        E(P(il.ball, 90), 1500, 610, at=4, anim="slide_r"),
        E(P(ui.label, "出来高", "green"), 1500, 330, at=4, delay=0.4),
    ], cam="in"),
    # 上限: 表 + 数字のカウントアップ
    S(CH1, [
        "この三つには、12球団の申し合わせで、上限が決められています。",
        "契約金は1億円、出来高は5000万円、年俸は1600万円までです。",
        "これを、最高標準額と呼びます。",
        "ドラフト1位の契約金が、毎年のように1億円で並ぶのは、このためです。",
    ], [
        E(P(il.building, "office"), 620, 560, at=0, until=1),
        E(P(ui.label, "12球団の申し合わせ", "navy", 76), 1300, 500, at=0, until=1, anim="slide_r"),
        E(P(ui.table, ["", "上限"], [["契約金", "1億円"], ["出来高", "5000万円"], ["年俸", "1600万円"]], [380, 520], 100, 1),
          960, 600, at=1, until=3, anim="wipe_right"),
        E(P(ui.big_word, "最高標準額", "red_brush", 130), 960, 255, at=2, until=3, anim="zoom"),
        E(P(il.person, "player", "happy", BLUE_CAP, "1", pose="cheer"), 600, 600, at=3, anim="slide_l"),
        C(10000, man, 1260, 520, at=3, color="red", size=170, dur=1.2),
    ], bg="dots", trans="wipe"),

    # ===== 2. 順位別の相場: 交渉の場面 → 下り階段 =====
    S(CH2, [
        "では、2位以下の選手は、いくらもらっているのでしょうか。",
        "実は、上限のほかに決まった金額はなく、球団と選手の交渉で決まります。",
        "ただ、これまでの報道をもとにすると、だいたいの相場が見えてきます。",
    ], [
        E(P(il.person, "player", "worried", GRAY_CAP, "2", pose="think"), 700, 600, at=0, anim="rise"),
        E(P(il.mark, "q", 200), 1000, 330, at=0, until=1, delay=0.5),
        E(P(il.person, "staff", "normal", TIE, pose="point"), 1300, 640, at=1, anim="slide_r", scale=0.85),
        E(P(ui.bubble, "この条件でどう？", 46, "down"), 1330, 300, at=1, until=2, delay=0.6),
        E(P(ui.label, "球団と選手の交渉で決まる", "navy", 70), 960, 250, at=2),
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
        E(P(stairs, 1), 960, 560, at=0, until=1, anim="wipe_up"),
        E(P(stairs, 2), 960, 560, at=1, until=2, anim="none"),
        E(P(stairs, 3), 960, 560, at=2, until=3, anim="none"),
        E(P(stairs, 5), 960, 560, at=3, until=4, anim="none"),
        E(P(stairs, 6), 960, 560, at=4, anim="none"),
        E(P(ui.gap_marker, 280, 125), 572, 428, at=5, until=6, anim="wipe_right", over=True),
        E(P(ui.label, "差 約3000万円", "red", 80), 1220, 250, at=5, until=6),
        E(P(ui.big_word, "順位ひとつで大差", "red", 110), 1220, 250, at=6, anim="zoom"),
    ], bg="tint", trans="slide", cam="in"),

    # ===== 3. 高卒・大卒・社会人: 3人並び → 左右比較 → 時間軸 =====
    S(CH3, [
        "次に、同じ順位でも、高卒・大卒・社会人で違いはあるのでしょうか。",
        "結論から言うと、契約金は順位でほぼ決まり、出身による差は小さめです。",
        "差が出やすいのは、年俸のほうです。",
    ], [
        E(P(il.person, "player", "normal", BLUE_CAP, "高"), 480, 600, at=0, anim="drop"),
        E(P(il.person, "player", "normal", GRAY_CAP, "大"), 960, 600, at=0, anim="drop", delay=0.5),
        E(P(il.person, "player", "normal", GREEN_CAP, "社"), 1440, 600, at=0, anim="drop", delay=0.85),
        E(P(ui.label, "高卒", "orange"), 480, 250, at=0, until=1, delay=0.9),
        E(P(ui.label, "大卒", "navy"), 960, 250, at=0, until=1, delay=1.2),
        E(P(ui.label, "社会人", "green"), 1440, 250, at=0, until=1, delay=1.5),
        E(P(ui.panel, 1040, 130, (255, 248, 230)), 960, 240, at=1, until=2, anim="fade"),
        E(P(ui.label, "契約金 ＝ 順位でほぼ決まる", "red", 60, 8), 960, 240, at=1, until=2, over=True),
        E(P(ui.big_word, "差が出るのは年俸", "yellow", 110), 960, 245, at=2, anim="zoom"),
    ], bg="dots"),
    S(CH3, [
        "すぐに一軍で戦える即戦力として見られる大卒や社会人は、年俸が高めに設定されがちです。",
        "一方で高卒の選手は、数年かけて育てる前提なので、年俸は低めからのスタートが多くなります。",
        "例えば同じ1位でも、大卒や社会人は上限に近い1500万円前後、高卒は1000万円前後から、というケースがよく見られます。",
        "もちろん、高卒でも目玉の選手なら、上限の1600万円で契約することもあります。",
    ], [
        E(P(il.person, "player", "happy", GRAY_CAP, "大", pose="cheer"), 330, 610, at=0, until=2, anim="slide_l"),
        E(P(il.person, "player", "happy", GREEN_CAP, "社", pose="cheer"), 680, 610, at=0, until=2, anim="slide_l", delay=0.3),
        E(P(ui.label, "即戦力", "red", 96), 505, 250, at=0, until=2, delay=0.6),
        E(P(il.person, "player", "normal", BLUE_CAP, "高", pose="think"), 1250, 610, at=1, until=2, anim="slide_r"),
        E(P(il.calendar, "数年"), 1620, 600, at=1, until=2, delay=0.5),
        E(P(ui.label, "じっくり育てる", "orange", 80), 1430, 250, at=1, until=2, delay=0.8),
        E(P(ui.label, "大卒・社会人", "navy", 72), 480, 300, at=2, anim="rise"),
        C(1500, lambda v: f"{int(v):,}万円前後", 480, 480, at=2, color="red", size=84, delay=0.4),
        E(P(ui.label, "高卒", "orange", 72), 1440, 300, at=2, anim="rise", delay=1.8),
        C(1000, lambda v: f"{int(v):,}万円前後〜", 1440, 480, at=2, color="navy", size=76, delay=2.2),
        E(P(ui.label, "1位の年俸の例", "ink", 56, 8), 960, 640, at=2, delay=0.2),
        E(P(ui.label, "※目玉の高卒は上限1600万円も", "ink", 50, 8), 1400, 770, at=3),
    ], bg="split", trans="zoom"),
    S(CH3, [
        "社会人の選手には、独特のルールもあります。",
        "高校を出て社会人チームに入った選手は3年、大学を出て入った選手は2年たたないと、ドラフトで指名できません。",
        "さらに社会人の選手は、慣例として、育成ドラフトでは指名されません。",
        "会社にとって選手は社員でもあるので、送り出すなら、きちんとした条件で、という事情があるのです。",
    ], [
        E(P(il.building, "company"), 560, 580, at=0, until=1),
        E(P(il.person, "player", "normal", GREEN_CAP, "社"), 1000, 600, at=0, until=1, anim="slide_r"),
        E(P(ui.label, "社会人のルール", "green", 84), 1470, 420, at=0, until=1, delay=0.5),
        E(P(tl, 1), 960, 500, at=1, until=(1, 2.2), anim="wipe_right"),
        E(P(tl, 2), 960, 500, at=1, until=(1, 4.6), anim="none", delay=2.2),
        E(P(tl, 3), 960, 500, at=1, until=2, anim="none", delay=4.6),
        E(P(ui.label, "育成ドラフト", "navy", 90), 960, 280, at=2, until=3),
        E(P(il.mark, "ng", 320), 960, 580, at=2, until=3, delay=0.4),
        E(P(il.building, "company"), 500, 590, at=3, anim="rise"),
        E(P(il.person, "staff", "normal", TIE2, pose="point"), 930, 640, at=3, anim="slide_l", scale=0.85),
        E(P(ui.bubble, "送り出すなら\n上位指名で！", 48, "left"), 1450, 360, at=3, delay=0.6),
    ], trans="fade"),

    # ===== 4. 指名縛り: 吹き出し → フローチャート → 新聞 =====
    S(CH4, [
        "ここで出てくるのが、指名縛りと呼ばれるものです。",
        "これは選手の側が、何位以内に指名されなければプロには行かない、と事前に球団へ伝えておくものです。",
        "3位以内でなければ進学する3位縛りや、育成なら行かない支配下縛りなどがあります。",
    ], [
        E(P(ui.big_word, "指名縛り", "red_brush", 220), 960, 480, at=0, until=1, anim="zoom"),
        E(P(il.person, "gakuran", "normal"), 560, 600, at=1, anim="rise"),
        E(P(ui.bubble, "3位以内じゃなければ\n大学に行きます", 50, "left"), 1180, 340, at=1, until=2, delay=0.5),
        E(P(ui.label, "3位縛り", "red", 90), 1200, 360, at=2, anim="slide_r"),
        E(P(ui.label, "支配下縛り", "navy", 90), 1250, 600, at=2, anim="slide_r", delay=2.4),
    ], bg="tint", cam="in"),
    S(CH4, [
        "なぜ、こんな条件をつけるのでしょうか。",
        "理由のひとつは、お金と将来のバランスです。",
        "下位指名だと契約金も年俸も低く、もしプロで結果が出なければ、数年で戦力外になることもあります。",
        "それなら大学や社会人で力をつけて、数年後に上位指名を目指したほうがいい、という考え方です。",
    ], [
        E(P(ui.diamond, "希望の順位で\n指名された？", 480, 280, 46), 470, 400, at=0, anim="pop"),
        E(P(ui.label, "お金と将来のバランス", "orange", 64), 470, 680, at=1, until=2, anim="rise"),
        E(P(ui.line_arrow, 0, 0, 380, -150, ui.GREEN, 8, "はい"), 905, 330, at=2, anim="wipe_right", over=True),
        E(P(ui.flow_box, "プロへ\n（下位は条件が低め）", "green", 520, 140, 44), 1400, 290, at=2, delay=0.4),
        E(P(ui.stamp, "下位だと数年で戦力外も", ui.RED, 62, -6), 470, 690, at=2, until=3, delay=1.4),
        E(P(ui.line_arrow, 0, 0, 380, 150, ui.NAVY, 8, "いいえ"), 905, 500, at=3, anim="wipe_right", over=True),
        E(P(ui.flow_box, "大学・社会人で力をつけ\n数年後に上位を狙う", "navy", 560, 140, 44), 1400, 640, at=3, delay=0.4),
    ], bg="dots", trans="slide"),
    S(CH4, [
        "また、進学先や就職先の枠を確保するために、大学や会社の側から、縛りをつけてほしいと求めることもあります。",
        "ただし、縛りが厳しいと、球団が指名を見送り、指名漏れになるリスクもあります。",
        "実際に、甲子園で注目された高校生が、3位縛りで指名漏れになったと報じられた例もあります。",
    ], [
        E(P(il.building, "university"), 480, 580, at=0, until=1, anim="rise"),
        E(P(il.building, "company"), 880, 580, at=0, until=1, anim="rise", delay=0.4),
        E(P(ui.bubble, "枠を空けて\n待ってるよ", 48, "left"), 1420, 360, at=0, until=1, delay=1.0),
        E(P(il.person, "gakuran", "worried"), 620, 600, at=1, anim="drop"),
        E(P(ui.stamp, "指名漏れ！", ui.RED, 120, -10), 1250, 420, at=1, until=2, delay=0.6),
        E(P(il.newspaper, "スポーツ報"), 1100, 600, at=2, anim="slide_r"),
        E(P(ui.label, "3位縛りで指名漏れと報道", "navy", 60, 8), 1300, 280, at=2, delay=0.5),
    ], trans="wipe"),

    # ===== 5. 育成: 数字のカウント → 左右比較 =====
    S(CH5, [
        "最後に、育成指名との差を見ておきましょう。",
        "育成選手には、契約金がありません。",
        ("代わりに支払われるのが支度金で、相場は200万円から300万円ほどです。", "代わりに支払われるのが、したくきんで、相場は200万円から300万円ほどです。"),
        "年俸も、数百万円台からのスタートです。",
    ], [
        E(P(ui.big_word, "育成指名", "yellow", 170), 960, 480, at=0, until=1, anim="zoom"),
        E(P(il.contract, amount="契約金"), 640, 560, at=1, until=2),
        E(P(il.mark, "ng", 320), 640, 560, at=1, until=2, delay=0.5, over=True),
        E(P(ui.label, "契約金なし", "red", 90), 1250, 560, at=1, until=2, anim="slide_r", delay=0.8),
        E(P(il.envelope, "支度金"), 600, 580, at=2, anim="drop"),
        E(P(ui.label, "支度金の相場", "orange", 70), 1250, 330, at=2, delay=0.6),
        C(300, lambda v: f"200〜{int(v)}万円" if v >= 200 else f"{int(v)}万円", 1250, 500, at=2, color="red", size=110,
          delay=1.0),
        E(P(ui.label, "年俸も数百万円台〜", "navy", 64), 1250, 720, at=3, anim="rise"),
    ], cam="in"),
    S(CH5, [
        "1位の契約金1億円と比べると、その差は30倍以上です。",
        "さらに育成契約は、3年以内に支配下登録されなければ、いったん自由契約になります。",
        "同じドラフトで指名されても、スタートラインはまったく違うのです。",
    ], [
        E(P(ui.label, "ドラフト1位", "navy", 70), 480, 240, at=0, until=1),
        E(P(il.money, 4), 480, 520, at=0, until=1, anim="rise", scale=1.15),
        C(10000, man, 480, 760, at=0, until=1, color="red", size=100, delay=0.3),
        E(P(ui.label, "育成", "orange", 70), 1440, 240, at=0, until=1, delay=0.6),
        E(P(il.envelope, "支度金"), 1440, 520, at=0, until=1, anim="rise", scale=0.75, delay=0.6),
        E(P(ui.number, "約300万円", "navy", 100), 1440, 760, at=0, until=1, anim="pop", delay=1.0),
        E(P(ui.big_word, "30倍以上", "red", 100), 960, 480, at=0, until=1, anim="zoom", delay=1.8),
        E(P(il.calendar, "3年"), 560, 560, at=1, until=2, anim="drop"),
        E(P(ui.label, "支配下登録されないと", "navy", 70), 1260, 450, at=1, until=2, delay=0.5),
        E(P(ui.label, "いったん自由契約", "red", 84), 1260, 620, at=1, until=2, delay=2.4),
        E(P(il.person, "player", "happy", BLUE_CAP, "1", pose="cheer"), 600, 610, at=2, anim="slide_l"),
        E(P(il.person, "player", "worried", GRAY_CAP, "育"), 1320, 610, at=2, anim="slide_r"),
        E(P(ui.label, "スタートラインが違う", "red", 80), 960, 250, at=2, delay=0.6),
    ], bg="split", trans="slide"),

    # ===== 6. なぜ上限があるのか: せり合い → 偏り → 新聞 → 天秤 =====
    S(CH6, [
        "では、なぜ契約金に上限があるのでしょうか。",
        "上限がないと、人気の選手を獲るために、球団どうしで契約金がどんどんつり上がってしまいます。",
        "そうなると、お金のある球団ばかりに有力な選手が集まり、戦力のバランスが崩れてしまいます。",
        "また2007年には、球団がアマチュア選手に金銭を渡していた問題が発覚し、大きな批判を浴びました。",
        "こうした反省もあって、上限を守り、ドラフトを公平に保とうという流れが強まったのです。",
    ], [
        E(P(il.mark, "q", 240), 960, 500, at=0, until=1),
        E(P(il.person, "staff", "normal", TIE), 560, 630, at=1, until=2, anim="slide_l", scale=0.85),
        E(P(il.person, "staff", "surprised", TIE2), 1360, 630, at=1, until=2, anim="slide_r", scale=0.85),
        E(P(ui.bubble, "1億5千万！", 50, "down"), 560, 290, at=1, until=2, delay=0.6),
        E(P(ui.bubble, "なら2億！", 50, "down"), 1360, 290, at=1, until=2, delay=2.0),
        E(P(ui.arrow, 240, ui.RED, 90), 960, 520, at=1, until=2, delay=2.6, anim="rise"),
        E(P(il.money, 4), 520, 600, at=2, until=3, anim="drop"),
        E(P(il.person, "player", "happy", BLUE_CAP, ""), 1060, 640, at=2, until=3, anim="slide_r", scale=0.6, delay=0.6),
        E(P(il.person, "player", "happy", GRAY_CAP, ""), 1290, 640, at=2, until=3, anim="slide_r", scale=0.6, delay=0.9),
        E(P(il.person, "player", "happy", GREEN_CAP, ""), 1520, 640, at=2, until=3, anim="slide_r", scale=0.6, delay=1.2),
        E(P(ui.label, "戦力バランスが崩れる", "red", 76), 960, 250, at=2, until=3, delay=1.8),
        E(P(il.newspaper, "スポーツ報"), 640, 560, at=3, until=4, anim="slide_l"),
        E(P(ui.stamp, "問題発覚", ui.RED, 120, -8), 1260, 540, at=3, until=4, delay=1.6),
        E(P(il.scale_balance), 620, 590, at=4, anim="rise"),
        E(P(ui.label, "ドラフトを公平に", "navy", 96), 1290, 430, at=4, delay=1.0),
        E(P(il.mark, "ok", 220), 1290, 650, at=4, delay=2.6),
    ], bg="dots", trans="fade"),

    # ===== 7. まとめ: 黒板 =====
    S(CH7, [
        "最後に、今回のまとめです。",
        "新人契約の上限は、契約金1億円と出来高5000万円、年俸1600万円。",
        "2位以下は決まった額がなく、順位が下がるごとに相場も下がります。",
        "高卒・大卒・社会人の差は、契約金よりも年俸に出やすくなります。",
        "指名縛りは、選手が将来を見すえてつける条件です。",
        "そして育成指名には契約金がなく、支度金だけ。スタートラインは大きく違います。",
    ], [
        E(P(board, 0), 960, 540, at=0, until=1, anim="none", delay=0, full=True),
        E(P(board, 1), 960, 540, at=1, until=2, anim="none", delay=0, full=True),
        E(P(board, 2), 960, 540, at=2, until=3, anim="none", delay=0, full=True),
        E(P(board, 3), 960, 540, at=3, until=4, anim="none", delay=0, full=True),
        E(P(board, 4), 960, 540, at=4, until=5, anim="none", delay=0, full=True),
        E(P(board, 5), 960, 540, at=5, anim="none", delay=0, full=True),
    ], bg="board", trans="zoom"),

    # ===== 終了画面: 右半分を YouTube の終了画面要素 (動画・登録ボタン) のために空けておく =====
    S(CH7, [
        "今回は、ドラフトの契約金のしくみを解説しました。",
        "次回は、FAで選手がいくら稼げるのかを見ていきます。",
    ], [
        E(P(ui.label, "次回予告", "orange", 70), 460, 300, at=1, anim="slide_l"),
        E(P(ui.label, "FAのお金のしくみ", "navy", 84), 460, 430, at=1, anim="slide_l", delay=0.4),
        E(P(il.person, "player", "happy", BLUE_CAP, "", pose="point"), 460, 680, at=0, anim="rise", scale=0.55),
    ], bg="end", trans="fade", hold=16),
]
