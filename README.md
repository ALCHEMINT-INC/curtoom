<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>ffmpeg-based skills for coding agents — encode, stitch, and verify video the way it actually ships.</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><b>English</b> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="README.ja.md">日本語</a> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## Install

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

One line, both agents: skills land in `~/.agents/skills` (Codex) and are symlinked into `~/.claude/skills` (Claude Code). Drop an `-a` to install for one agent only; `npx skills update` pulls new versions. No `npx`? Clone and symlink `skills/<name>` into those two directories.

## Skills

Three skills, one pipeline. **STITCH** turns generated takes into one usable clip. **ENCODE** turns that clip into a file phones can actually stream. **VERIFY** proves the page plays it — it encodes nothing and is optional; reach for it when a phone misbehaves or when you want proof before shipping without a phone in hand.

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**The problem** — A hero clip that plays perfectly on a laptop stalls on a phone. The real case: a 1792×3184 CRF 20 export came out at 11.7 Mbps / 69 MB; a phone link (Chrome "Fast 4G" measures about 7.5 Mbps) fed it one second of video per second of buffering, then froze.

**When to use** — Any 9:16 background / hero clip bound for phones, and any phone clip that already stutters.

**What it does** — One command. If the master is already H.264, ≤ 1440×2560 and ≤ 6 Mbps it only remuxes (moov to the front, no generation loss). Otherwise it scales to 1440×2560, encodes CRF 23 / preset slow, copies the audio, then measures per-second bitrate and prints `PASS` or `FAIL: rerun with 1920`.

**Why CRF 23** — CRF pins perceived quality, not bitrate. The same CRF 20 gives 6 Mbps on a calm shot and 8.6 Mbps on high-motion footage — measured — and 8.6 stalls on a 7.5 Mbps link. CRF 23 lands at 5.7 Mbps and is indistinguishable on a phone-sized background. Native resolution above 1440×2560 is never kept: phone screens top out at 1290×2796, so extra pixels are only extra bitrate.

**Payoff** — 69 MB → 34.5 MB, 11.7 → 5.7 Mbps; a 46-second clip plays through on Fast 4G while the page preloads the next clip in parallel.

<sub>Verified 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**How it differs from ENCODE** — It never touches the file. ENCODE produces a clip; VERIFY tells you whether the page will actually play it on a phone, and if not, why. Fully independent — use one without the other.

**The problem** — A phone shows a frozen hero and you cannot tell *starved* (bitrate above bandwidth) from *blocked* (autoplay policy, Low Power Mode, a stale tab still running yesterday's page). Desktop Chrome playing it proves nothing — the desktop hits neither failure.

**When to use** — Optional by design. Tier 0 always (one minute); tier 1 when someone reports stutter or when you want proof before shipping; tier 2 when the report is "no autoplay" or "a play button".

**What it does** — Tier 0: per-second bitrate ceiling, a `curl --limit-rate` quick screen, upload integrity via ETag = MD5 and faststart from the first 1.5 MB, the upload-before-push order, and the CDN range-cache trap. Tier 1: Chrome DevTools throttle harness with the clip picker forced through a `Math.random` override. Tier 2: iOS Simulator cold-load and app-switch screenshot diffs, no iPhone required.

**Payoff** — Separates a page bug from device state in about five minutes. It kept us from "fixing" visibility logic that was never broken, and it surfaced the trap where a same-name overwrite serves mixed old and new bytes for four hours (`HEAD` says `DYNAMIC`, a range `GET` says `HIT`).

<sub>Verified 2026-09-03 · Chrome 140 · iOS 26 Simulator</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**The problem** — Chained generation — feed the last frame of take N as the first frame of take N+1 — leaves every continuation with roughly half a second of near-still "dead water" at its head. Plain `concat` then reads as "it stuck" or "it repeated"; no frame is duplicated, the motion is broken. On top of that, container frame rates lie: 30 fps content packed as 60 fps shows 60 in every header.

**When to use** — Any 01 / 02 / 03 series from Dreamina, Runway, Higgsfield, Seedance and the like; any complaint of "stuck", "repeated", "not smooth", "overlap"; QC of generated footage before it goes anywhere.

**What it does** — `clip_qc.py` reports three frame rates (container, frame density, effective) and detects padded frames by their phase structure — 7.5× odd/even signature on padded footage versus 1.1× on real — plus stalled-frame ratio and preview-vs-HD mix-ups. `seam_probe.py` classifies each seam into one of three types with opposite treatments: different shot → hard cut; composition continuation → cut the dead water and dissolve; true overlap → cut the re-enacted segment. The cut point comes from the ratio of motion after the seam to motion before it, targeting 1.0. `join_clips.sh` encodes in a single pass with the `xfade` offset computed, not typed, and the three ffmpeg landmines pre-defused.

**Why the ratio rule** — A curve-only reading once proposed cutting 54 frames; the answer was 0 — the previous take simply ended slowly, so the low motion matched. Same curve, different baseline, opposite conclusion. Two visually identical batches needed 30 and 0.

**Payoff** — Seams that survive playback, and an honest acceptance step: duration reconciliation, seam frame grabs, segment-wise `volumedetect`.

<sub>Verified 2026-09-02 · ffmpeg 8.0</sub>

## Layout

One directory per skill — `skills/<name>/SKILL.md` plus the scripts it needs. Project-specific settings (URLs, buckets, CSP hash rules) stay in each project's `CLAUDE.md` / `AGENTS.md`, not here. Skill bodies are written in Traditional Chinese; scripts and their usage lines are English.

## Why these rules

Every rule was hit in production, not derived. The numbers — bitrate ceilings, thresholds, H.264 level limits — come from measurements recorded in each `SKILL.md`.

<br>

<p align="center"><sub>Made by <a href="https://alchemint.xyz">Alchemint</a> · every rule here was paid for once already</sub></p>
