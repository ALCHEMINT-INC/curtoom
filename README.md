<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.svg" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="760"></a></p>

<p align="center"><b>ffmpeg-based skills for coding agents — encode, stitch, and verify video the way it actually ships.</b></p>

<p align="center">
  <img alt="skills" src="https://img.shields.io/badge/skills-3-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-ready-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-ready-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="ffmpeg" src="https://img.shields.io/badge/ffmpeg-required-FDF3D1?style=flat-square&labelColor=05070a">
</p>

<p align="center">English · [繁體中文](README.zh-TW.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)</p>

<br>

## Install

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

One line, both agents: skills land in `~/.agents/skills` (Codex) and are symlinked into `~/.claude/skills` (Claude Code). Drop an `-a` to install for one agent only; `npx skills update` pulls new versions. No `npx`? Clone and symlink `skills/<name>` into those two directories.

## Skills

| | skill | when your agent reaches for it |
|:-:|---|---|
| 🎞️ | [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile) | Master → phone-sized 9:16 hero clip in one command: remux or re-encode automatically, measure per-second bitrate, print PASS / FAIL |
| 📱 | [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile) | Background / hero video on phones — "stutters", "won't autoplay", "shows ▶": bitrate ceiling, Chrome throttle harness, iOS Simulator, upload and CDN-cache checks |
| ✂️ | [`video-clip-stitching`](skills/video-clip-stitching) | Stitch AI-generated clips into one: find cut points, diagnose seams, check generated footage specs |

## Layout

One directory per skill — `skills/<name>/SKILL.md` plus the scripts it needs. Project-specific settings (URLs, buckets, CSP hash rules) stay in each project's `CLAUDE.md` / `AGENTS.md`, not here. Skill bodies are written in Traditional Chinese; scripts and their usage lines are English.

## Why these rules

Every rule was hit in production, not derived. The numbers — bitrate ceilings, thresholds, H.264 level limits — come from measurements recorded in each `SKILL.md`.

<br>

<p align="center"><sub>Made by <a href="https://alchemint.xyz">Alchemint</a> · every rule here was paid for once already</sub></p>
