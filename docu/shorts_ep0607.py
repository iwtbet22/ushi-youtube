"""球団は儲かってるのか (本編 ep06 セ・リーグ編 / ep07 パ・リーグ編) へつなぐショート動画 4本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_ce1   (short_ce2 / short_pa1 / short_pa2)

台本の文と数字は本編 (script/ep06_narration.txt, ep07_narration.txt と各 factcheck で確認済み) から取っている。
置き方は shorts_ep04 と同じ (x=480 中心、幅 840 以内、絵は上半分、大きな文字はその下)。
"""
from functools import partial as P

import charts as C
import look as L
import news as N
import props as R
import ep06
import ep07
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, fit, fog, head, pic


def photo(name, seed, tint=(1.0, 1.0, 1.0), focus=(0.5, 0.45), rot=-3):
    """霧の上に、白い縁の写真を1枚"""
    return pic(P(R.print_photo, name, 760, rot, focus), seed, tint, 840, 520, 640)


def to_main(seed, league):
    """最後の「続きは本編で」"""
    return S([f"{league}6球団のお金は、関連動画の本編で。"], fog(seed, GOLDF, 0.9), move="in", hold=1.0, els=[
        E(fit(P(L.text, "続きは本編で", "NotoSerifJP-Black.ttf", 100, L.GOLD)), CX, 700, anim="slam", sfx="boom"),
        E(fit(P(C.name_plate, "球団は儲かってるのか？", f"{league}編　下の関連動画から")), CX, 920, delay=0.6,
          anim="rise"),
        E(fit(P(L.text, "▼", "NotoSerifJP-Black.ttf", 90, L.GOLD)), 200, 1150, delay=1.2, anim="rise"),
    ])


# ---- セ・リーグ 1本目：球団の赤字は「広告費」 ------------------------------------
CE1 = [
    S(["プロ野球の球団の赤字。",
       "実はそれを埋めるお金は、親会社の「広告費」として扱えるのです。"],
      pic(P(N.stamp, "赤字", RED, 190), 1011, REDF, 700, 420), move="in", trans="cut", els=[
          head("球団の赤字は広告費？"),
          big("赤字を埋めるお金", 980, 110, WHITE, at=1, until=1, anim="rise", delay=0.3),
          big("＝広告費", 1130, 150, GOLD, at=1, anim="slam", sfx="boom", delay=1.6),
      ]),
    S(["1954年、国税庁は、ある通達を出しました。",
       "親会社が、子会社の球団の赤字を埋めるために出したお金は、その赤字の額までなら、広告宣伝費として扱ってよい、というものです。"],
      pic(P(N.document, "職業野球団に対して支出した広告宣伝費等の取扱について",
            ["親会社が球団の欠損金を補てんするため支出した金銭は、", "広告宣伝費の性質を有するものとして取り扱う"],
            ["広告宣伝費"]), 1012, BLUEF, 840, 520), move="in", els=[
          head("1954年 国税庁の通達"),
          big("1954年", 980, 150, GOLD, until=0, anim="slam", sfx="boom"),
          big("広告宣伝費", 980, 160, GOLD, at=1, anim="slam", sfx="boom", delay=2.5),
      ]),
    S(["広告宣伝費は、会社の経費になります。",
       "つまり親会社は、球団の赤字を埋めても、その分、自分の会社の利益が減り、税金も減る。",
       "球団は、親会社にとっての「広告」として扱われてきたのです。"],
      pic(P(C.bullet_list, ["球団の赤字を埋める", "親会社の経費になる", "親会社の税金が減る"], 64, 800), 1013, GOLDF, 840,
          420),
      move="in", els=[
          head("だから親会社は"),
          big("経費になる", 980, 150, GOLD, until=0, anim="slam", sfx="boom"),
          big("税金も減る", 980, 150, WHITE, at=1, until=1, anim="slam", sfx="boom"),
          big("球団＝広告", 980, 160, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    S(["だから、球団の数字は、親会社との関係で大きく変わります。",
       "決算を公表しているセ・リーグの4球団は、いずれも黒字。",
       "阪神が27億5400万円、DeNAが24億6100万円、ヤクルトが16億2500万円、広島が6億2800万円です。"],
      fog(1014, GOLDF, 0.8), move="in", els=[
          head("セ・リーグ 球団の純利益"),
          big("親会社しだい", 980, 150, WHITE, until=0, anim="slam", sfx="boom"),
          E(fit(P(C.money_bars, [("阪神", 27.54, True), ("DeNA", 24.61, False), ("ヤクルト", 16.25, False),
                                 ("広島", 6.28, False)], "億円", 840, 32)), CX, 690, at=1, anim="rise"),
          E(P(C.note, "※各球団の決算公告による純利益", 30), CX, 985, at=1),
          big("4球団とも黒字", 1120, 130, GOLD, at=1, until=1, anim="slam", sfx="boom"),
      ]),
    S(["一方、巨人と中日は、決算そのものを公表していません。"],
      pic(P(N.stamp, "非公表", RED, 190), 1015, REDF, 700, 420), move="in", els=[
          head("巨人と中日は"),
          big("決算を公表していない", 980, 110, RED, anim="glitch", sfx="boom", delay=0.6),
      ]),
    to_main(1016, "セ・リーグ"),
]

# ---- セ・リーグ 2本目：親会社のないカープの財布 ----------------------------------
CE2 = [
    S(["親会社のない球団、広島東洋カープ。",
       "赤字を埋めてくれる親会社がないのに、黒字を続けています。"],
      photo(ep06.MAZDA, 1021, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("親会社のない球団"),
          E(P(C.note, "※マツダスタジアム", 30), CX, 940),
          big("親会社なし", 1060, 150, RED, until=0, anim="slam", sfx="boom"),
          big("それでも黒字", 1060, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["2025年の売上は、174億5700万円。",
       "このうち、入場料の収入が61億100万円、グッズの売上が25億3300万円。",
       "入場料とグッズだけで、売上のおよそ半分です。"],
      fog(1022, BLUEF, 0.8), move="in", els=[
          head("カープの財布（2025年）"),
          E(fit(P(C.vbars, [("売上", 174.57, "174億5700万", False), ("入場料", 61.01, "61億100万", True),
                            ("グッズ", 25.33, "25億3300万", True)], "億円", 420, 190, 60)), CX, 680, anim="rise"),
          big("売上の約半分", 1080, 140, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    S(["観客動員は、204万人。",
       "1人あたり、入場料でおよそ3000円、グッズで1200円ほどを使ってくれた計算です。"],
      pic(P(R.people, 24, 7, 8, 1023), 1023, GOLDF, 820, 440), move="in", els=[
          head("お客さん1人あたり"),
          big("204万人", 980, 160, GOLD, until=0, anim="slam", sfx="boom"),
          big("入場料 約3000円", 980, 110, WHITE, at=1, anim="rise"),
          big("グッズ 約1200円", 1120, 110, WHITE, at=1, anim="rise", delay=1.6),
      ]),
    S(["出ていくお金は、まず選手の年俸。",
       "外国人選手の推定も合わせて、およそ30億円。売上の、およそ17%です。"],
      pic(P(N.money, "年俸", 3, None, 1024), 1024, BLUEF, 820, 460), move="in", els=[
          head("出ていくお金"),
          big("選手の年俸", 980, 150, WHITE, until=0, anim="slam", sfx="boom"),
          big("約30億円", 980, 160, GOLD, at=1, anim="slam", sfx="boom"),
          big("売上の約17%", 1130, 110, WHITE, at=1, anim="rise", delay=2.0),
          E(P(C.note, "※外国人選手の年俸は報道による推定", 30), CX, 370, at=1),
      ]),
    S(["2025年の純利益は、6億2800万円。",
       "お客さんを呼び、グッズを売り、自分で稼いだお金でやっていく。",
       "それが、親会社に頼らない球団の姿なのです。"],
      photo(ep06.MAZDA_AIR, 1025, GOLDF, (0.5, 0.5), 3), move="in", els=[
          head("自分で稼ぐ球団"),
          big("純利益 6億2800万円", 1060, 110, GOLD, until=0, anim="slam", sfx="boom"),
          big("自分で稼ぐ", 1060, 160, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    to_main(1026, "セ・リーグ"),
]

# ---- パ・リーグ 1本目：利益が毎年ぴったり0円 --------------------------------------
PA1 = [
    S(["利益が、毎年ぴったり0円。",
       "そんな決算が続いたプロ野球の球団があります。"],
      pic(P(N.stamp, "0円", RED, 220), 1031, REDF, 700, 440), move="in", trans="cut", els=[
          head("利益がぴったり0円"),
          big("毎年 0円", 980, 160, RED, until=0, anim="slam", sfx="boom"),
          big("どこの球団？", 980, 140, WHITE, at=1, anim="rise"),
      ]),
    S(["オリックス・バファローズを運営する、オリックス野球クラブ。",
       "決算公告を見ると、2019年から2023年までの5年間、会社にたまった利益が、毎年マイナス800万円のまま、1円も動いていません。"],
      pic(P(C.table, ["決算期", "利益剰余金"], [["2019年3月期", "▲800万円"], ["2020年3月期", "▲800万円"],
                                            ["2021年3月期", "▲800万円"], ["2022年3月期", "▲800万円"],
                                            ["2023年3月期", "▲800万円"]], [420, 380], 88, None, 42),
          1032, BLUEF, 820, 560, 660), move="in", els=[
          head("オリックス野球クラブ"),
          big("1円も動かない", 1060, 140, RED, at=1, anim="slam", sfx="boom", delay=3.5),
      ]),
    S(["つまり、毎年の利益が、ちょうど0円だったということです。",
       "会社の利益が、毎年ちょうど0円で終わることは、普通はまずありません。"],
      fog(1033, REDF, 0.85), move="in", els=[
          head("普通はありえない"),
          E(fit(P(C.big_number, "毎年の利益", "ちょうど0円", 150)), CX, 640, anim="rise"),
          big("普通はまずない", 1000, 140, WHITE, at=1, anim="slam", sfx="boom"),
      ]),
    S(["これは、親会社が赤字の分だけお金を出して、利益を0にそろえていると考えるのが自然です。",
       "球団の赤字を埋めたお金は、親会社の広告宣伝費として扱えるからです。"],
      pic(P(C.move, "親会社", "球団", "赤字の分だけ", 56, 800), 1034, GOLDF, 820, 360), move="in", els=[
          head("親会社がそろえている？"),
          E(P(C.note, "※決算公告の数字からの推測", 30), CX, 370),
          big("0にそろえる", 980, 150, GOLD, until=0, anim="slam", sfx="boom"),
          big("広告宣伝費", 980, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["ところが、2024年3月期だけは、42億8400万円の黒字になりました。",
       "球団の数字は、親会社がどう扱うかで、0円にもなれば、42億円にもなるのです。"],
      photo(ep07.KYOCERA, 1035, GOLDF, (0.5, 0.5)), move="in", els=[
          head("ところが2024年3月期"),
          E(P(C.note, "※京セラドーム大阪", 30), CX, 940),
          big("42億8400万円の黒字", 1060, 110, GOLD, until=0, anim="slam", sfx="boom"),
          big("0円にも 42億円にも", 1060, 110, WHITE, at=1, anim="rise"),
      ]),
    to_main(1036, "パ・リーグ"),
]

# ---- パ・リーグ 2本目：球団は赤字、球場の会社は70億 --------------------------------
PA2 = [
    S(["球団は、12億円の赤字。",
       "なのに、球場を運営する会社は、70億円の営業利益。"],
      photo(ep07.ESCON2, 1041, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("赤字の球団、稼ぐ球場"),
          E(P(C.note, "※エスコンフィールドHOKKAIDO", 30), CX, 940),
          big("球団 12億円の赤字", 1060, 110, RED, until=0, anim="slam", sfx="boom"),
          big("球場 70億円の利益", 1060, 110, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["北海道日本ハムファイターズは、2023年、北広島市に新しい球場を開業しました。",
       "運営しているのは、日本ハムグループの会社です。"],
      photo(ep07.ESCON_ROOF1, 1042, BLUEF, (0.5, 0.5), 3), move="in", els=[
          head("自前の球場"),
          big("2023年 開業", 1060, 140, GOLD, until=0, anim="slam", sfx="boom"),
          big("日本ハムグループ", 1060, 130, WHITE, at=1, anim="rise"),
      ]),
    S(["球団の2025年12月期は、12億6200万円の赤字。2期連続の赤字です。",
       "一方、球場の会社は、2025年12月期に、過去最高の70億8000万円の営業利益を出したと明らかにしています。"],
      fog(1043, BLUEF, 0.8), move="in", els=[
          head("2025年12月期"),
          big("2期連続の赤字", 1000, 130, RED, until=0, anim="glitch", sfx="boom", delay=2.0),
          E(fit(P(ep06.club_card, "北海道日本ハムファイターズ", [("純損益", "▲12億6200万円")])), CX, 600, anim="rise"),
          E(fit(P(ep06.parent_card, "ファイターズ スポーツ＆エンターテイメント",
                  [("営業利益", "70億8000万円")], "球場の会社")), CX, 900, at=1, anim="rise"),
          big("過去最高", 1150, 140, GOLD, at=1, anim="slam", sfx="boom", delay=3.0),
      ]),
    S(["札幌ドームを借りていた頃は、球場の飲食や看板の収入の多くが、球場側に入っていたとされます。",
       "自前の球場になって、そのお金がグループに残るようになりました。"],
      photo(ep07.SAPPORO, 1044, BLUEF, (0.5, 0.5)), move="in", els=[
          head("札幌ドーム時代は"),
          E(P(C.note, "※札幌ドーム", 30), CX, 940),
          big("球場側に入っていた", 1060, 110, WHITE, until=0, anim="rise"),
          big("グループに残る", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["球場の売上は、開業した2023年に251億円。",
       "札幌ドーム時代の2019年より、93億円増えたと発表されています。",
       "日本ハムは、お金を稼ぐ場所を、球団から球場へ移したのです。"],
      fog(1045, GOLDF, 0.8), move="in", els=[
          head("球場の売上"),
          E(fit(P(C.vbars, [("2019年", 158, "158億円", False), ("2023年", 251, "251億円", True)], "億円", 420, 190, 90)),
            CX, 680, anim="rise"),
          big("93億円増", 1080, 150, GOLD, at=1, until=1, anim="slam", sfx="boom"),
          big("稼ぐのは球場", 1080, 150, GOLD, at=2, anim="slam", sfx="boom"),
      ]),
    to_main(1046, "パ・リーグ"),
]

CE1, CE2, PA1, PA2 = (ep07._fix_speech(x) for x in (CE1, CE2, PA1, PA2))
