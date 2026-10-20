"""本人の録音を台本の文ごとに切り分けて、合成音声の代わりに使えるようにする。

  python3 tools/align_recording.py 録音.wav 開始文番号
    - 録音の文字起こし (faster-whisper) と台本を突き合わせ、録音を文ごとの wav に切る
    - 音量をそろえる (ハイパス・コンプレッサー・-16 LUFS・リミッター)
    - output/voice_rec/ に保存し、output/voice_rec/map.json に「台本の文 → wav」を追記する
  engine.py は map.json にある文は録音を、ない文は合成音声を使う。
"""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "explainer"))
from episode import SCENES  # noqa: E402

OUT = ROOT / "output" / "voice_rec"


def norm(s):
    return re.sub(r"[、。？！「」（）・\s,.?!]", "", s)


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def silences(wav, noise="-45dB", d=0.25):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", f"silencedetect=noise={noise}:d={d}",
                        "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    return list(zip(st, en))


def main():
    src, first = Path(sys.argv[1]), int(sys.argv[2])
    lines = [(l[0] if isinstance(l, tuple) else l) for sc in SCENES for l in sc["lines"]]
    OUT.mkdir(parents=True, exist_ok=True)

    # 1) 音量をそろえたモノラル 48kHz を作る
    clean = OUT / f"{src.stem}_clean.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "48000", "-af",
                    "highpass=f=80,acompressor=threshold=-24dB:ratio=3:attack=5:release=120,"
                    "loudnorm=I=-16:TP=-1.5:LRA=7,alimiter=limit=0.84", str(clean)], check=True)

    # 2) 文字起こし
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(str(clean), language="ja", beam_size=5, word_timestamps=True)
    segs = list(segs)
    words = [(w.start, w.end, w.word) for sg in segs for w in sg.words]
    segs = [(sg.start, sg.end, sg.text) for sg in segs]

    # 3) 文の数を文字起こしとの照合で決める (録音が台本のどこまでか)
    full = "".join(t for _, _, t in segs)
    best_n, best_v = 1, -1.0
    for n in range(1, len(lines) - first + 1):
        v = sim(full, "".join(lines[first:first + n]))
        if v > best_v:
            best_n, best_v = n, v
    n = best_n
    sent = lines[first:first + n]

    # 4) 台本の文字と、文字起こしの単語の時刻を対応づけて、各文の境目のおおよその時刻を出す
    #    → その近くの無音 (いちばん長いもの) で切る
    sil = [(s_, e_) for s_, e_ in silences(clean) if e_ - s_ >= 0.2]
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(clean)], capture_output=True, text=True).stdout)
    head = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    tail = sil[-1][0] if sil and sil[-1][1] > total - 0.05 else total
    asr_chars, asr_time = [], []
    for w0, w1, wt in words:
        c = norm(wt)
        for q, ch in enumerate(c):
            asr_chars.append(ch)
            asr_time.append(w0 + (w1 - w0) * q / max(1, len(c)))
    script = "".join(norm(t) for t in sent)
    sm = difflib.SequenceMatcher(None, script, "".join(asr_chars), autojunk=False)
    pairs = [(bl.a + q, bl.b + q) for bl in sm.get_matching_blocks() for q in range(bl.size)]

    def time_at(ci):
        """台本の ci 文字目が読まれたおおよその時刻 (前後の対応点から補間)"""
        before = [p_ for p_ in pairs if p_[0] <= ci]
        after = [p_ for p_ in pairs if p_[0] >= ci]
        if before and after:
            (a0, b0), (a1, b1) = before[-1], after[0]
            t0, t1 = asr_time[b0], asr_time[b1]
            return t0 if a1 == a0 else t0 + (t1 - t0) * (ci - a0) / (a1 - a0)
        return asr_time[(before or after)[0][1]]

    bounds, ci = [head], 0
    for t in sent[:-1]:
        ci += len(norm(t))
        guess = time_at(ci)
        last = bounds[-1] if isinstance(bounds[-1], float) else bounds[-1][1]
        near = [(e_ - s_, s_, e_) for s_, e_ in sil if s_ > last and abs((s_ + e_) / 2 - guess) < 2.0]
        if near:
            _, s_, e_ = max(near)
            bounds.append((s_, e_))
        else:
            bounds.append((guess, guess))
    bounds.append(tail)

    mapping_path = OUT / "map.json"
    mapping = json.loads(mapping_path.read_text()) if mapping_path.exists() else {}
    report = []
    for idx in range(n):
        a = bounds[idx] if idx == 0 else bounds[idx][1]
        b = bounds[idx + 1] if idx == n - 1 else bounds[idx + 1][0]
        a, b = max(0.0, a - 0.06), b + 0.10
        text = sent[idx]
        out = OUT / f"{src.stem}_{first + idx:03d}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(clean),
                        "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse", str(out)], check=True)
        heard = "".join(x.text for x in m.transcribe(str(out), language="ja", beam_size=5)[0])
        mapping[text] = str(out.relative_to(ROOT))
        report.append((first + idx, round(a, 2), round(b, 2), round(sim(heard, text), 2), text[:24], heard[:30]))
    score = sum(r[3] for r in report) / n
    mapping_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=1))
    print(f"matched {n} sentences, mean similarity {score:.2f}")
    for r in report:
        print(r)


if __name__ == "__main__":
    main()
