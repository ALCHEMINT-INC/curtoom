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

|  | skill | when your agent reaches for it |
|:--|:--|:--|
| <img alt="ENCODE" src="https://img.shields.io/badge/ENCODE-ffe45d?style=flat-square"> | [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile) | Master → phone-sized 9:16 hero clip in one command: remux or re-encode automatically, measure per-second bitrate, print PASS / FAIL |
| <img alt="VERIFY" src="https://img.shields.io/badge/VERIFY-9dc6ff?style=flat-square"> | [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile) | Background / hero video on phones — "stutters", "won't autoplay", "shows a play button": bitrate ceiling, Chrome throttle harness, iOS Simulator, upload and CDN-cache checks |
| <img alt="STITCH" src="https://img.shields.io/badge/STITCH-ff9fc6?style=flat-square"> | [`video-clip-stitching`](skills/video-clip-stitching) | Stitch AI-generated clips into one: find cut points, diagnose seams, check generated footage specs |

## Layout

One directory per skill — `skills/<name>/SKILL.md` plus the scripts it needs. Project-specific settings (URLs, buckets, CSP hash rules) stay in each project's `CLAUDE.md` / `AGENTS.md`, not here. Skill bodies are written in Traditional Chinese; scripts and their usage lines are English.

## Why these rules

Every rule was hit in production, not derived. The numbers — bitrate ceilings, thresholds, H.264 level limits — come from measurements recorded in each `SKILL.md`.

<br>

<p align="center"><sub>Made by <a href="https://alchemint.xyz">Alchemint</a> · every rule here was paid for once already</sub></p>
