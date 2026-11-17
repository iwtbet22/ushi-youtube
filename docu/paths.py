"""回の名前から、台本・調査・概要欄の置き場所を決める。
c2 で始まる回（2つ目のチャンネル）は ch2/script/、それ以外は script/。
読みの表 (script/yomi.tsv) は両方のチャンネルで共通。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def script_dir(ep: str) -> Path:
    return ROOT / ("ch2/script" if ep.startswith("c2") else "script")
