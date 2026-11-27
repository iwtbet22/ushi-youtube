"""18本目（戦力外のあと、引退のあと）で使う Wikimedia Commons の写真を取ってきて、credits.json に作者とライセンスを足す。

  python3 tools/fetch_ep17.py

Commons の API が回数制限で使えないため、作者とライセンスはファイルページ（?action=raw）で確かめた値を
下の表に書き、画像は upload.wikimedia.org から取る。CC BY / CC BY-SA / CC0 以外は入れない。
"""
import hashlib
import json
import subprocess
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "ep02" / "img"
UA = "EducationalVideoImageFetcher/1.0 (credits kept per file)"
# 保存名: (Commons のファイル名, 作者, ライセンス)
FILES = {
    "ep18_arai.jpg": ("HT-Takahiro-Arai.jpg", "Cake6", "CC BY-SA 3.0"),
}


def main():
    cj = IMG / "credits.json"
    for local, (name, author, lic) in FILES.items():
        out = IMG / local
        if not out.exists():
            n = name.replace(" ", "_")
            h = hashlib.md5(n.encode()).hexdigest()
            q = urllib.parse.quote(n)
            for u in (f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/1920px-{q}",
                      f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"):
                code = subprocess.run(["curl", "-s", "-o", str(out) + ".part", "-w", "%{http_code}", "-A", UA, u],
                                      capture_output=True, text=True).stdout
                if code == "200":
                    Path(str(out) + ".part").rename(out)
                    break
                Path(str(out) + ".part").unlink(missing_ok=True)
                time.sleep(10)
            print(local, code, flush=True)
            if not out.exists():
                continue
            time.sleep(20)
        credits = json.loads(cj.read_text())
        credits[local] = {"file": local, "author": author, "license": [lic],
                          "url": "https://commons.wikimedia.org/wiki/File:" + name.replace(" ", "_")}
        cj.write_text(json.dumps(credits, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
