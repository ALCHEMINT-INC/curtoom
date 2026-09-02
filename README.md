English | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

# cutroom

ffmpeg-based skills for coding agents — encode, stitch, and verify video the way it actually ships.

Shared by Claude Code and Codex. One directory per skill: `skills/<name>/SKILL.md` plus the scripts it needs. Project-specific settings (URLs, buckets, CSP hash rules) stay in each project's `CLAUDE.md` / `AGENTS.md`, not here. Skill bodies are currently written in Traditional Chinese; the scripts and their `--help`/usage lines are English.

| skill | what it does |
|---|---|
| `encoding-hero-video-for-mobile` | Master → phone-sized 9:16 hero clip in one command: remux or re-encode automatically, measure per-second bitrate, print PASS / FAIL |
| `verifying-hero-video-on-mobile` | Diagnose and prove background/hero video on phones — "stutters", "won't autoplay", "shows ▶": bitrate ceiling, Chrome throttle harness, iOS Simulator, upload and CDN-cache checks |
| `video-clip-stitching` | Stitch AI-generated clips into one: find cut points, diagnose seams, check generated footage specs |

## Install

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

One line for both agents: skills land in `~/.agents/skills` (Codex) and are symlinked into `~/.claude/skills` (Claude Code). Drop an `-a` to install for one agent only; run `npx skills update` to pull new versions. No `npx`? Clone the repo and symlink `skills/<name>` into those two directories yourself.

## Why these rules

Every rule in these skills was hit in production, not derived. The numbers (bitrate ceilings, thresholds, level limits) come from measurements recorded in each `SKILL.md`.
