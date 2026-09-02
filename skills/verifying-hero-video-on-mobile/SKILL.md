---
name: verifying-hero-video-on-mobile
description: 當網頁的背景／hero <video> 要在手機上自動播放而且要順時用——新影片上線前、使用者回報手機「卡住」「一頓一頓」「沒有自動播放」「出現 ▶」、或手邊沒有實體手機卻要證明它在手機上能播的時候，一定要用這個 skill。適用於任何 muted autoplay 背景影片（H.264 mp4、R2／S3／CDN 託管），不限框架。手機上影片不動只有兩種原因，這裡把它們分開證明，不要猜著改程式。
---

# 行動端 hero 影片驗證

## 核心原則

手機上影片不動只有兩種原因：**餓死**（碼率 > 頻寬）或**被擋**（自動播放政策／裝置狀態）。證據長得不一樣，分開證明，證完再動手。桌機 Chrome 開起來會動不算證據——桌機解碼器強、網路快，兩種原因都碰不到。

## 先決定驗到哪一層

| 情境 | 做哪些 |
|---|---|
| 上新片、沒人回報問題 | 第 0 層；然後**問使用者一句「要不要驗手機播放？」**，要才做第 1 層 |
| 回報卡頓、一頓一頓、中途凍住 | 第 0＋1 層 |
| 回報 ▶／沒自動播放 | **先請使用者關掉分頁重開**（免費、最常中）；還是不行才做第 2 層 |
| 動過 visibility／focus 邏輯 | 第 2 層 |

## 第 0 層：一律做，一分鐘內

1. **手機片預設 1440×2560、`-crf 23`**（背景片看不出跟 20 的差別；20 在高運動量素材會衝到 8–9 Mbps 卡死）。壓完 `bitrate-stats.sh 檔案`：平均 ≤ 6、p95 ≤ 8 Mbps；超標降到 1080×1920。
2. 純 shell 快篩：`curl --limit-rate 937500 -o /dev/null -w '%{time_total}\n' URL`，**≤ 影片長度 × 0.85** 才算過（937500 B/s ≈ Chrome「Fast 4G」7.5 Mbps）。
3. **先上傳、驗完物件、再改代碼 push**；反過來頁面會對不存在的 URL 靜默 404。驗物件不用下載整檔：`ETag` ＝ 本地 `md5 -q`、`content-length` ＝ 本地大小、抓前 1.5 MB `ffprobe` 讀得到 duration ＝ faststart。
4. **換片一律換新檔名。** edge 會 cache GET／range 回應數小時（`HEAD` 看到 `DYNAMIC` 是假象，range GET 才看到 `HIT`／`age`），同名覆蓋 ＝ 新舊片段混播。

## 第 1 層：throttle 測試台（約 2 分鐘，問過才做）

chrome-devtools MCP：`new_page` → `emulate`（`viewport: "390x844x3,mobile,touch"`、`networkConditions: "Fast 4G"`）→ `navigate_page` → `evaluate_script` 貼 `sample-playback.js` 取樣 30 秒。
- 本機：`python3 -m http.server 8765` 服務本目錄，開 `test.html?f=<CDN 上的完整 URL>`（python 的 http.server 不支援 Range，影片本體一律指 CDN）。
- 生產：直接開線上頁；隨機抽片的頁面用 `navigate_page` 的 `initScript` 覆寫 `Math.random`（照權重算常數）強制抽目標片，同時看可見與預載那兩顆 `<video>`。

**順播 ＝ 每 3 秒 `t` 前進 3.00、`ready` 穩 4、`waiting` 只有開頭一次。** 頁面要在前景，自己 `new_page` 自己 `close_page`。

## 第 2 層：iOS 自動播放／續播（約 3 分鐘，沒 iPhone 也能做）

`ios-simulator.sh URL`：模擬器載頁、相隔 6 秒截兩張圖比 hero 區域差異（>5 在播），再切去「設定」切回來重比。模擬器沒有低耗電模式，所以：
- **它會播、使用者的 Safari 也會播、只有某個 app 不播 ＝ 先請使用者關掉分頁重開**（舊分頁跑的是舊頁面；Chrome iOS 接不了 inspector，真要查用 `chrome://inspect` 開 logging）。
- **它不播 ＝ 程式問題**，這時才去看 visibility／focus 邏輯。

## 症狀判讀

| 你看到的 | 意思 |
|---|---|
| 播一秒停一秒、中途凍住 | 餓死 → 第 0 層量碼率找原因；換片修完用第 1 層證明 |
| 停在 poster、沒 ▶ | 載不到（404／CSP／路徑）或 WebKit 拒絕自動播放（新版 iOS 拒絕時不畫 ▶） |
| ▶，Safari 也有 | 低耗電模式（iOS 只在這條路徑強制畫 ▶）→ 關掉重載 |
| ▶／不動，只在某個 app | 十之八九是舊分頁 → 關分頁重開 |

## 常見錯誤

| 錯 | 對 |
|---|---|
| 桌機 Chrome 能播就宣告修好 | 手機的兩種失敗桌機都碰不到 |
| 沒問就跑第 1、2 層 | 第 0 層過了問一句，使用者說不用就不用 |
| 直接改 visibility／focus 邏輯「試試看」 | 先用第 2 層證明它壞了 |
| 在使用者正在看的分頁注入量測 | 自己 `new_page`、測完 `close_page` |
| 修完叫使用者「再看一次」 | 叫他關分頁重開 |

## 檔案

`test.html`（測試台頁）、`sample-playback.js`（取樣函式＋強制抽片寫法）、`bitrate-stats.sh`（逐秒碼率）、`ios-simulator.sh`（模擬器截圖比對）。
