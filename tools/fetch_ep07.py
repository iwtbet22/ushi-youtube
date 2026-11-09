"""7本目で使う Wikimedia Commons の写真を取ってきて、credits.json に作者とライセンスを足す。

  python3 tools/fetch_ep07.py

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
    "ep07_paypay_dome.jpg": ("Mizuho_PayPay_dome_Fukuoka_2025.jpg", "Keeteria", ["cc-by-sa-4.0"]),
    "ep07_takeshiba.jpg": ("TOKYO_PORTCITY_TAKESHIBA_OFFICE_TOWER.jpg", "Beryllium Transistor", ["cc-by-sa-4.0"]),
    "ep07_osaka_stadium_1951.jpg": ("Osaka_Stadium_1951.jpg", "作者不明（『野球場建設の研究』1951年）", ["Public domain"]),
    "ep07_nishinomiya.jpg": ("阪急西宮スタジアム.JPG", "オナガドリ", ["cc-by-sa-3.0"]),
    "ep07_schau_essen.jpg": ("Boiling_Schau_Essen,_Japanese_Brand_Sausage.jpg", "Miyuki Meinaka", ["cc-by-sa-4.0"]),
    "ep07_fvillage.jpg": ("F_Village_Le_JADE_Hokkaido_Ballpark.jpg", "掬茶", ["cc-by-sa-4.0"]),
    "ep07_sapporo_dome.jpg": ("Exterior_of_Sapporo_Dome_from_north.jpg", "掬茶", ["cc-by-sa-4.0"]),
    "ep07_kix_aerial.jpg": ("Kix_aerial_photo.jpg", "Tdk", ["cc-by-sa-3.0"]),
    "ep07_skytree_sumida.jpg": ("Tokyo_Skytree_&_Soramachi.jpg", "Kakidai", ["cc-by-sa-4.0"]),
    "ep07_kyocera_dome.jpg": ("Kyocera_Dome_Osaka,_-22_maart_2019.jpg", "thatlostdog-- (Flickr)", ["cc-by-2.0"]),
    "ep07_rakuten_hq.jpg": ("Rakuten_Crimson_House.jpg", "掬茶", ["cc-by-sa-4.0"]),
    "ep07_kioicho.jpg": ("Tokyo_Garden_Terrace_Kioicho.jpg", "Akonnchiroll", ["cc-by-sa-4.0"]),
    "ep07_seibu_laview.jpg": ("Seibu_series001_Laview.jpg", "SEMISAYAMASHI", ["cc-by-sa-4.0"]),
    "ep07_belluna_dome.jpg": ("ベルーナドーム.jpg", "Windyakin", ["cc-by-sa-4.0"]),
    "ep07_lotte_urawa.jpg": ("Lotte_factory_in_Urawa,_with_Ghana_and_雪見だいふく_signs.jpg", "Syced", ["CC0"]),
    # ユーザーが Google ドライブに集めてくれた写真 (2026-11-09)
    "ep07_takeshiba2.jpg": ("Portcity_Takeshiba.jpg", "Akonnchiroll", ["cc-by-sa-4.0"]),
    "ep07_escon2.jpg": ("エスコンフィールド北海道.jpg", "高梨慎太郎", ["cc-by-sa-4.0"]),
    "ep07_escon_roof1.jpg": ("ES_CON_FIELD_HOKKAIDO_TOWER11_02.jpg", "Endou subaru", ["CC0"]),
    "ep07_escon_roof2.jpg": ("ES_CON_FIELD_HOKKAIDO_Roof_Open_Photo_from_Left_Side.jpg", "StealthJPN", ["CC0"]),
    "ep07_nh_logo.png": ("NH_Foods_Logo.svg", "NH Foods Ltd.", ["Public domain"]),
    "ep07_orix_honmachi.jpg": ("ORIX_Honmachi_Bldg_20110328-001.jpg", "J o", ["cc-by-sa-3.0"]),
    "ep07_orix_rentacar.png": ("Orix_rent-a-car-logo.svg", "ORIX Auto Corporation", ["Public domain"]),
    "ep07_kyoto_aq.jpg": ("KYOTO_AQUARIUM.JPG", "Kirakirameister", ["cc-by-sa-3.0"]),
    "ep07_shinjuku_prince.jpg": ("新宿プリンスホテル_遠景.jpg", "松倉傑", ["CC0"]),
    "ep07_lotte_urawa2.jpg": ("ロッテ浦和工場.JPG", "ブツチチ", ["cc-by-sa-4.0"]),
    "ep07_lotte_hq.jpg": ("Walk_around_Hatsudai_-36260.jpeg", "Syced", ["CC0"]),
    "ep07_rakuten_shop.jpg": ("Rakuten_Mobile_Nansandori_Street_Shop.jpg", "Mr.ちゅらさん", ["cc-by-sa-4.0"]),
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
