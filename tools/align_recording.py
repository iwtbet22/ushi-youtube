"""本人の録音を台本の文ごとに切り分けて、合成音声の代わりに使えるようにする。

  python3 tools/align_recording.py 録音.wav [--first 0] [--asr 文字起こし.json] [--extra-case-study]
                                    [--fixes 手直し.json [--fix-only]]

  1. ノイズ除去と音量調整 (ハイパス → FFTノイズ除去 → 歯擦音の軽減 → コンプレッサー → -16 LUFS → リミッター)
  2. faster-whisper で単語ごとの時刻つき文字起こし (--asr で既存の結果を再利用できる)
  3. 台本の文字と文字起こしの文字を突き合わせて、各文の境目のおおよその時刻を出し、近くの無音で切る
  4. 切った文をもう一度文字起こしして、台本とどのくらい合っているかを表示する
  5. output/voice_rec/ に文ごとの wav を保存し、map.json に「台本の文 → wav」を書く

--extra-case-study: 録音に、本編から外したケーススタディの文も含まれているときに付ける。
  突き合わせには使い、map.json には入れない。
--fixes: 自動の切り分けがずれた文を手で直す。{"文の番号": [[開始, 終了], ...] または null}
  時刻はノイズ除去後の録音での秒。区間が複数あればつなげる (言い直しを飛ばすとき)。
  null は録音で読まなかった文で、map.json には空文字を書く (engine.py は字幕も音声も出さない)。
  --fix-only を付けると、前回の切り分けはそのままで、手直しの文だけ切り直す。
engine.py は map.json にある文は録音を、ない文は合成音声を使う。
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "explainer"))
import extra_scenes as X  # noqa: E402
from episode import SCENES  # noqa: E402

OUT = ROOT / "output" / "voice_rec"
CLEAN_FILTER = ("highpass=f=80,afftdn=nr=12:nf=-50:tn=1,deesser=i=0.25,"
                "acompressor=threshold=-24dB:ratio=3:attack=5:release=120,"
                "loudnorm=I=-16:TP=-1.5:LRA=7,alimiter=limit=0.84")


def disp(line):
    return line[0] if isinstance(line, tuple) else line


def norm(s):
    return re.sub(r"[、。？！「」（）・…\s,.?!]", "", s)


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()


def silences(wav, noise="-45dB", d=0.2):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", f"silencedetect=noise={noise}:d={d}",
                        "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    return list(zip(st, en))


def script_lines(with_case_study):
    """録音されている順の台本の文。(文, 本編に使うか) のリスト"""
    out = []
    case_first = disp(X.CASE_STUDY[0]["lines"][0])
    for sc in SCENES:
        for l in sc["lines"]:
            out.append((disp(l), True))
        # ケーススタディは「交渉には期限」の場面の直後にあった
        if with_case_study and disp(sc["lines"][0]).startswith("この交渉には、期限があります"):
            out += [(disp(l), False) for cs in X.CASE_STUDY for l in cs["lines"]]
    assert not with_case_study or any(t == case_first for t, _ in out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--first", type=int, default=0, help="録音が何文目から始まるか")
    ap.add_argument("--asr", help="文字起こしの結果 (json) を再利用する")
    ap.add_argument("--extra-case-study", action="store_true")
    ap.add_argument("--fixes", help="手で直す文の区間 (json)")
    ap.add_argument("--fix-only", action="store_true", help="手直しの文だけ切り直す")
    args = ap.parse_args()
    if args.fix_only:
        apply_fixes(Path(args.src), json.loads(Path(args.fixes).read_text()))
        return

    src = Path(args.src)
    lines = script_lines(args.extra_case_study)[args.first:]
    OUT.mkdir(parents=True, exist_ok=True)

    # 1) ノイズ除去と音量調整 (モノラル 48kHz)
    clean = OUT / f"{src.stem}_clean.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "48000",
                    "-af", CLEAN_FILTER, str(clean)], check=True)

    # 2) 文字起こし (単語の時刻つき)
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    if args.asr:
        segs = json.loads(Path(args.asr).read_text())
        words = [tuple(w) for s in segs for w in s["words"]]
    else:
        res, _ = model.transcribe(str(clean), language="ja", beam_size=5, word_timestamps=True)
        words = [(w.start, w.end, w.word) for s in res for w in s.words]

    # 3) 台本の文字 ↔ 文字起こしの文字 を対応づけ、文の境目の時刻を推定して近くの無音で切る
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(clean)], capture_output=True, text=True).stdout)
    sil = [(s_, e_) for s_, e_ in silences(clean) if e_ - s_ >= 0.2]
    head = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    tail = sil[-1][0] if sil and sil[-1][1] > total - 0.05 else total
    asr_chars, asr_time = [], []
    for w0, w1, wt in words:
        c = norm(wt)
        for q, ch in enumerate(c):
            asr_chars.append(ch)
            asr_time.append(w0 + (w1 - w0) * q / max(1, len(c)))
    script = "".join(norm(t) for t, _ in lines)
    sm = difflib.SequenceMatcher(None, script, "".join(asr_chars), autojunk=False)
    pairs = [(bl.a + q, bl.b + q) for bl in sm.get_matching_blocks() for q in range(bl.size)]
    pa = [p[0] for p in pairs]
    import bisect

    def time_at(ci):
        """台本の ci 文字目が読まれたおおよその時刻 (前後の対応点から補間)"""
        i = bisect.bisect_left(pa, ci)
        if 0 < i < len(pairs):
            (a0, b0), (a1, b1) = pairs[i - 1], pairs[i]
            t0, t1 = asr_time[b0], asr_time[b1]
            return t0 if a1 == a0 else t0 + (t1 - t0) * (ci - a0) / (a1 - a0)
        return asr_time[pairs[min(i, len(pairs) - 1)][1]]

    # 録音がどこまで続いているか (最後に対応がとれた台本の文字)
    last_char = pairs[-1][0] if pairs else 0
    n, acc = 0, 0
    for t, _ in lines:
        if acc >= last_char - 2:
            break
        acc += len(norm(t))
        n += 1
    lines = lines[:n]

    bounds, ci = [head], 0
    for t, _ in lines[:-1]:
        ci += len(norm(t))
        guess = time_at(ci)
        last = bounds[-1] if isinstance(bounds[-1], float) else bounds[-1][1]
        # 推定位置に近い無音ほど良く、長い無音 (文の区切りらしい) ほど良い
        near = [(min(e_ - s_, 1.5) - 0.6 * abs((s_ + e_) / 2 - guess), s_, e_)
                for s_, e_ in sil if s_ > last + 0.3 and abs((s_ + e_) / 2 - guess) < 2.5]
        if near:
            _, s_, e_ = max(near)
            bounds.append((s_, e_))
        else:
            g = max(guess, last + 0.3)  # 近くに無音がないときも、前の切れ目より後ろにする
            bounds.append((g, g))
    bounds.append(tail)

    # 4) 切り出して確認
    mapping = {}
    report = []
    for idx, (text, use) in enumerate(lines):
        a = bounds[idx] if idx == 0 else bounds[idx][1]
        b = bounds[idx + 1] if idx == len(lines) - 1 else bounds[idx + 1][0]
        a, b = max(0.0, a - 0.06), b + 0.10
        if b < a + 0.3:
            b = a + 0.3
        out = OUT / f"{src.stem}_{args.first + idx:03d}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(clean),
                        "-af", "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse", str(out)], check=True)
        heard = "".join(x.text for x in model.transcribe(str(out), language="ja", beam_size=5)[0])
        if use:
            mapping[text] = str(out.relative_to(ROOT))
        report.append({"no": args.first + idx, "start": round(a, 2), "end": round(b, 2),
                       "sim": round(sim(heard, text), 2), "used": use, "script": text, "heard": heard})
        print(f"{args.first + idx:3d} {a:8.2f}-{b:8.2f} {sim(heard, text):.2f} {'  ' if use else '除外'} "
              f"{text[:22]} | {heard[:26]}", flush=True)

    (OUT / "map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1))
    (OUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))
    print(f"aligned {len(lines)} sentences (used {len(mapping)}), "
          f"mean similarity {sum(r['sim'] for r in report) / len(report):.2f}")
    if args.fixes:
        apply_fixes(src, json.loads(Path(args.fixes).read_text()))


def apply_fixes(src, fixes):
    """report.json の文番号ごとに、指定の区間で切り直して map.json と report.json を更新する"""
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    clean = OUT / f"{src.stem}_clean.wav"
    mapping = json.loads((OUT / "map.json").read_text())
    report = {r["no"]: r for r in json.loads((OUT / "report.json").read_text())}
    for no, spans in fixes.items():
        r = report[int(no)]
        if spans is None:
            if r["used"]:
                mapping[r["script"]] = ""
            r.update(start=None, end=None, sim=None, heard="(読まなかった文)")
            print(f"{int(no):3d} 読まなかった文 {r['script'][:22]}")
            continue
        out = OUT / f"{src.stem}_{int(no):03d}.wav"
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for a, b in spans:
            cmd += ["-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(clean)]
        # 区間ごとに端を短くフェードしてからつなぐ
        fade = "afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse"
        graph = ";".join(f"[{i}:a]{fade}[p{i}]" for i in range(len(spans)))
        graph += ";" + "".join(f"[p{i}]" for i in range(len(spans))) + f"concat=n={len(spans)}:v=0:a=1[o]"
        subprocess.run(cmd + ["-filter_complex", graph, "-map", "[o]", str(out)], check=True)
        heard = "".join(x.text for x in model.transcribe(str(out), language="ja", beam_size=5)[0])
        if r["used"]:
            mapping[r["script"]] = str(out.relative_to(ROOT))
        r.update(start=spans[0][0], end=spans[-1][1], sim=round(sim(heard, r["script"]), 2), heard=heard)
        print(f"{int(no):3d} {r['sim']:.2f} {r['script'][:22]} | {heard[:26]}", flush=True)
    (OUT / "map.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1))
    (OUT / "report.json").write_text(json.dumps(list(report.values()), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
