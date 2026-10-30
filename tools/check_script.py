"""台本 (script/epXX_narration.txt) と場面の定義 (docu/epXX.py) の文が、順番どおり一致しているかを確かめる。

  python3 tools/check_script.py ep03
"""
import difflib
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "docu"))

ep = sys.argv[1]
t = (ROOT / "script" / f"{ep}_narration.txt").read_text().split("【オープニング】", 1)[1]
script = [l.strip() for l in t.split("\n") if l.strip() and not l.startswith("【")]
scenes = [l[0] if isinstance(l, tuple) else l for sc in importlib.import_module(ep).SCENES for l in sc["lines"]]
diff = list(difflib.unified_diff(script, scenes, "台本", "場面", lineterm="", n=0))
print(f"台本 {len(script)} 文 / 場面 {len(scenes)} 文 / {'一致' if not diff else '不一致'}")
for d in diff:
    print(d)
sys.exit(1 if diff else 0)
