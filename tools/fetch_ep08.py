"""8本目で使う Wikimedia Commons の写真を取ってきて、credits.json に作者とライセンスを足す。

  python3 tools/fetch_ep08.py

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
    "ep08_sutter_aerial.jpg": ("Aerial_view_of_Sutter_Health_Park_in_2024.jpg", "Quintin Soloviev", ["cc-by-4.0"]),
    "ep08_sacramento_game.jpg": ("Angels_Game_in_Sacramento_(54532351300).jpg", "slgckgc (Flickr)", ["cc-by-2.0"]),
    "ep08_vegas.jpg": ("Las_Vegas_Ballpark_front.jpg", "Raul Jusinto", ["cc-by-sa-2.0"]),
    "ep08_midland.jpg": ("Jefry_Marte_Midland_RockHounds_2014.jpg", "EricEnfermero", ["cc-by-sa-4.0"]),
    "ep08_lansing.jpg": ("Jackson_Field_-_Lansing_Lugnuts_Baseball_Team_-_Lansing_-_Michigan.jpg", "Tony Webster", ["cc-by-2.0"]),
    "ep08_lansing_game.jpg": ("Lawrence_Butler_(30).jpg", "Joel Dinda", ["cc-by-2.0"]),
    "ep08_lansing_empty.jpg": ("Cooley_Law_School_Stadium_not_full_(6906758084).jpg", "Joel Dinda", ["cc-by-2.0"]),
    "ep08_stockton_night.jpg": ("Banner_Island_Ballpark_Night_2014.jpg", "TaurusEmerald", ["cc-by-sa-4.0"]),
    "ep08_stockton_dusk.jpg": ("Stockton_Ports_gamedusk2.jpg", "NativeForeigner", ["cc-by-sa-3.0"]),
    "ep08_stockton_sunset.jpg": ("Stockton_ports_sunset.jpg", "NativeForeigner", ["cc-by-sa-3.0"]),
    "ep08_hohokam.jpg": ("Hohokam955.JPG", "2candle", ["cc-by-sa-3.0"]),
    "ep08_katoh_trenton.jpg": ("Gosuke_Katoh_July_23,_2019_(48362873187)_(cropped).jpg", "Ian D'Andrea (Flickr)", ["cc-by-sa-2.0"]),
    "ep08_katoh_fighters.jpg": ("Gosuke_Kato_20231102.jpg", "山村みきお", ["cc-by-sa-3.0"]),
    "ep08_ohtani_pitch.jpg": ("Shohei_Ohtani_vs_Texas_Rangers_(September_3,_2021).jpg", "Vera26", ["cc-by-sa-4.0"]),
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
