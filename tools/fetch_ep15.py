"""15本目（阪神編）で使う Wikimedia Commons の写真を取ってきて、credits.json に作者とライセンスを足す。

  python3 tools/fetch_ep15.py

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
    "ep15_hanshin_train.jpg": "Hanshin 5700 series 5701F (49904326192).jpg",
    "ep15_hanshin_train2.jpg": "Hanshin 5700 amagasaki.jpg",
    "ep15_hankyu_train.jpg": "Hankyu 1000F at Juso.jpg",
    "ep15_hankyu_umeda.jpg": "Hankyu Osaka Umeda Station 20200607.jpg",
    "ep15_hanshin_umeda.jpg": "Hanshin Umeda Main Store on 6th November 2023.jpg",
    "ep15_amagasaki_stadium.jpg": "日鉄鋼板SGLスタジアム尼崎内の様子 (2025年3月14日).jpg",
    "ep15_dotonbori.jpg": "Dotonbori, Osaka, at night, November 2016.jpg",
    "ep15_koshien_station.jpg": "Hanshin Koshien Station East Gate.jpg",
    "ep15_koshien_ginsan.jpg": "Koshien Stadium Ginsan and Liner Vision.jpg",
    "ep15_alps.jpg": "Chiben-w alps.jpg",
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
