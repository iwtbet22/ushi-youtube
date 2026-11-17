"""聞き比べ (check_word) をまとめて行う。
使い方: python3 tools/check_words.py <モジュール名> words.json   # words.json は [["語","正しい読み","間違った読み"], ...]
"""
import sys
sys.path.insert(0,'/home/user/ushi-youtube/tools'); sys.path.insert(0,'/home/user/ushi-youtube/render'); sys.path.insert(0,'/home/user/ushi-youtube/docu')
import check_word as cw, film, importlib; EP=importlib.import_module(sys.argv[1])
import json
T=json.load(open(sys.argv[2]))
for w,g,b in T:
    for sc in EP.SCENES:
        for line in sc["lines"]:
            sp=film._speech(line)
            if w not in sp: continue
            dg,db=cw.judge(sp,w,g,b)
            v="正しい" if dg<db*0.9 else ("読み間違い" if db<dg*0.9 else "微妙")
            print(f"{v} 正{dg:.2f}/誤{db:.2f} {w}→{g}? {film._display(line)[:40]}",flush=True)
