# cutroom

ffmpeg-based skills for coding agents — encode, stitch, and verify video the way it actually ships.

基於 ffmpeg 的 agent skill（Claude Code／Codex 共用）：壓碼率、接片段、驗播放——每一條規則都是實際撞出來的。每個 skill 一個目錄：`skills/<name>/SKILL.md`＋必要的腳本。專案專屬的設定（網址、bucket、hash 規則）不放這裡，留在各專案的 `CLAUDE.md`／`AGENTS.md`。

| skill | 用途 |
|---|---|
| `encoding-hero-video-for-mobile` | 母帶 → 手機 9:16 hero 片，一條指令：自動 remux／重壓、量碼率、給 PASS／FAIL |
| `verifying-hero-video-on-mobile` | 背景／hero 影片在手機上「卡住／沒自動播放／出現 ▶」的判讀與驗證：碼率門檻、throttle 測試台、iOS 模擬器、上傳與 CDN 快取 |
| `video-clip-stitching` | 把多段 AI 生成的片段接成一支，找切點、診斷接縫、驗收素材規格 |

## 安裝（每台機器一次）

```sh
git clone https://github.com/ALCHEMINT-INC/curtoom.git ~/Documents/cutroom
mkdir -p ~/.claude/skills ~/.agents/skills
for s in ~/Documents/cutroom/skills/*/; do
  n=$(basename "$s"); ln -sfn "$s" ~/.claude/skills/"$n"; ln -sfn "$s" ~/.agents/skills/"$n"
done
```

Claude Code 讀 `~/.claude/skills`，Codex 讀 `~/.agents/skills`；兩邊都是 symlink，改這裡即生效。
