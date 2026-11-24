"""16本目（ソフトバンク編）で使う Wikimedia Commons の写真を取ってきて、credits.json に作者とライセンスを足す。

  python3 tools/fetch_ep16.py

作者とライセンスは、取るときに Commons の API (extmetadata) から読み、credits.json に書く。
CC BY / CC BY-SA / CC0 / パブリックドメイン以外（NC・ND）は取らない。1枚ごとに間をあける。
"""
import json
import re
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "ep02" / "img"
FILES = {
    "ep16_dome_flickr.jpg": "Mizuho PayPay Dome FUKUOKA (55564766882).jpg",
    "ep16_dome_west.jpg": "Fukuoka Dome from west side.JPG",
    "ep16_hawkstown.jpg": "View of Fukuoka Dome and Hilton Fukuoka Sea Hawk Hotel.JPG",
    "ep16_momochi.jpg": "Fukuoka Seaside Momochi Aerial Shoot.jpg",
    "ep16_ezo.jpg": "E-zo fukuoka.jpg",
    "ep16_chikugo.jpg": "HAWKS Baseball Park Chikugo.jpg",
    "ep16_chikugo_air.jpg": "HAWKS Baseball Park Chikugo aerial photograph 2021.jpg",
    "ep16_chikugo2.jpg": "HAWKS Baseball Park Chikugo02.jpg",
    "ep16_senga2023.jpg": "Kodai Senga pitching, March 27, 2023 - Sequence 1 - 06.jpg",
    "ep16_shuto.jpg": "周東佑京 cropped from 202309241745 DSCN4571.jpg",
    "ep16_son.jpg": "Masayoshi Son (孫正義) on July 11, 2008.jpg",
    "ep16_oh.jpg": "Sadaharu Oh 2026.jpg",
    "ep16_parade2011.jpg": "Softbank Hawks 2011 Victory Parade.jpg",
}
UA = "EducationalVideoImageFetcher/1.0 (credits kept per file)"
OK = re.compile(r"^(CC BY(-SA)? [0-9.]+|CC0|Public domain)", re.I)


def get(url):
    for wait in (0, 60, 180, 400):
        time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            print("wait", e.code, flush=True)
    raise SystemExit("gave up")


def main():
    cj = IMG / "credits.json"
    credits = json.loads(cj.read_text())
    for local, name in FILES.items():
        if (IMG / local).exists() and local in credits:
            continue  # 取り込み済み（Commons に余計な問い合わせをしない）
        api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(
            action="query", prop="imageinfo", iiprop="extmetadata", format="json", titles="File:" + name))
        m = next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]["extmetadata"]
        lic = m.get("LicenseShortName", {}).get("value", "")
        artist = re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
        if not OK.match(lic):
            print("SKIP", local, lic, flush=True)
            continue
        out = IMG / local
        if not out.exists():
            time.sleep(8)
            out.write_bytes(get("https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=1920"))
        credits[local] = {"file": local, "author": artist, "license": [lic],
                          "url": "https://commons.wikimedia.org/wiki/File:" + name.replace(" ", "_")}
        cj.write_text(json.dumps(credits, ensure_ascii=False, indent=1))
        print("ok", local, artist, lic, flush=True)
        time.sleep(10)


if __name__ == "__main__":
    main()
