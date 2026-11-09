"""6本目で使う Wikimedia Commons の写真を取ってきて、credits.json に作者とライセンスを足す。

  python3 tools/fetch_ep06.py

ライセンスと作者は、各ファイルのページで確かめた (2026-11-06)。
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
    "ep06_shoriki_1955.jpg": ("Shoriki_Matsutaro_1955_(cropped).jpg", "読売新聞社", ["Public domain"]),
    "ep06_yomiuri_bldg.jpg": ("Yomiuri_Shimbun_Bldg.jpg", "Akonnchiroll", ["cc-by-sa-4.0"]),
    "ep06_yomiuriland_aerial.jpg": ("Yomiuri_land_aerial_shoot.jpg", "ブルーノ・プラス", ["cc-by-sa-4.0"]),
    "ep06_kawasaki_keiba.jpg": ("Kawasaki_Racecourse_Aerial_2019.jpg", GSI, ["出典明記で利用可"]),
    "ep06_funabashi_keiba.jpg": ("Funabashi_Racecourse_Aerial_view.jpg", "ブルーノ・プラス", ["cc-by-4.0"]),
    "ep06_grand_green.jpg": ("Grand_Green_Osaka.jpg", "Tokumeigakarinoaoshima", ["cc-by-sa-4.0"]),
    "ep06_takarazuka.jpg": ("Takarazuka_Grand_Theater_and_Hankyu_train.jpg", "Bubble Gum (Flickr)", ["cc-by-2.0"]),
    "ep06_koshien_1928.png": ("甲子園グラウンド_(『大大阪画報』大大阪画報社_昭和3年).png", "大大阪画報社", ["Public domain"]),
    "ep06_koshien_aerial.jpg": ("Koshien_Stadium_aerial_photograph_2021.jpg", GSI, ["cc-by-4.0"]),
    "ep06_basegate.jpg": ("Basegate_Kannai.jpg", "Akonnchiroll", ["cc-by-sa-4.0"]),
    "ep06_basegate_live.jpg": ("BASEGATE_Yokohama_Kannai_-_THE_LIVE_01.jpg", "NEO-NEED", ["cc-by-4.0"]),
    "ep06_bauer.jpg": ("横浜DeNAベイスターズ所属のバウアー20230422trevorbauer.jpg", "Moonlight Shado", ["cc-by-sa-4.0"]),
    "ep06_chunichi_bldg.jpg": ("Chunichi_Building_from_Hisaya-odori_Park_-_1.jpg", "Kyu3a", ["cc-by-sa-4.0"]),
    "ep06_chunichi_hq.jpg": ("Chunichi_Shimbun_Nagoya_Head_Office_-_1.jpg", "KKPCW（Kyu3）", ["cc-by-sa-4.0"]),
    "ep06_news_trucks.jpg": ("中日新聞_and_毎日新聞_trucks.jpg", "Pvcba", ["CC0"]),
    "ep06_yakult1000.jpg": ("Yakult_1000_-_1.jpg", "KKPCW（Kyu3）", ["cc-by-sa-4.0"]),
    "ep06_yakult_mexico.jpg": ("Yakult_Mexico.jpg", "RottenKitten", ["cc-by-sa-4.0"]),
    "ep06_yakult_china.jpg": ("YAKULT_PRODUCTS_IN_CHINA.jpg", "Dinkun Chen", ["cc-by-sa-4.0"]),
    "ep06_yakult_bike.jpg": ("Yakult_delivery_bicycle.jpg", "三上勝生 (elmikamino)", ["CC BY-SA 2.1 JP"]),
    "ep06_mazda_facade.jpg": ("MAZDA_Zoom-Zoom_Stadium_Hiroshima_facade.jpg", "HKT3012", ["cc-by-sa-3.0"]),
    "ep06_mazda_aerial.jpg": ("MAZDA_Zoom-Zoom_Stadium_Hiroshima_aerial_photograph_2023.jpg", GSI, ["cc-by-4.0"]),
    "ep06_hiroshima_1962.jpg": ("Hiroshima_Municipal_Stadium_aerial_photograph_1962.jpg", GSI, ["cc-by-4.0"]),
    # ユーザーが Google ドライブに集めてくれた写真 (2026-11-09。作者とライセンスは Commons の表示どおり)
    "ep06_ntv.jpg": ("Nippon_TV_Tower.jpg", "Akonnchiroll", ["cc-by-sa-4.0"]),
    "ep06_gtown.jpg": ("Yomiuri_Giants_stadium.jpg", "ブルーノ・プラス", ["cc-by-4.0"]),
    "ep06_tsukiji.jpg": ("Former_Tsukiji_Fish_Market,_Hamarikyu_Garden_and_Kachidoki_Sep_29,_2019.jpg", "Zengame", ["cc-by-2.0"]),
    "ep06_tokyo_shimbun.jpg": ("2_Chome_Kitazawa,_Setagaya-ku,_Tōkyō-to_155-0031,_Japan_-_panoramio_(139).jpg", "運転太郎", ["CC BY 3.0"]),
    "ep06_vantelin.jpg": ("Nagoya_Dome_-_3.jpg", "KKPCW（Kyu3）", ["cc-by-sa-4.0"]),
    "ep06_yakult_hq.jpg": ("Yakult_Honsha_Building_(2018-01-01).jpg", "Lombroso", ["cc-by-sa-4.0"]),
    "ep06_ginkgo.jpg": ("Avenue_of_ginkgo_trees,_Meiji_Shrine_Outer_Garden_20201129.jpg", "Suicasmo", ["cc-by-sa-4.0"]),
    "ep06_osuna.jpg": ("YS-Jose_Osuna20220812.jpg", "TSUBAME98", ["cc-by-sa-4.0"]),
    "ep06_santana.jpg": ("YS-Domingo_Santana20211010.jpg", "TSUBAME98", ["cc-by-sa-4.0"]),
    "ep06_genbaku.jpg": ("Genbaku_Dome04-r.JPG", "Oilstreet", ["cc-by-sa-3.0"]),
    "ep06_mazda_build.jpg": ("新広島市民球場・１階～６階筐体工事.jpg", "HKT3012", ["cc-by-sa-3.0"]),
    "ep06_austin.jpg": ("タイラー・オースティン.png", "日産・スカイライン", ["cc-by-4.0"]),
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
