<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>基於 ffmpeg 的 agent skill：壓碼率、接片段、驗播放——按影片實際上線的方式來做。</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><a href="README.md">English</a> &nbsp;·&nbsp; <b>繁體中文</b> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="README.ja.md">日本語</a> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## 安裝

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

一行裝好兩邊：skill 落在 `~/.agents/skills`（Codex 讀），並 symlink 到 `~/.claude/skills`（Claude Code 讀）。只裝一邊就拿掉另一個 `-a`；之後 `npx skills update` 更新。不用 `npx` 的話，clone 下來把 `skills/<name>` symlink 到那兩個目錄即可。

## Skills

|  | skill | 什麼時候會用到 |
|:--|:--|:--|
| <img alt="ENCODE" src="https://img.shields.io/badge/ENCODE-ffe45d?style=flat-square"> | [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile) | 母帶 → 手機 9:16 hero 片，一條指令：自動判斷 remux／重壓、量每秒碼率、印 PASS／FAIL |
| <img alt="VERIFY" src="https://img.shields.io/badge/VERIFY-9dc6ff?style=flat-square"> | [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile) | 背景／hero 影片在手機上「卡住」「沒自動播放」「出現播放鍵」：碼率門檻、Chrome throttle 測試台、iOS 模擬器、上傳與 CDN 快取檢查 |
| <img alt="STITCH" src="https://img.shields.io/badge/STITCH-ff9fc6?style=flat-square"> | [`video-clip-stitching`](skills/video-clip-stitching) | 把多段 AI 生成的片段接成一支：找切點、診斷接縫、驗收素材規格 |

## 目錄結構

每個 skill 一個目錄——`skills/<name>/SKILL.md` 加上它需要的腳本。專案專屬的設定（網址、bucket、CSP hash 規則）留在各專案的 `CLAUDE.md`／`AGENTS.md`，不放這裡。

## 為什麼是這些規則

每一條都是實際撞出來的，不是推導出來的。數字——碼率天花板、門檻、H.264 level 上限——都來自各 `SKILL.md` 裡記錄的實測。

<br>

<p align="center"><sub>由 <a href="https://alchemint.xyz">Alchemint</a> 製作 · 這裡每一條規則都已經付過一次學費</sub></p>
