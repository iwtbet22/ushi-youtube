"""ナレーション音声を作る (edge-tts / ja-JP-KeitaNeural)。

台本が変わったシーンだけ作り直すよう、原稿のハッシュをファイル名にしてキャッシュする。
仮ナレーション用。本番は VOICEVOX か本人の収録に差し替える想定。
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import ssl
import subprocess
import time
from pathlib import Path

VOICE = "ja-JP-KeitaNeural"
RATE = "+0%"
CACHE = Path(__file__).resolve().parent.parent / "output" / "voice"
CA = "/root/.ccr/ca-bundle.crt"


def path_for(text: str, rate: str = RATE, pitch: str = "+0Hz") -> Path:
    key = f"{VOICE}|{rate}|{text}" if pitch == "+0Hz" else f"{VOICE}|{rate}|{pitch}|{text}"
    h = hashlib.sha1(key.encode()).hexdigest()[:12]
    return CACHE / f"{h}.wav"


async def _synth(text: str, mp3: Path, rate: str, pitch: str):
    import aiohttp
    import edge_tts

    kw = {}
    if os.path.exists(CA):  # このクラウド環境のプロキシ越しに繋ぐための設定
        kw["connector"] = aiohttp.TCPConnector(ssl=ssl.create_default_context(cafile=CA))
        kw["proxy"] = os.environ.get("HTTPS_PROXY")
    await edge_tts.Communicate(text, VOICE, rate=rate, pitch=pitch, **kw).save(str(mp3))


def ensure(text: str, rate: str = RATE, pitch: str = "+0Hz") -> Path:
    """rate / pitch は edge-tts の指定 (例 "+8%", "-4Hz")。省略すると1本目と同じ声"""
    wav = path_for(text, rate, pitch)
    if wav.exists():
        return wav
    CACHE.mkdir(parents=True, exist_ok=True)
    mp3 = wav.with_suffix(".mp3")
    for attempt in range(5):  # 通信が一時的に切れることがあるので、間をあけて再試行する
        try:
            asyncio.run(_synth(text, mp3, rate, pitch))
            if mp3.exists() and mp3.stat().st_size > 0:
                break
        except Exception:  # noqa: BLE001
            if attempt == 4:
                raise
        time.sleep(2 ** (attempt + 1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", "48000", str(wav)],
                   check=True)
    mp3.unlink()
    return wav


def duration(wav: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout)
