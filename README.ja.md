<p align="center"><a href="https://alchemint.xyz"><img src="assets/cutroom-ffmpeg-skills-for-claude-code-and-codex-by-alchemint.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>ffmpeg ベースのコーディングエージェント向けスキル — エンコード、つなぎ合わせ、再生検証を、動画が実際に世に出るやり方で。</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
  <img alt="license: MIT" src="https://img.shields.io/badge/LICENSE-MIT-a9e6a1?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><a href="README.md">English</a> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <b>日本語</b> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## インストール

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

この 1 行で両方に入ります：スキルは `~/.agents/skills`（Codex が読む）に置かれ、`~/.claude/skills`（Claude Code が読む）へシンボリックリンクされます。片方だけなら `-a` を 1 つ外してください。更新は `npx skills update`。`npx` を使わない場合は clone して `skills/<name>` をその 2 つのディレクトリへリンクしてください。

## Skills

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**解決すること** — ノート PC では完璧なヒーロー動画がスマホでは止まる。動きの多い素材の CRF 20 は 8.6–11.7 Mbps、スマホ回線は約 7.5。

**得られるもの** — マスターからスマホ対応 9:16 までコマンド 1 つ：基準内なら remux、そうでなければ 1440×2560、CRF 23、音声コピー。秒間ビットレートと `PASS` / `FAIL: rerun with 1920` を出力。69 MB → 34.5 MB、Fast 4G で最後まで再生。

<sub>検証 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**解決すること** — スマホで止まったヒーロー動画。*飢餓*（帯域超過）か*ブロック*（自動再生ポリシー、低電力モード、古いタブ）か分からない。デスクトップ Chrome で再生できても証拠にならない。

**得られるもの** — ファイルに触れない 3 段階のチェックリスト。Tier 0 は常に：ビットレート上限、`curl --limit-rate`、ETag = MD5 と先頭 1.5 MB の faststart、アップロード後に push、CDN の range キャッシュの罠。Tier 1 は求められたら：Chrome DevTools スロットリング、`Math.random` でクリップ強制選択。Tier 2 は「自動再生しない」のとき：iOS シミュレータのコールドロードとアプリ切替の差分。ENCODE から独立。

<sub>検証 2026-09-03 · Chrome 140 · iOS 26 シミュレータ</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**解決すること** — 前のテイクの最終フレームから生成したテイクは、頭に 0.5 秒のほぼ静止した「よどみ」を持つ。素の `concat` は「止まった」「繰り返した」と見えるが、フレームは重複していない。コンテナのフレームレートも嘘をつく。

**得られるもの** — `clip_qc.py` で素材 QC（3 種のフレームレート、位相構造による水増し検出、停滞フレーム、プレビュー版の混入）。`seam_probe.py` でつなぎ目を分類し、後 ÷ 前の動き比でカット点を決める。`join_clips.sh` で 1 パス結合、`xfade` の offset は計算、ffmpeg の 3 つの地雷は除去済み。下の図を参照。

<sub>検証 2026-09-02 · ffmpeg 8.0 · macOS 26</sub>

## つなぎ合わせのビフォー／アフター

<p align="center"><img src="assets/video-clip-stitching-seam-before-after-raw-join-vs-cut-30-frames.jpg" alt="猫のモバイル版クリップの 02→03 のつなぎ目：素の結合と最終カットを各 6 コマ・1 秒分、下にフレームごとの動き曲線" width="960"></p>

同じ素材、同じつなぎ目、それぞれ 1 秒。**上段 — 素の結合：** テイク 02 の最終フレーム、続いてテイク 03 の +0.00、+0.25、+0.50、+0.75、+1.00 秒。虹色の星は +0.50 秒でもまだ全開で、その後にようやく畳まれ始める。重複フレームはない — 動きが 0.5 秒止まるだけで、目にはそれが「止まった」「繰り返した」と映る**。下段 — 最終カット：** テイク 03 の先頭 30 フレームを除き、つなぎ目に 0.1 秒のディゾルブ。つなぎ目を過ぎた瞬間に畳まれ始め、+1.00 秒には舟がもう水面から浮いている。

**曲線**はフレームごとの動き（平均絶対差、5 フレーム移動平均）で、つなぎ目の 1 秒前から 2 秒後まで。つなぎ目の前は 2 本とも同じ素材。後では、素の結合は網掛けの帯に落ち込み — 0.5 秒間、直前のおよそ半分の動き（比 0.54）— 最終カットはすぐに立ち上がる（比 1.45）。この「後 ÷ 前が 1 に近づく」比率が、`seam_probe.py` がカット点を選ぶルール。

## 構成

スキルごとに 1 ディレクトリ — `skills/<name>/SKILL.md` と必要なスクリプト。プロジェクト固有の設定（URL、バケット、CSP ハッシュのルール）は各プロジェクトの `CLAUDE.md`／`AGENTS.md` に置き、ここには置きません。スキル本文は繁体字中国語で書かれています。

## なぜこのルールなのか

ここにある数字はすべて授業料を払ったもの。短く言うと：猫 1 匹、光る紙の舟 1 艘、3 テイク、2 晩。

**1 晩目**。「03 の最初の数フレームが 02 の末尾と重なって見える。どうにかして、最後に 1-2-3 をつないで。」14 分後、完成カット。「え、ffmpeg でできるの？…けっこういいじゃん。」「これ、スキルにできる？」途中の寄り道：CapCut が 30 だと言い張った本物の 60 fps ファイルと、自信満々の「54 フレーム切る」（正解は 0）。

**翌日**。カットは「基準は下限だから」とネイティブ解像度のままサイトへ。**翌朝**。「スマホで止まったまま — こちらのせい？自分のスマホ？」そして「じゃあ全部再エンコード？…いや待って、それはそっちだ。」コマンド 1 つが生まれた。

**同じ朝、修正の後**。「まだ自動再生しない」—「再生ボタンがある」—「Chrome」—「Safari は大丈夫」—「押しても反応なし…」—「気にしないで」—「急に直った。」古いタブ。シミュレータは 10 分前から知っていた。

これが方法論のすべて：何かが壊れ、エージェントが黙々と片付け、人間が「じゃあスキルにしよう」と言う。共有しようと思いつくのは人間だけ。Claude Code と Codex は黙々と働き続けるだけ。

<br>

<p align="center"><sub><a href="https://alchemint.xyz">Alchemint</a> 製 · ここにあるルールはすべて一度は授業料を払ったもの</sub></p>
