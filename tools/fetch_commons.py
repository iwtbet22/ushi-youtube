"""Wikimedia Commons の画像を、ライセンスと作者の情報つきで取ってくる。

  python3 tools/fetch_commons.py "File名.jpg" [...] [--width 1920]

assets/ep02/img/ に画像を保存し、credits.json に「ファイル名 → 作者・ライセンス・元ページ」を書く。
動画の概要欄のクレジットは credits.json から作る。
Wikimedia は短い間隔で叩くと断られるので、1件ごとに間をあけ、断られたら待ってやり直す。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "ep02" / "img"
UA = "UshiYoutubeImageFetcher/0.2 (https://github.com/iwtbet22/ushi-youtube; educational video)"


def get(url, binary=False, tries=8):
    for k in range(tries):
        r = subprocess.run(["curl", "-sSL", "-A", UA, url], capture_output=True)
        body = r.stdout
        bad = r.returncode != 0 or b"Wikimedia Error" in body[:2000] or b"too many requests" in body[:2000]
        if not bad and body:
            return body if binary else body.decode("utf-8", "replace")
        time.sleep(30 * (k + 1))  # 断られたら長めに待つ (同じ IP からの連続アクセスを嫌うため)
    raise RuntimeError(f"failed: {url}")


def license_of(raw):
    lic = re.findall(r"\{\{\s*(?:self2?\|)?((?:cc-[\w.,-]+|GFDL|PD-[\w-]+|cc-zero)[^}|]*)", raw, re.I)
    author = re.search(r"\|\s*author\s*=\s*(.+)", raw, re.I)
    a = author.group(1).strip() if author else ""
    a = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", a)  # [[User:x|x]] → x
    a = re.sub(r"\{\{lang\|\w+\|([^}]*)\}\}", r"\1", a)  # {{lang|ja|x}} → x
    a = re.sub(r"\{\{[^}]*\}\}", "", a).strip()
    return a, sorted({l.strip() for l in lic})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--width", type=int, default=1280)  # 標準のサムネイル幅 (それ以外は断られやすい)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cred_path = OUT / "credits.json"
    credits = json.loads(cred_path.read_text()) if cred_path.exists() else {}
    failed = []
    for name in args.files:
        name = name.replace(" ", "_")
        q = urllib.parse.quote(name)
        local = re.sub(r"[^\w.-]", "_", name)
        if (OUT / local).exists() and local in credits:
            continue
        try:
            raw = get(f"https://commons.wikimedia.org/w/index.php?title=File:{q}&action=raw")
            author, lic = license_of(raw)
            img = get(f"https://commons.wikimedia.org/wiki/Special:FilePath/{q}?width={args.width}", binary=True)
        except RuntimeError as e:
            print("skip", name, e, flush=True)
            failed.append(name)
            continue
        (OUT / local).write_bytes(img)
        credits[local] = {"file": name, "author": author, "license": lic,
                          "url": f"https://commons.wikimedia.org/wiki/File:{q}"}
        cred_path.write_text(json.dumps(credits, ensure_ascii=False, indent=1))
        print(f"{local}  {author}  {lic}", flush=True)
        time.sleep(10)
    if failed:
        print("failed:", " ".join(failed))


if __name__ == "__main__":
    main()
