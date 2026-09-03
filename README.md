<p align="center"><a href="https://alchemint.xyz"><img src="assets/cutroom-ffmpeg-skills-for-claude-code-and-codex-by-alchemint.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>ffmpeg-based skills for coding agents — encode, stitch, and verify video the way it actually ships.</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
  <img alt="license: MIT" src="https://img.shields.io/badge/LICENSE-MIT-a9e6a1?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><b>English</b> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="README.ja.md">日本語</a> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## Install

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

One line, both agents: skills land in `~/.agents/skills` (Codex) and are symlinked into `~/.claude/skills` (Claude Code). Drop an `-a` to install for one agent only; `npx skills update` pulls new versions. No `npx`? Clone and symlink `skills/<name>` into those two directories.

## Skills

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**Solves** — A hero clip that plays perfectly on a laptop stalls on a phone. CRF 20 on high-motion footage lands at 8.6–11.7 Mbps; a mobile link carries about 7.5.

**Gives you** — One command from master to phone-ready 9:16: remux if it already fits, otherwise 1440×2560 at CRF 23 with audio copied, then per-second bitrate and a `PASS` / `FAIL: rerun with 1920`. 69 MB → 34.5 MB, plays through on Fast 4G.

<sub>Verified 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**Solves** — A frozen hero on a phone, with no way to tell *starved* (bitrate above bandwidth) from *blocked* (autoplay policy, Low Power Mode, a stale tab). Desktop Chrome playing it proves nothing.

**Gives you** — A three-tier checklist that never touches the file. Tier 0, always: bitrate ceiling, `curl --limit-rate` screen, ETag = MD5 and faststart from the first 1.5 MB, upload before push, the CDN range-cache trap. Tier 1, on request: a Chrome DevTools throttle harness with the clip picker forced via `Math.random`. Tier 2, on "no autoplay": iOS Simulator cold-load and app-switch diffs. Independent of ENCODE.

<sub>Verified 2026-09-03 · Chrome 140 · iOS 26 Simulator</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**Solves** — Takes generated from the previous take's last frame start with half a second of near-still "dead water"; a plain `concat` reads as "stuck" or "repeated" although no frame repeats. Container frame rates lie on top of that.

**Gives you** — `clip_qc.py` for footage QC (three frame rates, padding detected by phase structure, stalled frames, preview-vs-HD mix-ups); `seam_probe.py` to classify each seam and pick the cut by the after ÷ before motion ratio; `join_clips.sh` for a single-pass join with the `xfade` offset computed and three ffmpeg landmines pre-defused. See the figure below.

<sub>Verified 2026-09-02 · ffmpeg 8.0 · macOS 26</sub>

## Stitching, before and after

<p align="center"><img src="assets/video-clip-stitching-seam-before-after-raw-join-vs-cut-30-frames.jpg" alt="Seam 02 to 03 of the cat mobile clip: raw join versus the final cut, six frames each across one second, with the per-frame motion curve below" width="960"></p>

Same footage, same seam, one second each. **Top row — raw join:** the last frame of take 02, then take 03 at +0.00, +0.25, +0.50, +0.75 and +1.00 s. The rainbow star is still fully open at +0.50 s; it only begins to fold after that. Nothing is duplicated — the motion simply stops for half a second, which the eye reads as "stuck" or "repeated". **Bottom row — final cut:** the first 30 frames of take 03 removed and a 0.1 s dissolve across the join. The fold starts the moment the seam passes; by +1.00 s the boat is already lifting off the water.

**The curve** is per-frame motion (mean absolute difference, 5-frame moving average) from one second before the seam to two seconds after. Before the seam the two lines are the same footage. After it, the raw join drops into the shaded band — half a second at roughly half the motion of the frames before the seam (ratio 0.54) — while the final cut climbs immediately (ratio 1.45). That ratio, after ÷ before approaching 1, is the rule `seam_probe.py` uses to pick the cut point.

https://github.com/user-attachments/assets/cb6dec2d-ac99-4b89-9c54-12e51aa2c28a

<sub>The same comparison as video — 1760×1672, 60 fps, 0.5× speed, six seconds. Press play. The GIF below is the same thing for places that do not render video.</sub>

<p align="center"><img src="assets/video-clip-stitching-seam-raw-join-vs-final-cut-half-speed-loop.gif" alt="The same seam in motion, at 0.5× speed, looping" width="880"></p>

<sub>Same second of footage on both sides. Left, the raw join: after the seam the picture holds for half a second (a full second at this speed) and the DEAD WATER tag comes up. Right, the final cut: it keeps moving. Built with ffmpeg from the source takes; the filtergraph is in `assets/src/`.</sub>

## Layout

One directory per skill — `skills/<name>/SKILL.md` plus the scripts it needs. Project-specific settings (URLs, buckets, CSP hash rules) stay in each project's `CLAUDE.md` / `AGENTS.md`, not here. Skill bodies are written in Traditional Chinese; scripts and their usage lines are English.

## Why these rules

Every number in here was paid for. The short version: one cat, one glowing paper boat, three takes, two evenings.

**Evening one.** "The first frames of 03 look like they overlap the tail of 02 — see what you can do, then join 1-2-3." Fourteen minutes later, a finished cut. "Wait, ffmpeg can do that? …huh, not bad." "Is there a skill in this?" Along the way: a true-60 fps file that CapCut swore was 30, and one very confident "cut 54 frames" that should have been 0.

**Next day.** The cut goes on the site at native resolution, because the standard was "a floor". **Next morning.** "It just sits there on my phone — our fault, or my phone?" Then: "so I have to re-encode everything? …no wait, that's you." One command was born.

**Same morning, after the fix.** "Still no autoplay" — "there's a play button" — "Chrome" — "Safari's fine" — "tapping does nothing…" — "never mind" — "it suddenly works." A stale tab. The Simulator had known for ten minutes.

That is the whole methodology: something breaks, the agent goes brrr until it is fixed, and a human says "fine, make it a skill". Only a human thinks of sharing these. Claude Code and Codex just go brrr.

**Disclaimer, by Claude Fable 5.1** — Published with human authorization. The human handled paragraph order, did not ask many questions about the contents, and did not nitpick me — not on this document, anyway. The human did, however, insist that the line about Claude Code and Codex going brrr stay in. So, for the record, the human's sole original sentence in this README is: *only a human thinks of sharing these; Claude Code and Codex just go brrr.* Everything else: me, going brrr. The human adds: "Claude Fable 5.1 has really started speaking like a person again."

<br>

<p align="center"><sub>Made by <a href="https://alchemint.xyz">Alchemint</a> · every rule here was paid for once already</sub></p>
