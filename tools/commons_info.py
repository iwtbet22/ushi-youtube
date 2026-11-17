"""Wikimedia Commons の検索と、写真のライセンス・大きさの確認。
使い方: python3 tools/commons_info.py search "語" ...  /  python3 tools/commons_info.py info File名 ...
"""
import json,sys,subprocess,time,urllib.parse
UA="EducationalVideoImageFetcher/1.0 (credits kept per file)"
def api(params):
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
    for k in range(5):
        r=subprocess.run(["curl","-sS","-A",UA,url],capture_output=True,text=True)
        try: return json.loads(r.stdout)
        except Exception: time.sleep(40*(k+1))
    raise SystemExit("rate limited")
mode=sys.argv[1]
if mode=="search":
    for q in sys.argv[2:]:
        d=api(dict(action="query",list="search",srnamespace=6,srlimit=10,format="json",srsearch=q))
        print("==",q); [print("  ",x["title"]) for x in d["query"]["search"]]; time.sleep(4)
else:
    titles=sys.argv[2:]
    for i in range(0,len(titles),20):
        d=api(dict(action="query",prop="imageinfo",iiprop="extmetadata|size",format="json",titles="|".join(titles[i:i+20])))
        for p in d["query"]["pages"].values():
            if "imageinfo" not in p: print(p["title"],"MISSING"); continue
            ii=p["imageinfo"][0];m=ii["extmetadata"]
            g=lambda k:m.get(k,{}).get("value","")
            print(p["title"],ii["width"],ii["height"],g("LicenseShortName"),"|",g("DateTimeOriginal")[:30],"|",g("ImageDescription")[:160].replace("\n"," "))
        time.sleep(4)
