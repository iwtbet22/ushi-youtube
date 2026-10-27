"""2本目「FAのお金と歴史 完全解説」全編。

台本は script/ep02_narration.txt と同じ文。冒頭は ep02_open.py をそのまま使う。
写真は Wikimedia Commons から取ったもの (assets/ep02/img/credits.json)。取れなかった写真は、
ぼけた光の背景と名札に差し替わる (ph / pic)。
"""
from functools import partial as P

import charts as C
import look as L
from ep02_open import DOME, KONDO, KOSHIEN, MARU, OCHIAI
from ep02_open import SCENES as OPEN
from film import E, S

KANEDA = "Masaichi_Kaneda_1956_Scan10003.JPG"
KOMADA = "YB-Norihiro-Komada20090430.jpg"
KIYOHARA = "Kazuhiro_Kiyohara_19901013.jpg"
KUDO = "Kudo_Kimiyasu.jpg"
TOYODA = "TOYODA85.jpg"
KADOKURA = "Ken_Kadokura_2010__2_.jpg"
CHONO_G = "Hisayoshi_Chono_with_Yomiuri__2nd_.jpg"
CHONO_C = "Chono-hisayoshi_carp_.jpg"
SUMITANI = "Ginjiro_Sumitani_with_Saitama_Seibu__2nd_.jpg"
UTSUMI = "Giants_utsumi_26.jpg"
OTAKE = "Giants_Ohtake_17.JPG"
ICHIOKA = "Ichioka30_carp_.jpg"
SEIGI = "Seigi_Tanaka_Fighters_20230408.jpg"
CHANG = "Chang_Yi_Saitama_Seibu_Lions_20230423.jpg"
YAMAKAWA = "Hotaka_Yamakawa_Hawks_20240329.jpg"
WADA = "HAWKS21-WADA__cropped_.jpg"
KAINO = "SH-Hiroshi_Kaino20190812.jpg"
NISHIKAWA = "Ryoma_Nishikawa_Buffaloes_20260416.jpg"
NORIMOTO = "Takahiro_Norimoto_Giants_20260307.jpg"
KAI = "Kai.takuya.10.jpg"
OYAMA = "Yusuke_Ohyama_20230618.jpg"
ITOI = "Itoi-yoshio.jpg"
SUGIUCHI = "Toshiya_Sugiuchi_on_March_24__2012.jpg"
SYAMAGUCHI = "YB-Syun-Yamaguchi.jpg"
MATSUI = "Hideki_Matsui_in_USA-7.jpg"
KOMIYAMA = "LM-Satoru-Komiyama.jpg"
OHTANI = "Dodgers_at_Nationals__53677192000___cropped2_.jpg"
YAMAMOTO = "Yoshinobu_Yamamoto_in_2024__53676737736_.jpg"
SENGA = "Kodai_Senga__52801251674_.jpg"
JINGU = "Meiji_Jingu_Stadium_2019c.jpg"
JINGU_OLD = "Meiji-Jingu_Stadium_aerial_photograph_1936.jpg"
KOSHIEN_OLD = "Koshien_Stadium_aerial_photograph_1948.jpg"
FUKUOKA = "Fukuoka_dome01.jpg"
YANKEE = "YankeeStadium-9-21-22-1.jpg"
DODGER = "Dodger_Stadium_and_Chavez_Ravine_far_view__Chicago_Cubs_at_Los_Angeles_Dodgers___April_12__2025_.jpg"
MORI = "Tomoya_Mori_Orix_Buffaloes_20230.jpg"
NAGOYA = "Binnenkant_van_Nagoya_Dome__-21_maart_2019_a.jpg"
SCOREBOARD = "Nagoyadome_scoreboard_2025.jpg"
MIYAGI = "Rakuten_Mobile_Saikyo_Park_Miyagi_Inside.jpg"
CHIBA = "ZOZOマリンスタジアム_内景.jpg"
ESCON = "ES_CON_FIELD_HOKKAIDO_exterior_from_south_202607a.jpg"
SEIBU = "Seibu_Dome_baseball_stadium_-_19.jpg"
YOKOHAMA = "YokohamaStadium_view.jpg"
FANS = "YokohamaStadium_fans.jpg"
KAWASAKI = "Kawasaki_1989_02.jpg"
BALL = "Baseball-2.jpg"
BATS = "fourbats.jpg"
CITI = "Citi_Field__48613685207_.jpg"
DRAFT = "2012_プロ野球ドラフト会議_TOSHIBA__8122479103_.jpg"
VICTORY = "Moment_of_Saitama_Seibu_Lions_Victory_at_MetLife_Dome.jpg"
FIREWORKS = "Chiba_Marine_Stadium_Fireworks.jpg"


def has(name):
    return (L.IMG / name).exists()


def ph(name, mood="dark", layout="full", focus=(0.5, 0.35), seed=0):
    """写真の背景。写真がなければ光の粒の背景"""
    if name and has(name):
        return P(L.plate, name, mood, layout=layout, focus=focus)
    return P(L.bokeh, seed)


def pic(name, label, sub=None, focus=(0.5, 0.25), w=420, h=520):
    """人物の小さな写真。なければ名札"""
    if has(name):
        return P(C.portrait, name, focus, w, h)
    return P(C.name_plate, label, sub)


def chap(no, title, seed):
    return S([], P(L.bokeh, seed), move="in", hold=2.8, trans="fade", els=[
        E(P(C.chapter_card, no, title), 960, 470, anim="zoom", sfx="boom"),
    ])


def name_v(s, x=440, y=70, at=0, delay=0.3, size=120):
    return E(P(L.vertical, s, size), x, y, at=at, delay=delay, anim="wipe", anchor="t")


def big(s, size=120, color=L.WHITE):
    return P(L.text, s, "NotoSerifJP-Black.ttf", size, color)


T1, T2, T3, T4 = "FAとは何か", "FA前夜：10年選手制度", "FAはなぜ生まれたか", "1993年、最初のオフ"
T5, T6, T7, T8 = "FA権の取り方", "FAのお金のルール", "補償：ランクと人的補償", "揺れる人的補償"
T9, T10, T11 = "海外FAとポスティング", "歴代 大型契約ランキング", "FAは選手を幸せにしたか"

BODY = [
    # ---- 第一章 FAとは何か ------------------------------------------------
    chap(1, T1, 11),
    S(["プロ野球選手の多くは、球団と1年ごとに契約を結び直しています。",
       "1年契約なら、契約が切れたあとは、好きな球団に行けそうなものです。",
       "ところが、そうはなりません。"],
      ph(BALL, "dark"), move="right", tag=T1, els=[
          E(big("1年ごとの契約", 96), 960, 300, until=0, anim="rise"),
          E(big("契約が切れたら…自由？", 96), 960, 300, at=1, until=1, anim="rise"),
          E(big("そうはならない", 130, L.GOLD), 960, 420, at=2, anim="slam", sfx="boom"),
      ]),
    S(["プロ野球には、保留制度という仕組みがあるからです。",
       "球団はシーズンが終わると、来年も契約したい選手の名簿を出します。",
       "この名簿に載った選手は、ほかの球団と契約の話をすることができません。",
       "つまり選手は、球団が手放さない限り、ずっと同じ球団にいることになります。"],
      ph(SEIBU, "cold"), move="in", tag=T1, els=[
          E(P(L.scroll, "保留制度", "ほりゅうせいど"), 960, 380, until=0, anim="zoom", sfx="boom"),
          E(P(C.bullet_list, ["来年も契約したい選手の名簿を出す", "名簿に載ると、他球団と交渉できない"], 54),
            960, 380, at=1, until=2, anim="rise"),
          E(big("球団が手放さない限り、移れない", 92, L.GOLD), 960, 420, at=3, anim="rise"),
      ]),
    S(["前回の動画で、ドラフトで決まるのは入団ではなく、交渉権だとお話ししました。",
       "入口のドラフトでは行き先を選べず、入ったあとは保留制度で縛られる。",
       "この縛りを解いて、選手が自分で次の球団を選べるようにする権利。",
       "それが、FA、フリーエージェントです。"],
      ph(DRAFT, "dark", layout="blur", seed=12), move="in", tag=T1, els=[
          E(P(C.timeline, [("入口", "ドラフト\n交渉権"), ("在籍中", "保留制度\nで縛られる"), ("出口", "FA\n自分で選ぶ")], 0),
            960, 360, until=0, anim="fade"),
          E(P(C.timeline, [("入口", "ドラフト\n交渉権"), ("在籍中", "保留制度\nで縛られる"), ("出口", "FA\n自分で選ぶ")], 1),
            960, 360, at=1, until=1, anim="none"),
          E(P(C.timeline, [("入口", "ドラフト\n交渉権"), ("在籍中", "保留制度\nで縛られる"), ("出口", "FA\n自分で選ぶ")], 2),
            960, 360, at=2, until=2, anim="none"),
          E(P(L.gold, "FA", size=260), 960, 380, at=3, anim="slam", sfx="boom"),
      ]),
    S(["FA宣言した選手は、12球団のどこの球団とも、自由に交渉できます。",
       "海外FA権なら、メジャーリーグなど、海外の球団とも契約できます。",
       "ただし、この自由は、長い時間をかけて、ようやく手に入れたものでした。"],
      ph(MIYAGI, "dark"), move="left", tag=T1, els=[
          E(P(C.bullet_list, ["国内FA：12球団と自由に交渉", "海外FA：海外の球団とも契約できる"], 56),
            960, 360, until=1, anim="rise"),
          E(big("長い時間をかけて、手に入れた自由", 86, L.GOLD), 960, 420, at=2, anim="fade"),
      ]),

    # ---- 第二章 10年選手制度 ----------------------------------------------
    chap(2, T2, 21),
    S(["実は、FAが生まれる前にも、移籍の自由を認める仕組みがありました。",
       "1947年に始まった、10年選手制度です。",
       "10シーズン以上、現役としてプレーした選手に、特別な権利を与える制度でした。"],
      ph(JINGU_OLD, "sepia"), move="in", tag=T2, els=[
          E(P(L.gold, "1947年", size=200), 960, 330, at=1, until=1, anim="slam", sfx="boom"),
          E(P(L.scroll, "十年選手制度", "1947年〜1975年"), 960, 400, at=2, anim="zoom"),
      ]),
    S(["1952年の改正後は、同じ球団で10年を過ごした選手が、ボーナスを受け取るか、自由に移籍するかを選べるようになります。",
       "今で言えば、残留のごほうびをもらうか、FAで移籍するか、という選択です。"],
      ph(KOSHIEN_OLD, "sepia"), move="left", tag=T2, els=[
          E(P(C.option_cards, ("残る", "ボーナスを\n受け取る"), ("出る", "自由に\n移籍する"), "同じ球団で10年"),
            960, 420, anim="rise"),
      ]),
    S(["この制度を使った移籍で、もっとも有名なのが、金田正一投手です。",
       "国鉄スワローズのエースで、のちに通算400勝を挙げる大投手でした。",
       "1964年のオフ、金田投手はこの権利を使い、国鉄から巨人へ移ります。",
       "ちょうど国鉄の球団が、サンケイに譲り渡されることが決まった年でした。"],
      ph(KANEDA, "sepia", layout="right", focus=(0.5, 0.2), seed=22), move="in", tag=T2, els=[
          name_v("金田正一"),
          E(P(L.gold, "通算400勝", size=110), 470, 860, at=1, until=1, anim="rise", anchor="b"),
          E(P(C.move, "国鉄", "巨人", "1964年オフ"), 470, 860, at=2, anim="rise", anchor="b"),
      ]),
    S(["しかし、10年選手制度は、1975年限りで廃止されます。",
       "ここから、選手が自分の意思で移籍できる仕組みがない時代が、およそ18年続くことになります。"],
      ph(KAWASAKI, "sepia", seed=23), move="out", tag=T2, els=[
          E(P(L.gold, "1975年 廃止", size=150), 960, 330, anim="glitch", sfx="boom"),
          E(P(C.timeline, [("1947", "10年選手\n制度"), ("1975", "廃止"), ("1993", "FA導入")], 1), 960, 600,
            at=1, anim="fade"),
      ]),

    # ---- 第三章 FAはなぜ生まれたか -----------------------------------------
    chap(3, T3, 31),
    S(["流れを変えたのは、海の向こうのアメリカでした。",
       "メジャーリーグでも、かつては選手が球団に縛られる仕組みがありました。",
       "しかし1975年、選手の申し立てを受けた仲裁の裁定で、この縛りが崩れます。",
       "そして1976年から、メジャーリーグでFA制度が始まりました。"],
      ph(YANKEE, "cold"), move="right", tag=T3, els=[
          E(big("アメリカ", 140), 960, 360, until=1, anim="fade"),
          E(P(L.gold, "1975年 仲裁の裁定", size=110), 960, 360, at=2, until=2, anim="slam", sfx="boom"),
          E(P(L.gold, "1976年 MLBでFA開始", size=110), 960, 360, at=3, anim="rise"),
      ]),
    S(["日本でも、選手たちが動き出します。",
       "1985年、日本プロ野球選手会が、労働組合として認められました。",
       "球団と対等に話し合える立場を手に入れた選手会が、強く求めたのが、移籍の自由、FA制度でした。"],
      ph(SCOREBOARD, "dark"), move="in", tag=T3, els=[
          E(P(L.gold, "1985年", size=200), 960, 300, at=1, until=1, anim="slam", sfx="boom"),
          E(P(C.name_plate, "日本プロ野球選手会", "労働組合として認められる"), 960, 560, at=1, until=1, anim="rise"),
          E(big("求めたのは「移籍の自由」", 100, L.GOLD), 960, 420, at=2, anim="rise"),
      ]),
    S(["話し合いの末、1993年、ついにFA制度が導入されます。",
       "同じ年、ドラフトには、選手が行きたい球団を選べる逆指名の仕組みも入りました。"],
      ph(KOSHIEN, "gold"), move="left", tag=T3, els=[
          E(P(L.gold, "1993年 FA制度 導入", size=130), 960, 330, anim="slam", sfx="boom"),
          E(P(C.name_plate, "同じ年、ドラフトに「逆指名」", "選手が行きたい球団を選べる"), 960, 600, at=1, anim="rise"),
      ]),
    S(["ただし、生まれたFAは、使うのに条件の多い制度でした。",
       "権利を取るまでに長い年数がかかり、移籍するには補償も必要。",
       "この使いにくさは、今も続く議論の出発点になっています。"],
      ph(BATS, "dark", layout="blur", seed=33), move="in", tag=T3, els=[
          E(P(C.bullet_list, ["権利を取るまで、長い年数", "移籍するには、補償が必要"], 60), 960, 380, at=1, anim="rise"),
          E(big("使いにくいFA", 120, L.GOLD), 960, 380, until=0, anim="glitch", sfx="boom"),
      ]),

    # ---- 第四章 1993年、最初のオフ ------------------------------------------
    chap(4, T4, 41),
    S(["1993年のオフ、初めてのFA宣言の季節がやってきます。",
       "第1号となったのは、松永浩美選手。阪神からダイエーへの移籍でした。"],
      ph(FUKUOKA, "sepia"), move="in", tag=T4, els=[
          E(P(L.gold, "FA移籍 第1号", size=120), 960, 280, at=1, anim="slam", sfx="boom"),
          E(P(C.name_plate, "松永浩美", "阪神 → ダイエー（1993年オフ）"), 960, 520, at=1, delay=0.6, anim="rise"),
      ]),
    S(["そして、大きな話題をさらったのが、落合博満選手です。",
       "三冠王を3度獲った大打者が、40歳を目前にして、中日から巨人へ移りました。"],
      ph(OCHIAI, "sepia", layout="right", focus=(0.5, 0.3)), move="in", tag=T4, els=[
          name_v("落合博満"),
          E(P(L.gold, "三冠王 3度", size=100), 470, 760, at=1, until=1, anim="rise", anchor="b", delay=0.5),
          E(P(C.move, "中日", "巨人", "1993年オフ"), 470, 870, at=1, delay=2.5, anim="rise", anchor="b"),
          E(P(C.note, "※写真は中日監督時代", 28), 1860, 860, anchor="br"),
      ]),
    S(["一方、巨人の駒田徳広選手は、巨人から横浜へ。",
       "さらに、オリックスの石嶺和彦選手が阪神へ移り、最初のオフに、4人がFAで球団を移りました。"],
      ph(KOMADA, "sepia", layout="right", focus=(0.5, 0.25), seed=42), move="in", tag=T4, els=[
          name_v("駒田徳広"),
          E(P(C.move, "巨人", "横浜"), 470, 870, until=0, delay=1.0, anim="rise", anchor="b"),
          E(P(C.table, ["選手", "移籍"], [["松永浩美", "阪神 → ダイエー"], ["落合博満", "中日 → 巨人"],
                                        ["駒田徳広", "巨人 → 横浜"], ["石嶺和彦", "オリックス → 阪神"]], [300, 460], 80),
            520, 470, at=1, anim="rise"),
      ]),
    S(["その後も、FAの移籍先として目立ったのが、巨人でした。",
       "1994年には広沢克己選手と川口和久投手、1996年には清原和博選手、1999年には工藤公康投手と江藤智選手。",
       "各球団の主力が次々と巨人に集まり、FAは巨人のための制度ではないか、という声も上がりました。"],
      ph(KIYOHARA, "dark", layout="right", focus=(0.5, 0.25), seed=43), move="in", tag=T4, els=[
          E(P(C.timeline, [("1994", "広沢克己\n川口和久"), ("1996", "清原和博"), ("1999", "工藤公康\n江藤智")]),
            820, 330, at=1, until=1, anim="fade"),
          E(P(L.caption_small, "写真：清原和博（1990年・西武時代）", 28), 1860, 860, at=1, until=1, anchor="br"),
          E(big("「FAは巨人のための制度？」", 92, L.GOLD), 760, 400, at=2, anim="glitch", sfx="boom"),
      ]),

    # ---- 第五章 FA権の取り方 ----------------------------------------------
    chap(5, T5, 51),
    S(["では、FA権は、どうすれば手に入るのでしょうか。",
       "数えるのは、一軍に登録されていた日数です。",
       "1シーズンに145日、一軍に登録されると、1年と数えます。"],
      ph(NAGOYA, "dark"), move="in", tag=T5, els=[
          E(big("数えるのは「一軍の登録日数」", 92), 960, 300, at=1, anim="rise"),
          E(P(C.days_bar, 145), 960, 560, at=2, anim="rise"),
      ]),
    S(["145日を超えても、1シーズンで数えるのは145日まで。",
       "145日に届かない年は、ほかの年と足し合わせて、145日ごとに1年になります。"],
      P(L.bokeh, 52), move="in", tag=T5, els=[
          E(P(C.days_bar, 145, label="180日いても…145日まで"), 960, 330, until=0, anim="rise"),
          E(P(C.days_bar, 90, label="ある年 90日"), 960, 250, at=1, anim="rise"),
          E(P(C.days_bar, 55, label="別の年 55日 → 合わせて1年"), 960, 500, at=1, delay=1.6, anim="rise"),
      ]),
    S(["国内の球団へ移るための国内FA権は、高校からプロに入った選手で8年。",
       "大学や社会人からプロに入った選手は、7年です。",
       "海外の球団とも契約できる海外FA権は、全員が9年です。",
       "ずっと一軍にいても、国内FA権を取れるのは、高卒の選手で26歳前後、大卒の選手で29歳前後になります。"],
      ph(CHIBA, "dark"), move="right", tag=T5, els=[
          E(P(C.table, ["", "必要な年数"], [["国内FA（高卒）", "8年"], ["国内FA（大卒・社会人）", "7年"],
                                            ["海外FA（全員）", "9年"]], [620, 420], 110, None, 50),
            960, 390, until=2, anim="rise"),
          E(P(C.option_cards, ("高卒", "26歳\n前後"), ("大卒", "29歳\n前後"), "国内FA権を取れる年齢（最短）"),
            960, 420, at=3, anim="rise"),
      ]),
    S(["ケガをした選手には、特例もあります。",
       "試合などでのケガで登録を外れたとき、条件を満たせば、最大60日までを登録日数に足してもらえます。"],
      P(L.bokeh, 53, (120, 150, 170)), move="in", tag=T5, els=[
          E(P(L.scroll, "故障者特例", "最大60日を足せる"), 960, 400, anim="zoom"),
      ]),
    S(["さらに2024年からは、先発投手の特例も始まりました。",
       "先発投手は、登板の間隔をあけるために、いったん一軍登録を外れることがあります。いわゆる、投げ抹消です。",
       "この間の日数が数えられず、FA権が遠のく不公平を減らすため、条件付きで6日分を足すことになりました。"],
      ph(FUKUOKA, "dark"), move="left", tag=T5, els=[
          E(P(L.gold, "2024年〜 先発投手の特例", size=100), 960, 300, until=0, anim="slam", sfx="boom"),
          E(P(L.scroll, "投げ抹消", "登板のあと、いったん登録を外れる"), 960, 400, at=1, until=1, anim="zoom"),
          E(P(L.gold, "＋6日", size=220), 960, 400, at=2, delay=1.5, anim="slam", sfx="boom"),
      ]),
    S(["権利を使うときは、日本シリーズが終わった翌日から、土日と祝日を除く7日以内に、書面で申請します。",
       "申請した選手はFA宣言選手として公示され、その翌日から、すべての球団と交渉できるようになります。"],
      ph(YOKOHAMA, "cold"), move="in", tag=T5, els=[
          E(P(C.timeline, [("日本シリーズ", "終了"), ("7日以内", "書面で申請"), ("公示", "FA宣言選手"),
                           ("翌日", "交渉スタート")], 1), 960, 330, until=0, anim="fade"),
          E(P(C.timeline, [("日本シリーズ", "終了"), ("7日以内", "書面で申請"), ("公示", "FA宣言選手"),
                           ("翌日", "交渉スタート")], 3), 960, 330, at=1, anim="none"),
      ]),
    S(["宣言したうえで、元の球団に残ることもできます。これが、宣言残留です。",
       "ただし、宣言残留を認めない方針の球団もあり、宣言は、出ていく覚悟を問われる決断でもあります。",
       "一度宣言すると、次に権利を取り直せるのは4年後です。"],
      ph(OYAMA, "dark", layout="right", focus=(0.5, 0.25), seed=54), move="in", tag=T5, els=[
          E(P(L.scroll, "宣言残留", "宣言して、元の球団に残る"), 700, 380, until=0, anim="zoom"),
          E(big("出ていく覚悟", 120, L.GOLD), 640, 400, at=1, until=1, anim="glitch", sfx="boom"),
          E(P(L.gold, "再取得は4年後", size=110), 660, 400, at=2, anim="rise"),
          E(P(L.caption_small, "写真：大山悠輔（2024年オフに宣言残留）", 28), 1860, 860, anchor="br"),
      ]),

    # ---- 第六章 FAのお金のルール --------------------------------------------
    chap(6, T6, 61),
    S(["FAで新しい契約を結ぶとき、お金にもルールがあります。",
       "まず、翌シーズンの年俸は、今の年俸が上限。いわゆる現状維持までです。",
       "球団どうしが年俸をつり上げ合うのを防ぐためのルールです。"],
      ph(SCOREBOARD, "dark", layout="blur", seed=62), move="in", tag=T6, els=[
          E(P(L.scroll, "現状維持", "1年目の年俸は、前の年まで"), 960, 380, at=1, anim="zoom", sfx="boom"),
          E(P(C.note, "FA規約 第7条", 32), 960, 640, at=1, delay=1.0),
      ]),
    S(["ただし、抜け道もあります。",
       "2年目以降の年俸を上げること、契約年数を長くすること、出来高をつけることには、制限がありません。",
       "だからFA契約は、4年総額いくら、5年総額いくら、と総額で語られることが多いのです。",
       "例えば2022年のオフ、森友哉選手の契約は4年総額18億円と報じられましたが、移籍1年目の年俸は、前の年と同じ2億1000万円とされました。"],
      ph(MORI, "dark", layout="right", focus=(0.5, 0.25), seed=63), move="in", tag=T6, els=[
          E(big("抜け道", 150, L.GOLD), 640, 380, until=0, anim="glitch", sfx="boom"),
          E(P(C.bullet_list, ["2年目以降の年俸を上げる", "契約年数を長くする", "出来高をつける"], 54), 640, 400,
            at=1, until=2, anim="rise"),
          E(P(C.money_bars, [("1年目の年俸", 2.1, False), ("4年の総額", 18, True)], "億円", 1000), 660, 400, at=3,
            anim="rise"),
          E(P(C.note), 620, 600, at=3, delay=0.8),
          E(P(L.caption_small, "森友哉（オリックス）", 34), 1300, 860, at=3, anchor="b"),
      ]),
    S(["さらに、特別な事情があるとコミッショナーが認めれば、上限を超える契約もできます。",
       "2016年のオフ、DeNAから巨人へ移った山口俊投手は、前の年と同じ年俸と発表されましたが、のちに、この手続きで2億円を超える契約だったと報じられました。"],
      ph(SYAMAGUCHI, "dark", layout="right", focus=(0.5, 0.25), seed=64), move="in", tag=T6, els=[
          E(P(L.scroll, "特別な事情", "コミッショナーが認めれば例外"), 660, 400, until=0, anim="zoom"),
          name_v("山口俊", at=1),
          E(P(C.move, "DeNA", "巨人", "2016年オフ"), 560, 870, at=1, delay=1.4, anim="rise", anchor="b"),
      ]),
    S(["契約金にもルールがあります。",
       "ほかの球団へ移る場合、契約金は、翌シーズンの年俸の半分まで。",
       "元の球団に残る場合は、上限がありません。"],
      P(L.bokeh, 65), move="in", tag=T6, els=[
          E(P(C.option_cards, ("移籍する", "年俸の\n半分まで"), ("残留する", "上限\nなし"), "FAの契約金"), 960, 420,
            at=1, anim="rise"),
      ]),
    S(["そしてもう一つ。補償が必要な選手を、よその球団から獲得できるのは、原則として1球団2人までです。",
       "補償という言葉が出てきました。",
       "ここからが、FAのいちばん複雑で、いちばんドラマが生まれる部分です。"],
      ph(BATS, "dark"), move="in", tag=T6, els=[
          E(P(L.gold, "1球団 2人まで", size=150), 960, 380, until=0, anim="slam", sfx="boom"),
          E(P(L.scroll, "補償", "ほしょう"), 960, 400, at=1, anim="zoom", sfx="boom"),
      ]),

    # ---- 第七章 補償 -------------------------------------------------------
    chap(7, T7, 71),
    S(["FAで選手が出ていくと、元の球団は、大事な戦力を失います。",
       "その穴を埋めるために、獲得した球団から元の球団へ、補償をします。",
       "補償が必要かどうかは、選手のランクで決まります。",
       "ランクは、元の球団の日本人選手の中での、年俸の順位です。"],
      ph(ESCON, "cold"), move="left", tag=T7, els=[
          E(P(C.move, "元の球団", "獲得した球団"), 960, 340, until=0, anim="rise"),
          E(P(C.move, "獲得した球団", "元の球団（補償）"), 960, 340, at=1, until=1, anim="rise"),
          E(big("決め手は「ランク」", 110, L.GOLD), 960, 380, at=2, anim="slam", sfx="boom"),
      ]),
    S(["年俸が1位から3位ならAランク、4位から10位ならBランク、11位以下はCランクです。",
       "Cランクの選手は、補償なしで移籍できます。",
       "このランク分けは2008年から。それまでは、FAで移籍する全員に補償が必要でした。"],
      P(L.bokeh, 72), move="in", tag=T7, els=[
          E(P(C.table, ["ランク", "球団内の年俸順位", "補償"], [["A", "1〜3位", "必要"], ["B", "4〜10位", "必要"],
                                                          ["C", "11位以下", "なし"]], [240, 520, 260], 110, None, 52),
            960, 390, until=1, anim="rise"),
          E(P(C.timeline, [("1993", "全員に補償"), ("2008", "ランク制\nCは補償なし")], 1, 1200), 960, 380, at=2,
            anim="fade"),
      ]),
    S(["補償には2種類あります。お金を払う金銭補償と、選手を1人差し出す人的補償です。",
       "Aランクの場合、元の球団は、旧年俸の80%のお金か、選手1人と旧年俸の50%のお金か、を選べます。",
       "Bランクなら、60%のお金か、選手1人と40%のお金です。",
       "例えば年俸2億円のAランク選手なら、1億6000万円か、選手1人と1億円です。"],
      P(L.bokeh, 73), move="in", tag=T7, els=[
          E(P(C.option_cards, ("金銭補償", "お金"), ("人的補償", "選手1人\n＋お金"), "補償は2種類"), 960, 420,
            until=0, anim="rise"),
          E(P(C.option_cards, ("Aランク", "旧年俸の\n80%"), ("Aランク", "選手1人\n＋50%")), 960, 400, at=1, until=1,
            anim="rise"),
          E(P(C.option_cards, ("Bランク", "旧年俸の\n60%"), ("Bランク", "選手1人\n＋40%")), 960, 400, at=2, until=2,
            anim="none"),
          E(P(C.option_cards, ("年俸2億円・A", "1億\n6000万円"), ("年俸2億円・A", "選手1人\n＋1億円")), 960, 400,
            at=3, anim="none"),
      ]),
    S(["では、差し出す選手は、どう決まるのでしょうか。",
       "獲得した球団は、守りたい選手を28人まで、プロテクトできます。",
       "ほかに、外国人枠の選手、直近のドラフトで入った新人、育成選手も対象外です。",
       "それ以外の選手の名簿が元の球団に渡され、元の球団は、その中から1人を選びます。",
       "支配下の選手は、最大70人。主力を28人守っても、名簿にはまだ多くの選手が残ります。"],
      P(L.bokeh, 74, (120, 140, 170)), move="in", tag=T7, els=[
          E(P(C.protect_grid, 28), 960, 400, at=1, until=1, anim="rise"),
          E(P(C.bullet_list, ["外国人枠の選手", "直近のドラフトの新人", "育成選手"], 56), 960, 330, at=2, until=2,
            anim="rise"),
          E(P(L.caption_small, "これらも対象外", 40), 960, 610, at=2, until=2, delay=0.8),
          E(P(C.protect_grid, 28, 70, 14, 51), 960, 400, at=3, anim="rise"),
      ]),
    S(["選ばれた選手は、拒否できません。拒否すれば資格停止となり、試合に出られなくなります。",
       "自分の意思とは関係なく、ある日突然、別の球団への移籍が決まる。",
       "これが、人的補償です。"],
      ph(FANS, "dark"), move="out", tag=T7, els=[
          E(P(L.gold, "拒否 ＝ 資格停止", size=120), 960, 360, until=0, anim="slam", sfx="boom"),
          E(big("ある日突然、移籍が決まる", 100), 960, 380, at=1, until=1, anim="fade"),
          E(P(L.scroll, "人的補償", "じんてきほしょう"), 960, 400, at=2, anim="zoom", sfx="boom"),
      ]),
    S(["人的補償の第1号は、1995年のオフ。",
       "日本ハムから巨人へ移った河野博文投手の補償として、川邉忠義投手が、巨人から日本ハムへ移りました。"],
      ph(DOME, "sepia"), move="right", tag=T7, els=[
          E(P(L.gold, "人的補償 第1号", size=130), 960, 300, anim="slam", sfx="boom"),
          E(P(C.name_plate, "河野博文 → 巨人", "日本ハムからFA（1995年オフ）"), 600, 560, at=1, anim="rise"),
          E(P(C.name_plate, "川邉忠義 → 日本ハム", "人的補償"), 1320, 560, at=1, delay=1.8, anim="rise"),
      ]),
    S(["人的補償は、ときに、名の知れたベテランまで動かしてきました。",
       "2005年のオフ、西武から巨人へ移った豊田清投手の補償で、巨人の江藤智選手が西武へ。",
       "江藤選手は、6年前にFAで広島から巨人に来た選手でした。",
       "FAで来た選手が、今度は補償で出ていったのです。"],
      ph(TOYODA, "dark", layout="right", focus=(0.5, 0.25), seed=75), move="in", tag=T7, els=[
          name_v("豊田清", at=1),
          E(P(C.move, "西武", "巨人", "2005年オフ"), 470, 870, at=1, delay=1.0, until=1, anim="rise", anchor="b"),
          E(P(C.name_plate, "江藤智 → 西武", "人的補償"), 520, 600, at=1, delay=3.0, anim="rise"),
          E(P(L.gold, "FAで来て、補償で出る", size=76), 520, 780, at=3, anim="rise"),
      ]),
    S(["その翌年には、横浜から巨人へ移った門倉健投手の補償として、43歳の工藤公康投手が横浜へ移りました。",
       "工藤投手もまた、かつてFAで巨人に来た選手でした。"],
      ph(KUDO, "dark", layout="right", focus=(0.5, 0.25), seed=76), move="in", tag=T7, els=[
          name_v("工藤公康"),
          E(P(C.name_plate, "門倉健 → 巨人", "横浜からFA（2006年オフ）"), 470, 760, until=0, anim="rise"),
          E(P(L.gold, "43歳で人的補償", size=96), 470, 870, at=0, delay=4.0, anim="slam", anchor="b", sfx="boom"),
      ]),
    S(["そして2018年のオフ。",
       "広島から巨人へ移った丸佳浩選手の補償で、広島が選んだのは、巨人の長野久義選手でした。",
       "巨人で長く活躍してきた人気選手の移籍に、多くのファンが驚きました。"],
      ph(CHONO_G, "dark", layout="right", focus=(0.5, 0.25), seed=77), move="in", tag=T7, els=[
          E(P(L.gold, "2018年オフ", size=150), 640, 380, until=0, anim="slam", sfx="boom"),
          name_v("長野久義", at=1, delay=2.4),
          E(P(C.move, "丸佳浩：広島", "巨人"), 470, 870, at=1, until=1, anim="rise", anchor="b"),
          E(P(C.move, "長野久義：巨人", "広島"), 470, 870, at=2, anim="rise", anchor="b"),
      ]),
    S(["同じオフ、西武から巨人へ移った炭谷銀仁朗選手の補償では、巨人のエースとして活躍してきた内海哲也投手が、西武へ移っています。"],
      ph(UTSUMI, "dark", layout="right", focus=(0.5, 0.25), seed=78), move="in", tag=T7, els=[
          name_v("内海哲也", delay=2.5),
          E(P(C.move, "内海哲也：巨人", "西武", "2018年オフ"), 470, 870, delay=3.0, anim="rise", anchor="b"),
      ]),
    S(["一方で、人的補償が、新しいチャンスになった選手もいます。",
       "2013年のオフ、大竹寛投手の補償で巨人から広島へ移った一岡竜司投手は、広島のリリーフとして活躍しました。"],
      ph(ICHIOKA, "dark", layout="right", focus=(0.5, 0.25), seed=79), move="in", tag=T7, els=[
          E(big("新しいチャンス", 120, L.GOLD), 640, 380, until=0, anim="rise"),
          name_v("一岡竜司", at=1),
          E(P(C.move, "巨人", "広島", "2013年オフ"), 470, 870, at=1, delay=1.5, anim="rise", anchor="b"),
      ]),
    S(["2022年のオフ、近藤健介選手の補償でソフトバンクから日本ハムへ移った田中正義投手は、新天地で抑えを任されるまでになります。"],
      ph(SEIGI, "dark", layout="right", focus=(0.5, 0.25), seed=80), move="in", tag=T7, els=[
          name_v("田中正義"),
          E(P(C.move, "ソフトバンク", "日本ハム", "2022年オフ"), 470, 870, delay=2.0, anim="rise", anchor="b"),
      ]),
    S(["同じオフ、森友哉選手の補償でオリックスから西武へ移った張奕投手は、外国籍の選手として初めての人的補償でした。"],
      ph(CHANG, "dark", layout="right", focus=(0.5, 0.25), seed=81), move="in", tag=T7, els=[
          name_v("張奕"),
          E(P(C.move, "オリックス", "西武", "2022年オフ"), 470, 760, delay=2.0, anim="rise", anchor="b"),
          E(P(L.gold, "外国籍で初", size=90), 470, 880, delay=4.0, anim="slam", anchor="b", sfx="boom"),
      ]),

    # ---- 第八章 揺れる人的補償 ----------------------------------------------
    chap(8, T8, 91),
    S(["その人的補償をめぐって、大きな騒ぎが起きたのが、2024年の1月です。",
       "前の年のオフ、西武の山川穂高選手が、FAでソフトバンクへ移籍しました。",
       "西武は補償として、ソフトバンクから選手を1人選ぶことになります。"],
      ph(YAMAKAWA, "dark", layout="right", focus=(0.5, 0.25), seed=92), move="in", tag=T8, els=[
          E(P(L.gold, "2024年1月", size=150), 640, 380, until=0, anim="slam", sfx="boom"),
          name_v("山川穂高", at=1),
          E(P(C.move, "西武", "ソフトバンク", "2023年オフ"), 470, 870, at=1, delay=1.5, anim="rise", anchor="b"),
      ]),
    S(["1月11日、一部のスポーツ紙が、西武はソフトバンクの和田毅投手を指名する方針だと報じました。",
       "和田投手は、日米通算160勝を超える、42歳の大ベテランでした。",
       "ソフトバンクは、高い年俸のベテランは選ばれないだろうと考え、プロテクトから外していたと見られています。",
       "報道に、ファンは騒然となりました。"],
      ph(WADA, "dark", layout="right", focus=(0.5, 0.25), seed=93), move="in", tag=T8, els=[
          E(P(L.gold, "1月11日", size=120), 640, 300, until=0, anim="slam", sfx="boom"),
          E(P(C.name_plate, "「西武は和田毅を指名へ」", "一部スポーツ紙の報道"), 640, 520, until=0, delay=1.2, anim="rise"),
          name_v("和田毅", at=1),
          E(P(L.gold, "日米通算160勝超・42歳", size=76), 470, 870, at=1, until=1, anim="rise", anchor="b"),
          E(P(C.name_plate, "プロテクト外", "と見られている"), 470, 760, at=2, until=2, anim="rise"),
          E(big("騒然", 160, L.GOLD), 520, 400, at=3, anim="glitch", sfx="boom"),
      ]),
    S(["しかし、その日に西武が発表したのは、別の選手。剛速球が持ち味の、甲斐野央投手でした。",
       "なぜ指名が変わったのか。球団からの、はっきりした説明はありませんでした。"],
      ph(KAINO, "dark", layout="right", focus=(0.5, 0.25), seed=94), move="in", tag=T8, els=[
          name_v("甲斐野央", delay=2.0),
          E(P(C.move, "ソフトバンク", "西武", "人的補償"), 470, 870, delay=3.5, until=0, anim="rise", anchor="b"),
          E(big("説明は、なかった", 100, L.GOLD), 520, 820, at=1, anim="rise", anchor="b"),
      ]),
    S(["ただ、この一件で、人的補償の問題が一気に表に出ます。",
       "選手が、物のようにやり取りされていないか。",
       "守る選手と守らない選手を分ける名簿が、外にもれていないか。",
       "選手会の事務局長からは、起きるべくして起きた、という声も上がりました。"],
      ph(VICTORY, "cold", layout="blur", seed=95), move="in", tag=T8, els=[
          E(big("選手は「物」なのか", 110), 960, 300, at=1, anim="glitch", sfx="boom"),
          E(big("名簿は、もれていないか", 96), 960, 470, at=2, anim="rise"),
          E(P(C.quote, "起きるべくして起きた", 64), 960, 660, at=3, anim="rise"),
      ]),
    S(["人的補償は、獲得する球団にとっても、重い負担です。",
       "高額の契約に加えて、補償のお金、そして選手1人。",
       "このコストの重さが、FAでの移籍を少なくしている、という指摘もあります。"],
      ph(FUKUOKA, "dark"), move="right", tag=T8, els=[
          E(P(C.bullet_list, ["高額の契約", "補償のお金", "選手1人"], 64), 960, 380, at=1, anim="rise"),
          E(big("重すぎるコスト → FAが動かない", 88, L.GOLD), 960, 700, at=2, anim="rise"),
      ]),
    S(["そして2026年。人的補償をなくす議論が、本格的に動き出します。",
       "5月、NPBが人的補償の撤廃を検討していると報じられました。"],
      P(L.bokeh, 96), move="in", tag=T8, els=[
          E(P(L.gold, "2026年", size=230), 960, 360, until=0, anim="slam", sfx="boom"),
          E(P(C.timeline, [("5月", "撤廃を検討\nと報道"), ("6月", "実行委員会\n代わりの案"), ("8月", "選手会\n合意せず")], 0),
            960, 360, at=1, anim="fade"),
      ]),
    S(["6月の実行委員会では、代わりの案として、獲得した球団が、ドラフトの2位や3位に相当する指名権を、元の球団に渡す案が軸になりました。",
       "今いる選手の代わりに、未来の選手を選ぶ権利で補おう、という考え方です。",
       "メジャーリーグにも、FAで主力を失った球団に、ドラフトの指名権を与える仕組みがあります。"],
      P(L.bokeh, 97), move="in", tag=T8, els=[
          E(P(C.timeline, [("5月", "撤廃を検討\nと報道"), ("6月", "実行委員会\n代わりの案"), ("8月", "選手会\n合意せず")], 1),
            960, 250, until=0, anim="none"),
          E(P(C.move, "獲得した球団", "元の球団"), 960, 560, until=0, delay=2.0, anim="rise"),
          E(P(L.gold, "ドラフト2〜3位相当の指名権", size=72), 960, 690, until=0, delay=3.0, anim="rise"),
          E(P(C.option_cards, ("いま", "選手1人"), ("これから", "未来の選手を\n選ぶ権利")), 960, 420, at=1, until=1,
            anim="rise"),
          E(P(L.scroll, "MLBにも同じ考え方", "FAで主力を失った球団に指名権"), 960, 400, at=2, anim="zoom"),
      ]),
    S(["ところが8月、選手会は、この案を受け入れませんでした。",
       "指名権を渡す形では、移籍を活発にする助けにならない、と判断したと伝えられています。",
       "獲得する球団の負担が重いままでは、FAで動く選手は増えない、という考えです。"],
      P(L.bokeh, 98, (150, 150, 160)), move="in", tag=T8, els=[
          E(P(C.timeline, [("5月", "撤廃を検討\nと報道"), ("6月", "実行委員会\n代わりの案"), ("8月", "選手会\n合意せず")], 2),
            960, 250, until=0, anim="none"),
          E(P(L.gold, "選手会、受け入れず", size=120), 960, 560, until=0, delay=0.8, anim="slam", sfx="boom"),
          E(big("移籍を活発にする助けにならない", 86), 960, 400, at=1, until=1, anim="rise"),
          E(big("負担が重いまま → FAは増えない", 86, L.GOLD), 960, 400, at=2, anim="rise"),
      ]),
    S(["その結果、今年のオフも、今の制度のままFAが行われます。",
       "話し合いは、これからも続きます。",
       "選手が選ぶ自由と、球団どうしの戦力のバランス。",
       "人的補償のゆくえは、その両方をどう守るか、という問題なのです。"],
      ph(JINGU, "dark"), move="out", tag=T8, els=[
          E(P(L.scroll, "今オフは現行制度", "話し合いは続く"), 960, 380, until=1, anim="zoom"),
          E(P(C.option_cards, ("選手", "選ぶ自由"), ("球団", "戦力の\nバランス")), 960, 420, at=2, anim="rise"),
      ]),

    # ---- 第九章 海外FAとポスティング ----------------------------------------
    chap(9, T9, 101),
    S(["ここで、海外へ移るときの話もしておきましょう。",
       "海外FA権を使って海外の球団へ移る場合、元の球団への補償はありません。",
       "元の球団には、何も残らないのです。"],
      ph(YANKEE, "dark"), move="left", tag=T9, els=[
          E(P(C.table, ["", "元の球団に残るもの"], [["海外FA", "なし"]], [400, 560], 110, None, 52), 960, 380,
            at=1, anim="rise"),
          E(big("何も残らない", 130, L.GOLD), 960, 640, at=2, anim="slam", sfx="boom"),
      ]),
    S(["これに対して、FA権を持っていない選手が海外へ移る方法が、ポスティングです。",
       "ポスティングでは、球団が移籍を認めたうえで、移籍先の球団から元の球団へ、譲渡金が支払われます。",
       "球団にとっては、FAで何も残らずに出ていかれるより、ポスティングで送り出したほうが、お金が残るというわけです。"],
      ph(DODGER, "dark"), move="right", tag=T9, els=[
          E(P(L.scroll, "ポスティング", "FA権がなくても海外へ"), 960, 380, until=0, anim="zoom"),
          E(P(C.move, "海外の球団", "元の球団（譲渡金）"), 960, 380, at=1, until=1, anim="rise"),
          E(P(C.table, ["", "元の球団に残るもの"], [["海外FA", "なし"], ["ポスティング", "譲渡金"]], [440, 560], 110,
                       1, 52), 960, 380, at=2, anim="rise"),
      ]),
    S(["FAでメジャーへ渡った代表的な選手が、松井秀喜選手です。",
       "2002年のオフ、巨人からヤンキースへ移りました。"],
      ph(MATSUI, "dark", layout="right", focus=(0.5, 0.25), seed=102), move="in", tag=T9, els=[
          name_v("松井秀喜"),
          E(P(C.move, "巨人", "ヤンキース", "2002年オフ"), 470, 870, at=1, anim="rise", anchor="b"),
      ]),
    S(["一方、海外FAには、思わぬ落とし穴もありました。",
       "海外へ移った選手が短い期間で日本に戻ると、元の球団への補償が必要になる決まりがあるのです。",
       "2001年のオフ、FAで横浜からメッツへ移った小宮山悟投手は、翌年限りでメッツを退団しました。",
       "日本の球団と契約すると補償が必要になる期間だったため、獲得に動く球団は現れませんでした。",
       "小宮山投手は、2003年を、どこの球団にも所属せずに過ごします。",
       "そして2004年、ロッテに戻って、現役を続けました。"],
      ph(KOMIYAMA, "dark", layout="right", focus=(0.5, 0.25), seed=103), move="in", tag=T9, els=[
          E(big("落とし穴", 150, L.GOLD), 640, 380, until=0, anim="glitch", sfx="boom"),
          E(P(L.scroll, "早く戻ると補償", "海外FAの決まり"), 660, 400, at=1, until=1, anim="zoom"),
          name_v("小宮山悟", at=2),
          E(P(C.timeline, [("2001", "FAで\nメッツへ"), ("2002", "メッツ\n退団"), ("2003", "所属なし"),
                           ("2004", "ロッテ\nで復帰")], 3, 1180), 640, 720, at=2, anim="fade"),
      ]),

    # ---- 第十章 ランキング ------------------------------------------------
    chap(10, T10, 111),
    S(["お待たせしました。",
       "ここからは、FA権を使って結んだ契約の、総額ランキングです。",
       "対象は、宣言残留を含む、日本の球団との契約。",
       "金額はすべて、報道による推定です。"],
      ph(MIYAGI, "gold", layout="blur", seed=112), move="in", tag=T10, els=[
          E(P(L.gold, "歴代 大型契約ランキング", size=110), 960, 330, at=1, anim="slam", sfx="boom"),
          E(P(C.bullet_list, ["FA権を使った契約（宣言残留を含む）", "日本の球団との契約", "金額は報道による推定"], 48),
            960, 600, at=2, anim="rise"),
      ]),
    S(["第9位は、同じ金額で2人。",
       "2023年のオフ、広島からオリックスへ移った西川龍馬選手。",
       "そして、西武からソフトバンクへ移った山川穂高選手。",
       "どちらも、4年総額12億円と報じられました。"],
      P(L.bokeh, 113), move="in", tag=T10, els=[
          E(P(C.rank_card, 9, "西川龍馬", ["広島 → オリックス（2023年オフ）"], "4年 12億円", NISHIKAWA if has(NISHIKAWA) else None, h=370),
            960, 225, at=1, anim="rise", sfx="whoosh"),
          E(P(C.rank_card, 9, "山川穂高", ["西武 → ソフトバンク（2023年オフ）"], "4年 12億円", YAMAKAWA if has(YAMAKAWA) else None, h=370),
            960, 630, at=2, anim="rise", sfx="whoosh"),
          E(P(C.note), 1860, 118, at=1, anchor="tr"),
      ]),
    S(["第8位は、則本昂大投手。",
       "2025年のオフ、楽天から巨人へ。3年総額13億円です。"],
      ph(NORIMOTO, "dark", focus=(0.5, 0.3), seed=114), move="in", tag=T10, els=[
          E(P(C.rank_card, 8, "則本昂大", ["楽天 → 巨人（2025年オフ）"], "3年 13億円"), 960, 560, anim="rise", sfx="whoosh"),
          E(P(C.note), 1860, 118, anchor="tr"),
      ]),
    S(["第7位、甲斐拓也選手。",
       "2024年のオフ、ソフトバンクから巨人へ。5年総額15億円です。"],
      ph(KAI, "dark", focus=(0.5, 0.3), seed=115), move="in", tag=T10, els=[
          E(P(C.rank_card, 7, "甲斐拓也", ["ソフトバンク → 巨人（2024年オフ）"], "5年 15億円"), 960, 560, anim="rise",
            sfx="whoosh"),
          E(P(C.note), 1860, 118, anchor="tr"),
      ]),
    S(["第6位、大山悠輔選手。",
       "2024年のオフ、FA宣言のうえで、阪神に残留しました。5年総額17億円に、出来高がつきます。",
       "巨人も、最長6年で総額24億円を超える条件を出していたと報じられました。"],
      ph(OYAMA, "dark", focus=(0.5, 0.3), seed=116), move="in", tag=T10, els=[
          E(P(C.rank_card, 6, "大山悠輔", ["阪神に宣言残留（2024年オフ）"], "5年 17億円＋出来高"), 960, 560, until=1,
            anim="rise", sfx="whoosh"),
          E(P(C.name_plate, "巨人の条件：最長6年・総額24億円超", "と報じられた"), 960, 560, at=2, anim="rise"),
          E(P(C.note), 1860, 118, anchor="tr"),
      ]),
    S(["第4位は、同じ金額で2人です。",
       "2016年のオフ、オリックスから阪神へ移った糸井嘉男選手。4年総額18億円以上と報じられました。",
       "2022年のオフ、西武からオリックスへ移った森友哉選手。4年総額18億円です。"],
      P(L.bokeh, 117), move="in", tag=T10, els=[
          E(P(C.rank_card, 4, "糸井嘉男", ["オリックス → 阪神（2016年オフ）"], "4年 18億円以上", ITOI if has(ITOI) else None, h=370),
            960, 225, at=1, anim="rise", sfx="whoosh"),
          E(P(C.rank_card, 4, "森友哉", ["西武 → オリックス（2022年オフ）"], "4年 18億円", MORI if has(MORI) else None, h=370),
            960, 630, at=2, anim="rise", sfx="whoosh"),
          E(P(C.note), 1860, 118, at=1, anchor="tr"),
      ]),
    S(["第3位、杉内俊哉投手。",
       "2011年のオフ、ソフトバンクから巨人へ。4年総額20億円です。",
       "杉内投手は会見で、球団の幹部から、FAをしても必要とする球団はない、と言われたことを明かし、大きな話題になりました。"],
      ph(SUGIUCHI, "dark", focus=(0.5, 0.3), seed=118), move="in", tag=T10, els=[
          E(P(C.rank_card, 3, "杉内俊哉", ["ソフトバンク → 巨人（2011年オフ）"], "4年 20億円"), 960, 560, until=1,
            anim="rise", sfx="whoosh"),
          E(P(C.quote, "FAをしても必要とする球団はない", 60), 960, 420, at=2, anim="zoom"),
          E(P(C.note, "球団幹部に言われたと、本人が会見で明かした", 30), 960, 560, at=2, delay=1.0),
          E(P(C.note), 1860, 118, anchor="tr"),
      ]),
    S(["第2位、丸佳浩選手。",
       "2018年のオフ、広島から巨人へ。5年総額25億5000万円。",
       "広島で2年続けてMVPを獲った外野手が、巨人へ移りました。"],
      ph(MARU, "dark", focus=(0.5, 0.3), seed=119), move="in", tag=T10, els=[
          E(P(C.rank_card, 2, "丸佳浩", ["広島 → 巨人（2018年オフ）"], "5年 25億5000万円"), 960, 560, until=1,
            anim="rise", sfx="whoosh"),
          E(P(L.gold, "2年連続MVP", size=130), 960, 420, at=2, anim="slam", sfx="boom"),
          E(P(C.note), 1860, 118, anchor="tr"),
      ]),
    S(["そして第1位。",
       "近藤健介選手。2022年のオフ、日本ハムからソフトバンクへ。7年総額50億円規模。",
       "2位の丸選手の、およそ2倍です。",
       "近藤選手は、移籍1年目の2023年、ホームラン王と打点王の2冠に輝きました。"],
      ph(KONDO, "gold", focus=(0.5, 0.3)), move="in", tag=T10, els=[
          E(P(L.gold, "第1位", size=200), 960, 400, until=0, anim="slam", sfx="boom"),
          E(P(C.rank_card, 1, "近藤健介", ["日本ハム → ソフトバンク（2022年オフ）"], "7年 50億円規模"), 960, 560, at=1,
            until=1, anim="rise", sfx="whoosh"),
          E(P(C.money_bars, [("1位 近藤健介", 50, True), ("2位 丸佳浩", 25.5, False)], "億円", 1300), 960, 420, at=2,
            until=2, anim="rise"),
          E(P(L.gold, "移籍1年目に 本塁打王・打点王", size=84), 960, 420, at=3, anim="rise"),
          E(P(C.note), 1860, 118, anchor="tr"),
      ]),
    S(["なお、昔の大型移籍には、総額がはっきり報じられていないものも多く、今回は総額が報じられた契約に絞っています。"],
      P(L.bokeh, 120, (130, 130, 140)), move="in", tag=T10, els=[
          E(P(C.table, ["順位", "選手", "総額（推定）"], [
              ["1", "近藤健介", "7年 50億円規模"], ["2", "丸佳浩", "5年 25.5億円"], ["3", "杉内俊哉", "4年 20億円"],
              ["4", "糸井嘉男・森友哉", "4年 18億円"], ["6", "大山悠輔", "5年 17億円＋出来高"], ["7", "甲斐拓也", "5年 15億円"],
              ["8", "則本昂大", "3年 13億円"], ["9", "西川龍馬・山川穂高", "4年 12億円"]], [140, 520, 520], 76, None, 40),
            900, 470, anim="rise"),
      ]),
    S(["番外編として、メジャーリーグにも目を向けてみましょう。",
       "桁が、ひとつ変わります。",
       "2023年のオフ、大谷翔平選手は、エンゼルスからFAとなり、ドジャースと10年総額7億ドルの契約を結びました。",
       "当時、北米のプロスポーツで史上最高額と報じられました。"],
      ph(OHTANI, "dark", layout="right", focus=(0.5, 0.25), seed=121), move="in", tag=T10, els=[
          E(P(L.gold, "番外編 メジャーリーグ", size=96), 640, 380, until=1, anim="slam", sfx="boom"),
          name_v("大谷翔平", at=2),
          E(P(L.gold, "10年 7億ドル", size=110), 470, 870, at=2, delay=2.5, anim="slam", anchor="b", sfx="boom"),
      ]),
    S(["同じオフ、山本由伸投手は、オリックスからポスティングでドジャースへ。12年総額3億2500万ドル、投手として史上最高額と報じられました。",
       "こちらはFAではなくポスティングなので、オリックスには譲渡金が支払われています。"],
      ph(YAMAMOTO, "dark", layout="right", focus=(0.5, 0.25), seed=122), move="in", tag=T10, els=[
          name_v("山本由伸"),
          E(P(L.gold, "12年 3億2500万ドル", size=86), 470, 870, delay=4.0, until=0, anim="slam", anchor="b", sfx="boom"),
          E(P(C.move, "ドジャース", "オリックス（譲渡金）"), 520, 870, at=1, anim="rise", anchor="b"),
      ]),
    S(["日本からFAでメジャーへ渡った例では、2022年のオフ、ソフトバンクからメッツへ移った千賀滉大投手の、5年総額7500万ドルが目立ちます。"],
      ph(SENGA, "dark", layout="right", focus=(0.5, 0.25), seed=123), move="in", tag=T10, els=[
          name_v("千賀滉大"),
          E(P(L.gold, "5年 7500万ドル", size=100), 470, 870, delay=4.0, anim="slam", anchor="b", sfx="boom"),
      ]),

    # ---- 第十一章 ------------------------------------------------------
    chap(11, T11, 131),
    S(["FA制度が始まって、30年あまり。",
       "FAは、選手に、選ぶ自由をもたらしました。",
       "移籍先で輝いた選手もいれば、思うような結果を残せなかった選手もいます。",
       "それでもFAは、選手が自分のキャリアを、自分で決めるための、大切な権利です。"],
      ph(KOSHIEN, "gold"), move="left", tag=T11, els=[
          E(P(L.gold, "1993 → 2026", size=150), 960, 380, until=0, anim="slam", sfx="boom"),
          E(big("選ぶ自由", 150), 960, 400, at=1, until=2, anim="rise"),
          E(big("キャリアを、自分で決める", 104, L.GOLD), 960, 400, at=3, anim="rise"),
      ]),
    S(["一方で、人的補償のように、ある選手の自由が、別の選手の運命を変えてしまう場面もあります。",
       "制度は、今も変わり続けています。",
       "今年のオフ、誰がFAを宣言するのか。そして、補償のルールは、どう変わっていくのか。",
       "その目線でストーブリーグを見ると、プロ野球は、もっとおもしろくなるはずです。"],
      ph(FIREWORKS, "dark"), move="out", tag=T11, els=[
          E(big("今年のオフ、誰が動くのか", 104, L.GOLD), 960, 400, at=2, anim="rise"),
      ]),

    # ---- まとめ ---------------------------------------------------------
    S(["それでは、まとめです。",
       "FAは、球団の保留から選手を解き放つ権利で、日本では1993年に始まりました。",
       "国内FA権は高卒8年、大卒と社会人7年、海外FA権は9年。一軍登録145日で1年と数えます。",
       "FAで移籍すると、ランクに応じて補償が必要になり、人的補償は今、見直しの議論が続いています。",
       "歴代の大型契約の1位は、近藤健介選手の、7年総額50億円規模でした。"],
      P(L.bokeh, 141), move="in", trans="flash", tag="まとめ", els=[
          E(P(L.gold, "まとめ", size=150), 960, 200, anim="slam", sfx="boom"),
          E(P(C.bullet_list, ["FAは「保留」から選手を解き放つ権利（1993年〜）"], 50, 1500), 960, 340, at=1, anim="rise"),
          E(P(C.bullet_list, ["国内FA 高卒8年・大卒社会人7年／海外FA 9年"], 50, 1500), 960, 470, at=2, anim="rise"),
          E(P(C.bullet_list, ["補償はランク次第、人的補償は見直しの議論中"], 50, 1500), 960, 600, at=3, anim="rise"),
          E(P(C.bullet_list, ["歴代1位は近藤健介 7年50億円規模（推定）"], 50, 1500), 960, 730, at=4, anim="rise"),
      ]),
]


def _cta(t):
    import ui
    return ui.cta_frame(t)


ENDING = [
    S(["最後まで見ていただき、ありがとうございました。",
       "このチャンネルでは、FAや年俸、育成契約など、プロ野球のお金と制度のしくみを、わかりやすく解説しています。",
       "動画が役に立ったと思ったら、高評価とチャンネル登録、そして通知のオンをお願いします。"],
      P(L.bokeh, 151), move="in", hold=1.0, els=[
          E(P(L.gold, "ご視聴ありがとうございました", size=90), 960, 420, until=0, anim="zoom"),
          E(P(L.gold, "プロ野球 お金と制度のしくみ", size=84), 960, 220, at=1, anim="rise"),
          E(P(C.bullet_list, ["FA", "年俸", "育成契約"], 56, 520), 960, 520, at=1, until=1, anim="rise"),
          E(_cta, 960, 560, at=2, delay=0.3, anim="none", dyn=True),
      ]),
]

SCENES = OPEN + BODY + ENDING
