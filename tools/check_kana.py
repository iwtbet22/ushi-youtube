"""合成音声が実際にどう読んだかを、ひらがなで聞き取って台本の正しい読みと比べる。

check_speech.py は文字起こしが漢字で返るので、読み間違えても漢字に直されて見逃していた。
こちらはひらがなだけを出す音声認識 (wav2vec2) を使うので、読みの違いがそのまま出る。
正しい読みは OpenJTalk の読みに、読み方の指定 (EXPECT) を上書きして作る。

  python3 tools/check_kana.py ep03            # 全文
  python3 tools/check_kana.py ep03 0 40       # 0〜39文目だけ
"""
from __future__ import annotations

import difflib
import importlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pyopenjtalk

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docu"))
sys.path.insert(0, str(ROOT / "render"))
import film  # noqa: E402
import tts  # noqa: E402

MODEL = "vumichien/wav2vec2-large-xlsr-japanese-hiragana"

# OpenJTalk が間違える語の、正しい読み (カタカナ、発音どおり)
EXPECT = {}


def kata(s):
    return "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)


VOW = {}
for row, v in [("アカサタナハマヤラワガザダバパァャ", "ア"), ("イキシチニヒミリギジヂビピィ", "イ"),
               ("ウクスツヌフムユルグズヅブプゥュ", "ウ"), ("エケセテネヘメレゲゼデベペェ", "エ"),
               ("オコソトノホモヨロヲゴゾドボポォョ", "オ")]:
    for c in row:
        VOW[c] = v


def norm(s):
    """長音・助詞・小さい字などの書き方の差をなくして、音として比べられる形にする"""
    s = kata(s)
    s = re.sub(r"[^ァ-ヴー]", "", s)
    # 聞き取り側は助詞の「は」「へ」を字のまま返すので、両方そろえる
    s = s.translate(str.maketrans("ヲヅヂヮハヘ", "オズジワワエ"))
    out = []
    for c in s:
        if c == "ー" and out:
            c = VOW.get(out[-1], "")
        out.append(c)
    s = "".join(out)
    # エイ→エエ、オウ→オオ のように伸ばす音はどちらでも同じに聞こえる
    s = re.sub(r"(?<=[エケセテネヘメレゲゼデベペ])イ", "エ", s)
    s = re.sub(r"(?<=[オコソトノホモヨロゴゾドボポョ])ウ", "オ", s)
    return s


def expected(text):
    for k in sorted(EXPECT, key=len, reverse=True):
        text = text.replace(k, EXPECT[k])
    return pyopenjtalk.g2p(text, kana=True)


class Ear:
    def __init__(self):
        import torch
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
        self.torch = torch
        self.proc = Wav2Vec2Processor.from_pretrained(MODEL)
        self.model = Wav2Vec2ForCTC.from_pretrained(MODEL).eval()

    def __call__(self, wav):
        import soundfile as sf
        import librosa
        a, sr = sf.read(str(wav))
        a = librosa.resample(a.astype(np.float32), orig_sr=sr, target_sr=16000)
        x = self.proc(a, sampling_rate=16000, return_tensors="pt").input_values
        with self.torch.no_grad():
            ids = self.model(x).logits.argmax(-1)
        return self.proc.batch_decode(ids)[0]


def sentences(ep):
    mod = importlib.import_module(ep)
    out = []
    for sc in mod.SCENES:
        for line in sc["lines"]:
            out.append((film._display(line), film._speech(line)))
    return out


def diffs(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    res = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            res.append(f"{a[max(0, i1 - 3):i2 + 3]} → {b[max(0, j1 - 3):j2 + 3]}")
    return sm.ratio(), res


def main():
    ep = sys.argv[1]
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
    ear = Ear()
    rows = []
    for i, (disp, sp) in enumerate(sentences(ep)):
        if not lo <= i < hi:
            continue
        wav = tts.ensure(sp, **film.VOICE)
        exp, heard = expected(disp), ear(wav)
        r, d = diffs(norm(exp), norm(heard))
        rows.append({"i": i, "text": disp, "speech": sp, "expect": exp, "heard": heard, "ratio": r, "diff": d})
        print(f"{r:.2f} {i:3d} {disp}\n     正: {exp}\n     聞: {kata(heard)}\n     差: {' / '.join(d)}", flush=True)
    (ROOT / "output" / f"kana_{ep}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
