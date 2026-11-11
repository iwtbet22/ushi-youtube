"""読み方の点検：合成音声に渡す文を、2つの辞書で読ませて食い違う語と、確認していない固有名詞を出す。

これまでの check_kana.py は「正しい読み」を OpenJTalk の読みから作っていたので、
OpenJTalk と合成音声が同じように読み間違える語 (例：横浜関内 → よこはませきうち) は見逃していた。
ここでは別の辞書 (Sudachi) の読みと、人の目で確かめた読みの表 (script/yomi.tsv) を「正しい読み」にして比べる。

出すもの
  1. 食い違い：OpenJTalk の読みが、表 (なければ Sudachi) の読みと違う語。
     → 合成音声も読み間違えている見込みが高い。読み方の指定 (SPEECH_FIX / readings.py) で直すか、
       正しく読めていると確かめたら yomi.tsv に「ok」と書く。
  2. 未確認の固有名詞：人名・地名・組織名などで、yomi.tsv にまだない語。
     → 正しい読みを調べて yomi.tsv に足す (出典も書く)。
  どちらも 0 件になるまで、書き出しに進まない。

  python3 tools/check_yomi.py ep09
  python3 tools/check_yomi.py ep09 --all     # 確認済みの語も含めて全部出す
"""
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pyopenjtalk
from sudachipy import dictionary, tokenizer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docu"))
sys.path.insert(0, str(ROOT / "render"))
sys.path.insert(0, str(ROOT / "tools"))
import film  # noqa: E402
from check_kana import norm  # noqa: E402

TABLE = ROOT / "script" / "yomi.tsv"
KANJI = re.compile(r"[一-鿿々〆ヶ]")
SUDACHI = dictionary.Dictionary().create()  # noqa

MODE = tokenizer.Tokenizer.SplitMode.C


def load_table():
    """yomi.tsv：語<TAB>正しい読み (カタカナ)<TAB>出典・メモ。読みに ok と書くと、OpenJTalk の読みで正しいという意味"""
    t = {}
    if TABLE.exists():
        for ln in TABLE.read_text().splitlines():
            if not ln.strip() or ln.startswith("#"):
                continue
            parts = ln.split("\t")
            t[parts[0]] = parts[1] if len(parts) > 1 else "ok"
    return t


def spans_sudachi(text):
    out = []
    for m in SUDACHI.tokenize(text, MODE):
        out.append((m.begin(), m.end(), m.surface(), m.reading_form(), m.part_of_speech()))
    return out


def spans_ojt(text):
    out, pos = [], 0
    for f in pyopenjtalk.run_frontend(text):
        s = f["string"]
        i = text.find(s, pos)
        if i < 0:  # 数字や記号は書き換えられて見つからないことがある
            continue
        out.append((i, i + len(s), s, f["read"]))
        pos = i + len(s)
    return out


def ojt_reading(oj, b, e):
    """b〜e の範囲をちょうど覆う OpenJTalk の語の読み。区切りが合わなければ、はみ出す分も含めて返す"""
    sel = [x for x in oj if x[1] > b and x[0] < e]
    if not sel:
        return None, b, e
    return "".join(x[3] for x in sel), sel[0][0], sel[-1][1]


def sudachi_reading(sd, b, e, table):
    r = []
    for x in sd:
        if x[1] > b and x[0] < e:
            t = table.get(x[2])
            r.append(x[3] if t in (None, "ok") else t)
    return "".join(r)


DAKU = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")


def same(a, b):
    """長音の書き方と、語の頭の濁り (会社 カイシャ／ガイシャ) の差は同じとみなす"""
    a, b = norm(a), norm(b)
    return a == b or (a[1:] == b[1:] and a[:1].translate(DAKU) == b[:1].translate(DAKU))


def sentences(ep):
    mod = importlib.import_module(ep)
    for sc in mod.SCENES:
        for line in sc["lines"]:
            yield film._display(line), film._speech(line)


def check(ep, show_all=False):
    table = load_table()
    mism, unknown, seen = [], {}, set()
    for disp, sp in sentences(ep):
        sd, oj = spans_sudachi(sp), spans_ojt(sp)
        for b, e, surf, rd, pos in sd:
            if not KANJI.search(surf) or re.search(r"[0-9０-９]", sp[max(0, b - 1):e]):
                continue  # 数字のからむ語 (億・万など) は、辞書どうしの数字の扱いの差ばかりなので見ない
            proper = pos[1] == "固有名詞"
            o, ob, oe = ojt_reading(oj, b, e)
            if proper and surf not in table:
                unknown.setdefault(surf, (rd, o or "", " ".join(pos[2:4]), disp))
            if o is None:
                continue
            want = sudachi_reading(sd, ob, oe, table)
            t = table.get(surf)
            if t == "ok":
                continue
            if not same(o, want):
                key = (surf, o, want)
                if key in seen and not show_all:
                    continue
                seen.add(key)
                mism.append((surf, sp[ob:oe], o, want, "表" if t else "Sudachi", disp))
    print(f"== {ep}：食い違い {len(mism)} 件 ==")
    for surf, span, o, want, src, disp in mism:
        print(f"  {span}  合成側(OpenJTalk) {o}  ／ 正({src}) {want}\n      {disp}")
    print(f"== {ep}：未確認の固有名詞 {len(unknown)} 語 ==")
    for surf, (rd, o, kind, disp) in sorted(unknown.items(), key=lambda x: x[1][2]):
        print(f"  {surf}\tSudachi {rd}\t合成側 {o}\t{kind}\t{disp[:40]}")
    return mism, unknown


if __name__ == "__main__":
    check(sys.argv[1], "--all" in sys.argv)
