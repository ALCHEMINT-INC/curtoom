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

一隻貓、一艘會發光的紙船、三支 skill。官網的 hero 片是一隻貓跟著紙船走進夜晚的街道，分三段生成——每一段都從前一段的最後一幀起頭。這個 repo 裡的每一條規則，都是兩個晚上在這一段素材上撞出來的，順序就是下面這樣。

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**起因** — 2026-09-01 晚上。原話差不多是：「Downloads 裡有 cat mobile 01、02、03，03 的前幾幀跟 02 的尾巴好像有 overlap，你看一下剪的時候怎麼處理，最後把 1、2、3 連起來合成一支。」十四分鐘後成片回來了，回覆是：「欸？我以為可以用 FFmpeg 處理啊？……我看了一下，還不錯啊！」——全程就是 ffmpeg，沒開任何剪輯軟體。這個意外就是這支 skill 存在的理由，下一句話就是「有啥 skill 可以創造嗎」。

**真正的問題** — 不是 overlap。02 的結尾是紙船展開成六角彩虹星，03 的開頭是星形收攏回紙船、然後升空。中間那半秒，03 幾乎不動——鏈式生成從參考幀起步時的通病。所以觀眾看到的是：星星開到頂、停半秒、才收。那個停頓就是「卡住」「好像重複」；沒有任何一幀重複，是動作斷了。砍掉 30 幀，接縫兩側的運動量比從 0.54 變 1.35，再加 0.1 秒溶接，因為兩段材質永遠對不完全。

**接著是幀率驚魂** — 「我記得原影片是 60 吧？為什麼出來變 30？」——其實沒有。剪映顯示的是它自己 30 fps 的專案時間軸。實測：2,789 幀裡只有 2 幀重複。但一量就量出兩個真問題——02 有 13.4% 的停滯幀（生成瑕疵，不是轉檔），而 Downloads 裡的 desktop 03 是 854×480／24 fps 的預覽版，不是高清版。這就是為什麼 `clip_qc.py` 要回報三種幀率，還用相位結構抓灌水幀（灌水素材奇偶相位差 7.5×，真素材 1.1×）。

**然後是 54 幀的錯** — 橫版那批看起來一模一樣，運動曲線說要砍 54 幀，正解是 0——前一段本來就收得慢，接縫處的低運動量是匹配的。同一條曲線配不同基準線，結論相反。留下來的規則就是：接縫後運動量 ÷ 接縫前運動量要趨近 1（低於 0.75 是死水，高於 1.4 是暴衝）。

**它現在做什麼** — `clip_qc.py` 驗素材；`seam_probe.py` 把每個接縫分類——不同鏡位 → 硬切、構圖延續 → 砍死水＋溶接、真重疊 → 砍掉被重演的段落；`join_clips.sh` 一次編碼完成，`xfade` 的 offset 是算的不是手填的，三個 ffmpeg 地雷事先拆掉。最後一套老實的驗收：時長對帳、接縫定格、分段 `volumedetect`。

**效益** — 兩支成片（直版 46.5 秒、橫版 45 秒）接縫經得起實際播放，外加一份「哪些該重生成」的清單——那才是人真正需要的部分。

<sub>驗證於 2026-09-02 · ffmpeg 8.0 · macOS 26</sub>

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**起因** — 接好的貓片——1792×3184、19 Mbps、112 MB——隔天就進了官網的手機輪播。加它的那個 commit 白紙黑字寫著：解析度標準是下限，所以保留原生尺寸「不縮」。CRF 20 壓下來 11.7 Mbps／69 MB。筆電上看，美極了。

**隔天早上** — 「之前行動端載入後會自動播放，不知道為什麼現在會卡在那裡。是哪裡出問題，還是我手機的問題？」Chrome 的「Fast 4G」實測約 7.5 Mbps。這支片播一秒、等一秒，9.16 秒處凍住。另外三支手機片 5.4–6.6 Mbps，同一條線上全程順播。

**為什麼是 CRF 23** — 縮到手機標準 1440×2560、CRF 20，還是 8.6 Mbps——39 秒卡 5 次。CRF 鎖的是感知品質不是碼率：同一個 CRF 20，靜態鏡頭 6 Mbps，貓帶紙船過馬路 8.6。CRF 23 壓出 5.7 Mbps，一邊預載下一支一邊全程順播；手機大小的背景片分不出 23 跟 20。（當天稍晚：「你說的 CRF 23 是比較好的是吧？相較於 20？」——不是。數字越低品質越高；23 是塞得進水管的那個。）高於 1440×2560 的原生解析度一律不留：手機螢幕最寬 1290×2796，多的像素只是多的碼率。

**「所以我現在全部都要重壓是吧？」** — 這是下一個問題——「……不對，是你這邊來重新壓縮是吧？」一支檔，而且已經壓好了。這段對話就是整支 skill 的產品規格：一條指令、不用做決定。

**它做什麼** — 母帶已經是 H.264、≤ 1440×2560、≤ 6 Mbps 就只 remux（moov 搬到前面，零損耗）；否則 1440×2560、CRF 23、preset slow、音軌原封複製。壓完印每秒碼率——平均、p95、峰值——和 `PASS` 或 `FAIL: rerun with 1920`。

**效益** — 69 MB → 34.5 MB、11.7 → 5.7 Mbps，46 秒的片在手機上從頭播到尾。

<sub>驗證於 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**起因** — 修正版 04:47 上線。接下來依序是：「我手機還是沒有自動播放」——「我看到的是播放按鈕」——「移動 app Chrome」——「Safari 倒是沒問題」——「Chrome 則是連點了播放鍵都沒反應。。。」——「沒事」——「突然好了。」二十分鐘。bug 是一個還在跑昨天頁面、昨天 69 MB 片的 Chrome 分頁；Chrome 自己重載，問題蒸發。

**為什麼變成 skill** — 同一時間，這台機器已經開了 iOS 模擬器冷載入網站、切去「設定」再切回來，證明頁面會自動播放也會續播。嫌疑人就只剩手機和分頁兩個，也讓人沒去「修」一段根本沒壞的 visibility 邏輯。當天下午，草稿版 skill 的測試跑出另一個坑：CDN 上同名覆蓋會在四小時內吐出新舊混合的片段（`HEAD` 說 `DYNAMIC`，range `GET` 才說 `HIT`）。兩件事都直接進了檢查表。

**跟 ENCODE 的差別** — 它完全不碰檔案。ENCODE 產片；VERIFY 回答「頁面在手機上到底播不播得出來，不播是為什麼」。兩者獨立，各用各的。

**什麼時候用** — 設計上就是選用。第 0 層一律做（一分鐘）；有人回報卡頓、或想在沒手機的情況下先拿證據才做第 1 層；回報「沒自動播放」「有播放鍵」才做第 2 層——而且第一步是請他關分頁重開。

**它做什麼** — 第 0 層：每秒碼率門檻、`curl --limit-rate` 快篩、ETag＝MD5 與前 1.5 MB 驗上傳完整與 faststart、先上傳再 push 的順序、CDN range 快取的坑。第 1 層：Chrome DevTools throttle 測試台，覆寫 `Math.random` 強制抽到你要測的那支。第 2 層：iOS 模擬器冷載入與切 app 的截圖比對。

**效益** — 五分鐘內把「餓死」和「被擋」分開，靠證據不靠直覺。

<sub>驗證於 2026-09-03 · Chrome 140 · iOS 26 模擬器</sub>

## ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

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
