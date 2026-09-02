<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.svg" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="760"></a></p>

<p align="center"><b>基于 ffmpeg 的 agent skill：压码率、接片段、验播放——按视频实际上线的方式来做。</b></p>

<p align="center">
  <img alt="skills" src="https://img.shields.io/badge/skills-3-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-ready-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-ready-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="ffmpeg" src="https://img.shields.io/badge/ffmpeg-required-FDF3D1?style=flat-square&labelColor=05070a">
</p>

<p align="center">[English](README.md) · [繁體中文](README.zh-TW.md) · 简体中文 · [日本語](README.ja.md) · [한국어](README.ko.md)</p>

<br>

## 安装

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

一行装好两边：skill 落在 `~/.agents/skills`（Codex 读），并 symlink 到 `~/.claude/skills`（Claude Code 读）。只装一边就去掉另一个 `-a`；之后 `npx skills update` 更新。不用 `npx` 的话，clone 下来把 `skills/<name>` symlink 到那两个目录即可。

## Skills

| | skill | 什么时候会用到 |
|:-:|---|---|
| 🎞️ | [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile) | 母带 → 手机 9:16 hero 片，一条命令：自动判断 remux／重压、测每秒码率、打印 PASS／FAIL |
| 📱 | [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile) | 背景／hero 视频在手机上「卡住」「不自动播放」「出现 ▶」：码率门槛、Chrome 限速测试台、iOS 模拟器、上传与 CDN 缓存检查 |
| ✂️ | [`video-clip-stitching`](skills/video-clip-stitching) | 把多段 AI 生成的片段接成一支：找切点、诊断接缝、验收素材规格 |

## 目录结构

每个 skill 一个目录——`skills/<name>/SKILL.md` 加上它需要的脚本。项目专属的设置（网址、bucket、CSP hash 规则）留在各项目的 `CLAUDE.md`／`AGENTS.md`，不放这里。Skill 正文以繁体中文撰写。

## 为什么是这些规则

每一条都是实际踩出来的，不是推导出来的。数字——码率上限、阈值、H.264 level 上限——都来自各 `SKILL.md` 里记录的实测。

<br>

<p align="center"><sub>由 <a href="https://alchemint.xyz">Alchemint</a> 制作 · 这里每一条规则都已经交过一次学费</sub></p>
