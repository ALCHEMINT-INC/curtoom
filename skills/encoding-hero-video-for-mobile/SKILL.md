---
name: encoding-hero-video-for-mobile
description: 當要把一支影片母帶壓成手機用（9:16 直式）的網頁背景／hero mp4、或現有手機片碼率太高在手機上會卡而要重壓的時候用。只管壓制與碼率，不含播放驗證（那是 verifying-hero-video-on-mobile）。
---

# 手機 hero 影片壓制

## 規則（只有四條）

1. **1440×2560、`-crf 23`、`-preset slow`、音軌 `-c:a copy`、`+faststart`。** 不保留高於 1440×2560 的原生解析度（手機螢幕最寬 1290×2796，多的只是碼率）；CRF 20 在高運動量素材會衝到 8–9 Mbps，手機餵不飽。
2. **壓完看碼率，不看 CRF**：平均 ≤ 6 Mbps、p95 ≤ 8。超標 → 降到 1080×1920 再壓一次。
3. 母帶已經是 H.264、≤ 1440×2560、≤ 6 Mbps（例如 dreamina 成品）→ **只 remux 不重壓**，再壓只會多一代損耗。
4. 檔名帶上實際用的 CRF（`_crf23`），換片一律換新檔名（CDN 會 cache 舊片段）。

## 一條指令

```sh
encode-mobile.sh 母帶.mp4 輸出_crf23.mp4          # 1440×2560
encode-mobile.sh 母帶.mp4 輸出_crf23.mp4 1920     # 超標時：1080×1920
```

腳本自己判斷 remux 或重壓，壓完印出解析度／每秒碼率 avg・p95・max／faststart，最後一行 `PASS` 或 `FAIL: rerun with 1920`。

## 之後

上傳、驗物件、播放測試不在這裡——用 `verifying-hero-video-on-mobile`（第 0 層一分鐘）。
