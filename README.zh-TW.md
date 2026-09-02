[English](README.md) | 繁體中文 | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

# cutroom

基於 ffmpeg 的 agent skill：壓碼率、接片段、驗播放——按影片實際上線的方式來做。

Claude Code 與 Codex 共用。每個 skill 一個目錄：`skills/<name>/SKILL.md` 加上它需要的腳本。專案專屬的設定（網址、bucket、CSP hash 規則）留在各專案的 `CLAUDE.md`／`AGENTS.md`，不放這裡。

| skill | 用途 |
|---|---|
| `encoding-hero-video-for-mobile` | 母帶 → 手機 9:16 hero 片，一條指令：自動判斷 remux／重壓、量每秒碼率、印 PASS／FAIL |
| `verifying-hero-video-on-mobile` | 背景／hero 影片在手機上「卡住」「沒自動播放」「出現 ▶」的判讀與驗證：碼率門檻、Chrome throttle 測試台、iOS 模擬器、上傳與 CDN 快取檢查 |
| `video-clip-stitching` | 把多段 AI 生成的片段接成一支：找切點、診斷接縫、驗收素材規格 |

## 安裝（每台機器一次）

```sh
git clone https://github.com/ALCHEMINT-INC/curtoom.git ~/Documents/cutroom
mkdir -p ~/.claude/skills ~/.agents/skills
for s in ~/Documents/cutroom/skills/*/; do
  n=$(basename "$s"); ln -sfn "$s" ~/.claude/skills/"$n"; ln -sfn "$s" ~/.agents/skills/"$n"
done
```

Claude Code 讀 `~/.claude/skills`，Codex 讀 `~/.agents/skills`；兩邊都是 symlink，改這裡即生效。

## 為什麼是這些規則

每一條都是實際撞出來的，不是推導出來的。數字（碼率天花板、門檻、level 上限）都來自各 `SKILL.md` 裡記錄的實測。
