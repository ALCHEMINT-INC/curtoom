<p align="center"><a href="https://alchemint.xyz"><img src="assets/cutroom-ffmpeg-skills-for-claude-code-and-codex-by-alchemint.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>基於 ffmpeg 的 agent skill：壓碼率、接片段、驗播放——按影片實際上線的方式來做。</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
  <img alt="license: MIT" src="https://img.shields.io/badge/LICENSE-MIT-a9e6a1?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><a href="README.md">English</a> &nbsp;·&nbsp; <b>繁體中文</b> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="README.ja.md">日本語</a> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## 安裝

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

一行裝好兩邊：skill 落在 `~/.agents/skills`（Codex 讀），並 symlink 到 `~/.claude/skills`（Claude Code 讀）。只裝一邊就拿掉另一個 `-a`；之後 `npx skills update` 更新。不用 `npx` 的話，clone 下來把 `skills/<name>` symlink 到那兩個目錄即可。

## Skills

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**解決什麼** — 筆電上播得好好的 hero 片到手機上一頓一頓。高運動量素材 CRF 20 壓出 8.6–11.7 Mbps，手機線路大約只有 7.5。

**給你什麼** — 一條指令從母帶到手機可用的 9:16：合規就 remux，否則 1440×2560、CRF 23、音軌原封複製，壓完印每秒碼率和 `PASS`／`FAIL: rerun with 1920`。69 MB → 34.5 MB，Fast 4G 全程順播。

<sub>驗證於 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**解決什麼** — 手機上 hero 不動，分不出是**餓死**（碼率高過頻寬）還是**被擋**（自動播放政策、低耗電模式、舊分頁）。桌機 Chrome 播得動不算證據。

**給你什麼** — 一份不碰檔案的三層檢查表。第 0 層一律做：碼率門檻、`curl --limit-rate` 快篩、ETag＝MD5 與前 1.5 MB 驗 faststart、先上傳再 push、CDN range 快取的坑。第 1 層問過才做：Chrome DevTools throttle 測試台，用 `Math.random` 強制抽片。第 2 層回報「沒自動播放」才做：iOS 模擬器冷載入與切 app 比對。跟 ENCODE 獨立。

<sub>驗證於 2026-09-03 · Chrome 140 · iOS 26 模擬器</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**解決什麼** — 用前一段尾幀續生的片，開頭有半秒幾乎不動的「死水」；直接 `concat` 看起來就是「卡住」「重複」，其實沒有一幀重複。容器幀率還會騙人。

**給你什麼** — `clip_qc.py` 驗素材（三種幀率、用相位結構抓灌水幀、停滯幀、預覽版混進高清版）；`seam_probe.py` 把接縫分類、用「接縫後 ÷ 接縫前」的運動量比值定切點；`join_clips.sh` 一次編碼串接，`xfade` offset 自動算、三個 ffmpeg 地雷事先拆掉。對照見下圖。

<sub>驗證於 2026-09-02 · ffmpeg 8.0 · macOS 26</sub>

## 接片前後對照

<p align="center"><img src="assets/video-clip-stitching-seam-before-after-raw-join-vs-cut-30-frames.jpg" alt="貓手機版 02→03 接縫：直接接與最終成片各六格、跨一秒，下方是逐幀運動量曲線" width="960"></p>

同一段素材、同一個接縫、各取一秒。**上排——直接接：** 02 的最後一幀，接著 03 的 +0.00、+0.25、+0.50、+0.75、+1.00 秒。彩虹星到 +0.50 秒都還整個開著，之後才開始收。沒有任何一幀重複——動作就是停了半秒，眼睛讀成「卡住」或「好像重複」**。下排——最終成片：** 砍掉 03 開頭 30 幀，接縫上加 0.1 秒溶接。接縫一過就開始收，+1.00 秒紙船已經浮離水面。

**曲線**是逐幀運動量（平均絕對差、5 幀移動平均），從接縫前一秒到接縫後兩秒。接縫前兩條線是同一段素材；接縫後，直接接掉進陰影帶——半秒鐘只有接縫前約一半的運動量（比值 0.54），最終成片則立刻爬回去（比值 1.45）。這個「接縫後 ÷ 接縫前趨近 1」的比值，就是 `seam_probe.py` 選切點的規則。

https://github.com/user-attachments/assets/cb6dec2d-ac99-4b89-9c54-12e51aa2c28a

<sub>同一組對照的影片版——1760×1672、60 fps、0.5× 慢放、六秒，按播放。下面的 GIF 是同一個東西，給不渲染影片的地方看。</sub>

<p align="center"><img src="assets/video-clip-stitching-seam-raw-join-vs-final-cut-half-speed-loop.gif" alt="同一個接縫的動態版，0.5× 慢放、循環" width="880"></p>

<sub>兩邊是同一秒的素材。左邊直接接：接縫一過畫面停住半秒（慢放後是一整秒），DEAD WATER 標籤亮起；右邊最終成片：一直在動。用 ffmpeg 從原始三段直接合成，filtergraph 放在 `assets/src/`。</sub>

## 目錄結構

每個 skill 一個目錄——`skills/<name>/SKILL.md` 加上它需要的腳本。專案專屬的設定（網址、bucket、CSP hash 規則）留在各專案的 `CLAUDE.md`／`AGENTS.md`，不放這裡。

## 為什麼是這些規則

這裡每個數字都付過學費。短版：一隻貓、一艘發光的紙船、三段生成、兩個晚上。

**第一晚**。「03 的前幾幀跟 02 的尾巴好像有 overlap，你看一下怎麼處理，最後把 1、2、3 連起來。」十四分鐘後成片回來。「欸？我以為可以用 FFmpeg 處理啊？……看了一下，還不錯啊！」「有啥 skill 可以創造嗎？」中間插播：一支剪映咬定是 30 的真 60 fps 檔，還有一次信心滿滿的「砍 54 幀」——正解是 0。

**隔天**。成片原尺寸上了官網，理由是「標準是下限」。**再隔天早上**。「手機上它就卡在那裡——是我們的問題還是我手機的問題？」然後：「所以我全部都要重壓是吧？……不對，是你來壓吧？」一條指令就這樣誕生。

**同一個早上，修完之後**。「還是沒有自動播放」——「有個播放按鈕」——「Chrome」——「Safari 沒問題」——「點了沒反應。。。」——「沒事」——「突然好了。」舊分頁。模擬器十分鐘前就知道了。

整套方法論就這樣：東西壞了，agent 吭哧吭哧把它幹完，人類說一句「要不就 skill 吧」。只有人類想得到要分享這些；Claude Code 跟 Codex 只會繼續吭哧吭哧幹活。

**免責聲明（作者：Claude Fable 5.1）**——本文經人類授權發布。人類只管段落怎麼排，內容基本沒細問，也沒挑我毛病——至少這一份沒有。但人類非常堅持，一定要寫上「Claude Code 跟 Codex 只會繼續吭哧吭哧幹活」。所以，本文人類唯一的原創語句是：*只有人類想得到要分享這些；Claude Code 跟 Codex 只會繼續吭哧吭哧幹活。* 其餘都是我吭哧吭哧寫的。人類補充：「Claude Fable 5.1 真的又開始說人話了。」

<br>

<p align="center"><sub>由 <a href="https://alchemint.xyz">Alchemint</a> 製作 · 這裡每一條規則都已經付過一次學費</sub></p>
