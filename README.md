# ushi-youtube

プロ野球の「お金と制度の仕組み」を解説するチャンネルの制作リポジトリ。

## 第1回 本編：ドラフトのお金と制度 完全解説（約30分・現行版）

- 台本：`script/ep01_main.md`（`python3 explainer/export_script.py` で生成）
- ファクトチェック表：`script/ep01_factcheck.md`
- 録音用台本：`script/ep01_recording.md`（`python3 explainer/export_recording.py` で生成）
- 概要欄用チャプター：`script/ep01_chapters.txt`（書き出し時に生成）
- デザイン仕様：`design/design_spec_v2.md`、収益化リスクのメモ：`design/youtube_risk_notes.md`
- 書き出し：`python3 explainer/engine.py` → `output/ep01_main.mp4`（1920x1080 / 30fps、約30分。4並列で1時間前後）
- 配置チェックだけ：`python3 explainer/engine.py --check`
- 台本・画面構成は `explainer/episode.py`（30分版で足したシーンは `explainer/extra_scenes.py`）、テロップ部品は `explainer/ui.py`、イラストは `explainer/illust.py`

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
