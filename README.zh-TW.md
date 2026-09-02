<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

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

三支 skill，一條產線。**STITCH** 把分段生成的片接成一支能用的素材；**ENCODE** 把素材壓成手機真的串得動的檔；**VERIFY** 證明頁面播得出來——它不壓任何東西、可用可不用，手機出狀況或你想在沒有實體手機的情況下先拿到證據時再開。

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**解決的問題** — 筆電上播得好好的 hero 片，到手機上一頓一頓。實際案例：1792×3184、CRF 20 的成品壓出 11.7 Mbps／69 MB；手機網路（Chrome「Fast 4G」實測約 7.5 Mbps）餵它一秒播一秒等，然後凍住。

**什麼時候用** — 任何要上手機的 9:16 背景／hero 片，以及已經在手機上卡的片。

**它做什麼** — 一條指令。母帶已經是 H.264、≤ 1440×2560、≤ 6 Mbps 就只 remux（moov 搬到前面，零損耗）；否則縮到 1440×2560、CRF 23、preset slow、音軌原封複製，壓完量每秒碼率，印 `PASS` 或 `FAIL: rerun with 1920`。

**為什麼是 CRF 23** — CRF 鎖的是感知品質，不是碼率。同一個 CRF 20，靜態鏡頭 6 Mbps、高運動量素材 8.6 Mbps——實測——而 8.6 在 7.5 Mbps 的線上就是卡。CRF 23 落在 5.7 Mbps，手機大小的背景片看不出差別。高於 1440×2560 的原生解析度一律不留：手機螢幕最寬 1290×2796，多的像素只是多的碼率。

**效益** — 69 MB → 34.5 MB、11.7 → 5.7 Mbps；46 秒的片在 Fast 4G 下從頭播到尾，同時頁面還在背景預載下一支。

<sub>驗證於 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**跟 ENCODE 的差別** — 它完全不碰檔案。ENCODE 產出一支片；VERIFY 告訴你頁面在手機上到底播不播得出來、不播是為什麼。兩者獨立，各用各的。

**解決的問題** — 手機上 hero 不動，你分不出是**餓死**（碼率高過頻寬）還是**被擋**（自動播放政策、低耗電模式、一個還在跑昨天頁面的舊分頁）。桌機 Chrome 播得動不算證據——桌機兩種失敗都碰不到。

**什麼時候用** — 設計上就是選用。第 0 層一律做（一分鐘）；有人回報卡頓、或上線前想拿證據才做第 1 層；回報「沒自動播放」「出現播放鍵」才做第 2 層。

**它做什麼** — 第 0 層：每秒碼率門檻、`curl --limit-rate` 快篩、用 ETag＝MD5 與前 1.5 MB 驗上傳完整與 faststart、先上傳再 push 的順序、CDN range 快取的坑。第 1 層：Chrome DevTools throttle 測試台，用覆寫 `Math.random` 強制抽到目標片。第 2 層：iOS 模擬器冷載入與切 app 的截圖比對，不需要 iPhone。

**效益** — 五分鐘內把「頁面有 bug」和「裝置狀態」切開。它讓我們沒有去「修」一段根本沒壞的 visibility 邏輯，還挖出同名覆蓋會在四小時內吐出新舊混合片段的坑（`HEAD` 說 `DYNAMIC`，range `GET` 才說 `HIT`）。

<sub>驗證於 2026-09-03 · Chrome 140 · iOS 26 模擬器</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**解決的問題** — 鏈式生成——拿第 N 段的尾幀當第 N+1 段的首幀——每一段續生的開頭都會有約半秒幾乎不動的「死水」。直接 `concat` 看起來就是「卡住了」「好像重複」；其實沒有任何一幀重複，是動作斷了。再加上容器幀率會騙人：30 fps 的內容包成 60 fps，每個標頭都寫 60。

**什麼時候用** — Dreamina、Runway、Higgsfield、Seedance 這類 01／02／03 分段生成的系列；任何「卡住」「重複」「不順」「有 overlap」的抱怨；生成素材送去任何地方之前的驗收。

**它做什麼** — `clip_qc.py` 回報三種幀率（容器、幀密度、有效），用相位結構抓灌水幀——灌水素材的奇偶相位差 7.5×，真素材 1.1×——外加停滯幀比例與預覽版混進高清版的情況。`seam_probe.py` 把每個接縫分成三種處理相反的類型：不同鏡位 → 硬切；構圖延續 → 砍死水＋溶接；真重疊 → 砍掉被重演的段落。切點由「接縫後運動量 ÷ 接縫前運動量」決定，目標趨近 1。`join_clips.sh` 一次編碼完成，`xfade` 的 offset 是算出來的不是手填的，三個 ffmpeg 地雷事先拆掉。

**為什麼是比值** — 只看曲線曾經推出要砍 54 幀，正解是 0——前一段本來就收得慢，後段開頭的低運動量是匹配的。同一條曲線配不同基準線，結論相反。兩批看起來一模一樣的素材，切點分別是 30 和 0。

**效益** — 接縫經得起實際播放，還有一套老實的驗收：時長對帳、接縫定格、分段 `volumedetect`。

<sub>驗證於 2026-09-02 · ffmpeg 8.0</sub>

## 目錄結構

每個 skill 一個目錄——`skills/<name>/SKILL.md` 加上它需要的腳本。專案專屬的設定（網址、bucket、CSP hash 規則）留在各專案的 `CLAUDE.md`／`AGENTS.md`，不放這裡。

## 為什麼是這些規則

每一條都是實際撞出來的，不是推導出來的。數字——碼率天花板、門檻、H.264 level 上限——都來自各 `SKILL.md` 裡記錄的實測。

<br>

<p align="center"><sub>由 <a href="https://alchemint.xyz">Alchemint</a> 製作 · 這裡每一條規則都已經付過一次學費</sub></p>
