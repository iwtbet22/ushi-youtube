"""11/27・11/29・11/30 のショート 3本 (縦 1080x1920)。

  DOCU_VERTICAL=1 python3 docu/film.py short_bp2   (short_tv1, short_ht1)

  short_bp2  11/27  破綻した市民のドーム（12本目 球場編）
  short_tv1  11/29  WBCが地上波から消えた（14本目 放映権編。11/28 公開の翌日）
  short_ht1  11/30  阪神に30億円（15本目 阪神編。12/1 公開の前日）

台本の文と数字は、本編の台本 (script/ep12・ep14・ep15_narration.txt。出典と確度は各回の research.md) から取っている。
報道や Wikipedia だけの数字（大阪ドームの約90億円、WBC の約150億円、29億円の免除）は、本編と同じく断定しない。
置き方は shorts_s3 と同じ。最後はチャンネル登録のお願いで締める。
"""
from functools import partial as P

import charts as C
import ep12
import ep14
import ep15
from film import E, S
from shorts_ep04 import CX, GOLD, RED, WHITE, REDF, GOLDF, BLUEF, big, head, pic
from shorts_s3 import photo, subscribe, END

# ---- 11/27：破綻した市民のドーム (12本目 球場編) ---------------------------------------
BP2 = [
    S(["負債588億円を抱えて、破綻した球場があります。",
       "今の、京セラドーム大阪です。"],
      photo(ep12.KYOCERA, 1401, REDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("破綻したドーム"),
          E(P(C.note, "※京セラドーム大阪", 30), CX, 940),
          big("負債 588億円", 1060, 150, RED, until=0, anim="slam", sfx="boom"),
          big("京セラドーム大阪", 1060, 130, WHITE, at=1, anim="slam", sfx="boom"),
      ]),
    S(["もとの名前は、大阪ドーム。",
       "大阪市が筆頭株主の、第三セクターの会社が運営していました。"],
      photo(ep12.OSAKA_LAST, 1402, BLUEF, (0.5, 0.5), 3), move="in", els=[
          head("もとは大阪ドーム"),
          E(P(C.note, "※大阪ドーム（2004年9月）", 30), CX, 940),
          big("大阪市が筆頭株主", 1060, 120, GOLD, at=1, anim="rise"),
      ]),
    S(["1997年に開業しましたが、毎年15億円前後の赤字が続いたといわれます。",
       "建てたときのお金を、球場の稼ぎで返せなかったのです。"],
      pic(P(C.big_number, "毎年の赤字", "約15億円", 160), 1403, REDF, 820, 460), move="in", els=[
          head("1997年 開業"),
          big("建てたお金を返せない", 1000, 110, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["2005年10月、会社は会社更生法を申し立てました。",
       "翌年、球場は、最低100億円で売りに出されます。",
       "しかし、手を挙げたのは1社だけで、その中身は不十分と判断されました。"],
      pic(P(C.big_number, "2005年10月", "会社更生法", 150), 1404, BLUEF, 820, 460), move="in", els=[
          head("そして破綻"),
          big("最低 100億円で売りに", 1000, 110, GOLD, at=1, until=1, anim="rise"),
          big("買い手が決まらない", 1000, 120, RED, at=2, anim="slam", sfx="boom"),
      ]),
    S(["最後に球場を手に入れたのは、オリックスのグループでした。",
       "その額は、およそ90億円と報じられています。"],
      pic(P(C.vbars, [("負債", 588, "588億円", False), ("買われた額", 90, "約90億円", True)], "億円", 420, 190, 60),
          1405, GOLDF, 820, 460), move="in", els=[
          head("買ったのはオリックス"),
          big("約90億円", 1080, 160, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["市民のお金で建てたドームは、建てたお金を返せないまま、球団のグループのものになったのです。"],
      photo(ep12.BUFF_FANS, 1406, GOLDF, (0.5, 0.5), 3), move="in", els=[
          head("市民のドームの行方"),
          E(P(C.note, "※大阪ドームの近鉄ファン（2004年7月）", 30), CX, 940),
          big("球団のグループのものに", 1060, 110, GOLD, anim="rise"),
      ]),
    subscribe(1407, END),
]
BP2 = ep12._fix_speech(BP2)

# ---- 11/29：WBCが地上波から消えた (14本目 放映権編) --------------------------------------
TV1 = [
    S(["2026年のWBC。",
       "侍ジャパンの試合は、テレビの地上波では、生中継されませんでした。"],
      photo(ep14.WBC23, 1501, BLUEF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("WBCが地上波から消えた"),
          E(P(C.note, "※2023年WBC 準々決勝（東京ドーム）", 30), CX, 940),
          big("地上波の生中継 なし", 1060, 120, RED, at=1, anim="slam", sfx="boom"),
      ]),
    S(["日本の放送と配信の権利を、Netflixが独り占めにしたのです。",
       "最初の試合から決勝まで、全47試合です。"],
      pic(P(C.big_number, "日本の権利を独り占め", "Netflix", 170), 1502, REDF, 820, 460), move="in", els=[
          head("権利を買ったのは"),
          big("全47試合", 1000, 150, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["放映権料は、前の大会の約30億円から、およそ150億円に跳ね上がったと報じられています。",
       "地上波のテレビ局には、払える額ではなかったともいわれます。"],
      pic(P(C.vbars, [("2023年", 30, "約30億円", False), ("2026年", 150, "約150億円", True)], "億円", 420, 190, 60),
          1503, GOLDF, 820, 460), move="in", els=[
          head("放映権料（報道）"),
          big("約5倍", 1080, 170, GOLD, until=0, anim="slam", sfx="boom"),
          big("テレビ局には払えない", 1080, 110, RED, at=1, anim="rise"),
      ]),
    S(["前の大会では、主催者が読売新聞社を通して、日本のテレビ局に権利を与えていました。",
       "ところが2026年は、読売新聞社を通さず、Netflixに直接、権利を与えたのです。"],
      photo(ep14.NTV, 1504, BLUEF, (0.5, 0.5), 3), move="in", els=[
          head("権利の渡り方が変わった"),
          E(P(C.note, "※日本テレビタワー", 30), CX, 940),
          big("読売新聞社 → テレビ局", 1060, 100, WHITE, until=0, anim="rise"),
          big("Netflixに直接", 1060, 140, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    S(["それでも、試合は多くの人に見られました。",
       "Netflixの発表では、全47試合を見た人は、のべ3140万人。",
       "35歳より若い人や、女性が中心だったといいます。"],
      pic(P(C.big_number, "全47試合を見た人（のべ）", "3140万人", 150), 1505, GOLDF, 820, 460), move="in", els=[
          head("Netflixの発表"),
          big("若い人と女性が中心", 1000, 110, GOLD, at=2, anim="rise"),
      ]),
    subscribe(1506, END),
]
TV1 = ep14._fix_speech(TV1)

# ---- 11/30：阪神に30億円 (15本目 阪神編。翌日公開) ------------------------------------------
HT_END = ["明日の夜6時、阪神タイガースのお金を、長い動画で解説します。",
          "チャンネル登録して、見逃さないでください。"]

HT1 = [
    S(["親会社が変わっただけで、30億円を払えと言われた球団があります。",
       "阪神タイガースです。"],
      photo(ep15.KOSHIEN_AIR, 1601, GOLDF, (0.5, 0.5)), move="in", trans="cut", els=[
          head("阪神に30億円？"),
          E(P(C.note, "※甲子園球場", 30), CX, 940),
          big("30億円", 1060, 170, GOLD, until=0, anim="slam", sfx="boom"),
          big("阪神タイガース", 1060, 140, WHITE, at=1, anim="slam", sfx="boom"),
      ]),
    S(["始まりは2005年。",
       "村上ファンドが、親会社の阪神電鉄の株を、およそ27%持っていることがわかりました。",
       "そして、タイガースを上場させてはどうか、と求めたのです。"],
      photo(ep15.HANSHIN_TRAIN, 1602, BLUEF, (0.5, 0.5), 3), move="in", els=[
          head("始まりは村上ファンド"),
          E(P(C.note, "※阪神電鉄の電車", 30), CX, 940),
          big("株の約27%", 1060, 150, WHITE, at=1, until=1, anim="slam", sfx="boom"),
          big("タイガースを上場？", 1060, 130, RED, at=2, anim="slam", sfx="boom"),
      ]),
    S(["2006年、そこに現れたのが、阪急でした。",
       "1株930円で株を買い取り、阪急阪神ホールディングスが生まれます。"],
      photo(ep15.HANKYU_TRAIN, 1603, REDF, (0.5, 0.5)), move="in", els=[
          head("阪急がやってきた"),
          E(P(C.note, "※阪急電鉄の電車", 30), CX, 940),
          big("1株930円", 1060, 150, GOLD, until=0, anim="slam", sfx="boom"),
          big("阪急阪神HD 誕生", 1060, 130, WHITE, at=1, anim="slam", sfx="boom"),
      ]),
    S(["すると、プロ野球のオーナー会議が、待ったをかけます。",
       "親会社の上に阪急が来たのだから、新しい球団が入ってくるのと同じだ。",
       "楽天やソフトバンクのときと同じように、合わせて30億円を払うべきだ、と決めたのです。"],
      pic(P(C.big_number, "2006年7月 オーナー会議", "30億円", 170), 1604, REDF, 820, 460), move="in", els=[
          head("プロ野球が待った"),
          big("新しい球団と同じ扱い", 1000, 110, RED, at=1, anim="rise"),
      ]),
    S(["阪神側は全額の免除を求めましたが、圧倒的な多数で否決。",
       "最終的には、29億円が免除されることで決着したとされています。"],
      pic(P(C.big_number, "免除の求めは", "否決", 170), 1605, BLUEF, 820, 460), move="in", els=[
          head("阪神の反論"),
          E(P(C.note, "※29億円の免除は Wikipedia ほかによる", 30), CX, 900),
          big("29億円免除で決着", 1000, 120, GOLD, at=1, anim="slam", sfx="boom"),
      ]),
    subscribe(1606, HT_END),
]
HT1 = ep15._fix_speech(HT1)


def _say(scenes, fix):
    """ショートだけの読みの指定 (check_word で「微妙」だったもの)"""
    for sc in scenes:
        out = []
        for ln in sc["lines"]:
            text, sp = ln if isinstance(ln, tuple) else (ln, ln)
            for k, v in fix.items():
                sp = sp.replace(k, v)
            out.append((text, sp) if sp != text else text)
        sc["lines"] = out
    return scenes


_say(BP2, {"会社が運営して": "会社が、うんえいして", "を抱えて": "をかかえて"})
