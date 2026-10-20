"""30分版で追加したシーン。episode.py から読み込んで、各章の決まった位置に差し込む。"""
from __future__ import annotations

from functools import partial as P

import illust as il
import ui
from episode_parts import BLUE_CAP, GRAY_CAP, GREEN_CAP, TIE, TIE2, C, E, S, man  # noqa: F401

TEAM_COLORS = {"A": (214, 32, 40), "B": (28, 52, 130), "C": (36, 150, 72), "D": (236, 108, 28)}


def team(name, w=230, h=110, size=52):
    return ui.flow_box(f"{name}球団", TEAM_COLORS[name], w, h, size)


# 交渉権のたとえ (1章)
KOUSHOUKEN = S("ドラフトとは何か", [
    "交渉権は、たとえるなら、人気のお店の予約券のようなものです。",
    "予約券を持っている人だけが、そのお店に入れます。",
    "ただし予約券があっても、条件が合わなければ、入らずに帰ることもできます。",
    "ドラフトも同じで、球団は交渉権を手に入れますが、選手のほうが入団を断ることもできるのです。",
], [
    E(P(il.lottery_card, "予約券"), 600, 520, at=0, anim="drop"),
    E(P(ui.label, "交渉権", "red", 84), 600, 300, at=0, delay=0.8),
    E(P(il.building, "company"), 1300, 560, at=1, until=2, anim="rise"),
    E(P(ui.label, "人気のお店", "navy", 70), 1300, 250, at=1, until=2, delay=0.4),
    E(P(il.person, "player", "normal", BLUE_CAP, "", pose="think"), 1300, 600, at=2, until=3, anim="slide_r"),
    E(P(ui.bubble, "やっぱり\nやめておこう", 46, "left"), 1600, 300, at=2, until=3, delay=0.8),
    E(P(il.contract, amount="入団"), 1300, 560, at=3, anim="drop"),
    E(P(il.mark, "ng", 260), 1300, 560, at=3, delay=0.8, over=True),
    E(P(ui.label, "選手は断ることもできる", "navy", 56, 8), 1300, 800, at=3, delay=1.4),
], bg="tint", trans="slide")

# ドラフト当日の流れ (1章)
DRAFT_DAY = S("ドラフトとは何か", [
    "ドラフト会議は、毎年10月ごろに、1日で行われます。",
    "会場には、2009年から東京都内のホテルが使われています。",
    "当日は、まず1位の入札と抽選、次に2位以降の指名、最後に育成ドラフトという順番で進みます。",
    "テレビやネットで中継されるので、指名された瞬間の選手の表情を、見たことがある人も多いと思います。",
], [
    E(P(il.calendar, "10月"), 560, 520, at=0, until=1, anim="drop"),
    E(P(ui.label, "毎年10月ごろ・1日で", "navy", 70), 1250, 500, at=0, until=1, anim="slide_r", delay=0.6),
    E(P(il.building, "office"), 560, 560, at=1, until=2, anim="rise", name="hotel"),
    E(P(ui.label, "2009年から都内のホテル", "orange", 64), 1250, 680, at=1, until=2, delay=0.6),
    E(P(ui.flow_box, "1位の入札・抽選", "red", 470, 130, 48), 420, 300, at=2, anim="drop", over=True),
    E(P(ui.flow_box, "2位以降の指名", "navy", 470, 130, 48), 960, 300, at=2, anim="drop", delay=1.6, over=True),
    E(P(ui.flow_box, "育成ドラフト", "orange", 470, 130, 48), 1500, 300, at=2, anim="drop", delay=3.2, over=True),
    E(P(il.person, "gakuran", "happy", pose="cheer"), 960, 620, at=3, anim="rise", scale=0.8),
    E(P(ui.label, "中継で見られる", "green", 70), 1450, 640, at=3, delay=0.8),
], bg="dots", trans="wipe")

# 1978年・1991年の変化 (2章)
HISTORY_MORE = S("ドラフトの歴史", [
    "ちなみに、全球団が同時に指名して、重なったら抽選という、今の1位指名に近いやり方が始まったのは1978年です。",
    "また、昔はドラフトで指名されなかった選手を、あとから自由に獲得するドラフト外入団という方法もありました。",
    "このドラフト外入団は、1991年に廃止されています。",
], [
    C(1978, lambda v: f"{int(v)}年", 560, 470, at=0, until=1, color="navy", size=160, dur=1.0),
    E(P(il.lottery_box), 1300, 540, at=0, until=1, anim="drop", delay=1.0),
    E(P(ui.big_word, "ドラフト外入団", "ink_brush", 130), 960, 450, at=1, until=2, anim="zoom"),
    C(1991, lambda v: f"{int(v)}年", 560, 470, at=2, color="red", size=160, dur=1.0),
    E(P(ui.stamp, "廃止", ui.RED, 150, -10), 1300, 470, at=2, delay=1.2),
], trans="fade")

# 志望届を出しても (3章)
SHIBOU_COUNT = S("プロ志望届", [
    "ただ、志望届を出せば必ず指名されるわけではありません。",
    "例えば2025年は、高校生124人、大学生176人が志望届を出して、ドラフトの対象として公示されました。",
    "一方で、ドラフトで指名できるのは12球団あわせて原則120人まで。しかも、そこには社会人や独立リーグの選手も含まれます。",
    "志望届を出した選手の多くは、名前を呼ばれずにドラフトを終えることになるのです。",
], [
    E(P(il.form_paper, "プロ野球志望届"), 620, 520, at=0, until=1, anim="drop"),
    E(P(ui.label, "出せば必ず指名…ではない", "red", 64), 1260, 500, at=0, until=1, delay=0.6),
    E(P(ui.label, "高校生", "orange", 70), 560, 280, at=1, until=2),
    C(124, lambda v: f"{int(v)}人", 560, 480, at=1, until=2, color="orange", size=140, delay=0.4),
    E(P(ui.label, "大学生", "navy", 70), 1360, 280, at=1, until=2, delay=1.4),
    C(176, lambda v: f"{int(v)}人", 1360, 480, at=1, until=2, color="navy", size=140, delay=1.8),
    E(P(ui.label, "2025年に公示", "ink", 54, 8), 960, 700, at=1, until=2, delay=2.6),
    C(120, lambda v: f"原則{int(v)}人まで", 960, 420, at=2, until=3, color="red", size=130, dur=1.0),
    E(P(ui.label, "社会人・独立リーグも含む", "navy", 60, 8), 960, 640, at=2, until=3, delay=2.8),
    E(P(il.person, "gakuran", "worried"), 960, 600, at=3, anim="rise"),
    E(P(ui.label, "多くは名前を呼ばれない", "navy", 66), 960, 220, at=3, delay=0.6),
], bg="split", trans="slide")

# 外国人選手 (4章)
FOREIGN = S("指名できる選手のルール", [
    "ちなみに、外国人選手は、ドラフトの対象ではありません。",
    "ドラフトの対象になるのは、日本国籍を持つ選手か、日本の中学・高校・大学などに在学したことがある選手です。",
    "そのため、海外で育った外国人選手は、ドラフトを通さずに、球団が直接契約して獲得します。",
], [
    E(P(il.plane), 600, 500, at=0, until=1, anim="slide_l"),
    E(P(ui.label, "外国人選手はドラフト対象外", "red", 64), 1250, 500, at=0, until=1, delay=0.6),
    E(P(il.plane), 600, 500, at=2, anim="slide_l", name="plane2"),
    E(P(ui.checklist, [("日本国籍を持つ選手", True), ("日本の中学・高校・大学などに在学経験", True)], 99, 1080, 50),
      1250, 470, at=1, until=2, anim="slide_r"),
    E(P(ui.label, "どちらかなら対象", "navy", 60, 8), 1250, 720, at=1, until=2, delay=2.0),
    E(P(ui.label, "球団が直接契約", "green", 84), 1250, 500, at=2, anim="zoom"),
], bg="tint", trans="zoom")

# 抽選の確率 (5章)
ODDS = S("1位指名：入札と抽選", [
    "では、抽選に勝てる確率は、どのくらいなのでしょうか。",
    "2球団が重なれば、確率は2分の1。",
    "4球団なら4分の1、8球団なら8分の1まで下がります。",
    "人気の選手ほど、交渉権を手に入れられるかどうかは、まさに運しだいなのです。",
], [
    E(P(il.lottery_box), 960, 520, at=0, until=1, anim="drop"),
    E(P(ui.label, "2球団", "navy", 70), 400, 260, at=1),
    C(50, lambda v: f"{int(v)}%", 400, 470, at=1, color="navy", size=130, delay=0.4),
    E(P(ui.label, "4球団", "orange", 70), 960, 260, at=2),
    C(25, lambda v: f"{int(v)}%", 960, 470, at=2, color="orange", size=130, delay=0.4),
    E(P(ui.label, "8球団", "red", 70), 1520, 260, at=2, delay=2.0),
    C(12.5, lambda v: f"{v:.1f}%", 1520, 470, at=2, color="red", size=130, delay=2.4),
    E(P(ui.big_word, "運しだい", "red_brush", 140), 960, 700, at=3, anim="zoom"),
], bg="dots", trans="slide")

# 抽選のシミュレーション (5章)
SIMULATION = S("1位指名：入札と抽選", [
    "例えば、A、B、C、Dの4球団が、同じ選手に入札したとします。",
    "抽選でA球団が当たりを引けば、交渉権はA球団のものです。",
    "外れたB、C、Dの3球団は、別の選手を選んで、もう一度入札します。",
    "そこでB球団とC球団が同じ選手に入札すれば、今度はその2球団で抽選。",
    "それでも外れた球団は、さらにもう一度入札する、というわけです。",
], [
    E(P(team, "A"), 330, 280, at=0, anim="drop"),
    E(P(team, "B"), 750, 280, at=0, anim="drop", delay=0.3),
    E(P(team, "C"), 1170, 280, at=0, anim="drop", delay=0.6),
    E(P(team, "D"), 1590, 280, at=0, anim="drop", delay=0.9),
    E(P(il.lottery_box), 960, 610, at=0, until=2, anim="rise", delay=1.4),
    E(P(il.lottery_card, "A球団 交渉権"), 330, 560, at=1, anim="rise"),
    E(P(ui.label, "外れ → 再入札", "navy", 60, 8), 1170, 470, at=2, until=3),
    E(P(il.lottery_box), 960, 620, at=3, until=4, anim="drop"),
    E(P(ui.label, "B・Cで抽選", "red", 66), 960, 440, at=3, until=4, delay=0.6),
    E(P(ui.label, "外れたらまた入札", "orange", 70), 1170, 600, at=4, anim="rise"),
], trans="fade")

# なぜ1位だけ抽選か (5章)
WHY_LOTTERY = S("1位指名：入札と抽選", [
    "では、なぜ1位だけは抽選なのでしょうか。",
    "もし1位からウェーバー方式にすると、最下位の球団が、その年いちばん人気の選手を必ず獲得できてしまいます。",
    "1位だけは全球団にチャンスを残すために、入札と抽選にしていると考えられます。",
], [
    E(P(il.mark, "q", 220), 960, 480, at=0, until=1),
    E(P(ui.snake_order, 1, 12, 1, 1560, 200, ("1巡目？",)), 960, 360, at=1, until=2, anim="wipe_right"),
    E(P(ui.label, "最下位が必ず一番人気を獲得", "red", 60, 8), 960, 620, at=1, until=2, delay=2.0),
    E(P(il.lottery_box), 600, 560, at=2, anim="drop"),
    E(P(ui.label, "全球団にチャンス", "green", 84), 1280, 520, at=2, delay=0.8),
], bg="tint", trans="slide")

# ウェーバーのたとえ (6章)
WAIVER_EXAMPLE = S("2位以降：ウェーバー方式", [
    "ウェーバー方式は、たとえるなら、成績の悪かったチームから順番に、好きな選手を選べるルールです。",
    "例えば最下位の球団は、2巡目では1番目に指名できますが、3巡目では12番目になります。",
    "逆に優勝した球団は、2巡目では12番目ですが、3巡目では1番目です。",
    "こうして交互にすることで、極端に有利な球団が出ないように調整しているのです。",
], [
    E(P(il.person, "player", "worried", GRAY_CAP, "最"), 480, 610, at=0, anim="slide_l"),
    E(P(il.person, "player", "happy", BLUE_CAP, "優"), 1440, 610, at=0, anim="slide_r", delay=0.4),
    E(P(ui.label, "最下位", "orange", 76), 480, 250, at=0, delay=0.6),
    E(P(ui.label, "優勝", "navy", 76), 1440, 250, at=0, delay=0.9),
    E(P(ui.label, "2巡目 1番目", "red", 60, 8), 960, 400, at=1, until=3),
    E(P(ui.label, "3巡目 12番目", "ink", 60, 8), 960, 540, at=1, until=3, delay=2.4),
    E(P(ui.label, "2巡目 12番目", "ink", 60, 8), 960, 680, at=2, until=3),
    E(P(ui.label, "3巡目 1番目", "red", 60, 8), 960, 800, at=2, until=3, delay=1.6),
    E(P(il.scale_balance), 960, 560, at=3, anim="rise", scale=0.85),
], bg="split", trans="wipe")

# 2巡目以降の読み合い (6章)
READING = S("2位以降：ウェーバー方式", [
    "2巡目以降には、また別の駆け引きがあります。",
    "順番が後ろの球団は、自分の番が来るまでに、ほしい選手をほかの球団に取られてしまうかもしれません。",
    "そのため、ほかの球団が狙っていそうな選手を読み、どの順番で誰を指名するかを考えるのです。",
], [
    E(P(ui.big_word, "読み合い", "red_brush", 170), 960, 450, at=0, until=1, anim="zoom"),
    E(P(il.person, "staff", "worried", TIE2, pose="think"), 600, 620, at=1, anim="rise", scale=0.85),
    E(P(ui.bubble, "先に取られる\nかも…", 46, "left"), 1100, 330, at=1, until=2, delay=0.6),
    E(P(ui.flow_box, "誰を・どの順番で", "navy", 560, 130, 50), 1300, 420, at=2, anim="slide_r"),
    E(P(il.mark, "q", 180), 1300, 650, at=2, delay=1.2),
], trans="zoom")

# 出来高と年俸の補足 (9章)
BONUS_DETAIL = S("新人契約の3点セット", [
    "出来高は、入団したあとの成績に応じて支払われるボーナスのようなものです。",
    "新人王を取ったら、規定の投球回数に届いたら、といった条件が、契約ごとに決められます。",
    "よく聞く「契約金1億円プラス出来高5000万円」は、この出来高を上限いっぱいまでつけた形です。",
    "そして年俸は、1年ごとの給料です。毎年の契約更改で、成績によって上がったり下がったりします。",
], [
    E(P(il.ball, 100), 560, 520, at=0, until=2, anim="drop"),
    E(P(ui.label, "出来高 ＝ 入団後のボーナス", "green", 64), 1250, 500, at=0, until=1, delay=0.6),
    E(P(ui.checklist, [("新人王を取ったら", True), ("規定投球回に届いたら", True)], 99, 900, 56), 1250, 500, at=1,
      until=2, anim="slide_r"),
    C(10000, man, 560, 450, at=2, until=3, color="red", size=120, dur=1.0),
    E(P(ui.label, "＋", "ink", 100), 960, 450, at=2, until=3, delay=1.0),
    C(5000, man, 1400, 450, at=2, until=3, color="green", size=120, dur=1.0, delay=1.4),
    E(P(ui.label, "出来高を上限までつけた形", "navy", 60, 8), 960, 680, at=2, until=3, delay=2.4),
    E(P(il.money, 3), 600, 580, at=3, anim="rise"),
    E(P(ui.label, "年俸は毎年の契約更改で", "navy", 62), 1250, 440, at=3, delay=0.6),
    E(P(ui.label, "上がる・下がる", "red", 84), 1250, 620, at=3, delay=1.8),
], bg="dots", trans="slide")

# ケーススタディ (8章のあと)
CASE_STUDY = [
    S("ケーススタディ：ある高校生の秋", [
        "ここで、ここまでの流れを、架空の高校生、Aくんの例でおさらいしてみましょう。",
        "夏の甲子園が終わったあと、Aくんはプロ野球志望届を提出しました。",
        "10月のドラフト会議。Aくんには、2つの球団が1位で入札しました。",
        "抽選の結果、交渉権を引き当てたのはB球団です。",
    ], [
        E(P(il.person, "gakuran", "happy"), 960, 600, at=0, anim="drop"),
        E(P(ui.label, "架空の高校生 Aくん", "navy", 72), 960, 230, at=0, delay=0.6),
        E(P(il.form_paper, "プロ野球志望届"), 1400, 520, at=1, anim="slide_r"),
        E(P(team, "B"), 420, 300, at=2, anim="drop"),
        E(P(team, "C"), 420, 480, at=2, anim="drop", delay=0.4),
        E(P(ui.label, "1位で2球団が入札", "red", 56, 8), 420, 680, at=2, until=3, delay=1.0),
        E(P(il.lottery_card, "B球団 交渉権"), 420, 700, at=3, anim="rise"),
    ], bg="tint"),
    S("ケーススタディ：ある高校生の秋", [
        "数日後、B球団のスカウトが指名のあいさつに訪れ、交渉が始まります。",
        "1位指名なので、条件は契約金1億円、出来高5000万円という、上限いっぱいの提示でした。",
        "Aくんは高校生なので、年俸は大学生や社会人の1位より、少し低めに設定されることもあります。",
        "条件に納得したAくんは仮契約を結び、翌年の3月末の期限よりずっと前に、入団が決まりました。",
    ], [
        E(P(il.person, "staff", "happy", TIE2, pose="point"), 520, 620, at=0, until=1, anim="slide_l", scale=0.85),
        E(P(il.person, "gakuran", "happy"), 1080, 620, at=0, until=1, anim="slide_r", scale=0.85),
        E(P(ui.bubble, "ぜひB球団に", 46, "right"), 900, 300, at=0, until=1, delay=0.8),
        E(P(ui.table, ["", "提示"], [["契約金", "1億円"], ["出来高", "5000万円"]], [300, 400], 96, 1), 960, 460,
          at=1, until=3, anim="wipe_right"),
        E(P(ui.label, "高卒は年俸低めのことも", "orange", 56, 8), 960, 760, at=2, until=3),
        E(P(il.contract, amount="仮契約"), 620, 560, at=3, anim="drop"),
        E(P(ui.big_word, "入団決定", "red", 140), 1280, 480, at=3, anim="zoom", delay=1.0),
    ], trans="slide"),
    S("ケーススタディ：ある高校生の秋", [
        "もしAくんが「3位縛り」をつけていて、どの球団も3位までに指名しなかったら、どうなっていたでしょうか。",
        "その場合Aくんは、予定どおり大学に進学します。",
        "そして4年後、大学4年生で再び志望届を出し、もう一度ドラフトに挑戦することになるのです。",
    ], [
        E(P(ui.label, "もしも3位縛りだったら？", "red", 76), 960, 250, at=0, anim="zoom"),
        E(P(il.person, "gakuran", "worried"), 560, 610, at=0, until=1, anim="rise"),
        E(P(il.building, "university"), 560, 560, at=1, anim="rise"),
        E(P(ui.label, "大学へ進学", "navy", 80), 1260, 520, at=1, until=2, delay=0.6),
        E(P(ui.timeline, [(0.05, "1年", "大学", "navy"), (0.4, "2年", "", "navy"), (0.7, "3年", "", "navy"),
                          (0.97, "4年", "再び志望届", "red")], 1000, 300), 1300, 520, at=2, anim="wipe_right"),
    ], bg="dots", trans="fade"),
]

# よくある疑問 (13章の前)
QA = [
    S("よくある疑問", [
        "ここからは、ドラフトについてよくある疑問に答えていきます。",
        "まず、指名されたら、必ずプロに入らないといけないのでしょうか。",
        "答えは、いいえ。選手は入団を断ることができ、実際に、断って大学や社会人に進んだ選手もいます。",
    ], [
        E(P(ui.big_word, "よくある疑問", "yellow", 160), 960, 450, at=0, until=1, anim="zoom"),
        E(P(ui.flow_box, "Q1", "red", 160, 120, 64), 260, 260, at=1, anim="pop"),
        E(P(ui.label, "指名されたら必ず入団？", "navy", 70), 960, 260, at=1, anim="slide_r"),
        E(P(il.mark, "ng", 260), 600, 580, at=2, anim="pop"),
        E(P(ui.label, "断ることもできる", "red", 80), 1250, 560, at=2, delay=0.6),
    ], bg="tint"),
    S("よくある疑問", [
        "次に、大学を途中でやめれば、すぐにドラフトで指名されるのでしょうか。",
        "実は、その年の4月1日以降に大学などを退学した選手は、その年のドラフトでは指名できないルールがあります。",
        "途中でやめてすぐプロへ、という抜け道は、ふさがれているのです。",
    ], [
        E(P(ui.flow_box, "Q2", "red", 160, 120, 64), 260, 260, at=0, anim="pop"),
        E(P(ui.label, "大学をやめたらすぐ指名？", "navy", 70), 960, 260, at=0, anim="slide_r"),
        E(P(il.calendar, "4/1"), 600, 580, at=1, anim="drop"),
        E(P(ui.label, "以降に退学 → その年は指名不可", "red", 56, 8), 1220, 560, at=1, delay=1.0),
        E(P(ui.label, "抜け道はふさがれている", "orange", 60, 8), 1220, 760, at=2),
    ], trans="slide"),
    S("よくある疑問", [
        "育成選手として入団しても、一軍で活躍できるのでしょうか。",
        "支配下登録されれば、一軍の試合に出られます。",
        "実際に、育成から支配下に上がり、一軍の主力になった選手もいます。ただ、それはごく一部です。",
    ], [
        E(P(ui.flow_box, "Q3", "red", 160, 120, 64), 260, 260, at=0, anim="pop"),
        E(P(ui.label, "育成からでも一軍で活躍できる？", "navy", 64), 1000, 260, at=0, anim="slide_r"),
        E(P(il.person, "player", "happy", GRAY_CAP, "123"), 560, 610, at=1, anim="rise"),
        E(P(ui.arrow, 260, ui.GREEN, 0), 960, 600, at=1, delay=0.8),
        E(P(il.person, "player", "happy", BLUE_CAP, "12", pose="cheer"), 1360, 610, at=1, anim="rise", delay=1.4),
        E(P(ui.label, "ただし、ごく一部", "red", 60, 8), 960, 420, at=2, delay=2.0),
    ], bg="split", trans="wipe"),
    S("よくある疑問", [
        "契約金1億円は、そのまま手元に残るのでしょうか。",
        "契約金も収入なので、所得税などの税金がかかります。",
        "1億円がまるごと選手のものになるわけではない、というのも覚えておきたいポイントです。",
    ], [
        E(P(ui.flow_box, "Q4", "red", 160, 120, 64), 260, 260, at=0, anim="pop"),
        E(P(ui.label, "1億円はまるごと手元に？", "navy", 70), 960, 260, at=0, anim="slide_r"),
        E(P(il.money, 4), 600, 580, at=1, anim="drop"),
        E(P(ui.label, "税金がかかる", "red", 84), 1250, 520, at=1, delay=0.6),
        E(P(ui.label, "まるごとは残らない", "navy", 66), 1250, 700, at=2),
    ], trans="zoom"),
    S("よくある疑問", [
        "最後に、交渉の期限までに契約がまとまらなかったら、どうなるのでしょうか。",
        "その場合、球団の交渉権はなくなります。",
        "選手は、条件を満たせば、また別の年のドラフトで指名を受けることができます。",
    ], [
        E(P(ui.flow_box, "Q5", "red", 160, 120, 64), 260, 260, at=0, anim="pop"),
        E(P(ui.label, "期限までに契約できなかったら？", "navy", 64), 1000, 260, at=0, anim="slide_r"),
        E(P(il.contract, amount="交渉権"), 600, 580, at=1, anim="drop"),
        E(P(ui.stamp, "消滅", ui.RED, 130, -10), 600, 560, at=1, delay=0.8, over=True),
        E(P(ui.label, "別の年のドラフトで", "navy", 66), 1250, 500, at=2),
        E(P(ui.label, "また指名されうる", "green", 80), 1250, 680, at=2, delay=1.0),
    ], bg="dots", trans="fade"),
]
