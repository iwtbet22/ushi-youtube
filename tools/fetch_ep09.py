"""9本目で使う Wikimedia Commons の写真を取ってきて、credits.json に作者とライセンスを足す。

  python3 tools/fetch_ep09.py

ライセンスと作者は、各ファイルのページで確かめた (2026-11-09)。
Commons の負担にならないよう、1枚ごとに間をあける。
"""
import json
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "ep02" / "img"
GSI = "国土地理院（国土交通省）"
FILES = {
    # 保存名: (Commons のファイル名, 作者, ライセンス)
    "ep09_yamauchi.jpg": ("Yamauchi_Kazuhiro.jpg", "朝日新聞社", ["Public domain"]),
    "ep09_koyama.jpg": ("Masaaki_Koyama_1959_Scan10016.jpg", "博友社", ["Public domain"]),
    "ep09_enatsu.jpg": ("Yutaka_ENATSU_CARP-Legend_20220321.jpg", "neko kabachi", ["cc-by-sa-2.0"]),
    "ep09_emoto.jpg": ("Takenori_EMOTO_20201003.jpg", "高木豊", ["cc-by-3.0"]),
    "ep09_harimoto1959.jpg": ("Isao_Harimoto_1959_Scan10007.jpg", "博友社", ["Public domain"]),
    "ep09_harimoto2024.jpg": ("張本勲_202405281751_DSCN6781.jpg", "ウィ貴公子", ["cc-by-sa-4.0"]),
    "ep09_tabuchi.jpg": ("RE-Koichi-Tabuchi20110309.jpg", "Cake6", ["cc-by-sa-4.0"]),
    "ep09_egawa.jpg": ("Suguru_Egawa_20180615.jpg", "高木豊", ["cc-by-3.0"]),
    "ep09_akiyama.jpg": ("Akiyama_Kouji.jpg", "Wiki591801", ["cc-by-3.0"]),
    "ep09_sasaki.jpg": ("NTT西日本・佐々木誠監督_(14187271467)_(cropped).jpg", "boomer-44 (Flickr)", ["cc-by-2.0"]),
    "ep09_kokubo2010.jpg": ("Hiroki_Kokubo_2010.jpg", "Gaffky", ["Public domain"]),
    "ep09_kokubo2012.jpg": ("HAWKS9-KOKUBO.jpg", "Gaffky", ["Public domain"]),
    "ep09_shimizu.jpg": ("Naoyuki_Shimizu_on_May_5,_2010.jpg", "ぽ", ["cc-by-sa-3.0"]),
    "ep09_saburo2010.jpg": ("Saburo_Ohmura_2010.jpg", "taka", ["cc-by-sa-3.0"]),
    "ep09_saburo2012.jpg": ("2011marines_saburo_3.jpg", "Nsgok", ["cc-by-sa-3.0"]),
    "ep09_ota.jpg": ("打撃をする大田泰示.jpg", "Junglnote1", ["cc-by-sa-4.0"]),
    "ep09_nakata.jpg": ("Giants_Sho_Nakata_20220311.jpg", "Orixbaseballclub", ["cc-by-sa-4.0"]),
    "ep09_kai.jpg": ("Takuya_Kai.jpg", "Hotta Akahane", ["cc0"]),
    "ep09_kai_hr.jpg": ("甲斐拓也_cropped_from_202309242129_DSCN5505.jpg", "ウィ貴公子", ["cc-by-sa-4.0"]),
    "ep09_haneda.jpg": ("Tokyo-International-Airport_Satellite.jpg", "MaedaAkihiko", ["cc-by-sa-4.0"]),
}

UA = "ushi-youtube-video/1.0 (credits kept per file)"


def main():
    cj = IMG / "credits.json"
    credits = json.loads(cj.read_text())
    for local, (name, author, lic) in FILES.items():
        out = IMG / local
        if not out.exists():
            url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=1280"
            for wait in (0, 120, 300, 600):
                time.sleep(wait)
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        out.write_bytes(r.read())
                    break
                except urllib.error.HTTPError as e:
                    print("wait", local, e.code, flush=True)
            else:
                print("skip", local, flush=True)
                continue
            print("got", local, out.stat().st_size, flush=True)
            time.sleep(30)
        if not out.exists():
            continue
        credits[local] = {"file": name.replace("_", " "), "author": author, "license": lic,
                          "url": "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(name)}
    cj.write_text(json.dumps(credits, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
