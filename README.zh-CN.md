<p align="center"><a href="https://alchemint.xyz"><img src="assets/cutroom-banner.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>基于 ffmpeg 的 agent skill：压码率、接片段、验播放——按视频实际上线的方式来做。</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
  <img alt="license: MIT" src="https://img.shields.io/badge/LICENSE-MIT-a9e6a1?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><a href="README.md">English</a> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a> &nbsp;·&nbsp; <b>简体中文</b> &nbsp;·&nbsp; <a href="README.ja.md">日本語</a> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## 安装

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

一行装好两边：skill 落在 `~/.agents/skills`（Codex 读），并 symlink 到 `~/.claude/skills`（Claude Code 读）。只装一边就去掉另一个 `-a`；之后 `npx skills update` 更新。不用 `npx` 的话，clone 下来把 `skills/<name>` symlink 到那两个目录即可。

## Skills

一只猫、一艘会发光的纸船、三个 skill。官网的 hero 片是一只猫跟着纸船走进夜晚的街道，分三段生成——每一段都从前一段的最后一帧起头。这个 repo 里的每一条规则，都是两个晚上在这一段素材上撞出来的，顺序就是下面这样。

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**起因** — 2026-09-01 晚上。原话差不多是：「Downloads 里有 cat mobile 01、02、03，03 的前几帧跟 02 的尾巴好像有 overlap，你看一下剪的时候怎么处理，最后把 1、2、3 连起来合成一支。」十四分钟后成片回来了，回复是：「欸？我以为可以用 FFmpeg 处理啊？……我看了一下，还不错啊！」——全程就是 ffmpeg，没开任何剪辑软件。这个意外就是这个 skill 存在的理由，下一句话就是「有啥 skill 可以创造吗」。

**真正的问题** — 不是 overlap。02 的结尾是纸船展开成六角彩虹星，03 的开头是星形收拢回纸船、然后升空。中间那半秒，03 几乎不动——链式生成从参考帧起步时的通病。所以观众看到的是：星星开到顶、停半秒、才收。那个停顿就是「卡住」「好像重复」；没有任何一帧重复，是动作断了。砍掉 30 帧，接缝两侧的运动量比从 0.54 变 1.35，再加 0.1 秒叠化，因为两段材质永远对不完全。

**接着是帧率惊魂** — 「我记得原视频是 60 吧？为什么出来变 30？」——其实没有。剪映显示的是它自己 30 fps 的项目时间轴。实测：2,789 帧里只有 2 帧重复。但一测就测出两个真问题——02 有 13.4% 的停滞帧（生成瑕疵，不是转档），而 Downloads 里的 desktop 03 是 854×480／24 fps 的预览版，不是高清版。这就是为什么 `clip_qc.py` 要报告三种帧率，还用相位结构抓灌水帧（灌水素材奇偶相位差 7.5×，真素材 1.1×）。

**然后是 54 帧的错** — 横版那批看起来一模一样，运动曲线说要砍 54 帧，正解是 0——前一段本来就收得慢，接缝处的低运动量是匹配的。同一条曲线配不同基准线，结论相反。留下来的规则就是：接缝后运动量 ÷ 接缝前运动量要趋近 1（低于 0.75 是死水，高于 1.4 是暴冲）。

**它现在做什么** — `clip_qc.py` 验素材；`seam_probe.py` 把每个接缝分类——不同机位 → 硬切、构图延续 → 砍死水＋叠化、真重叠 → 砍掉被重演的段落；`join_clips.sh` 一次编码完成，`xfade` 的 offset 是算的不是手填的，三个 ffmpeg 地雷事先拆掉。最后一套诚实的验收：时长对账、接缝定格、分段 `volumedetect`。

**收益** — 两支成片（竖版 46.5 秒、横版 45 秒）接缝经得起实际播放，外加一份「哪些该重生成」的清单——那才是人真正需要的部分。

<sub>验证于 2026-09-02 · ffmpeg 8.0 · macOS 26</sub>

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**起因** — 接好的猫片——1792×3184、19 Mbps、112 MB——第二天就进了官网的手机轮播。加它的那个 commit 白纸黑字写着：分辨率标准是下限，所以保留原生尺寸「不缩」。CRF 20 压下来 11.7 Mbps／69 MB。笔记本上看，美极了。

**第二天早上** — 「之前移动端加载后会自动播放，不知道为什么现在会卡在那里。是哪里出问题，还是我手机的问题？」Chrome 的「Fast 4G」实测约 7.5 Mbps。这支片播一秒、等一秒，9.16 秒处冻住。另外三支手机片 5.4–6.6 Mbps，同一条线上全程流畅。

**为什么是 CRF 23** — 缩到手机标准 1440×2560、CRF 20，还是 8.6 Mbps——39 秒卡 5 次。CRF 锁的是感知质量不是码率：同一个 CRF 20，静态镜头 6 Mbps，猫带纸船过马路 8.6。CRF 23 压出 5.7 Mbps，一边预载下一支一边全程流畅；手机大小的背景片分不出 23 跟 20。（当天稍晚：「你说的 CRF 23 是比较好的是吧？相较于 20？」——不是。数字越低质量越高；23 是塞得进水管的那个。）高于 1440×2560 的原生分辨率一律不留：手机屏幕最宽 1290×2796，多的像素只是多的码率。

**「所以我现在全部都要重压是吧？」** — 这是下一个问题——「……不对，是你这边来重新压缩是吧？」一个文件，而且已经压好了。这段对话就是整个 skill 的产品规格：一条命令、不用做决定。

**它做什么** — 母带已经是 H.264、≤ 1440×2560、≤ 6 Mbps 就只 remux（moov 搬到前面，零损耗）；否则 1440×2560、CRF 23、preset slow、音轨原样复制。压完打印每秒码率——平均、p95、峰值——和 `PASS` 或 `FAIL: rerun with 1920`。

**收益** — 69 MB → 34.5 MB、11.7 → 5.7 Mbps，46 秒的片在手机上从头播到尾。

<sub>验证于 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**起因** — 修正版 04:47 上线。接下来依次是：「我手机还是没有自动播放」——「我看到的是播放按钮」——「移动 app Chrome」——「Safari 倒是没问题」——「Chrome 则是连点了播放键都没反应。。。」——「没事」——「突然好了。」二十分钟。bug 是一个还在跑昨天页面、昨天 69 MB 片的 Chrome 标签页；Chrome 自己重载，问题蒸发。

**为什么变成 skill** — 同一时间，这台机器已经开了 iOS 模拟器冷加载网站、切去「设置」再切回来，证明页面会自动播放也会续播。嫌疑人就只剩手机和标签页两个，也让人没去「修」一段根本没坏的 visibility 逻辑。当天下午，草稿版 skill 的测试跑出另一个坑：CDN 上同名覆盖会在四小时内吐出新旧混合的片段（`HEAD` 说 `DYNAMIC`，range `GET` 才说 `HIT`）。两件事都直接进了检查表。

**跟 ENCODE 的区别** — 它完全不碰文件。ENCODE 产片；VERIFY 回答「页面在手机上到底播不播得出来，不播是为什么」。两者独立，各用各的。

**什么时候用** — 设计上就是选用。第 0 层一律做（一分钟）；有人反馈卡顿、或想在没手机的情况下先拿证据才做第 1 层；反馈「不自动播放」「有播放键」才做第 2 层——而且第一步是请他关标签页重开。

**它做什么** — 第 0 层：每秒码率门槛、`curl --limit-rate` 快筛、ETag＝MD5 与前 1.5 MB 验上传完整与 faststart、先上传再 push 的顺序、CDN range 缓存的坑。第 1 层：Chrome DevTools 限速测试台，覆写 `Math.random` 强制抽到你要测的那支。第 2 层：iOS 模拟器冷加载与切 app 的截图比对。

**收益** — 五分钟内把「饿死」和「被挡」分开，靠证据不靠直觉。

<sub>验证于 2026-09-03 · Chrome 140 · iOS 26 模拟器</sub>

## ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**解决的问题** — 笔记本上播得好好的 hero 片，到手机上一顿一顿。实际案例：1792×3184、CRF 20 的成品压出 11.7 Mbps／69 MB；手机网络（Chrome「Fast 4G」实测约 7.5 Mbps）喂它一秒播一秒等，然后冻住。

**什么时候用** — 任何要上手机的 9:16 背景／hero 片，以及已经在手机上卡的片。

**它做什么** — 一条命令。母带已经是 H.264、≤ 1440×2560、≤ 6 Mbps 就只 remux（moov 搬到前面，零损耗）；否则缩到 1440×2560、CRF 23、preset slow、音轨原样复制，压完测每秒码率，打印 `PASS` 或 `FAIL: rerun with 1920`。

**为什么是 CRF 23** — CRF 锁的是感知质量，不是码率。同一个 CRF 20，静态镜头 6 Mbps、高运动量素材 8.6 Mbps——实测——而 8.6 在 7.5 Mbps 的线路上就是卡。CRF 23 落在 5.7 Mbps，手机大小的背景片看不出差别。高于 1440×2560 的原生分辨率一律不留：手机屏幕最宽 1290×2796，多的像素只是多的码率。

**收益** — 69 MB → 34.5 MB、11.7 → 5.7 Mbps；46 秒的片在 Fast 4G 下从头播到尾，同时页面还在后台预载下一支。

<sub>验证于 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**跟 ENCODE 的区别** — 它完全不碰文件。ENCODE 产出一支片；VERIFY 告诉你页面在手机上到底播不播得出来、不播是为什么。两者独立，各用各的。

**解决的问题** — 手机上 hero 不动，你分不清是**饿死**（码率高过带宽）还是**被挡**（自动播放策略、低电量模式、一个还在跑昨天页面的旧标签页）。桌面 Chrome 播得动不算证据——桌面两种失败都碰不到。

**什么时候用** — 设计上就是选用。第 0 层一律做（一分钟）；有人反馈卡顿、或上线前想拿证据才做第 1 层；反馈「不自动播放」「出现播放键」才做第 2 层。

**它做什么** — 第 0 层：每秒码率门槛、`curl --limit-rate` 快筛、用 ETag＝MD5 与前 1.5 MB 验上传完整与 faststart、先上传再 push 的顺序、CDN range 缓存的坑。第 1 层：Chrome DevTools 限速测试台，用覆写 `Math.random` 强制抽到目标片。第 2 层：iOS 模拟器冷加载与切 app 的截图比对，不需要 iPhone。

**收益** — 五分钟内把「页面有 bug」和「设备状态」分开。它让我们没有去「修」一段根本没坏的 visibility 逻辑，还挖出同名覆盖会在四小时内吐出新旧混合片段的坑（`HEAD` 说 `DYNAMIC`，range `GET` 才说 `HIT`）。

<sub>验证于 2026-09-03 · Chrome 140 · iOS 26 模拟器</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**解决的问题** — 链式生成——拿第 N 段的尾帧当第 N+1 段的首帧——每一段续生的开头都会有约半秒几乎不动的「死水」。直接 `concat` 看起来就是「卡住了」「好像重复」；其实没有任何一帧重复，是动作断了。再加上容器帧率会骗人：30 fps 的内容包成 60 fps，每个头都写 60。

**什么时候用** — Dreamina、Runway、Higgsfield、Seedance 这类 01／02／03 分段生成的系列；任何「卡住」「重复」「不顺」「有 overlap」的抱怨；生成素材送去任何地方之前的验收。

**它做什么** — `clip_qc.py` 报告三种帧率（容器、帧密度、有效），用相位结构抓灌水帧——灌水素材的奇偶相位差 7.5×，真素材 1.1×——外加停滞帧比例与预览版混进高清版的情况。`seam_probe.py` 把每个接缝分成三种处理相反的类型：不同机位 → 硬切；构图延续 → 砍死水＋叠化；真重叠 → 砍掉被重演的段落。切点由「接缝后运动量 ÷ 接缝前运动量」决定，目标趋近 1。`join_clips.sh` 一次编码完成，`xfade` 的 offset 是算出来的不是手填的，三个 ffmpeg 地雷事先拆掉。

**为什么是比值** — 只看曲线曾经推出要砍 54 帧，正解是 0——前一段本来就收得慢，后段开头的低运动量是匹配的。同一条曲线配不同基准线，结论相反。两批看起来一模一样的素材，切点分别是 30 和 0。

**收益** — 接缝经得起实际播放，还有一套诚实的验收：时长对账、接缝定格、分段 `volumedetect`。

<sub>验证于 2026-09-02 · ffmpeg 8.0</sub>

## 目录结构

每个 skill 一个目录——`skills/<name>/SKILL.md` 加上它需要的脚本。项目专属的设置（网址、bucket、CSP hash 规则）留在各项目的 `CLAUDE.md`／`AGENTS.md`，不放这里。Skill 正文以繁体中文撰写。

## 为什么是这些规则

每一条都是实际踩出来的，不是推导出来的。数字——码率上限、阈值、H.264 level 上限——都来自各 `SKILL.md` 里记录的实测。

<br>

<p align="center"><sub>由 <a href="https://alchemint.xyz">Alchemint</a> 制作 · 这里每一条规则都已经交过一次学费</sub></p>
