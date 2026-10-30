"""台本の全文を合成音声で読ませ、文字起こしして台本と比べる (読み間違い・聞き取りにくい文を探す)。

両方をひらがなに直して比べるので、漢字の書き方の違いでは引っかからない。
似ている度合いが低い文を、低い順に出す。

  python3 tools/check_speech.py script/ep03_narration.txt
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

import pykakasi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docu"))
sys.path.insert(0, str(ROOT / "render"))
import film  # noqa: E402
import readings  # noqa: E402
import tts  # noqa: E402

KK = pykakasi.kakasi()


def hira(s):
    s = re.sub(r"[、。？！「」（）・…\s,.?!]", "", s)
    return "".join(x["hira"] for x in KK.convert(s))


def lines(path):
    t = Path(path).read_text().split("【オープニング】", 1)[1]
    return [l.strip() for l in t.split("\n") if l.strip() and not l.startswith("【")]


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    out = []
    for i, line in enumerate(lines(sys.argv[1])):
        wav = tts.ensure(readings.speech(line), **film.VOICE)
        heard = "".join(s.text for s in model.transcribe(str(wav), language="ja", beam_size=5)[0])
        r = difflib.SequenceMatcher(None, hira(line), hira(heard), autojunk=False).ratio()
        out.append((r, i, line, heard))
        print(f"{r:.2f} {i:3d} {line[:30]} | {heard[:30]}", flush=True)
    print("\n--- 低い順 ---")
    for r, i, line, heard in sorted(out)[:40]:
        print(f"{r:.2f} {i:3d}\n  台本: {line}\n  聞取: {heard}")


if __name__ == "__main__":
    main()
