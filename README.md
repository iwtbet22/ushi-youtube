# ushi-youtube

プロ野球の「お金と制度の仕組み」を解説するチャンネルの制作リポジトリ。

## 第1回 本編：ドラフトの契約金はいくら？（白背景の解説スタイル・現行版）

- 台本：`script/ep01_main.md`
- デザイン仕様：`design/design_spec_v2.md`
- 書き出し：`python3 explainer/engine.py` → `output/ep01_main.mp4`（1920x1080 / 30fps）
- 台本を書き出す：`python3 explainer/export_script.py`
- 台本・画面構成は `explainer/episode.py`、テロップ部品は `explainer/ui.py`、イラストは `explainer/illust.py`

## 旧版：冒頭3分のシネマ調プロト（参考用）

- 台本：`script/ep01_opening.md`
- デザイン仕様：`design/design_spec.md`
- 完成動画：`output/ep01_opening.mp4`（1920x1080 / 30fps / 約3分）。生成物なので Git では追跡しない（`python3 render/render.py` で作り直す）

### 書き出し方
```bash
pip install numpy pillow edge-tts   # ffmpeg も必要
python3 render/render.py                 # 本番
python3 render/render.py --preview       # 960x540 / 15fps の確認用
python3 render/render.py --stills out/   # 各シーンの静止画だけ
```
台本を書き出すには `python3 render/export_script.py` を実行する。
台本・ナレーション・構成を変えるときは `render/timeline.py`、テロップの見た目を変えるときは `render/style.py` を編集する。
