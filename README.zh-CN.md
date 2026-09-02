[English](README.md) | [繁體中文](README.zh-TW.md) | 简体中文 | [日本語](README.ja.md)

# cutroom

基于 ffmpeg 的 agent skill：压码率、接片段、验播放——按视频实际上线的方式来做。

Claude Code 与 Codex 共用。每个 skill 一个目录：`skills/<name>/SKILL.md` 加上它需要的脚本。项目专属的设置（网址、bucket、CSP hash 规则）留在各项目的 `CLAUDE.md`／`AGENTS.md`，不放这里。Skill 正文目前以繁体中文撰写。

| skill | 用途 |
|---|---|
| `encoding-hero-video-for-mobile` | 母带 → 手机 9:16 hero 片，一条命令：自动判断 remux／重压、测每秒码率、打印 PASS／FAIL |
| `verifying-hero-video-on-mobile` | 背景／hero 视频在手机上「卡住」「不自动播放」「出现 ▶」的判读与验证：码率门槛、Chrome 限速测试台、iOS 模拟器、上传与 CDN 缓存检查 |
| `video-clip-stitching` | 把多段 AI 生成的片段接成一支：找切点、诊断接缝、验收素材规格 |

## 安装（每台机器一次）

```sh
git clone https://github.com/ALCHEMINT-INC/curtoom.git ~/Documents/cutroom
mkdir -p ~/.claude/skills ~/.agents/skills
for s in ~/Documents/cutroom/skills/*/; do
  n=$(basename "$s"); ln -sfn "$s" ~/.claude/skills/"$n"; ln -sfn "$s" ~/.agents/skills/"$n"
done
```

Claude Code 读 `~/.claude/skills`，Codex 读 `~/.agents/skills`；两边都是 symlink，改这里即生效。

## 为什么是这些规则

每一条都是实际踩出来的，不是推导出来的。数字（码率上限、阈值、level 上限）都来自各 `SKILL.md` 里记录的实测。
