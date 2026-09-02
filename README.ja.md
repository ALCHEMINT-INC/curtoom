<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

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

3 つのスキルで 1 本のパイプライン。**STITCH** は分割生成したテイクを使える 1 本にまとめ、**ENCODE** はそれをスマホが実際にストリーミングできるファイルにし、**VERIFY** はページが再生できることを証明します — 何もエンコードせず、任意で使うもの。スマホで不具合が出たとき、または実機なしで出荷前に証拠が欲しいときに。

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**解決する問題** — ノート PC では完璧に再生されるヒーロー動画がスマホでは止まる。実例：1792×3184、CRF 20 の書き出しが 11.7 Mbps / 69 MB。スマホ回線（Chrome「Fast 4G」実測約 7.5 Mbps）では 1 秒再生して 1 秒バッファ、その後フリーズ。

**使いどころ** — スマホ向けの 9:16 背景／ヒーロー動画すべて。すでにスマホでカクつく動画も。

**やること** — コマンド 1 つ。マスターがすでに H.264、1440×2560 以下、6 Mbps 以下なら remux のみ（moov を先頭へ、世代劣化なし）。それ以外は 1440×2560 に縮小、CRF 23 / preset slow、音声はコピー。最後に秒間ビットレートを測り `PASS` か `FAIL: rerun with 1920` を出力。

**なぜ CRF 23 か** — CRF が固定するのは知覚品質であってビットレートではない。同じ CRF 20 でも静かなショットは 6 Mbps、動きの多い素材は 8.6 Mbps — 実測 — そして 8.6 は 7.5 Mbps 回線で止まる。CRF 23 は 5.7 Mbps に収まり、スマホサイズの背景では区別がつかない。1440×2560 を超えるネイティブ解像度は残さない：スマホ画面の最大は 1290×2796、余分な画素は余分なビットレートでしかない。

**効果** — 69 MB → 34.5 MB、11.7 → 5.7 Mbps。46 秒の動画が Fast 4G で最後まで再生され、同時にページは次の動画を先読みしている。

<sub>検証 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**ENCODE との違い** — ファイルには一切触れない。ENCODE は動画を作り、VERIFY はページがそれをスマホで実際に再生できるか、できないなら理由は何かを教える。完全に独立、どちらか一方だけでも使える。

**解決する問題** — スマホでヒーローが止まったとき、*飢餓*（帯域を超えるビットレート）と*ブロック*（自動再生ポリシー、低電力モード、昨日のページを動かし続ける古いタブ）を見分けられない。デスクトップ Chrome で再生できても証拠にならない — デスクトップはどちらの失敗にも当たらない。

**使いどころ** — 設計上、任意。Tier 0 は常に（1 分）。Tier 1 はカクつきの報告があるとき、または出荷前に証拠が欲しいとき。Tier 2 は「自動再生しない」「再生ボタンが出る」という報告のとき。

**やること** — Tier 0：秒間ビットレート上限、`curl --limit-rate` の簡易スクリーニング、ETag = MD5 と先頭 1.5 MB によるアップロード整合性と faststart、アップロード後に push する順序、CDN の range キャッシュの罠。Tier 1：Chrome DevTools のスロットリング環境、`Math.random` を上書きして対象クリップを強制選択。Tier 2：iOS シミュレータでコールドロードとアプリ切替のスクリーンショット差分、iPhone 不要。

**効果** — ページのバグと端末状態を約 5 分で切り分ける。壊れていない visibility ロジックを「修正」せずに済み、同名上書きが 4 時間にわたり新旧混在のバイトを配信する罠（`HEAD` は `DYNAMIC`、range `GET` は `HIT`）も見つけた。

<sub>検証 2026-09-03 · Chrome 140 · iOS 26 シミュレータ</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**解決する問題** — 連鎖生成 — テイク N の最終フレームをテイク N+1 の先頭フレームに渡す — では、続きの各テイクの頭に約 0.5 秒のほぼ静止した「よどみ」が残る。素の `concat` では「止まった」「繰り返した」と見える。フレームは重複していない、動きが途切れている。加えてコンテナのフレームレートは嘘をつく：30 fps の内容を 60 fps で包むと、どのヘッダーも 60 と言う。

**使いどころ** — Dreamina、Runway、Higgsfield、Seedance などの 01 / 02 / 03 シリーズ。「止まる」「繰り返す」「滑らかでない」「重なる」という苦情。生成素材をどこかへ出す前の QC。

**やること** — `clip_qc.py` は 3 種のフレームレート（コンテナ、フレーム密度、実効）を報告し、位相構造で水増しフレームを検出 — 水増し素材は奇偶位相差 7.5×、本物は 1.1× — さらに停滞フレーム比率とプレビュー版の混入も。`seam_probe.py` は各つなぎ目を処理が正反対の 3 種に分類：別ショット → ハードカット、構図の連続 → よどみを切ってディゾルブ、真の重複 → 再演部分を切る。カット点は「つなぎ目後の動き ÷ 前の動き」が 1.0 に近づく値。`join_clips.sh` は 1 パスでエンコードし、`xfade` の offset は手入力ではなく計算、ffmpeg の 3 つの地雷は事前に除去。

**なぜ比率なのか** — 曲線だけを見て 54 フレーム切ると判断したことがあるが、正解は 0 だった — 前のテイクがもともとゆっくり終わっていたので、低い動きは一致していた。同じ曲線でも基準線が違えば結論は逆。見た目が同じ 2 バッチで 30 と 0。

**効果** — 再生に耐えるつなぎ目と、正直な受け入れ手順：尺の照合、つなぎ目のフレーム抜き出し、区間ごとの `volumedetect`。

<sub>検証 2026-09-02 · ffmpeg 8.0</sub>

## 構成

スキルごとに 1 ディレクトリ — `skills/<name>/SKILL.md` と必要なスクリプト。プロジェクト固有の設定（URL、バケット、CSP ハッシュのルール）は各プロジェクトの `CLAUDE.md`／`AGENTS.md` に置き、ここには置きません。スキル本文は繁体字中国語で書かれています。

## なぜこのルールなのか

どの項目も本番で実際にぶつかったものです。数値 — ビットレート上限、しきい値、H.264 level 制限 — は各 `SKILL.md` に記録した実測に基づきます。

<br>

<p align="center"><sub><a href="https://alchemint.xyz">Alchemint</a> 製 · ここにあるルールはすべて一度は授業料を払ったもの</sub></p>
