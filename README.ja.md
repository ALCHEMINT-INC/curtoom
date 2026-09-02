<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>ffmpeg ベースのコーディングエージェント向けスキル — エンコード、つなぎ合わせ、再生検証を、動画が実際に世に出るやり方で。</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><a href="README.md">English</a> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <b>日本語</b> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## インストール

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

この 1 行で両方に入ります：スキルは `~/.agents/skills`（Codex が読む）に置かれ、`~/.claude/skills`（Claude Code が読む）へシンボリックリンクされます。片方だけなら `-a` を 1 つ外してください。更新は `npx skills update`。`npx` を使わない場合は clone して `skills/<name>` をその 2 つのディレクトリへリンクしてください。

## Skills

| skill | 使いどころ |
|:--|:--|
| [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile) | **ENCODE** · マスター → スマホ向け 9:16 ヒーロー動画をコマンド 1 つで：remux か再エンコードかを自動判定、秒間ビットレートを計測、PASS / FAIL を出力 |
| [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile) | **VERIFY** · 背景／ヒーロー動画がスマホで「カクつく」「自動再生しない」「再生ボタンが出る」：ビットレート上限、Chrome スロットリング環境、iOS シミュレータ、アップロードと CDN キャッシュの確認 |
| [`video-clip-stitching`](skills/video-clip-stitching) | **STITCH** · AI 生成クリップを 1 本につなぐ：カット点の探索、つなぎ目の診断、生成素材の仕様チェック |

## 構成

スキルごとに 1 ディレクトリ — `skills/<name>/SKILL.md` と必要なスクリプト。プロジェクト固有の設定（URL、バケット、CSP ハッシュのルール）は各プロジェクトの `CLAUDE.md`／`AGENTS.md` に置き、ここには置きません。スキル本文は繁体字中国語で書かれています。

## なぜこのルールなのか

どの項目も本番で実際にぶつかったものです。数値 — ビットレート上限、しきい値、H.264 level 制限 — は各 `SKILL.md` に記録した実測に基づきます。

<br>

<p align="center"><sub><a href="https://alchemint.xyz">Alchemint</a> 製 · ここにあるルールはすべて一度は授業料を払ったもの</sub></p>
