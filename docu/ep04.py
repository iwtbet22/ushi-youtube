"""4本目「黒い霧事件」全編。

台本は script/ep04_narration.txt と同じ文 (tools/export_narration で書き出し、check_script で一致を確かめる)。
事実と出典は script/ep04_factcheck.md。

3本目までとの違い (参考にした政治解説チャンネルの作り):
- 冒頭は、黒い画面の一言 → 単語の連打 → 問い3つ → 登場人物紹介 → 題
- 本編は「第0章〜第6章」の物語として扱い、章の扉に筆文字の題を出す
- 文ごとに要の単語を大きく出す (kw)。ときどき口語のツッコミも字幕で出す
- 1つの場面を短くして、絵を早めに切り替える。話す速さも少し上げる
"""
from functools import partial as P

import charts as C
import look as L
import news as N
from ep02 import BALL, DOME, FANS, NAGOYA, ph, pic
import film
from film import E, S

film.VOICE = {"rate": "+8%", "pitch": "-4Hz"}  # 3本目 (+0%) より速く、1分あたり約300字
film.TAIL = 0.24

IKENAGA = "Ikenaga_1965.jpg"
HEIWADAI = "Heiwadai_1956.png"
HEIWADAI2 = "Heiwadai_Stadium01.jpg"
NAKANISHI = "Futoshi_Nakanishi_1954_NPB_All-star_game.jpg"
BLACKSOX = "Eight_men_banned.png"
DIET = "National_Diet_Building.jpg"
AUTORACE = "Auto_Race_in_Kawaguchi.jpg"

RED = (226, 52, 44)
WHITE = L.WHITE
GOLD = L.GOLD

T0, T1, T2, T3 = "第0章 野球賭博", "第1章 消えた投手", "第2章 告白", "第3章 広がる霧"
T4, T5, T6 = "第4章 100万円", "第5章 ライオンズ消滅の危機", "第6章 35年後"

# 読み上げで読み間違えやすい名前は、(画面の字, 読み上げる字) で書く
NAGAYASU = "永易"


def kw(s, size=150, color=WHITE):
    """文ごとに大きく出す要の単語 (太いゴシックに黒い縁)"""
    return P(L.text, s, "DelaGothicOne-Regular.ttf", size, color, 10, (0, 0, 0))


def brush(s, size=200, color=WHITE):
    """筆文字 (冒頭の一言、章の題)。筆の書体は数字が崩れて読みにくいので、数字を含むときは明朝にする"""
    if any(c.isdigit() for c in s):
        return P(L.text, s, "NotoSerifJP-Black.ttf", round(size * 0.9), color)
    return P(L.text, s, "YujiBoku-Regular.ttf", size, color)


def tsukkomi(s, size=64):
    """口語のツッコミ (画面の右上に斜めぎみに出す小さめの字)"""
    return P(L.text, s, "DelaGothicOne-Regular.ttf", size, (255, 214, 64), 6, (0, 0, 0))


def name_v(s, at=0, until=None, delay=0.2, color=WHITE):
    return E(P(L.vertical, s, 130, "YujiBoku-Regular.ttf", color), 150, 70, at=at, until=until, delay=delay,
             anim="wipe", anchor="t")


def note(s="※金額は報道・証言による"):
    return E(P(C.note, s), 1860, 118, anchor="tr")


def chap(no, title, seed):
    """章の扉 (ナレーションなし)。概要欄のチャプター名を chapter に持たせる"""
    return dict(S([], P(L.plain), move="in", hold=2.6, trans="fade", els=[
        E(P(L.text, f"第{no}章", "NotoSerifJP-Black.ttf", 64, GOLD), 960, 330, anim="rise"),
        E(brush(f"「{title}」", 170), 960, 520, delay=0.3, anim="zoom", sfx="boom"),
    ]), chapter=f"第{no}章 {title}")


def cast(name, role, bg, color):
    """登場人物紹介の1カット (ナレーションなし、音楽と効果音だけ)。写真がなければ、その人の色で文字が流れる背景"""
    if getattr(bg, "func", None) is L.bokeh:
        bg = P(N.code_rain, bg.args[0], color)
    return S([], bg, move="in", hold=1.25, trans="cut", els=[
        E(P(L.vertical, name, 150, "YujiBoku-Regular.ttf", color), 1500, 110, anim="glitch", anchor="t", sfx="whoosh"),
        E(kw(role, 84, WHITE), 640, 760, delay=0.25, anim="slam"),
    ])


def W(word, i, color=WHITE, size=150, y=440):
    """i 番目の文のあいだだけ出す単語"""
    return E(kw(word, size, color), 960, y, at=i, until=i, anim="slam", sfx="boom")


# ---- 冒頭 -------------------------------------------------------------------
OPEN = [
    S(["100万円。"], P(L.plain), move="in", trans="cut", hold=0.4, els=[
        E(brush("100万円", 260), 960, 440, anim="zoom", sfx="boom"),
    ]),
    S(["このお金を受け取り、返さなかった。",
       "それだけの理由で、プロ野球から永久に追放されたエースがいます。"],
      ph(IKENAGA, "dark", focus=(0.5, 0.3)), move="in", els=[
          E(kw("返さなかった", 130), 960, 420, until=0, anim="slam", sfx="boom"),
          E(kw("永久追放", 190, RED), 960, 420, at=1, anim="glitch", sfx="boom"),
      ]),
    S([("新人でいきなり20勝。入団から5年で99勝。", "新人でいきなり20しょう。入団から5年で99勝。"),  # 20勝 は にじゅっかち と読まれる
       "300勝も夢ではないと言われた投手でした。"],
      ph(IKENAGA, "gold", focus=(0.5, 0.3)), move="in", els=[
          E(P(L.gold, "新人 20勝", size=150), 960, 380, until=0, anim="slam", sfx="boom"),
          E(P(L.gold, "5年で 99勝", size=150), 960, 560, until=0, delay=1.6, anim="slam", sfx="boom"),
          E(kw("300勝も夢じゃない", 120), 960, 440, at=1, anim="rise"),
      ]),
    S(["舞台は、1969年からのプロ野球。",
       "八百長。", "野球賭博。", "暴力団。", "口止め料。", "国会。", "そして、逮捕。"],
      ph(HEIWADAI, "cold", seed=401), move="in", trans="cut", els=[
          E(kw("1969年〜", 150, GOLD), 960, 440, until=0, anim="slam"),
          W("八百長", 1, RED, 210), W("野球賭博", 2, WHITE, 190), W("暴力団", 3, RED, 210),
          W("口止め料", 4, GOLD, 190), W("国会", 5, WHITE, 230), W("逮捕", 6, RED, 240),
      ]),
    S(["プロ野球の歴史で最大のスキャンダルとも呼ばれる、黒い霧事件です。"],
      P(L.plain), move="in", trans="cut", hold=0.5, els=[
          E(brush("黒い霧事件", 230), 960, 440, anim="zoom", sfx="boom"),
      ]),
    S(["なぜ選手たちは、八百長に手を染めたのか。",
       "なぜ、八百長はしていないと言い続けたエースまで、追放されたのか。",
       "そして球界は、この事件のあと、何を変えたのか。"],
      ph(DOME, "dark"), move="in", els=[
          E(kw("なぜ手を染めたのか", 110), 960, 440, until=0, anim="rise"),
          E(kw("なぜエースまで追放？", 110, RED), 960, 440, at=1, until=1, anim="rise"),
          E(kw("球界は何を変えたのか", 110, GOLD), 960, 440, at=2, anim="rise"),
      ]),
    S(["2025年には、プロ野球選手のオンラインカジノ利用が、次々に明らかになりました。",
       "賭けごとと野球の問題は、決して昔話ではありません。",
       "今だからこそ知っておきたい、球界の黒歴史を、お金と制度の目線で解説します。"],
      ph(FANS, "dark"), move="in", els=[
          E(kw("2025年 オンラインカジノ問題", 96), 960, 420, until=0, anim="slam", sfx="boom"),
          E(kw("昔話ではない", 150, RED), 960, 440, at=1, until=1, anim="slam"),
          E(P(L.gold, "お金と制度の目線で", size=110), 960, 440, at=2, anim="rise"),
      ]),
    # 登場人物紹介 (ナレーションなし)
    cast("永易将之", "消えた投手", P(L.bokeh, 402, (190, 60, 60)), (255, 120, 120)),
    cast("池永正明", "100万円のエース", ph(IKENAGA, "cold", focus=(0.5, 0.3)), (140, 220, 255)),
    cast("田中勉", "100万円を渡した男", P(L.bokeh, 403, (120, 160, 220)), (150, 255, 200)),
    cast("小川健太郎", "現役のまま逮捕", P(L.bokeh, 404, (200, 160, 80)), (255, 220, 110)),
    cast("森安敏明", "受け取った50万円", P(L.bokeh, 405, (160, 90, 200)), (230, 160, 255)),
    cast("西鉄オーナー", "口止め料550万円", ph(HEIWADAI2, "cold", seed=406), (255, 140, 90)),
    S([], P(L.plain), move="in", hold=3.0, trans="fade", els=[
        E(brush("黒い霧事件", 220), 960, 420, anim="zoom", sfx="boom"),
        E(P(L.text, "プロ野球 史上最大のスキャンダル", "NotoSerifJP-Black.ttf", 60, GOLD), 960, 640, delay=0.6,
          anim="rise"),
    ]),
]

# ---- 第0章 野球賭博 ----------------------------------------------------------
CH0 = [
    chap(0, "野球賭博", 410),
    S(["物語に入る前に、まずお金の流れを押さえておきましょう。",
       "野球賭博とは、プロ野球の試合の勝ち負けに、お金を賭けるものです。",
       "もちろん違法です。当時、その裏には暴力団がいたと報じられています。"],
      ph(BALL, "dark"), move="in", tag=T0, els=[
          E(kw("お金の流れ", 140, GOLD), 960, 420, until=0, anim="slam"),
          E(P(N.pict, [("group", "客"), ("money", "胴元"), ("ball", "試合の勝ち負け")], 1), 960, 470, at=1, until=1, anim="rise"),
          E(kw("違法", 220, RED), 960, 420, at=2, anim="slam", sfx="boom"),
      ]),
    S(["賭ける側がいちばん欲しいのは、試合の結果を前もって知ることです。",
       "そのいちばん確実な方法。",
       "それは、選手に、わざと負けてもらうことでした。",
       "これが八百長です。"],
      P(L.bokeh, 411, (170, 60, 50)), move="in", tag=T0, els=[
          E(kw("結果を前もって知りたい", 110), 960, 420, until=0, anim="rise"),
          E(kw("わざと負けてもらう", 130, RED), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(brush("八百長", 240, RED), 960, 420, at=3, anim="zoom", sfx="boom"),
      ]),
    S(["選手に数十万円を渡しても、賭けで勝てば、それ以上のお金が戻ってくる。",
       "実際、この事件で重い処分を受けた選手は、みな投手でした。",
       "試合の勝ち負けを、いちばん左右しやすい立場です。"],
      ph(DOME, "dark"), move="in", tag=T0, els=[
          E(P(N.pict, [("money", "選手に数十万円"), ("person", "わざと負ける"), ("group", "賭けで大もうけ")], 2), 960, 470, until=0, anim="rise"),
          E(kw("狙われたのは投手", 140, RED), 960, 420, at=1, anim="slam", sfx="boom"),
      ]),
    S(["アメリカでも1919年、ワールドシリーズでの八百長で、8人の選手が永久追放されました。",
       "ブラックソックス事件です。",
       "野球と賭けの問題は、それほど古くからあるのです。"],
      ph(BLACKSOX, "cold", seed=412), move="in", tag=T0, els=[
          E(kw("1919年 アメリカ", 120, GOLD), 960, 300, until=0, anim="rise"),
          E(kw("8人が永久追放", 130, RED), 960, 440, until=0, delay=2.0, anim="slam", sfx="boom"),
          E(brush("ブラックソックス事件", 140), 960, 420, at=1, anim="zoom"),
      ]),
    S(["一方の日本のプロ野球にも、八百長を禁じるルールがありました。",
       "野球協約の第355条、敗退行為です。",
       "わざと負ける、負けようとする、勝つための最善の努力を怠る。",
       "こうした選手は、永久にその職務を停止される、とされていました。"],
      P(L.bokeh, 413), move="in", tag=T0, els=[
          E(P(L.scroll, "野球協約 第355条", "敗退行為"), 960, 420, at=1, until=1, anim="zoom", sfx="boom"),
          E(P(C.bullet_list, ["わざと負ける", "負けようとする", "最善の努力を怠る"], 64, 900), 960, 430, at=2, until=2,
            anim="rise"),
          E(kw("永久に職務停止", 150, RED), 960, 420, at=3, anim="slam", sfx="boom"),
      ]),
    S(["そしてこの条文には、もう1つ、怖い一文があります。",
       "八百長に誘われたのに、そのことを報告しなかった者も、同じように罰せられるのです。",
       "つまり、自分はやっていなくても、誘われて黙っていただけで、アウトになりうる。",
       "この一文が、のちに1人のエースの運命を変えることになります。"],
      P(L.bokeh, 414, (150, 40, 40)), move="in", tag=T0, els=[
          E(kw("もう1つの怖い一文", 120), 960, 420, until=0, anim="rise"),
          E(kw("誘われて報告しない＝同罪", 110, RED), 960, 420, at=1, until=1, anim="slam", sfx="boom"),
          E(kw("黙っていただけでアウト", 120, RED), 960, 420, at=2, until=2, anim="slam"),
          E(tsukkomi("え、やってなくても！？"), 1500, 230, at=2, until=2, delay=1.2, anim="slam"),
          E(brush("1人のエースの運命", 150), 960, 420, at=3, anim="zoom", sfx="boom"),
      ]),
]

# ---- 第1章 消えた投手 --------------------------------------------------------
CH1 = [
    chap(1, "消えた投手", 420),
    S(["1969年のシーズン中。",
       "福岡の西鉄ライオンズで、ある疑いが持ち上がります。",
       "うちの選手が、八百長をしているのではないか。"],
      ph(HEIWADAI, "dark", seed=421), move="in", tag=T1, els=[
          E(kw("1969年", 170, GOLD), 960, 420, until=0, anim="slam"),
          E(kw("西鉄ライオンズ", 150), 960, 420, at=1, until=1, anim="rise"),
          E(kw("八百長の疑い", 160, RED), 960, 420, at=2, anim="slam", sfx="boom"),
      ]),
    S(["きっかけの1つは、主砲のカール・ボレス選手が、記者にささやいたひと言でした。",
       "ウチには、わざとエラーする選手がいる。",
       "チームの主砲から、まさかの内部告発です。"],
      P(L.bokeh, 422), move="in", tag=T1, els=[
          E(P(C.name_plate, "カール・ボレス", "西鉄の主砲"), 960, 400, until=0, anim="rise"),
          E(P(C.quote, "ウチには、わざとエラーする選手がいる", 76), 960, 420, at=1, until=1, anim="zoom", sfx="boom"),
          E(kw("まさかの内部告発", 140, RED), 960, 420, at=2, anim="slam"),
      ]),
    S([("球団がひそかに調べた結果、名前が挙がったのが、永易将之投手です。",
        f"球団がひそかに調べた結果、名前が挙がったのが、{NAGAYASU}まさゆき投手です。"),
       ("球団の社長が本人を問いただすと、永易投手は肯定も否定もせず、ただ震えていたといいます。",
        f"球団の社長が本人を問いただすと、{NAGAYASU}投手は肯定も否定もせず、ただ震えていたといいます。")],
      P(L.bokeh, 423, (190, 60, 60)), move="in", tag=T1, els=[
          name_v("永易将之", color=(255, 150, 150)),
          E(P(C.name_plate, "永易将之 投手", "西鉄"), 1000, 400, until=0, delay=1.5, anim="rise"),
          E(kw("肯定も否定もせず", 120), 1000, 360, at=1, anim="rise"),
          E(kw("ただ震えていた", 140, RED), 1000, 540, at=1, delay=2.4, anim="slam", sfx="boom"),
      ]),
    S([("10月8日、読売新聞と報知新聞が、永易投手の八百長を報じます。",
        f"10月8日、読売新聞と報知新聞が、{NAGAYASU}投手の八百長を報じます。"),
       ("ところが、その日から、永易投手は姿を消してしまいます。",
        f"ところが、その日から、{NAGAYASU}投手は姿を消してしまいます。"),
       "球界は、本人に話を聞こうにも、本人がいない、という状態になりました。"],
      P(L.bokeh, 424, (120, 120, 140)), move="in", tag=T1, els=[
          E(P(N.paper, "西鉄・永易投手が八百長", None, "読売新聞 1969年10月8日"), 1380, 470, until=0, anim="zoom", sfx="boom"),
          E(kw("10月8日 報道", 120), 640, 640, until=0, delay=0.6, anim="slam"),
          E(P(C.note, "※見出しは当時の報道より（再現）", 28), 1860, 118, until=0, anchor="tr"),
          E(kw("失踪", 260, RED), 960, 420, at=1, until=1, anim="glitch", sfx="boom"),
          E(tsukkomi("本人、どこ行った！？"), 1480, 230, at=2, anim="slam"),
          E(kw("本人不在", 170), 960, 440, at=2, anim="rise"),
      ]),
    S(["数日後、夕刊フジの記者が、福岡から大阪へ向かう飛行機の中で、偶然本人を見つけます。",
       "神に誓って、やっていない。",
       "そう話した永易投手は、ふたたび行方をくらましました。"],
      P(L.bokeh, 426, (120, 150, 200)), move="in", tag=T1, els=[
          E(kw("機内で発見", 170), 960, 420, until=0, delay=1.5, anim="slam", sfx="boom"),
          E(P(C.quote, "神に誓って、やっていない", 96), 960, 420, at=1, until=1, anim="zoom"),
          E(kw("また消えた", 190, RED), 960, 420, at=2, anim="glitch", sfx="boom"),
          E(tsukkomi("忍者か"), 1520, 230, at=2, delay=1.2, anim="slam"),
      ]),
    S(["騒ぎに火をつけたのが、創刊したばかりの週刊誌でした。",
       "週刊ポストは、ほかにも疑わしい選手が8人いる、として実名を挙げ、八百長を広めたのは中日の田中勉投手だ、と書いたのです。",
       "田中投手は、事実無根だとして、雑誌を名誉毀損で訴えました。",
       "この裁判の行方は、のちに意外な形で決着します。"],
      P(L.bokeh, 427, (200, 160, 80)), move="in", tag=T1, els=[
          E(kw("週刊誌が実名で告発", 130, RED), 960, 420, until=1, anim="slam", sfx="boom"),
          E(kw("田中勉「事実無根」", 140), 960, 420, at=2, until=2, anim="slam"),
          E(kw("名誉毀損で提訴", 150, GOLD), 960, 600, at=2, delay=1.4, until=2, anim="rise"),
          E(brush("この裁判、意外な結末へ", 140), 960, 420, at=3, anim="zoom", sfx="boom"),
      ]),
    S(["本人がいないまま迎えた、11月28日。",
       ("コミッショナー委員会は、永易投手の永久追放を決めました。",
        f"コミッショナー委員会は、{NAGAYASU}投手の永久追放を決めました。"),
       "わざと負けたことを理由にした永久追放は、プロ野球で初めてのことでした。"],
      P(L.plain), move="in", tag=T1, els=[
          E(kw("11月28日", 150, GOLD), 960, 420, until=0, anim="slam"),
          E(brush("永久追放", 240, RED), 960, 420, at=1, until=1, anim="zoom", sfx="boom"),
          E(kw("史上初", 220, GOLD), 960, 420, at=2, anim="slam", sfx="boom"),
      ]),
    S(["チームの成績も落ち込み、監督の中西太さんはこのシーズン限りで退任。",
       "あとを託されたのは、西鉄の大エースだった稲尾和久さんでした。",
       "1人を追放したことで、問題は片づいた。",
       "誰もがそう思っていました。",
       "しかし、本当の嵐はここからでした。"],
      ph(NAKANISHI, "dark", focus=(0.5, 0.3), seed=425), move="in", tag=T1, els=[
          E(P(C.name_plate, "中西太 監督", "このシーズン限りで退任"), 960, 400, until=0, anim="rise"),
          E(P(C.name_plate, "稲尾和久 新監督", "西鉄の大エース"), 960, 400, at=1, until=1, anim="rise"),
          E(kw("これで片づいた…？", 140), 960, 420, at=2, until=3, anim="rise"),
          E(brush("本当の嵐は、ここから", 150, RED), 960, 420, at=4, anim="zoom", sfx="boom"),
      ]),
]

# ---- 第2章 告白 --------------------------------------------------------------
CH2 = [
    chap(2, "告白", 430),
    S(["1970年2月には、巨人の投手コーチ、藤田元司さんが、知らずに暴力団員に仕事を頼んでいたことが報じられます。",
       "新聞の見出しは、ジャイアンツよ、お前もか。",
       "球界と暴力団の近さが、いよいよ社会問題になっていきます。"],
      ph(DOME, "cold", seed=438), move="in", tag=T2, els=[
          E(P(C.name_plate, "藤田元司", "巨人の投手コーチ（当時）"), 960, 400, until=0, delay=1.5, anim="rise"),
          E(P(C.quote, "ジャイアンツよ、お前もか", 100), 960, 420, at=1, until=1, anim="zoom", sfx="boom"),
          E(kw("社会問題へ", 180, RED), 960, 420, at=2, anim="slam"),
      ]),
    S(["そして3月。",
       "事件は、国会にまで持ち込まれます。",
       "暴力団とプロ野球の関係を問題にした議員たちが、国会で黒い霧を追及し始めたのです。",
       ("行方不明の永易投手は、暴力団に監禁されているのではないか、とまで言われました。",
        f"行方不明の{NAGAYASU}投手は、暴力団に監禁されているのではないか、とまで言われました。")],
      ph(DIET, "cold", seed=431), move="in", tag=T2, els=[
          E(kw("1970年3月", 170, GOLD), 960, 420, until=0, anim="slam"),
          E(brush("国会", 260), 960, 420, at=1, until=2, anim="zoom", sfx="boom"),
          E(kw("監禁説", 200, RED), 960, 420, at=3, anim="glitch", sfx="boom"),
      ]),
    S(["ところが本人は、恋人と札幌で、ひっそりと暮らしていました。",
       "監禁どころか、北海道で静かに暮らしていたわけです。"],
      P(L.bokeh, 432, (120, 150, 200)), move="in", tag=T2, els=[
          E(kw("札幌", 230), 960, 420, until=0, anim="slam", sfx="boom"),
          E(tsukkomi("監禁されてなかった"), 1480, 230, at=1, anim="slam"),
      ]),
    S([("そして春。永易投手は、ついに口を開きます。",
        f"そして春。{NAGAYASU}投手は、ついに口を開きます。"),
       "八百長は、やった。",
       "そして、八百長をしたのは、自分1人ではない。",
       "さらに、西鉄の球団から、合わせて550万円を受け取っていた。"],
      P(L.bokeh, 433, (190, 60, 60)), move="in", tag=T2, els=[
          E(brush("告白", 260), 960, 420, until=0, anim="zoom", sfx="boom"),
          E(P(C.quote, "八百長は、やった", 96), 960, 420, at=1, until=1, anim="zoom", sfx="boom"),
          E(P(C.quote, "自分1人ではない", 96), 960, 420, at=2, until=2, anim="zoom"),
          E(P(L.gold, "550万円", size=230), 960, 420, at=3, anim="slam", sfx="boom"),
          E(tsukkomi("口止め料！？"), 1500, 230, at=3, delay=1.8, anim="slam"),
          note("※永易の主張"),
      ]),
    S([("永易投手によれば、オーナーからは、何も言うな、一生面倒を見る、と言われていたといいます。",
        f"{NAGAYASU}投手によれば、オーナーからは、何も言うな、一生面倒を見る、と言われていたといいます。"),
       "その一生の保証が、550万円だった、というわけです。"],
      ph(HEIWADAI2, "dark", seed=434), move="in", tag=T2, els=[
          E(P(C.quote, "何も言うな。一生面倒を見る", 80), 960, 420, until=0, delay=1.5, anim="zoom"),
          E(kw("一生＝550万円", 160, GOLD), 960, 420, at=1, anim="slam", sfx="boom"),
          note("※永易の主張"),
      ]),
    S(["4月10日。開幕の前日です。",
       ("永易投手は、衆議院の議員会館で、半年ぶりに人前に姿を現します。",
        f"{NAGAYASU}投手は、衆議院の議員会館で、半年ぶりに人前に姿を現します。"),
       ("記者たちに迫られた永易投手は、八百長に関わったとする仲間の名前を、次々に挙げていきました。",
        f"記者たちに迫られた{NAGAYASU}投手は、八百長に関わったとする仲間の名前を、次々に挙げていきました。"),
       "その中には、西鉄のエース、池永正明投手の名前もありました。"],
      ph(DIET, "dark", seed=435), move="in", tag=T2, els=[
          E(kw("4月10日 開幕前日", 130, GOLD), 960, 420, until=0, anim="slam"),
          E(kw("議員会館で会見", 140), 960, 420, at=1, until=1, anim="rise"),
          E(kw("仲間の実名を挙げる", 130, RED), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(pic(IKENAGA, "池永正明", "西鉄のエース", (0.5, 0.3), 380, 470), 960, 400, at=3, anim="rise", sfx="whoosh"),
          E(kw("池永正明", 90, (140, 220, 255)), 960, 720, at=3, delay=0.6, anim="slam"),
      ]),
    S(["名前を言うのをためらう永易投手に、記者たちは厳しく迫りました。",
       "ここは国会の中だ。特定の記者に話したことを、ここで言えないのは失礼だと思わないか。",
       "うつむき、額に汗をにじませた永易投手は、やがて顔を上げ、一気に名前を口にします。",
       "その様子を見たベテラン記者は、殺人犯が自供するときのようだ、とつぶやいたといいます。"],
      P(L.bokeh, 439, (150, 40, 40)), move="in", tag=T2, els=[
          E(kw("詰め寄る記者たち", 150), 960, 420, until=0, anim="rise"),
          E(P(C.quote, "ここは国会の中だ", 110), 960, 420, at=1, until=1, anim="zoom", sfx="boom"),
          E(kw("一気に名前を口にする", 130, RED), 960, 420, at=2, until=2, delay=2.0, anim="slam", sfx="boom"),
          E(P(C.quote, "殺人犯が自供するときのようだ", 86), 960, 420, at=3, anim="zoom"),
          note("※週刊読売 1970年4月24日号より"),
      ]),
    S(["西鉄の球団は、名前の挙がった選手は全員シロ、つまり八百長はしていないと発表します。",
       "オーナーも、アホらしくて相手にできない、と全面否定でした。"],
      P(L.bokeh, 436), move="in", tag=T2, els=[
          E(kw("全員シロ", 200), 960, 420, until=0, anim="slam", sfx="boom"),
          E(P(C.quote, "アホらしくて相手にできない", 90), 960, 420, at=1, anim="zoom"),
      ]),
    S(["ところが新聞の取材で、永易投手の家族が、西鉄から受け取ったお金の残りを見せます。",
       "残っていたのは、37万円。",
       "母親は、あの子の言っていることは本当です、と涙ながらに訴えました。",
       "一方のオーナーは、会社の決算発表の場から途中で退席し、追いかける記者を振り切って姿を消します。"],
      P(L.bokeh, 440, (200, 140, 80)), move="in", tag=T2, els=[
          E(P(L.gold, "残金 37万円", size=170), 960, 420, at=1, until=1, anim="slam", sfx="boom"),
          E(P(C.quote, "あの子の言っていることは本当です", 82), 960, 420, at=2, until=2, anim="zoom"),
          E(kw("オーナー、逃げる", 160, RED), 960, 420, at=3, anim="slam", sfx="boom"),
          E(tsukkomi("こっちも消えた"), 1500, 230, at=3, delay=2.5, anim="slam"),
      ]),
    S(["ところが4月末。そのオーナーが、永易投手にお金を渡していたことを認めます。",
       "その額は、550万円。",
       ("永易投手の言った金額と、ぴたりと一致していました。",
        f"{NAGAYASU}投手の言った金額と、ぴたりと一致していました。"),
       "オーナーは、泣きつかれたので、立ち直るための資金として渡した、と説明しました。",
       "しかし5月、西鉄の社長とオーナーを辞任します。"],
      P(L.bokeh, 437, (200, 160, 80)), move="in", tag=T2, els=[
          E(kw("オーナーが認めた", 150, RED), 960, 420, until=0, anim="glitch", sfx="boom"),
          E(P(N.paper, "五百五十万円を渡す", "永易発言とぴたり一致", "朝日新聞 1970年4月30日"), 1380, 470, at=1, until=2, anim="zoom", sfx="boom"),
          E(P(L.gold, "550万円", size=190), 640, 460, at=1, until=1, anim="slam", sfx="boom"),
          E(kw("ぴたり一致", 170, RED), 640, 460, at=2, until=2, anim="slam", sfx="boom"),
          E(P(C.note, "※見出しは当時の報道より（再現）", 28), 1860, 118, at=1, until=2, anchor="tr"),
          E(P(C.quote, "泣きつかれたので渡した", 86), 960, 420, at=3, until=3, anim="zoom"),
          E(kw("オーナー辞任", 170), 960, 420, at=4, anim="slam", sfx="boom"),
      ]),
    S(["否定していた側が、認めた。",
       ("こうなると、永易投手の告白は、一気に重みを増します。",
        f"こうなると、{NAGAYASU}投手の告白は、一気に重みを増します。"),
       "そして霧は、西鉄の外へも広がっていきます。"],
      P(L.plain), move="in", tag=T2, els=[
          E(kw("否定 → 一転、認める", 130), 960, 420, until=1, anim="rise"),
          E(brush("霧は、外へ", 170, RED), 960, 420, at=2, anim="zoom", sfx="boom"),
      ]),
]

# ---- 第3章 広がる霧 ----------------------------------------------------------
CH3 = [
    chap(3, "広がる霧", 440),
    S(["次の舞台は、オートレースでした。",
       "オートレースでも、選手を買収して順位を操る八百長が、警察に次々と摘発されていたのです。",
       "4月23日、この事件で、元中日の田中勉投手が逮捕されます。"],
      ph(AUTORACE, "dark", seed=441), move="in", tag=T3, els=[
          E(brush("オートレース", 200), 960, 420, until=0, anim="zoom", sfx="boom"),
          E(kw("買収して順位を操る", 130, RED), 960, 420, at=1, until=1, anim="slam"),
          E(P(C.name_plate, "田中勉", "元中日の投手"), 960, 380, at=2, anim="rise"),
          E(kw("逮捕", 200, RED), 960, 600, at=2, delay=1.6, anim="glitch", sfx="boom"),
      ]),
    S(["5月6日には、中日のエース、小川健太郎投手が、現役のまま逮捕されました。",
       "現役のプロ野球選手の逮捕に、ファンは大きな衝撃を受けます。"],
      ph(NAGOYA, "cold", seed=442), move="in", tag=T3, els=[
          E(P(C.name_plate, "小川健太郎", "中日のエース"), 960, 380, until=0, anim="rise"),
          E(kw("現役のまま逮捕", 150, RED), 960, 600, until=0, delay=2.4, anim="glitch", sfx="boom"),
          E(kw("前代未聞の衝撃", 150), 960, 420, at=1, anim="slam"),
      ]),
    S(["さらに田中投手は、取り調べで、プロ野球の試合でも八百長をしたと認めます。",
       "そして、池永投手に、八百長を頼むお金として100万円を渡した、と話したのです。"],
      P(L.bokeh, 443, (190, 60, 60)), move="in", tag=T3, els=[
          E(kw("プロ野球でも八百長", 140, RED), 960, 420, until=0, anim="slam", sfx="boom"),
          E(P(N.pict, [("person", "田中勉"), ("money", "100万円"), ("person", "池永正明")], 1), 960, 470, at=1, anim="rise", sfx="whoosh"),
      ]),
    S(["ここで、第1章の裁判を思い出してください。",
       "週刊誌を名誉毀損で訴えていた、あの田中投手です。",
       "八百長を認めた以上、記事は事実だったことになります。",
       "田中投手は、世間を騒がせて申し訳ない、と訴えを取り下げました。"],
      P(L.bokeh, 447, (200, 160, 80)), move="in", tag=T3, els=[
          E(kw("第1章の裁判", 150, GOLD), 960, 420, until=1, anim="rise"),
          E(kw("記事は事実だった", 150, RED), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(kw("訴え、取り下げ", 160), 960, 420, at=3, anim="slam"),
          E(tsukkomi("訴えた側が…"), 1500, 230, at=3, delay=1.5, anim="slam"),
      ]),
    S(["では、八百長を仕組んだ側は、もうかったのでしょうか。",
       "選手との仲介役だった男は、逮捕の直前、新聞の取材にこう話しています。",
       "西鉄の選手を買収しようとしたのは10回。うまくいったのは、わずか2回。",
       "残ったのは、4500万円近い借金だけだった。",
       "八百長は、仕組んだ側にとっても、割に合わない商売だったのです。"],
      P(L.bokeh, 448, (120, 120, 140)), move="in", tag=T3, els=[
          E(kw("仕組んだ側はもうかった？", 120), 960, 420, until=1, anim="rise"),
          E(kw("10回挑んで 成功2回", 140, GOLD), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(P(L.gold, "借金 4500万円", size=170), 960, 420, at=3, until=3, anim="slam", sfx="boom"),
          E(tsukkomi("大赤字"), 1520, 230, at=3, delay=1.5, anim="slam"),
          E(kw("割に合わない", 180, RED), 960, 420, at=4, anim="slam"),
          note("※朝日新聞 1970年4月24日の本人談"),
      ]),
    S(["東映フライヤーズでも、森安敏明投手が、永易投手から50万円を受け取っていたことを認めます。",
       "記者から、たかが50万円でバカなことをしたと思うか、と聞かれた森安投手は、",
       "そりゃあそうでしょうね、と答えました。",
       "そして、やがて目に涙を浮かべ、ファンの一人ひとりに土下座したい、と語りました。"],
      P(L.bokeh, 444, (160, 90, 200)), move="in", tag=T3, els=[
          E(P(C.name_plate, "森安敏明", "東映フライヤーズ"), 960, 380, until=0, anim="rise"),
          E(P(L.gold, "50万円", size=200), 960, 620, until=0, delay=2.6, anim="slam", sfx="boom"),
          E(P(C.quote, "たかが50万円で、バカなことを？", 80), 960, 420, at=1, until=1, anim="zoom"),
          E(P(C.quote, "そりゃあそうでしょうね", 90), 960, 420, at=2, until=2, anim="zoom"),
          E(P(C.quote, "ファンの一人ひとりに土下座したい", 82), 960, 420, at=3, anim="zoom", sfx="boom"),
      ]),
    S(["こうして、最も重い永久追放を受けたのは6人。",
       "全員が投手でした。",
       "ほかにも、活動停止や戒告など、処分を受けた選手は15人を超えました。"],
      P(L.bokeh, 445), move="in", tag=T3, els=[
          E(P(C.table, ["選手", "球団", "処分"],
              [["永易将之", "西鉄", "永久追放"], ["池永正明", "西鉄", "永久追放"], ["ほか西鉄の投手2人", "西鉄", "永久追放"],
               ["小川健太郎", "中日", "永久追放"], ["森安敏明", "東映", "永久追放"]],
              [420, 220, 260], 78, None, 44), 960, 440, until=1, anim="rise"),
          E(kw("処分者 15人超", 170, RED), 960, 420, at=2, anim="slam", sfx="boom"),
          note("※黒い霧事件の処分一覧（1969〜71年）"),
      ]),
    S(["一方で、誘いをきっぱり断った選手もいました。",
       "近鉄のエースだった鈴木啓示さんは、のちに、暴力団関係者からの八百長の誘いを断っていたと明かしています。",
       "同じように誘われても、断れば、それで終わる。",
       "しかし、断りきれなかった、あるいは、お金を返しそびれた選手を待っていたのは、厳しい処分でした。"],
      ph(DOME, "dark", seed=446), move="in", tag=T3, els=[
          E(kw("断った選手もいた", 140, GOLD), 960, 420, until=0, anim="rise"),
          E(P(C.name_plate, "鈴木啓示", "近鉄のエース"), 960, 400, at=1, until=1, anim="rise"),
          E(kw("断れば、終わる", 150), 960, 420, at=2, until=2, anim="slam"),
          E(kw("返しそびれた選手は…", 140, RED), 960, 420, at=3, anim="slam", sfx="boom"),
      ]),
    S(["処分を発表したコミッショナー委員会の委員長は、こう語ったとされます。",
       "これで終わりかと言われたら、そう言い切る自信はない。",
       "その言葉どおり、その後も賭博がらみの処分は続きました。",
       "当時、阪神のエースだった江夏豊投手も、賭博に関わる人物と付き合っていたとして、戒告を受けています。"],
      P(L.bokeh, 449), move="in", tag=T3, els=[
          E(P(C.quote, "これで終わりと言い切る自信はない", 80), 960, 420, until=1, delay=2.0, anim="zoom"),
          E(kw("処分は続いた", 170, RED), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(P(C.name_plate, "江夏豊", "阪神・戒告処分（1970年）"), 960, 420, at=3, anim="rise"),
      ]),
]

# ---- 第4章 100万円 -----------------------------------------------------------
CH4 = [
    chap(4, "100万円", 450),
    S(["ここで、冒頭のエースの話に戻りましょう。",
       "池永正明。山口県の下関商業から、1965年に西鉄に入った投手です。",
       ("1年目から20勝を挙げて新人王。3年目には最多勝。", "1年目から20しょうを挙げて新人王。3年目には最多勝。"),
       "入団から5年で99勝。打っても、通算で13本のホームランを打っています。",
       "西鉄の大エース、稲尾和久さんの後継者と言われた投手でした。"],
      ph(IKENAGA, "gold", layout="right", focus=(0.5, 0.3), seed=451), move="in", tag=T4, els=[
          name_v("池永正明", at=1, color=(170, 230, 255)),
          E(kw("1965年 西鉄入団", 110), 700, 420, at=1, until=1, anim="rise"),
          E(P(L.gold, "新人 20勝", size=130), 700, 360, at=2, until=2, anim="slam", sfx="boom"),
          E(kw("新人王・最多勝", 100, GOLD), 700, 560, at=2, until=2, delay=1.5, anim="rise"),
          E(P(L.gold, "5年で99勝", size=140), 700, 420, at=3, until=3, anim="slam", sfx="boom"),
          E(kw("稲尾の後継者", 130), 700, 420, at=4, anim="rise"),
          E(P(C.note, "※写真は1965年、20勝を挙げた日", 28), 1860, 860, anchor="br"),
      ]),
    S(["ちなみに、池永投手と同じ年に西鉄に入った選手に、尾崎将司さんがいます。",
       "そう、のちのプロゴルファー、ジャンボ尾崎さんです。",
       "尾崎さんは、池永投手を見て、あんなすごいやつがいたら、自分が野球で成功するのは無理だと思った、と語っています。",
       "ゴルフ界のスターに、野球をあきらめさせた投手。それが池永正明でした。"],
      P(L.bokeh, 456, (120, 180, 120)), move="in", tag=T4, els=[
          E(P(C.name_plate, "尾崎将司", "1965年 西鉄に投手で入団"), 960, 400, until=0, delay=1.5, anim="rise"),
          E(kw("のちのジャンボ尾崎", 140, GOLD), 960, 420, at=1, until=1, anim="slam", sfx="boom"),
          E(P(C.quote, "あんなすごいやつがいたら、無理だと思った", 70), 960, 420, at=2, until=2, anim="zoom"),
          E(kw("野球をあきらめさせた男", 130), 960, 420, at=3, anim="rise"),
      ]),
    S(["そんな池永投手に、中日の田中勉投手から、100万円が渡されます。",
       "八百長を頼む、という意味のお金でした。",
       "池永投手は、お金を受け取ったことは認めました。",
       "しかし、八百長はしていない、と言い続けました。"],
      P(L.bokeh, 452, (190, 60, 60)), move="in", tag=T4, els=[
          E(P(L.gold, "100万円", size=240), 960, 420, until=1, anim="slam", sfx="boom"),
          E(kw("受け取った", 170), 960, 420, at=2, until=2, anim="slam"),
          E(kw("八百長は、していない", 140, (140, 220, 255)), 960, 420, at=3, anim="rise"),
      ]),
    S(["1970年5月25日。コミッショナー委員会は、池永投手を永久追放にします。",
       "理由は、受け取った100万円を返さなかったこと。",
       "返さなかったのは、八百長を引き受けたのと同じだ、と見なされたのです。",
       "さらに、誘われたことを報告しなかったことも、理由に挙げられました。",
       ("第0章で見た、あの一文です。", "第ゼロ章で見た、あの一文です。")],
      P(L.plain), move="in", tag=T4, els=[
          E(P(N.paper, "永久追放与田・益田・池永", "西鉄六選手に裁決", "朝日新聞 1970年5月26日"), 1400, 470, until=0, delay=1.2, anim="zoom", sfx="boom"),
          E(brush("永久追放", 220, RED), 620, 460, until=0, delay=1.8, anim="zoom"),
          E(P(C.note, "※見出しは当時の報道より（再現）", 28), 1860, 118, until=0, anchor="tr"),
          E(kw("100万円を返さなかった", 130), 960, 420, at=1, until=1, anim="slam"),
          E(kw("返さない＝引き受けた", 140, RED), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(kw("報告しなかった", 150), 960, 420, at=3, until=3, anim="slam"),
          E(P(L.scroll, "野球協約 第355条", "誘われて報告しない者も同罪"), 960, 420, at=4, anim="zoom", sfx="boom"),
      ]),
    S(["同じく永久追放となった西鉄の2人の投手は、",
       "池永が自分たちと同じ処分なんて球界の損失だ、と涙ながらに訴えたと伝えられています。",
       "しかし、処分は変わりませんでした。",
       "このとき池永投手は、まだ23歳。",
       "通算103勝で、プロ野球の記録は止まりました。"],
      ph(IKENAGA, "cold", focus=(0.5, 0.3), seed=453), move="in", tag=T4, els=[
          E(P(C.quote, "球界の損失だ", 110), 960, 420, until=1, delay=0.5, anim="zoom"),
          E(kw("処分は変わらず", 150, RED), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(P(L.gold, "23歳", size=230), 960, 420, at=3, until=3, anim="slam", sfx="boom"),
          E(P(L.gold, "通算103勝", size=170), 960, 420, at=4, anim="rise"),
      ]),
    S(["球界を去った池永さんは、福岡の繁華街、中洲で、バーを開きます。",
       "店のトイレの壁は、訪れたファンの励ましの言葉で、びっしりと埋まったといいます。",
       "かつての仲間やファンは、処分の取り消しを求める署名を集め続けました。"],
      P(L.bokeh, 454, (200, 140, 80)), move="in", tag=T4, els=[
          E(kw("中洲のバー", 170), 960, 420, until=0, anim="rise"),
          E(kw("壁を埋めた励まし", 140, GOLD), 960, 420, at=1, until=1, anim="slam"),
          E(kw("処分取り消しの署名", 130), 960, 420, at=2, anim="rise"),
      ]),
    S(["1997年には、およそ18万8000人分の署名が、コミッショナーのもとに届けられます。",
       "しかし翌1998年、この願いは退けられました。",
       "一度出た処分を、あらためて審理することはできない、という理由でした。",
       "永久追放には、出口がなかったのです。"],
      P(L.bokeh, 455, (120, 120, 140)), move="in", tag=T4, els=[
          E(P(L.gold, "18万7787人", size=170), 960, 400, until=0, anim="slam", sfx="boom"),
          E(kw("1998年 却下", 170, RED), 960, 420, at=1, until=2, anim="slam", sfx="boom"),
          E(brush("出口のない「永久」", 160), 960, 420, at=3, anim="zoom", sfx="boom"),
      ]),
]

# ---- 第5章 ライオンズ消滅の危機 -----------------------------------------------
CH5 = [
    chap(5, "ライオンズ消滅の危機", 460),
    S(["事件の傷は、球団そのものにも深く残りました。",
       "主力の投手を一度に失った西鉄は、1970年、球団で初めての最下位に沈みます。",
       "そこから3年連続の最下位。地元福岡での人気も、急落しました。",
       "そして1972年のオフ、西鉄は球団を手放します。"],
      ph(HEIWADAI, "cold", seed=461), move="in", tag=T5, els=[
          E(kw("球団初の最下位", 150, RED), 960, 420, at=1, until=1, anim="slam", sfx="boom"),
          E(kw("3年連続 最下位", 150, RED), 960, 420, at=2, until=2, anim="slam", sfx="boom"),
          E(brush("球団、身売り", 190), 960, 420, at=3, anim="zoom", sfx="boom"),
      ]),
    S(["ライオンズはその後、持ち主が何度も変わり、",
       "1979年、埼玉の所沢へと移っていきます。",
       "これが今の、埼玉西武ライオンズです。"],
      P(L.bokeh, 462), move="in", tag=T5, els=[
          E(P(C.flow, ["西鉄", "持ち主が\n何度も交代", "西武\n（所沢へ）"], 2), 960, 420, anim="rise"),
          E(kw("今の埼玉西武ライオンズ", 120, GOLD), 960, 640, at=2, anim="rise"),
      ]),
    S(["ところが、この大ピンチで、人生が変わった選手もいます。",
       "1年目に二軍で打ち込まれ、野手への転向まで考えていた、若い投手。",
       "投手が足りなくなったチームで、彼は一軍で投げ続けることになります。",
       "のちに251勝を挙げる、東尾修さんです。",
       "東尾さんは、あの事件は自分の野球人生にとって最大のチャンスだった、と振り返っています。"],
      ph(DOME, "gold", seed=463), move="in", tag=T5, els=[
          E(kw("人生が変わった選手", 140, GOLD), 960, 420, until=0, anim="rise"),
          E(kw("野手転向も考えた", 140), 960, 420, at=1, until=1, anim="rise"),
          E(kw("一軍で投げ続ける", 140), 960, 420, at=2, until=2, anim="slam"),
          E(P(C.name_plate, "東尾修", "通算251勝"), 960, 420, at=3, until=3, anim="rise", sfx="whoosh"),
          E(P(C.quote, "最大のチャンスだった", 100), 960, 420, at=4, anim="zoom"),
      ]),
]

# ---- 第6章 35年後 ------------------------------------------------------------
CH6 = [
    chap(6, "35年後", 470),
    S(["時は流れ、2001年。",
       "プロ野球のOBが集まる新しいリーグで、池永さんは、再びマウンドに上がります。",
       "監督は、かつての大エース、稲尾和久さんでした。",
       "3回を投げて、ヒットを1本も許しませんでした。",
       "このころ池永さんは、もういい加減、許していただけないだろうか、と語っています。"],
      P(L.bokeh, 471, (200, 160, 80)), move="in", tag=T6, els=[
          E(kw("2001年", 170, GOLD), 960, 420, until=0, anim="slam"),
          E(kw("再びマウンドへ", 160), 960, 420, at=1, until=1, anim="rise"),
          E(P(C.name_plate, "稲尾和久 監督", "福岡ドンタクズ"), 960, 420, at=2, until=2, anim="rise"),
          E(kw("3回 ノーヒット", 160, GOLD), 960, 420, at=3, until=3, anim="slam", sfx="boom"),
          E(P(C.quote, "もういい加減、許していただけないだろうか", 70), 960, 420, at=4, anim="zoom"),
      ]),
    S(["同じころ、巨人の渡邉恒雄オーナーまでが、いつまで永久追放にしているんだ、と声を上げます。",
       "球界の大物の言葉で、空気が少しずつ変わり始めました。"],
      P(L.bokeh, 474), move="in", tag=T6, els=[
          E(P(C.quote, "いつまで永久追放にしているんだ", 86), 960, 420, until=0, delay=2.0, anim="zoom", sfx="boom"),
          E(kw("空気が変わり始める", 150, GOLD), 960, 420, at=1, anim="rise"),
      ]),
    S(["2004年、新しいコミッショナーの言葉が、流れを変えます。",
       "無期懲役の服役囚でも、15年から20年で仮釈放されるのが普通。",
       "永久追放というのは、ちょっと。"],
      P(L.bokeh, 472), move="in", tag=T6, els=[
          E(kw("2004年 新コミッショナー", 120, GOLD), 960, 420, until=0, anim="rise"),
          E(P(C.quote, "無期懲役でも、15〜20年で仮釈放", 76), 960, 420, at=1, until=1, anim="zoom"),
          E(P(C.quote, "永久追放というのは、ちょっと", 90), 960, 420, at=2, anim="zoom", sfx="boom"),
      ]),
    S(["そして2005年、プロ野球はルールそのものを変えます。",
       "永久追放でも、処分から15年がたち、本人が申請し、深く反省していると認められれば、復帰できる。",
       "永久という言葉に、初めて出口が作られたのです。"],
      P(L.plain), move="in", tag=T6, els=[
          E(kw("2005年 協約改正", 150, GOLD), 960, 420, until=0, anim="slam", sfx="boom"),
          E(P(N.pict, [("paper", "処分から15年"), ("person", "本人が申請"), ("paper", "反省が認められる")], 2), 960, 470, at=1, until=1, anim="rise"),
          E(brush("「永久」に出口", 190, GOLD), 960, 420, at=2, anim="zoom", sfx="boom"),
      ]),
    S(["2005年4月25日。池永さんの処分は解かれました。",
       "追放から、35年がたっていました。",
       "池永さんは、2022年に76歳で亡くなっています。"],
      ph(IKENAGA, "gold", focus=(0.5, 0.3), seed=473), move="in", tag=T6, els=[
          E(kw("2005年4月25日 復権", 130, GOLD), 960, 420, until=0, anim="slam", sfx="boom"),
          E(P(L.gold, "35年", size=260), 960, 420, at=1, until=1, anim="slam", sfx="boom"),
      ]),
]

# ---- まとめ ------------------------------------------------------------------
def _cta(t):
    import ui
    return ui.cta_frame(t)


ENDING = [
    S(["黒い霧事件を、お金と制度の目線で振り返ると、3つのことが見えてきます。",
       "1つ目。数十万円から100万円というお金で、選手の人生が大きく変わったこと。",
       "2つ目。誘われて黙っていただけでも、罰せられるルールがあったこと。",
       "3つ目。永久追放に出口ができるまで、35年かかったこと。"],
      P(L.bokeh, 481), move="in", els=[
          E(P(L.gold, "まとめ", size=110), 960, 200, anim="rise"),
          E(P(C.bullet_list, ["数十万〜100万円で人生が変わった", "黙っていただけでも処分", "「永久」に出口ができるまで35年"],
              58, 1500), 960, 470, at=1, anim="rise"),
      ]),
    S(["2025年のオンラインカジノ問題を見ても、賭けごとと選手の距離は、今も球界の課題です。",
       "ルールは、事件が起きるたびに書き換えられてきました。",
       "その出発点にあるのが、黒い霧事件なのです。"],
      ph(FANS, "dark", seed=482), move="in", els=[
          E(kw("今も続く課題", 160), 960, 420, until=0, anim="rise"),
          E(kw("事件のたびに書き換わるルール", 110, GOLD), 960, 420, at=1, until=1, anim="rise"),
          E(brush("出発点は、黒い霧", 180, RED), 960, 420, at=2, anim="zoom", sfx="boom"),
      ]),
    S(["最後まで見ていただき、ありがとうございました。",
       "このチャンネルでは、FAや年俸、契約更改など、プロ野球のお金と制度のしくみをわかりやすく解説しています。",
       "動画が役に立ったと思ったら、高評価とチャンネル登録、そして通知のオンをお願いします。"],
      P(L.bokeh, 483), move="in", hold=1.0, els=[
          E(P(L.gold, "ご視聴ありがとうございました", size=90), 960, 420, until=0, anim="zoom"),
          E(P(L.gold, "プロ野球 お金と制度のしくみ", size=84), 960, 220, at=1, anim="rise"),
          E(P(C.bullet_list, ["FA", "年俸", "契約更改"], 56, 520), 960, 520, at=1, until=1, anim="rise"),
          E(_cta, 960, 560, at=2, delay=0.3, anim="none", dyn=True),
      ]),
]

# ---- 報道ドキュメンタリー風への置き換え ----------------------------------------
# 光の粒の背景は、章ごとの写真を資料映像風にしたものに替える
POOLS = {
    None: ["Kawasaki_1989_02.jpg", "Hanshin_Koshien_Stadium_2009.jpg", "Baseball-2.jpg"],
    T0: ["Baseball-2.jpg", "fourbats.jpg", "Kawasaki_1989_02.jpg"],
    T1: [NAKANISHI, "Kawasaki_1989_02.jpg", IKENAGA],
    T2: [DIET, NAKANISHI, "Kawasaki_1989_02.jpg"],
    T3: [AUTORACE, "Kawasaki_1989_02.jpg", "Hanshin_Koshien_Stadium_2009.jpg"],
    T4: [IKENAGA, "Kawasaki_1989_02.jpg", NAKANISHI],
    T5: ["Kawasaki_1989_02.jpg", NAKANISHI, "Meiji_Jingu_Stadium_2019c.jpg"],
    T6: ["Meiji_Jingu_Stadium_2019c.jpg", "Kawasaki_1989_02.jpg", "Baseball-2.jpg"],
}


def _outlined(fn, px=8):
    return N._outline(fn(), px)


def _restyle(scenes):
    for i, sc in enumerate(scenes):
        bg = sc["bg"]
        f = getattr(bg, "func", None)
        photo = True
        if f is L.bokeh:
            pool = POOLS.get(sc["tag"], POOLS[None])
            seed = bg.args[0] if bg.args else i
            sc["bg"] = P(N.archive, pool[seed % len(pool)], seed=seed, bright=0.5)
        elif f is L.plate:
            if bg.args[0] == DOME:  # 東京ドームは1970年の話に合わないので、古い球場の写真に替える
                bg = P(L.plate, ["Meiji_Jingu_Stadium_2019c.jpg", "Hanshin_Koshien_Stadium_2009.jpg"][i % 2], *bg.args[1:],
                       **bg.keywords)
            sc["bg"] = P(N.archive, bg.args[0], bg.keywords.get("focus", (0.5, 0.4)), seed=i,
                         bright=0.58 if bg.args[1:2] != ("gold",) else 0.66,
                         tint=(1.08, 1.0, 0.86) if bg.args[1:2] == ("gold",) else (1.0, 0.97, 0.92))
        elif f is L.plain:
            sc["bg"] = P(N.dark, i)
            photo = False
        else:
            photo = f is N.archive
        for e in sc["els"]:
            fn = e["fn"]
            ff = getattr(fn, "func", None)
            a = fn.args if ff else ()
            if ff is L.text and a[1:2] == ("DelaGothicOne-Regular.ttf",):
                text, size, color = a[0], a[2], a[3]
                if color == RED:
                    e["fn"] = P(N.tel_red, text, round(size * 0.92))
                elif color == GOLD:
                    e["fn"] = P(N.tel_gold, text, round(size * 0.92))
                else:
                    e["fn"] = P(N.tel, text, round(size * 0.92), color)
            elif ff is L.text and a[1:2] == ("YujiBoku-Regular.ttf",):
                e["fn"] = P(_outlined, fn)
            elif ff is L.text and a[1:2] == ("NotoSerifJP-Black.ttf",) and len(a) > 3 and a[2] >= 100:
                e["fn"] = P(_outlined, fn)
            elif ff is L.gold:
                e["fn"] = P(N.tel_gold, a[0], round(fn.keywords.get("size", 160) * 0.9))
            elif ff is C.quote:
                e["fn"] = P(N.tel, f"「{a[0]}」", a[1] if len(a) > 1 else 58)
            elif ff is C.name_plate:
                e["fn"] = P(N.card, a[0], [a[1]] if len(a) > 1 and a[1] else [])
            # 写真の上では、真ん中の文字を少し下 (下3分の1) に寄せる
            if photo and e["anchor"] == "c" and 360 <= e["y"] <= 480 and e["x"] in (960, 1000) and ff is not C.flow:
                e["y"] += 190
    return scenes


def _shrink(fn, maxw):
    """画像が maxw より広ければ縮める"""
    from PIL import Image
    im = fn()
    if im.width <= maxw:
        return im
    return im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)


def _arrange(scenes):
    """縦書きの名前は左端の列 (x=150) に置き、紹介する文の間だけ出す。
    人物写真が右にある場面では、左側の文字を x=700 に寄せて幅 820 以内に縮める。
    それ以外の文字も、画面からはみ出さないよう幅 1700 以内に縮める"""
    for sc in scenes:
        right = getattr(sc["bg"], "keywords", {}).get("layout") == "right"
        for e in sc["els"]:
            fn = e["fn"]
            if e["dyn"]:
                continue
            if getattr(fn, "func", None) is L.vertical:
                if e["x"] < 400 and e["until"] is None:
                    e["until"] = e["at"]
                continue
            if right and e["x"] <= 760:
                e["x"] = 700
                e["fn"] = P(_shrink, fn, 820)
            else:
                e["fn"] = P(_shrink, fn, 1700)
    return scenes


SCENES = _arrange(_restyle(OPEN + CH0 + CH1 + CH2 + CH3 + CH4 + CH5 + CH6 + ENDING))
