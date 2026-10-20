"""第1回 本編: ドラフトのお金と制度 完全解説 (約35分)

事実関係は script/ep01_factcheck.md に出典つきでまとめている。台本を直すときは必ずそちらも更新する。

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

from episode_parts import BLUE_CAP, GRAY_CAP, GREEN_CAP, TIE, TIE2, C, E, S, man  # noqa: E402,F401


STEPS = [("1位", 1.0, "1億"), ("2位", 0.7, "7000万"), ("3位", 0.55, "5〜6000万"),
         ("4位", 0.4, "4000万"), ("5位", 0.3, "3000万"), ("6位〜", 0.22, "2000万台")]


def stairs(k):
    return ui.staircase(STEPS, k, w=1500, h=560)


def board(k, part=1):
    pts = {1: ["①プロ志望届を出した学生だけが対象",
               "②1位は入札→重複したら抽選",
               "③2位以降は下位チームから交互に",
               "④交渉期限は原則、翌年3月末",
               "⑤育成は3年で支配下を目指す"],
           2: ["①上限は契約金1億＋出来高5000万",
               "②2位以下は順位ごとに相場が下がる",
               "③出身の差は契約金より年俸に出る",
               "④指名縛りは将来を見すえた条件",
               "⑤上限とウェーバーで戦力を均衡に"]}[part]
    return ui.chalkboard(pts[:k], title="まとめ（制度編）" if part == 1 else "まとめ（お金編）")


def tl(k):
    marks = [(0.02, "入社", "社会人1年目", "ink"), (0.5, "2年", "大卒は指名OK", "navy"),
             (0.98, "3年", "高卒も指名OK", "orange")]
    return ui.timeline(marks, w=1500, h=300, upto=k)


HIST = [("1965", "第1回ドラフト会議", "navy"), ("1993", "逆指名制度がスタート", "orange"),
        ("2001", "自由獲得枠に名前が変わる", "orange"), ("2005", "希望入団枠（1人まで）", "orange"),
        ("2007", "希望入団枠を廃止", "red"), ("2008", "高校生と大学・社会人を一本化", "green")]


def hist(k):
    return ui.vtimeline(HIST, upto=k, w=1100, row_h=112)


def months():
    return ui.month_bar(["10月", "11月", "12月", "1月", "2月", "3月"],
                        [(0, "ドラフト", "red"), (3, "社会人の期限", "green"), (5, "学生などの期限", "navy")], 1500, 250)


def paths(k):
    """指名漏れ後の進路"""
    return ui.checklist([("大学へ（4年後に再挑戦）", True), ("社会人へ（高卒は3年後）", True),
                         ("独立リーグへ（1年目から対象）", True)], upto=k, w=1200, size=54)


CH0 = "はじめに"
CH1 = "ドラフトとは何か"
CH2 = "ドラフトの歴史"
CH3 = "プロ志望届"
CH4 = "指名できる選手のルール"
CH5 = "1位指名：入札と抽選"
CH6 = "2位以降：ウェーバー方式"
CH7 = "育成ドラフト"
CH8 = "指名されたあとの流れ"
CH9 = "新人契約の3点セット"
CH10 = "ドラフト順位別の契約金の相場"
CH11 = "高卒・大卒・社会人で何が違う？"
CH12 = "指名縛り・入団拒否・指名漏れ"
CH13 = "なぜ上限とウェーバーがあるのか"
CH14 = "まとめ"
CH7B = "育成選手のお金"

SCENES = [
    # ===== 0. はじめに =====
    S(CH0, [
        "毎年秋に行われる、プロ野球のドラフト会議。",
        "名前が読み上げられる瞬間はニュースで見ても、その裏側のルールまで知っている人は、意外と少ないかもしれません。",
        "なぜ1位だけ抽選があるのか。2位以降の順番は、どう決まっているのか。",
        "そして、指名された選手は、実際にいくらもらえるのか。",
        "今回は、ドラフトのお金と制度を、最初から最後までまとめて解説します。",
    ], [
        E(il.stadium, 960, 520, at=0, until=2, anim="rise"),
        E(P(ui.label, "毎年秋のドラフト会議", "navy", 80), 960, 230, at=0, until=2, delay=0.5),
        E(P(il.mark, "q", 200), 560, 500, at=2, until=3),
        E(P(il.lottery_box), 1300, 520, at=2, until=3, anim="drop", delay=0.8),
        E(P(il.money, 3), 960, 560, at=3, until=4, anim="rise"),
        E(P(ui.label, "いくらもらえる？", "red", 90), 960, 260, at=3, until=4, delay=0.4),
        E(P(ui.big_word, "お金と制度", "yellow", 170), 960, 330, at=4, anim="zoom"),
        E(P(ui.label, "ドラフト完全解説", "navy", 96), 960, 600, at=4, delay=0.8),
    ], cam="in"),

    # ===== 1. ドラフトとは何か =====
    S(CH1, [
        "ドラフト会議の正式な名前は、新人選手選択会議といいます。",
        "主催するのは、プロ野球の12球団でつくる日本野球機構、通称NPBです。",
        "ここで大事なのは、ドラフトで決まるのは入団ではなく、その選手と交渉できる権利だということです。",
        "これを、交渉権と呼びます。",
        "指名された球団だけがその選手と交渉でき、ほかの球団は手を出せません。",
    ], [
        E(P(ui.label, "正式名称", "ink", 64), 960, 250, at=0, until=2),
        E(P(ui.big_word, "新人選手選択会議", "ink_brush", 140), 960, 450, at=0, until=1, anim="zoom"),
        E(P(il.building, "office"), 620, 560, at=1, until=2, anim="rise"),
        E(P(ui.label, "日本野球機構（NPB）", "navy", 76), 1260, 520, at=1, until=2, anim="slide_r"),
        E(P(il.contract, amount="交渉権"), 620, 560, at=2, anim="drop"),
        E(P(ui.label, "決まるのは入団ではなく", "navy", 64), 1250, 380, at=2, delay=0.6),
        E(P(ui.big_word, "交渉権", "red", 150), 1250, 580, at=3, anim="zoom"),
        E(P(ui.label, "他球団は交渉できない", "ink", 58, 8), 1250, 770, at=4),
    ]),
    S(CH1, [
        "ドラフトには、大きく分けて二つの会議があります。",
        "一つは、一軍の試合にも出られる支配下選手を選ぶ、通常のドラフト。",
        "もう一つは、その後に行われる、育成選手を選ぶ育成ドラフトです。",
        "それぞれ、ルールもお金の動き方もかなり違うので、この動画では順番に見ていきます。",
    ], [
        E(P(ui.flow_box, "ドラフト会議", "ink", 520, 130, 56), 960, 250, at=0, anim="pop"),
        E(P(ui.line_arrow, 0, 0, -330, 160, ui.NAVY, 8), 800, 400, at=1, anim="wipe_right", over=True),
        E(P(ui.flow_box, "通常のドラフト\n（支配下選手）", "navy", 540, 170, 50), 560, 600, at=1, delay=0.4),
        E(P(ui.line_arrow, 0, 0, 330, 160, ui.ORANGE, 8), 1120, 400, at=2, anim="wipe_right", over=True),
        E(P(ui.flow_box, "育成ドラフト\n（育成選手）", "orange", 540, 170, 50), 1360, 600, at=2, delay=0.4),
        E(P(ui.label, "ルールもお金も別物", "red", 70), 960, 800, at=3, anim="rise"),
    ], bg="dots", trans="slide"),

    # ===== 2. 歴史 =====
    S(CH2, [
        "ドラフトが始まったのは、1965年です。",
        "それまでは、球団が自由に選手と交渉する、いわば早い者勝ちの時代でした。",
        "その結果、人気の選手には契約金がどんどんつり上がり、お金のある球団に有力な選手が集まっていきました。",
        "そこで、戦力のバランスを保ち、契約金の高騰を抑えるために導入されたのが、ドラフト制度です。",
    ], [
        C(1965, lambda v: f"{int(v)}年", 960, 450, at=0, until=1, color="navy", size=200, dur=1.2),
        E(P(il.person, "staff", "normal", TIE, pose="point"), 520, 620, at=1, until=3, anim="slide_l", scale=0.85),
        E(P(il.person, "staff", "surprised", TIE2), 1400, 620, at=1, until=3, anim="slide_r", scale=0.85),
        E(P(ui.bubble, "うちに来て！", 48, "down"), 520, 290, at=1, until=2, delay=0.5),
        E(P(ui.bubble, "いや、うちに！", 48, "down"), 1400, 290, at=1, until=2, delay=1.4),
        E(P(ui.arrow, 240, ui.RED, 90), 960, 520, at=2, until=3, anim="rise"),
        E(P(ui.label, "契約金が高騰", "red", 80), 960, 250, at=2, until=3, delay=0.4),
        E(P(il.scale_balance), 620, 580, at=3, anim="rise"),
        E(P(ui.label, "戦力の均衡", "navy", 84), 1300, 420, at=3, delay=0.6),
        E(P(ui.label, "契約金の抑制", "orange", 84), 1300, 620, at=3, delay=1.6),
    ], cam="in"),
    S(CH2, [
        "ただ、その後のドラフトは、何度も形を変えてきました。",
        "1993年には、大学生や社会人の選手が、行きたい球団を自分で選べる逆指名制度が始まります。",
        "2001年には、これが自由獲得枠という名前に変わりました。",
        "2005年からは希望入団枠となり、使える人数が1球団1人までに減らされます。",
        "そして2007年、この希望入団枠は廃止されました。",
        "翌年の2008年からは、高校生と、大学生や社会人のドラフトが一本化され、今の形に近づいていきます。",
    ], [
        E(P(hist, 1), 960, 510, at=0, until=1, anim="wipe_up"),
        E(P(hist, 2), 960, 510, at=1, until=2, anim="none"),
        E(P(hist, 3), 960, 510, at=2, until=3, anim="none"),
        E(P(hist, 4), 960, 510, at=3, until=4, anim="none"),
        E(P(hist, 5), 960, 510, at=4, until=5, anim="none"),
        E(P(hist, 6), 960, 510, at=5, anim="none"),
    ], bg="tint", trans="wipe"),
    S(CH2, [
        "なぜ、選手が球団を選べる仕組みは、なくなったのでしょうか。",
        "きっかけは、お金の問題でした。",
        "選手に選んでもらうために、球団がアマチュア選手に裏で金銭を渡す問題が、相次いで発覚したのです。",
        "2007年には西武に、制裁金3000万円と、その年の高校生ドラフトで上位2人の指名権をはく奪する処分が下されました。",
        "ドラフトで指名権が取り上げられたのは、制度が始まって以来、初めてのことでした。",
        "こうして、選手が球団を選べる枠はなくなり、くじ引きとウェーバーを中心とした今の仕組みに落ち着いたのです。",
    ], [
        E(P(il.mark, "q", 220), 960, 480, at=0, until=1),
        E(P(il.money, 3), 960, 560, at=1, until=2, anim="drop"),
        E(P(il.person, "staff", "normal", TIE), 640, 600, at=2, until=3, anim="slide_l", scale=0.85),
        E(P(il.money, 1), 1060, 640, at=2, until=3, anim="slide_r", delay=0.8),
        E(P(ui.stamp, "裏で金銭", ui.RED, 110, -8), 1350, 360, at=2, until=3, delay=1.6),
        E(P(il.newspaper, "スポーツ報"), 560, 560, at=3, until=5, anim="slide_l"),
        E(P(ui.label, "制裁金3000万円", "red", 76), 1250, 400, at=3, until=5, delay=0.6),
        E(P(ui.label, "上位2人の指名権はく奪", "navy", 64), 1250, 580, at=3, until=5, delay=2.4),
        E(P(ui.stamp, "制度初", ui.RED, 100, -8), 1250, 760, at=4, until=5),
        E(P(il.lottery_box), 620, 560, at=5, anim="drop"),
        E(P(ui.label, "くじ引き＋ウェーバー", "navy", 80), 1250, 560, at=5, delay=0.6),
    ], trans="slide"),

    # ===== 3. プロ志望届 =====
    S(CH3, [
        "ここからは、ドラフトの流れに沿って見ていきます。",
        "最初の関門が、プロ野球志望届です。",
        "高校生や大学生がドラフトで指名されるには、事前にこの届を出しておく必要があります。",
        "出していない学生は、進学や就職を希望しているとみなされ、指名を受けることができません。",
    ], [
        E(P(il.person, "gakuran", "normal"), 620, 600, at=0, until=1, anim="rise"),
        E(P(ui.big_word, "最初の関門", "yellow", 140), 1260, 450, at=0, until=1, anim="zoom", delay=0.6),
        E(P(il.form_paper, "プロ野球志望届"), 960, 520, at=1, until=2, anim="drop"),
        E(P(il.person, "gakuran", "happy"), 560, 600, at=2, until=3, anim="slide_l"),
        E(P(il.form_paper, "プロ野球志望届"), 1000, 520, at=2, until=3, anim="pop", delay=0.6),
        E(P(ui.label, "出した学生だけ", "red", 80), 1500, 420, at=2, until=3, delay=1.4),
        E(P(il.person, "gakuran", "worried"), 560, 600, at=3, anim="rise"),
        E(P(ui.label, "出していない", "ink", 64), 1250, 330, at=3, delay=0.4),
        E(P(ui.label, "→ 指名できない", "red", 84), 1250, 500, at=3, delay=1.4),
    ], bg="dots"),
    S(CH3, [
        "届けを出す先は、高校生なら高校野球連盟、大学生なら所属する大学野球連盟です。",
        "高校生の場合、受け付けは夏の甲子園が終わってから始まり、締め切りはドラフト会議の2週間前です。",
        "一方で、社会人チームや独立リーグの選手は、この届を出さなくても指名の対象になります。",
    ], [
        E(P(ui.checklist, [("高校3年生 → 高校野球連盟", True), ("大学4年生 → 大学野球連盟", True)], 99, 1200, 56),
          960, 470, at=0, until=1, anim="wipe_right"),
        E(P(ui.timeline, [(0.05, "甲子園のあと", "受付開始", "orange"), (0.55, "2週間前", "締め切り", "red"),
                          (0.95, "ドラフト", "会議", "navy")], 1500, 300), 960, 480, at=1, until=2, anim="wipe_right"),
        E(P(ui.checklist, [("社会人チームの選手", False), ("独立リーグの選手", False)], 99, 1000, 56),
          760, 520, at=2, anim="slide_l"),
        E(P(ui.label, "志望届は不要", "green", 84), 1450, 520, at=2, delay=1.0),
    ], trans="zoom"),
    S(CH3, [
        "この志望届の制度は、高校生では2004年度、大学生では2007年度から始まりました。",
        "それ以前は、進学や就職を決めていた選手を球団が強引に指名し、トラブルになる例がありました。",
        "志望届は、本人がプロに行く意思があるかどうかを、事前にはっきりさせるための仕組みなのです。",
    ], [
        E(P(ui.timeline, [(0.1, "2004年度", "高校生で開始", "orange"), (0.9, "2007年度", "大学生でも開始", "navy")], 1400, 300),
          960, 480, at=0, until=1, anim="wipe_right"),
        E(P(il.person, "gakuran", "surprised"), 600, 600, at=1, until=2, anim="rise"),
        E(P(ui.bubble, "大学に行く\nつもりなのに…", 48, "left"), 1150, 330, at=1, until=2, delay=0.4),
        E(P(ui.stamp, "強行指名", ui.RED, 100, -8), 1280, 650, at=1, until=2, delay=1.6),
        E(P(il.form_paper, "プロ野球志望届"), 620, 520, at=2, anim="drop"),
        E(P(ui.label, "プロに行く意思を", "navy", 70), 1240, 420, at=2, delay=0.6),
        E(P(ui.label, "事前にはっきり", "red", 84), 1240, 600, at=2, delay=1.4),
    ], bg="tint", trans="fade"),

    # ===== 4. 指名できる選手のルール =====
    S(CH4, [
        "志望届のほかにも、指名できる選手にはいくつかのルールがあります。",
        "まず社会人野球の選手は、高校を出て入った場合は3年、大学などを出て入った場合は2年たたないと、指名できません。",
        "これは、日本野球連盟との取り決めによるものです。",
        "入ってすぐにプロへ引き抜かれてしまうと、社会人チームの側は困ってしまいます。",
    ], [
        E(P(ui.label, "指名できる選手のルール", "navy", 80), 960, 450, at=0, until=1, anim="zoom"),
        E(P(tl, 1), 960, 480, at=1, until=(1, 3.0), anim="wipe_right"),
        E(P(tl, 2), 960, 480, at=1, until=(1, 5.6), anim="none", delay=3.0),
        E(P(tl, 3), 960, 480, at=1, until=2, anim="none", delay=5.6),
        E(P(il.building, "company"), 600, 560, at=2, anim="rise"),
        E(P(ui.label, "日本野球連盟との取り決め", "green", 64), 1240, 450, at=2, delay=0.5),
        E(P(ui.label, "チームを守るため", "orange", 80), 1240, 640, at=3, anim="slide_r"),
    ]),
    S(CH4, [
        "一方で、独立リーグの選手は、入った1年目からドラフトの対象になります。",
        "高校で指名されなかった選手が、独立リーグで1年プレーして、再びドラフトに挑戦するという道もあるわけです。",
        "また、日本国籍の選手が、日本の球団を経由せず海外のプロに入った場合は、帰国後もドラフトを経て入団するのが原則です。",
        "かつては、ドラフトを拒否して海外に渡った選手は一定期間、日本の球団と契約できないという取り決めもありました。",
        "この取り決めは、2008年から2020年まで続き、田澤ルールと呼ばれていました。",
    ], [
        E(P(il.stadium, 480, 260), 620, 560, at=0, until=2, anim="rise"),
        E(P(ui.label, "独立リーグ", "orange", 84), 620, 300, at=0, until=2),
        E(P(ui.label, "1年目から対象", "red", 84), 1300, 480, at=0, until=1, anim="slide_r", delay=0.5),
        E(P(ui.timeline, [(0.05, "高3", "指名なし", "ink"), (0.5, "独立1年目", "プレー", "orange"),
                          (0.95, "ドラフト", "再挑戦", "red")], 860, 300), 1340, 520, at=1, until=2, anim="wipe_right"),
        E(P(il.plane), 620, 500, at=2, anim="slide_l"),
        E(P(ui.label, "海外から戻っても", "navy", 66), 1260, 400, at=2, until=3, delay=0.5),
        E(P(ui.label, "原則ドラフトを経由", "red", 72), 1260, 560, at=2, until=3, delay=1.8),
        E(P(ui.label, "一定期間は契約できない", "navy", 64), 1260, 480, at=3, until=4, delay=0.4),
        E(P(ui.big_word, "田澤ルール", "ink_brush", 130), 1260, 420, at=4, anim="zoom"),
        E(P(ui.label, "2008〜2020年", "orange", 72), 1260, 620, at=4, delay=0.8),
    ], bg="dots", trans="slide"),

    # ===== 5. 1位指名：入札と抽選 =====
    S(CH5, [
        "いよいよ、ドラフト当日の指名の流れです。",
        "1巡目、つまり1位指名は、入札抽選という方式で行われます。",
        "12球団が、ほしい選手の名前を、一斉に書いて提出します。",
        "ほかの球団と重ならなければ、その時点で交渉権が確定します。",
        "もし複数の球団が同じ選手を指名したら、くじ引きで交渉権を決めます。",
    ], [
        E(P(ui.big_word, "ドラフト当日", "yellow", 150), 960, 450, at=0, until=1, anim="zoom"),
        E(P(ui.big_word, "入札抽選", "red_brush", 180), 960, 450, at=1, until=2, anim="zoom"),
        E(P(il.person, "staff", "normal", TIE), 400, 620, at=2, until=4, anim="drop", scale=0.75),
        E(P(il.person, "staff", "normal", TIE2), 760, 620, at=2, until=4, anim="drop", scale=0.75, delay=0.3),
        E(P(il.person, "staff", "normal", (40, 140, 80)), 1120, 620, at=2, until=4, anim="drop", scale=0.75, delay=0.6),
        E(P(il.person, "staff", "normal", (230, 140, 30)), 1480, 620, at=2, until=4, anim="drop", scale=0.75, delay=0.9),
        E(P(ui.label, "一斉に提出", "navy", 80), 960, 250, at=2, until=3, delay=1.2),
        E(P(ui.label, "重ならなければ交渉権確定", "green", 70), 960, 250, at=3, until=4),
        E(P(il.lottery_box), 700, 560, at=4, anim="drop"),
        E(P(il.lottery_card), 1260, 470, at=4, anim="rise", delay=1.2),
        E(P(ui.label, "重複したら抽選", "red", 80), 1260, 700, at=4, delay=1.8),
    ], cam="in"),
    S(CH5, [
        "抽選に外れた球団は、外れた球団どうしで、もう一度入札をします。",
        "そこでまた重なれば、また抽選。",
        "これを、全球団の1位が決まるまで繰り返します。",
        "いわゆる、外れ1位、外れ外れ1位と呼ばれるのは、このためです。",
        "これまでの最多は、1人の選手に8球団の指名が重なったケースです。",
    ], [
        E(P(ui.flow_box, "1回目の入札", "navy", 420, 120, 50), 400, 280, at=0, anim="pop"),
        E(P(ui.line_arrow, 0, 0, 200, 0, ui.INK, 8), 720, 280, at=0, anim="wipe_right", over=True, delay=0.4),
        E(P(ui.flow_box, "重複→抽選", "red", 380, 120, 50), 1060, 280, at=0, delay=0.8),
        E(P(ui.line_arrow, 0, 0, 0, 160, ui.INK, 8), 1060, 450, at=0, anim="wipe_up", over=True, delay=1.6),
        E(P(ui.flow_box, "外れた球団だけで\n再入札", "orange", 460, 150, 46), 1060, 640, at=0, delay=2.0),
        E(P(ui.line_arrow, 0, 0, -380, -250, ui.ORANGE, 8, "くり返す"), 640, 520, at=1, anim="wipe_right", over=True),
        E(P(ui.label, "全球団の1位が決まるまで", "navy", 56, 8), 420, 760, at=2),
        E(P(ui.big_word, "外れ1位", "yellow", 110), 1580, 470, at=3, anim="zoom", scale=0.8),
        E(P(ui.label, "最多は8球団競合", "red", 64), 1500, 780, at=4, anim="rise"),
    ], bg="dots", trans="wipe"),
    S(CH5, [
        "この1位指名には、駆け引きもあります。",
        "人気の選手に入札すれば、抽選に外れるリスクがあります。",
        "逆に、競合しにくい選手を一本釣りすれば、確実に交渉権を手に入れられます。",
        "最近は、ドラフトの前に1位で指名する選手を公表する球団も増えていて、2022年には12球団のうち9球団が事前に公表しました。",
        "公表することで、ほかの球団の入札をけん制する狙いもあると言われています。",
    ], [
        E(P(il.person, "staff", "normal", TIE, pose="think"), 600, 620, at=0, until=3, anim="rise", scale=0.85),
        E(P(ui.big_word, "駆け引き", "red_brush", 150), 1260, 450, at=0, until=1, anim="zoom"),
        E(P(ui.label, "人気選手に入札", "navy", 70), 1260, 330, at=1, until=3),
        E(P(ui.label, "→ 抽選に外れるかも", "red", 66), 1260, 470, at=1, until=3, delay=1.0),
        E(P(ui.label, "競合しにくい選手", "navy", 70), 1260, 620, at=2, until=3),
        E(P(ui.label, "→ 確実に交渉権", "green", 66), 1260, 760, at=2, until=3, delay=1.0),
        E(P(il.newspaper, "1位指名を公表"), 600, 560, at=3, anim="slide_l"),
        C(9, lambda v: f"{int(v)}球団", 1260, 440, at=3, color="red", size=150, dur=1.0, delay=2.6),
        E(P(ui.label, "2022年・12球団中", "navy", 64), 1260, 640, at=3, delay=2.0),
        E(P(ui.label, "けん制のねらいも", "orange", 66), 1260, 790, at=4, anim="rise"),
    ], trans="zoom"),

    # ===== 6. 2位以降：ウェーバー方式 =====
    S(CH6, [
        "2巡目からは、抽選ではなく、順番に1人ずつ指名していきます。",
        "2巡目は、その年の成績が悪かった球団から順番に指名します。",
        "これを、ウェーバー方式と呼びます。",
        "3巡目は逆に、成績が良かった球団から指名します。こちらは逆ウェーバー方式です。",
        "4巡目以降も、ウェーバーと逆ウェーバーを交互にくり返していきます。",
    ], [
        E(P(ui.big_word, "2巡目からは順番に", "yellow", 120), 960, 450, at=0, until=1, anim="zoom"),
        E(P(ui.snake_order, 3, 12, 1), 960, 500, at=1, until=3, anim="wipe_right"),
        E(P(ui.label, "ウェーバー方式", "red", 70), 1500, 800, at=2, until=3),
        E(P(ui.snake_order, 3, 12, 2), 960, 500, at=3, until=4, anim="none"),
        E(P(ui.label, "逆ウェーバー方式", "navy", 70), 1500, 800, at=3, until=4, delay=3.0),
        E(P(ui.snake_order, 3, 12, 3), 960, 500, at=4, anim="none"),
    ], bg="tint"),
    S(CH6, [
        "ここで言う成績とは、その年のレギュラーシーズンの順位です。",
        "セ・リーグとパ・リーグで同じ順位の球団があるため、どちらのリーグを先にするかは、2019年からは1年ごとに入れ替えています。",
        "つまり2巡目の1番目は、どちらかのリーグの最下位の球団になります。",
        "この仕組みのおかげで、弱かった球団ほど、2巡目で良い選手を先に指名できるのです。",
    ], [
        E(P(ui.label, "その年の順位", "navy", 90), 960, 450, at=0, until=1, anim="zoom"),
        E(P(ui.flow_box, "セ・リーグ", "green", 380, 120, 54), 560, 380, at=1, until=2, anim="slide_l"),
        E(P(ui.flow_box, "パ・リーグ", "navy", 380, 120, 54), 1360, 380, at=1, until=2, anim="slide_r"),
        E(P(ui.label, "どちらが先かは1年ごとに交代", "red", 60, 8), 960, 620, at=1, until=2, delay=2.0),
        E(P(il.person, "player", "worried", GRAY_CAP, "6"), 640, 610, at=2, anim="rise"),
        E(P(ui.label, "最下位の球団が", "navy", 70), 1250, 420, at=2, delay=0.5),
        E(P(ui.label, "2巡目の1番目", "red", 86), 1250, 580, at=2, delay=1.4),
        E(P(ui.label, "弱い球団ほど先に選べる", "orange", 70), 1250, 760, at=3, anim="rise"),
    ], trans="fade"),
    S(CH6, [
        "指名できる人数にも決まりがあります。",
        "1球団あたりの指名は、原則として10人まで。",
        "12球団の合計が120人に届いていなければ、11人目以降も指名できます。",
        "逆に、合計が120人に達した時点で、指名はそこで終わりです。",
        "ただし、独立リーグの選手や海外のプロ選手を指名した場合、その人数は120人に含めません。",
    ], [
        E(P(ui.big_word, "指名人数", "yellow", 160), 960, 450, at=0, until=1, anim="zoom"),
        C(10, lambda v: f"1球団{int(v)}人", 960, 400, at=1, until=2, color="navy", size=150, dur=0.8),
        E(P(ui.label, "原則", "ink", 70), 960, 620, at=1, until=2, delay=0.8),
        C(120, lambda v: f"合計{int(v)}人", 960, 380, at=2, until=4, color="red", size=150, dur=1.0),
        E(P(ui.label, "届かなければ11人目以降もOK", "navy", 60, 8), 960, 600, at=2, until=3, delay=1.2),
        E(P(ui.label, "達したらそこで終了", "red", 72), 960, 600, at=3, until=4),
        E(P(ui.checklist, [("独立リーグの選手", False), ("海外のプロ選手", False)], 99, 900, 56), 960, 470, at=4,
          anim="slide_l"),
        E(P(ui.label, "120人に数えない", "orange", 72), 960, 740, at=4, delay=1.6),
    ], bg="dots", trans="slide"),

    # ===== 7. 育成ドラフト =====
    S(CH7, [
        "通常のドラフトが終わると、続いて育成ドラフトが行われます。",
        "育成選手の制度は2005年に始まりました。",
        "社会人野球のチームが次々と休部や廃部になり、選手の受け皿が減っていたことも、背景の一つです。",
        "育成ドラフトは、ウェーバーと逆ウェーバーを交互にくり返す方式で、参加したい球団だけが指名します。",
    ], [
        E(P(ui.big_word, "育成ドラフト", "yellow", 160), 960, 450, at=0, until=1, anim="zoom"),
        C(2005, lambda v: f"{int(v)}年", 520, 480, at=1, until=2, color="navy", size=170, dur=1.0),
        E(P(ui.label, "育成選手制度がスタート", "orange", 70), 1340, 480, at=1, until=2, delay=1.0),
        E(P(il.building, "company"), 600, 560, at=2, until=3, anim="rise"),
        E(P(ui.stamp, "休部・廃部", ui.RED, 110, -8), 1260, 420, at=2, until=3, delay=0.8),
        E(P(ui.label, "選手の受け皿が減った", "navy", 66), 1260, 660, at=2, until=3, delay=2.4),
        E(P(ui.label, "参加したい球団だけ", "navy", 76), 960, 280, at=3, anim="slide_r"),
        E(P(ui.label, "ウェーバー ⇄ 逆ウェーバー", "red", 70), 960, 520, at=3, delay=1.4),
    ], cam="in"),
    S(CH7, [
        "育成選手と支配下選手の一番の違いは、一軍の試合に出られるかどうかです。",
        "育成選手は背番号が3桁で、出られるのは二軍の試合だけ。",
        "一軍の試合に出るには、支配下選手として登録される必要があります。",
        "支配下選手の枠は1球団70人まで。シーズン中に支配下登録できるのは、7月31日までです。",
    ], [
        E(P(il.person, "player", "happy", BLUE_CAP, "12"), 560, 610, at=0, until=3, anim="slide_l"),
        E(P(il.person, "player", "worried", GRAY_CAP, "123"), 1360, 610, at=0, until=3, anim="slide_r", delay=0.6),
        E(P(ui.label, "支配下", "navy", 80), 560, 250, at=0, until=3, delay=0.3),
        E(P(ui.label, "育成", "orange", 80), 1360, 250, at=0, until=3, delay=0.9),
        E(P(ui.label, "背番号3桁・二軍のみ", "orange", 54, 8), 960, 790, at=1, until=2),
        E(P(ui.label, "一軍には支配下登録", "red", 54, 8), 960, 790, at=2, until=3),
        C(70, lambda v: f"{int(v)}人まで", 960, 380, at=3, color="red", size=120, dur=0.8),
        E(P(ui.label, "支配下登録は7月31日まで", "navy", 56, 8), 960, 560, at=3, delay=1.4),
    ], bg="split", trans="slide"),
    S(CH7, [
        "そして育成選手には、3年という区切りがあります。",
        "育成選手として3シーズン在籍して、翌年に支配下の契約を結べなかった場合、11月末でいったん自由契約になります。",
        "ただし、自由契約になったあとで、同じ球団や別の球団と、育成選手として契約し直すことはできます。",
        "毎年、育成から支配下に上がる選手はいますが、その数は限られています。",
    ], [
        E(P(il.calendar, "3年"), 960, 480, at=0, until=1, anim="drop"),
        E(P(ui.timeline, [(0.05, "1年目", "育成", "orange"), (0.38, "2年目", "育成", "orange"),
                          (0.7, "3年目", "育成", "orange"), (0.97, "11月末", "自由契約", "red")], 1500, 300),
          960, 480, at=1, until=2, anim="wipe_right"),
        E(P(il.contract, amount="再契約"), 640, 560, at=2, until=3, anim="drop"),
        E(P(ui.label, "同じ球団・別の球団と", "navy", 66), 1260, 440, at=2, until=3, delay=0.6),
        E(P(ui.label, "育成で再契約できる", "green", 76), 1260, 620, at=2, until=3, delay=1.6),
        E(P(ui.arrow, 300, ui.GREEN, 90), 620, 520, at=3, anim="rise"),
        E(P(ui.label, "支配下へ上がれるのは一部", "red", 66), 1220, 520, at=3, delay=0.8),
    ], trans="wipe"),

    # ===== 8. 指名されたあとの流れ =====
    S(CH8, [
        "では、指名されたあと、選手はどうなるのでしょうか。",
        "ドラフトのあと、球団のスカウトや幹部が、選手のもとに指名のあいさつに訪れます。",
        "そこから契約金や年俸の交渉が始まり、条件がまとまると仮契約、そして入団発表という流れです。",
    ], [
        E(P(il.mark, "q", 220), 960, 480, at=0, until=1),
        E(P(il.person, "staff", "happy", TIE, pose="point"), 560, 620, at=1, until=2, anim="slide_l", scale=0.85),
        E(P(il.person, "gakuran", "happy"), 1100, 620, at=1, until=2, anim="slide_r", scale=0.85),
        E(P(ui.bubble, "指名のごあいさつに\n来ました", 46, "right"), 900, 280, at=1, until=2, delay=0.8),
        E(P(ui.flow_box, "指名あいさつ", "navy", 380, 120, 50), 330, 480, at=2),
        E(P(ui.flow_box, "交渉", "orange", 260, 120, 50), 760, 480, at=2, delay=1.0),
        E(P(ui.flow_box, "仮契約", "green", 300, 120, 50), 1160, 480, at=2, delay=2.0),
        E(P(ui.flow_box, "入団発表", "red", 330, 120, 50), 1580, 480, at=2, delay=3.0),
        E(P(ui.label, "→", "ink", 80), 545, 480, at=2, delay=0.8, over=True),
        E(P(ui.label, "→", "ink", 80), 960, 480, at=2, delay=1.8, over=True),
        E(P(ui.label, "→", "ink", 80), 1370, 480, at=2, delay=2.8, over=True),
    ], bg="dots"),
    S(CH8, [
        "この交渉には、期限があります。",
        "交渉権が有効なのは、原則としてドラフトの翌年の3月末まで。",
        "社会人野球の選手は、翌年の1月末までです。",
        "期限までに契約できなければ、交渉権はなくなります。",
    ], [
        E(P(ui.big_word, "交渉には期限", "red", 140), 960, 450, at=0, until=1, anim="zoom"),
        E(P(months), 960, 520, at=1, anim="wipe_right"),
        E(P(ui.stamp, "交渉権が消える", ui.RED, 90, -6), 960, 250, at=3, anim="zoom"),
    ], trans="zoom"),

    # ===== 9. 新人契約の3点セット =====
    S(CH9, [
        "ここからは、お金の話です。",
        "新人の契約は、大きく分けて三つのお金でできています。",
        "入団するときに一度だけもらう、契約金。",
        "毎年もらう給料である、年俸。",
        ("そして、成績に応じて上乗せされる、出来高です。", "そして、成績に応じて上乗せされる、できだかです。"),
    ], [
        E(P(ui.big_word, "ここからはお金の話", "yellow", 120), 960, 450, at=0, until=1, anim="zoom"),
        E(P(ui.big_word, "3つのお金", "yellow", 150), 960, 480, at=1, until=2, anim="zoom"),
        E(P(il.contract, amount="契約金"), 420, 610, at=2, anim="slide_l"),
        E(P(ui.label, "契約金", "orange"), 420, 330, at=2, delay=0.4),
        E(P(il.money, 3), 960, 640, at=3, anim="rise"),
        E(P(ui.label, "年俸", "navy"), 960, 330, at=3, delay=0.4),
        E(P(il.ball, 90), 1500, 610, at=4, anim="slide_r"),
        E(P(ui.label, "出来高", "green"), 1500, 330, at=4, delay=0.4),
    ], cam="in"),
    S(CH9, [
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

    # ===== 10. 順位別の相場 =====
    S(CH10, [
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
    S(CH10, [
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

    # ===== 11. 高卒・大卒・社会人 =====
    S(CH11, [
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
    S(CH11, [
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

    # ===== 12. 指名縛り・入団拒否・指名漏れ =====
    S(CH12, [
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
    S(CH12, [
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
    S(CH12, [
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
    S(CH12, [
        "指名されても、選手が入団を断ることもできます。これが入団拒否です。",
        "入団を断った場合、その年に指名した球団は、原則として翌年のドラフトで同じ選手を指名できません。",
        "そして指名漏れや入団拒否のあと、もう一度ドラフトを目指す道は、大きく三つあります。",
        "大学に進めば、4年後に大学生として再挑戦。",
        "社会人チームに入れば、高卒の場合は3年後から指名の対象になります。",
        "独立リーグに入れば、1年目から指名の対象です。",
    ], [
        E(P(il.contract, amount="入団"), 620, 560, at=0, until=2, anim="drop"),
        E(P(il.mark, "ng", 300), 620, 560, at=0, until=2, delay=1.2, over=True),
        E(P(ui.big_word, "入団拒否", "red_brush", 150), 1260, 450, at=0, until=1, anim="zoom", delay=0.6),
        E(P(ui.label, "指名した球団は", "navy", 66), 1260, 400, at=1, until=2),
        E(P(ui.label, "翌年は同じ選手を指名できない", "red", 56, 8), 1260, 560, at=1, until=2, delay=1.4),
        E(P(ui.big_word, "再挑戦の道", "yellow", 140), 960, 450, at=2, until=3, anim="zoom"),
        E(P(paths, 1), 960, 500, at=3, until=4, anim="slide_l"),
        E(P(paths, 2), 960, 500, at=4, until=5, anim="none"),
        E(P(paths, 3), 960, 500, at=5, anim="none"),
    ], bg="dots", trans="fade"),

    # ===== 育成のお金 =====
    S(CH7B, [
        "ここで、育成選手のお金も見ておきましょう。",
        "育成選手には、契約金がありません。",
        ("代わりに支払われるのが支度金で、標準はおよそ300万円です。", "代わりに支払われるのが、したくきんで、標準はおよそ300万円です。"),
        "年俸の最低ラインも200万円台前半と、支配下の選手よりかなり低く抑えられています。",
        "1位の契約金1億円と比べると、その差は30倍以上です。",
    ], [
        E(P(ui.big_word, "育成選手のお金", "yellow", 150), 960, 480, at=0, until=1, anim="zoom"),
        E(P(il.contract, amount="契約金"), 640, 560, at=1, until=2),
        E(P(il.mark, "ng", 320), 640, 560, at=1, until=2, delay=0.5, over=True),
        E(P(ui.label, "契約金なし", "red", 90), 1250, 560, at=1, until=2, anim="slide_r", delay=0.8),
        E(P(il.envelope, "支度金"), 600, 580, at=2, until=4, anim="drop"),
        E(P(ui.label, "支度金の標準", "orange", 70), 1250, 330, at=2, until=4, delay=0.6),
        C(300, lambda v: f"約{int(v)}万円", 1250, 500, at=2, until=4, color="red", size=110, delay=1.0),
        E(P(ui.label, "年俸の最低は200万円台前半", "navy", 58, 8), 1250, 720, at=3, until=4, anim="rise"),
        E(P(ui.label, "ドラフト1位", "navy", 70), 480, 240, at=4),
        E(P(il.money, 4), 480, 520, at=4, anim="rise", scale=1.15),
        C(10000, man, 480, 760, at=4, color="red", size=100, delay=0.3),
        E(P(ui.label, "育成", "orange", 70), 1440, 240, at=4, delay=0.6),
        E(P(il.envelope, "支度金"), 1440, 520, at=4, anim="rise", scale=0.75, delay=0.6),
        E(P(ui.number, "約300万円", "navy", 100), 1440, 760, at=4, anim="pop", delay=1.0),
        E(P(ui.big_word, "30倍以上", "red", 100), 960, 480, at=4, anim="zoom", delay=1.8),
    ], bg="split", trans="slide"),

    # ===== 13. なぜ上限とウェーバーがあるのか =====
    S(CH13, [
        "最後に、なぜ契約金の上限やウェーバー方式があるのかを、あらためて整理しておきます。",
        "もし上限がなければ、人気の選手をめぐって、球団どうしで契約金がどんどんつり上がってしまいます。",
        "そうなると、お金のある球団ばかりに有力な選手が集まり、戦力のバランスが崩れてしまいます。",
        "ウェーバー方式で弱い球団から選べるようにしているのも、同じ理由です。",
        "そして、過去のお金の問題への反省から、上限を守り、ドラフトを公平に保とうという流れが続いているのです。",
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
        E(P(ui.snake_order, 1, 12, 1, 1560, 200, ("2巡目",)), 960, 450, at=3, until=4, anim="wipe_right"),
        E(P(ui.label, "弱い球団から選べる", "orange", 76), 960, 700, at=3, until=4, delay=0.8),
        E(P(il.scale_balance), 620, 590, at=4, anim="rise"),
        E(P(ui.label, "ドラフトを公平に", "navy", 96), 1290, 430, at=4, delay=1.0),
        E(P(il.mark, "ok", 220), 1290, 650, at=4, delay=2.6),
    ], bg="dots", trans="fade"),

    # ===== 14. まとめ =====
    S(CH14, [
        "それでは、まとめです。まずは制度の話から。",
        "高校生と大学生は、プロ野球志望届を出した選手だけが指名の対象になります。",
        "1位は一斉に入札し、重なったら抽選。外れた球団は、もう一度入札します。",
        "2位以降は、成績が悪かった球団から、ウェーバーと逆ウェーバーを交互にくり返します。",
        "交渉の期限は、原則としてドラフトの翌年の3月末まで。",
        "育成選手は、3年を区切りに支配下を目指します。",
    ], [
        E(P(board, 0, 1), 960, 540, at=0, until=1, anim="none", delay=0, full=True),
        E(P(board, 1, 1), 960, 540, at=1, until=2, anim="none", delay=0, full=True),
        E(P(board, 2, 1), 960, 540, at=2, until=3, anim="none", delay=0, full=True),
        E(P(board, 3, 1), 960, 540, at=3, until=4, anim="none", delay=0, full=True),
        E(P(board, 4, 1), 960, 540, at=4, until=5, anim="none", delay=0, full=True),
        E(P(board, 5, 1), 960, 540, at=5, anim="none", delay=0, full=True),
    ], bg="board", trans="zoom"),
    S(CH14, [
        "続いて、お金の話です。",
        "新人契約の上限は、契約金1億円と出来高5000万円、年俸1600万円。",
        "2位以下は決まった額がなく、順位が下がるごとに相場も下がります。",
        "高卒・大卒・社会人の差は、契約金よりも年俸に出やすくなります。",
        "指名縛りは、選手が将来を見すえてつける条件です。",
        "そして、契約金の上限とウェーバー方式は、どちらも戦力のバランスを保つための仕組みなのです。",
    ], [
        E(P(board, 0, 2), 960, 540, at=0, until=1, anim="none", delay=0, full=True),
        E(P(board, 1, 2), 960, 540, at=1, until=2, anim="none", delay=0, full=True),
        E(P(board, 2, 2), 960, 540, at=2, until=3, anim="none", delay=0, full=True),
        E(P(board, 3, 2), 960, 540, at=3, until=4, anim="none", delay=0, full=True),
        E(P(board, 4, 2), 960, 540, at=4, until=5, anim="none", delay=0, full=True),
        E(P(board, 5, 2), 960, 540, at=5, anim="none", delay=0, full=True),
    ], bg="board", trans="slide"),

    # ===== 終了画面: 右半分を YouTube の終了画面要素のために空けておく =====
    S(CH14, [
        "今回は、ドラフトのお金と制度を、まとめて解説しました。",
        "次回は、FAで選手がいくら稼げるのかを見ていきます。",
    ], [
        E(P(ui.label, "次回予告", "orange", 70), 460, 300, at=1, anim="slide_l"),
        E(P(ui.label, "FAのお金のしくみ", "navy", 84), 460, 430, at=1, anim="slide_l", delay=0.4),
        E(P(il.person, "player", "happy", BLUE_CAP, "", pose="point"), 460, 680, at=0, anim="rise", scale=0.55),
    ], bg="end", trans="fade", hold=16),
]


# ---- 30分版で追加したシーンを差し込む -------------------------------------------
import extra_scenes as X  # noqa: E402


def _after(first_line, *new):
    """first_line で始まるシーンの直後に new を差し込む"""
    for i, sc in enumerate(SCENES):
        l0 = sc["lines"][0]
        l0 = l0[0] if isinstance(l0, tuple) else l0
        if l0.startswith(first_line):
            SCENES[i + 1:i + 1] = list(new)
            return
    raise KeyError(first_line)


_after("ドラフト会議の正式な名前", X.KOUSHOUKEN)
_after("ドラフトには、大きく分けて二つ", X.DRAFT_DAY)
_after("ドラフトが始まったのは、1965年", *X.PRE_DRAFT)
_after("ただ、その後のドラフトは", X.HISTORY_MORE, *X.EGAWA, X.ICHIBA)
_after("届けを出す先は", X.SHIBOU_COUNT)
_after("一方で、独立リーグの選手は", *X.TAZAWA, X.FOREIGN)
_after("いよいよ、ドラフト当日", X.SIMULATION)
_after("抽選に外れた球団は", X.ODDS, X.WHY_LOTTERY)
_after("ここで言う成績とは", X.WAIVER_EXAMPLE, X.READING)
_after("この三つには、12球団の申し合わせ", X.BONUS_DETAIL)
_after("この交渉には、期限があります", *X.CASE_STUDY)
_after("ここで、育成選手のお金も", *X.QA)
