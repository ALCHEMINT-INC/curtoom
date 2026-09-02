# saltjar-skills

跨專案、跨 runtime（Claude Code／Codex）共用的 skill。每個 skill 一個目錄：`skills/<name>/SKILL.md`＋必要的工具檔。專案專屬的設定（網址、bucket、hash 規則）不放這裡，留在各專案的 `CLAUDE.md`／`AGENTS.md`。

## 安裝（每台機器一次）

```sh
git clone <this repo> ~/Documents/saltjar-skills
mkdir -p ~/.claude/skills ~/.agents/skills
for s in ~/Documents/saltjar-skills/skills/*/; do
  n=$(basename "$s"); ln -sfn "$s" ~/.claude/skills/"$n"; ln -sfn "$s" ~/.agents/skills/"$n"
done
```

Claude Code 讀 `~/.claude/skills`，Codex 讀 `~/.agents/skills`；兩邊都是 symlink，改這裡即生效。

## Skills

| name | 用途 |
|---|---|
| `verifying-hero-video-on-mobile` | 背景／hero 影片在手機上「卡住／沒自動播放／出現 ▶」的判讀與驗證：碼率門檻、throttle 測試台、iOS 模擬器、上傳與 CDN 快取 |
