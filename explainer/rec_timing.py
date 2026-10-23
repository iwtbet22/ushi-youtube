"""本人の録音について、字幕の各ページを読み始める時刻を求める。

字幕を文字数の比で切り替えると、間をあけて読んだところや早口のところで声とずれる。
そこで各録音を faster-whisper で文字起こしして文字ごとの時刻を出し、台本の文字と突き合わせて、
ページの最初の文字が読まれる時刻を使う。文字起こしは output/voice_rec/prep/timing.json にキャッシュする。
"""
from __future__ import annotations

import bisect
import difflib
import json
import re
from pathlib import Path

CACHE_NAME = "timing.json"


def norm(s):
    return re.sub(r"[、。？！「」（）・…\s,.?!]", "", s)


def _cache_path(wavs):
    return Path(wavs[0]).parent / CACHE_NAME


def ensure(wavs):
    """まだ文字起こししていない (または作り直された) 録音を文字起こしして、キャッシュに足す"""
    wavs = [Path(w) for w in wavs]
    if not wavs:
        return
    path = _cache_path(wavs)
    cache = json.loads(path.read_text()) if path.exists() else {}
    todo = [w for w in wavs if cache.get(w.name, {}).get("mtime") != w.stat().st_mtime]
    if not todo:
        return
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    for i, w in enumerate(todo):
        segs, _ = model.transcribe(str(w), language="ja", beam_size=5, word_timestamps=True)
        chars = []
        for s in segs:
            for wd in s.words:
                c = norm(wd.word)
                chars += [[round(wd.start + (wd.end - wd.start) * q / len(c), 3), ch] for q, ch in enumerate(c)]
        cache[w.name] = {"mtime": w.stat().st_mtime, "chars": chars}
        if i % 20 == 19:
            path.write_text(json.dumps(cache, ensure_ascii=False))
    path.write_text(json.dumps(cache, ensure_ascii=False))


def page_starts(wav, pages):
    """各ページを読み始める時刻 (録音の頭からの秒)。突き合わせられないときは None"""
    wav = Path(wav)
    path = _cache_path([wav])
    if not path.exists():
        return None
    entry = json.loads(path.read_text()).get(wav.name)
    if not entry or not entry["chars"]:
        return None
    times = [t for t, _ in entry["chars"]]
    asr = "".join(c for _, c in entry["chars"])
    script = "".join(norm(p) for p in pages)
    sm = difflib.SequenceMatcher(None, script, asr, autojunk=False)
    pairs = [(b.a + q, b.b + q) for b in sm.get_matching_blocks() for q in range(b.size)]
    if len(pairs) < len(script) * 0.4:
        return None
    pa = [a for a, _ in pairs]

    def time_at(ci):
        i = bisect.bisect_left(pa, ci)
        if i < len(pairs) and pa[i] == ci:
            return times[pairs[i][1]]
        if 0 < i < len(pairs):
            (a0, b0), (a1, b1) = pairs[i - 1], pairs[i]
            return times[b0] + (times[b1] - times[b0]) * (ci - a0) / (a1 - a0)
        return times[pairs[min(i, len(pairs) - 1)][1]]

    out, ci = [], 0
    for p in pages:
        out.append(0.0 if ci == 0 else time_at(ci))
        ci += len(norm(p))
    # 前のページより後ろになるようにそろえる
    for k in range(1, len(out)):
        out[k] = max(out[k], out[k - 1] + 0.4)
    return out
