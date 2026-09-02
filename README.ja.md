[English](README.md) | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md) | 日本語

# cutroom

ffmpeg ベースのコーディングエージェント向けスキル — エンコード、つなぎ合わせ、再生検証を、動画が実際に世に出るやり方で。

Claude Code と Codex で共用。スキルごとに 1 ディレクトリ：`skills/<name>/SKILL.md` と必要なスクリプト。プロジェクト固有の設定（URL、バケット、CSP ハッシュのルール）は各プロジェクトの `CLAUDE.md`／`AGENTS.md` に置き、ここには置きません。スキル本文は現在、繁体字中国語で書かれています。

| skill | 内容 |
|---|---|
| `encoding-hero-video-for-mobile` | マスター → スマホ向け 9:16 ヒーロー動画をコマンド 1 つで：remux か再エンコードかを自動判定、秒間ビットレートを計測、PASS / FAIL を出力 |
| `verifying-hero-video-on-mobile` | 背景／ヒーロー動画がスマホで「カクつく」「自動再生しない」「▶ が出る」ときの切り分けと検証：ビットレート上限、Chrome スロットリング環境、iOS シミュレータ、アップロードと CDN キャッシュの確認 |
| `video-clip-stitching` | AI 生成クリップを 1 本につなぐ：カット点の探索、つなぎ目の診断、生成素材の仕様チェック |

## インストール（マシンごとに 1 回）

```sh
git clone https://github.com/ALCHEMINT-INC/curtoom.git ~/Documents/cutroom
mkdir -p ~/.claude/skills ~/.agents/skills
for s in ~/Documents/cutroom/skills/*/; do
  n=$(basename "$s"); ln -sfn "$s" ~/.claude/skills/"$n"; ln -sfn "$s" ~/.agents/skills/"$n"
done
```

Claude Code は `~/.claude/skills`、Codex は `~/.agents/skills` を読みます。どちらもシンボリックリンクなので、ここを編集すればすぐ反映されます。

## なぜこのルールなのか

どの項目も本番で実際にぶつかったものです。数値（ビットレート上限、しきい値、level 制限）は各 `SKILL.md` に記録した実測に基づきます。
