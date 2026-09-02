<p align="center"><a href="https://alchemint.xyz"><img src="assets/cutroom-ffmpeg-skills-for-claude-code-and-codex-by-alchemint.png" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="960"></a></p>

<p align="center"><b>ffmpeg-based skills for coding agents — encode, stitch, and verify video the way it actually ships.</b></p>

<p align="center">
  <img alt="skills: 3" src="https://img.shields.io/badge/SKILLS-3-ffe45d?style=for-the-badge&labelColor=141414">
  <img alt="Claude Code" src="https://img.shields.io/badge/CLAUDE_CODE-READY-9dc6ff?style=for-the-badge&labelColor=141414">
  <img alt="Codex" src="https://img.shields.io/badge/CODEX-READY-c7afff?style=for-the-badge&labelColor=141414">
  <img alt="ffmpeg" src="https://img.shields.io/badge/FFMPEG-REQUIRED-ff9fc6?style=for-the-badge&labelColor=141414">
  <img alt="license: MIT" src="https://img.shields.io/badge/LICENSE-MIT-a9e6a1?style=for-the-badge&labelColor=141414">
</p>

<p align="center"><b>English</b> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="README.ja.md">日本語</a> &nbsp;·&nbsp; <a href="README.ko.md">한국어</a></p>

<br>

## Install

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

One line, both agents: skills land in `~/.agents/skills` (Codex) and are symlinked into `~/.claude/skills` (Claude Code). Drop an `-a` to install for one agent only; `npx skills update` pulls new versions. No `npx`? Clone and symlink `skills/<name>` into those two directories.

## Skills

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**Problem** — A hero clip that plays perfectly on a laptop stalls on a phone: 1792×3184 at CRF 20 came out at 11.7 Mbps / 69 MB, and a ~7.5 Mbps mobile link fed it one second of video per second of buffering.

**When** — Any 9:16 background / hero clip bound for phones; any phone clip that already stutters.

**What** — One command. Remux only if the master already fits (H.264, ≤ 1440×2560, ≤ 6 Mbps); otherwise 1440×2560, CRF 23, preset slow, audio copied. Prints per-second bitrate and `PASS` or `FAIL: rerun with 1920`.

**Why CRF 23** — CRF pins perceived quality, not bitrate: CRF 20 is 6 Mbps on a calm shot and 8.6 on high motion — and 8.6 stalls. CRF 23 lands at 5.7 and is indistinguishable on a phone-sized background. Nothing above 1440×2560 is kept; phone screens top out at 1290×2796.

**Payoff** — 69 MB → 34.5 MB, 11.7 → 5.7 Mbps, plays through on Fast 4G with the next clip preloading.

<sub>Verified 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**Problem** — A frozen hero on a phone, and no way to tell *starved* (bitrate above bandwidth) from *blocked* (autoplay policy, Low Power Mode, a stale tab). Desktop Chrome playing it proves nothing.

**Difference from ENCODE** — Touches no file. ENCODE makes the clip; VERIFY answers "will the page play it on a phone, and if not, why". Independent — use either alone.

**When** — Optional. Tier 0 always (one minute); tier 1 on a stutter report or for proof before shipping without a phone; tier 2 on "no autoplay" / "a play button" — and the first move there is closing the tab and reopening.

**What** — Tier 0: bitrate ceiling, `curl --limit-rate` screen, ETag = MD5 and faststart from the first 1.5 MB, upload-before-push, the CDN range-cache trap. Tier 1: Chrome DevTools throttle harness with the clip picker forced via `Math.random`. Tier 2: iOS Simulator cold-load and app-switch screenshot diffs.

**Payoff** — Page bug versus device state, separated in about five minutes with evidence.

<sub>Verified 2026-09-03 · Chrome 140 · iOS 26 Simulator</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**Problem** — Chained generation — last frame of take N becomes the first frame of take N+1 — leaves every continuation with about half a second of near-still "dead water". Plain `concat` reads as "stuck" or "repeated"; no frame repeats, the motion breaks. Container frame rates also lie.

**When** — Any 01 / 02 / 03 series from Dreamina, Runway, Higgsfield, Seedance and the like; any "stuck / repeated / not smooth / overlap" complaint; QC of generated footage.

**What** — `clip_qc.py` reports three frame rates and catches padded frames by phase structure (7.5× odd/even signature vs 1.1× real), stalled frames, preview-vs-HD mix-ups. `seam_probe.py` classifies each seam — different shot → hard cut; composition continuation → cut the dead water and dissolve; true overlap → cut the re-enacted part. `join_clips.sh` encodes in one pass with the `xfade` offset computed and three ffmpeg landmines pre-defused.

**Why a ratio** — The cut point is where motion after the seam ÷ motion before it approaches 1.0 (below 0.75 is dead water, above 1.4 a lurch). A curve-only reading once said cut 54 frames; the answer was 0.

**Payoff** — Seams that survive playback — see below.

<sub>Verified 2026-09-02 · ffmpeg 8.0 · macOS 26</sub>

## Stitching, before and after

<p align="center"><img src="assets/video-clip-stitching-seam-before-after-raw-join-vs-cut-30-frames.jpg" alt="Seam 02 to 03 of the cat mobile clip: raw join versus the final cut, six frames each across one second, with the per-frame motion curve below" width="960"></p>

Same footage, same seam, one second each. **Top row — raw join:** the last frame of take 02, then take 03 at +0.00, +0.25, +0.50, +0.75 and +1.00 s. The rainbow star is still fully open at +0.50 s; it only begins to fold after that. Nothing is duplicated — the motion simply stops for half a second, which the eye reads as "stuck" or "repeated". **Bottom row — final cut:** the first 30 frames of take 03 removed and a 0.1 s dissolve across the join. The fold starts the moment the seam passes; by +1.00 s the boat is already lifting off the water.

**The curve** is per-frame motion (mean absolute difference, 5-frame moving average) from one second before the seam to two seconds after. Before the seam the two lines are the same footage. After it, the raw join drops into the shaded band — half a second at roughly half the motion of the frames before the seam (ratio 0.54) — while the final cut climbs immediately (ratio 1.45). That ratio, after ÷ before approaching 1, is the rule `seam_probe.py` uses to pick the cut point.

## STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**How it started** — Evening of 2026-09-01. The ask, more or less verbatim: "There's cat mobile 01, 02, 03 in Downloads. The first frames of 03 look like they overlap the tail of 02 — figure out how to handle that, then join 1-2-3 into one video." Fourteen minutes later a finished file came back, and the reply was: "Wait, I thought you could do this with ffmpeg? …huh, that looks pretty good." It had been done entirely in ffmpeg, no editor. That surprise is the reason this skill exists — the very next question was "is there a skill to be made out of this?"

**What was actually wrong** — Not overlap. Take 02 ends with the paper boat unfolding into a six-pointed rainbow star; take 03 opens with the star folding back into a boat before it lifts off. Between them, 03's first half second barely moves — chained generation warms up from its reference frame. So: star opens to the top, freezes for half a second, then folds. That freeze is what reads as "stuck" or "repeated". Not one frame is duplicated; the motion is broken. Cutting 30 frames took the motion ratio across the seam from 0.54 to 1.35, plus a 0.1 s dissolve because the textures never match exactly.

**Then the frame-rate scare** — "I thought the originals were 60 fps — why did the output come out 30?" It hadn't. CapCut was showing its own 30 fps project timeline. Measured: 2 duplicate frames in 2,789. But the measuring turned up two real problems — take 02 had 13.4 % stalled frames (a generation defect, not a conversion), and the desktop 03 in Downloads was the 854×480 / 24 fps preview download, not the HD one. That is why `clip_qc.py` reports three different frame rates and detects padding by phase structure (7.5× odd/even signature on padded footage, 1.1× on real).

**Then the 54-frame mistake** — The desktop batch looked identical. The motion curve said cut 54 frames. The answer was 0 — the previous take simply ended slowly, so the low motion at the seam matched it. Same curve, different baseline, opposite conclusion. Hence the rule that survived: the ratio of motion after the seam to motion before it should approach 1.0 (below 0.75 is dead water, above 1.4 is a lurch).

**What it does now** — `clip_qc.py` for footage QC, `seam_probe.py` to classify each seam — different shot → hard cut, composition continuation → cut the dead water and dissolve, true overlap → cut the re-enacted part — and `join_clips.sh` for a single-pass encode with the `xfade` offset computed, not typed, and three ffmpeg landmines pre-defused. Then an honest acceptance: duration reconciliation, seam frame grabs, segment-wise `volumedetect`.

**Payoff** — Two finished cuts (46.5 s portrait, 45 s landscape) with seams that survive playback, and a list of what to regenerate — which is the part a human actually needs.

<sub>Verified 2026-09-02 · ffmpeg 8.0 · macOS 26</sub>

### ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**How it started** — The stitched cat clip — 1792×3184, 19 Mbps, 112 MB — went into the site's mobile rotation the next day. The commit that added it said, in so many words, that the resolution standard was a floor, so the native size was kept "rather than resampled down". CRF 20 brought it to 11.7 Mbps / 69 MB. On a laptop it was gorgeous.

**Next morning** — "It used to autoplay on mobile. Now it just sits there. Is it something on our side or is it my phone?" Chrome's "Fast 4G" throttle measures about 7.5 Mbps. The clip played one second, buffered one second, and froze at 9.16 s. The other three mobile clips, at 5.4–6.6 Mbps, played through on the same throttle without a hiccup.

**Why CRF 23** — Scaling to the mobile standard, 1440×2560, at CRF 20 still gave 8.6 Mbps — five stalls in 39 seconds. CRF pins perceived quality, not bitrate: the same CRF 20 lands at 6 Mbps on a calm shot and 8.6 on a cat and a boat crossing a street. CRF 23 came out at 5.7 Mbps and played through with the next clip preloading in parallel. On a phone-sized background you cannot tell 23 from 20. (Later that day: "so CRF 23 is *better* than 20, right?" — no. Lower is higher quality; 23 is the one that fits through the pipe.) Anything above 1440×2560 is never kept: phone screens top out at 1290×2796, extra pixels are only extra bitrate.

**"So I have to re-encode everything?"** — That was the next question — "…no wait, you're the one re-encoding, right?" One file, and it was already done. That exchange is the whole product spec: one command, no decisions.

**What it does** — If the master is already H.264, ≤ 1440×2560 and ≤ 6 Mbps, it only remuxes (moov to the front, zero generation loss). Otherwise 1440×2560, CRF 23, preset slow, audio copied. Then per-second bitrate — average, p95, peak — and `PASS` or `FAIL: rerun with 1920`.

**Payoff** — 69 MB → 34.5 MB, 11.7 → 5.7 Mbps, a 46-second clip that plays through on a phone.

<sub>Verified 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**How it started** — The fix went live at 04:47. Then, in order: "still doesn't autoplay on my phone" — "I see a play button" — "mobile Chrome app" — "Safari is fine" — "in Chrome even tapping play does nothing…" — "never mind" — "it suddenly works." Twenty minutes. The bug was a Chrome tab still running yesterday's page with yesterday's 69 MB clip; Chrome reloaded it on its own and the problem evaporated.

**What made it a skill** — While that was happening, the machine had booted an iOS Simulator, cold-loaded the site, switched to Settings and back, and proven the page both autoplayed and resumed. That left exactly two suspects — the phone and the tab — and kept anyone from "fixing" visibility logic that was never broken. The same afternoon, a test run of the draft skill found that a same-name overwrite on the CDN serves mixed old and new bytes for four hours (`HEAD` says `DYNAMIC`, a range `GET` says `HIT`). Both went straight into the checklist.

**How it differs from ENCODE** — It never touches the file. ENCODE makes a clip; VERIFY answers "will the page actually play it on a phone, and if not, why". Fully independent — you can use either without the other.

**When to use** — Optional by design. Tier 0 always (one minute). Tier 1 when someone reports stutter or you want proof before shipping without a phone in hand. Tier 2 when the report is "no autoplay" or "a play button" — and the first move there is asking them to close the tab and reopen.

**What it does** — Tier 0: per-second bitrate ceiling, a `curl --limit-rate` quick screen, upload integrity via ETag = MD5 and faststart from the first 1.5 MB, the upload-before-push order, the CDN range-cache trap. Tier 1: a Chrome DevTools throttle harness with the clip picker forced through a `Math.random` override, so you test the clip you mean to. Tier 2: iOS Simulator cold-load and app-switch screenshot diffs.

**Payoff** — "Starved" versus "blocked" separated in about five minutes, with evidence instead of a hunch.

<sub>Verified 2026-09-03 · Chrome 140 · iOS 26 Simulator</sub>

## ENCODE · [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile)

**The problem** — A hero clip that plays perfectly on a laptop stalls on a phone. The real case: a 1792×3184 CRF 20 export came out at 11.7 Mbps / 69 MB; a phone link (Chrome "Fast 4G" measures about 7.5 Mbps) fed it one second of video per second of buffering, then froze.

**When to use** — Any 9:16 background / hero clip bound for phones, and any phone clip that already stutters.

**What it does** — One command. If the master is already H.264, ≤ 1440×2560 and ≤ 6 Mbps it only remuxes (moov to the front, no generation loss). Otherwise it scales to 1440×2560, encodes CRF 23 / preset slow, copies the audio, then measures per-second bitrate and prints `PASS` or `FAIL: rerun with 1920`.

**Why CRF 23** — CRF pins perceived quality, not bitrate. The same CRF 20 gives 6 Mbps on a calm shot and 8.6 Mbps on high-motion footage — measured — and 8.6 stalls on a 7.5 Mbps link. CRF 23 lands at 5.7 Mbps and is indistinguishable on a phone-sized background. Native resolution above 1440×2560 is never kept: phone screens top out at 1290×2796, so extra pixels are only extra bitrate.

**Payoff** — 69 MB → 34.5 MB, 11.7 → 5.7 Mbps; a 46-second clip plays through on Fast 4G while the page preloads the next clip in parallel.

<sub>Verified 2026-09-03 · ffmpeg 8.0 · macOS 26</sub>

### VERIFY · [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile)

**How it differs from ENCODE** — It never touches the file. ENCODE produces a clip; VERIFY tells you whether the page will actually play it on a phone, and if not, why. Fully independent — use one without the other.

**The problem** — A phone shows a frozen hero and you cannot tell *starved* (bitrate above bandwidth) from *blocked* (autoplay policy, Low Power Mode, a stale tab still running yesterday's page). Desktop Chrome playing it proves nothing — the desktop hits neither failure.

**When to use** — Optional by design. Tier 0 always (one minute); tier 1 when someone reports stutter or when you want proof before shipping; tier 2 when the report is "no autoplay" or "a play button".

**What it does** — Tier 0: per-second bitrate ceiling, a `curl --limit-rate` quick screen, upload integrity via ETag = MD5 and faststart from the first 1.5 MB, the upload-before-push order, and the CDN range-cache trap. Tier 1: Chrome DevTools throttle harness with the clip picker forced through a `Math.random` override. Tier 2: iOS Simulator cold-load and app-switch screenshot diffs, no iPhone required.

**Payoff** — Separates a page bug from device state in about five minutes. It kept us from "fixing" visibility logic that was never broken, and it surfaced the trap where a same-name overwrite serves mixed old and new bytes for four hours (`HEAD` says `DYNAMIC`, a range `GET` says `HIT`).

<sub>Verified 2026-09-03 · Chrome 140 · iOS 26 Simulator</sub>

### STITCH · [`video-clip-stitching`](skills/video-clip-stitching)

**The problem** — Chained generation — feed the last frame of take N as the first frame of take N+1 — leaves every continuation with roughly half a second of near-still "dead water" at its head. Plain `concat` then reads as "it stuck" or "it repeated"; no frame is duplicated, the motion is broken. On top of that, container frame rates lie: 30 fps content packed as 60 fps shows 60 in every header.

**When to use** — Any 01 / 02 / 03 series from Dreamina, Runway, Higgsfield, Seedance and the like; any complaint of "stuck", "repeated", "not smooth", "overlap"; QC of generated footage before it goes anywhere.

**What it does** — `clip_qc.py` reports three frame rates (container, frame density, effective) and detects padded frames by their phase structure — 7.5× odd/even signature on padded footage versus 1.1× on real — plus stalled-frame ratio and preview-vs-HD mix-ups. `seam_probe.py` classifies each seam into one of three types with opposite treatments: different shot → hard cut; composition continuation → cut the dead water and dissolve; true overlap → cut the re-enacted segment. The cut point comes from the ratio of motion after the seam to motion before it, targeting 1.0. `join_clips.sh` encodes in a single pass with the `xfade` offset computed, not typed, and the three ffmpeg landmines pre-defused.

**Why the ratio rule** — A curve-only reading once proposed cutting 54 frames; the answer was 0 — the previous take simply ended slowly, so the low motion matched. Same curve, different baseline, opposite conclusion. Two visually identical batches needed 30 and 0.

**Payoff** — Seams that survive playback, and an honest acceptance step: duration reconciliation, seam frame grabs, segment-wise `volumedetect`.

<sub>Verified 2026-09-02 · ffmpeg 8.0</sub>

## Layout

One directory per skill — `skills/<name>/SKILL.md` plus the scripts it needs. Project-specific settings (URLs, buckets, CSP hash rules) stay in each project's `CLAUDE.md` / `AGENTS.md`, not here. Skill bodies are written in Traditional Chinese; scripts and their usage lines are English.

## Why these rules

Every rule was hit in production, not derived. The numbers — bitrate ceilings, thresholds, H.264 level limits — come from measurements recorded in each `SKILL.md`.

## How these came to be

None of this was planned. The hero clip on our site is a cat following a glowing paper boat down a night street, generated in three takes, each started from the last frame of the one before. Over two evenings that one piece of footage produced all three skills, in this order.

**STITCH, evening of 2026-09-01.** The ask was roughly: "There's cat mobile 01, 02, 03 in Downloads. The first frames of 03 look like they overlap the tail of 02 — figure out how to handle that, then join 1-2-3 into one." Fourteen minutes later a finished file came back, and the reply was "Wait, I thought you could do this with ffmpeg? …huh, that looks pretty good." It had been done entirely in ffmpeg. The next question was whether there was a skill in it. Along the way: a frame-rate scare ("I thought the originals were 60 — why did it come out 30?" — CapCut was showing its own 30 fps timeline; the file was true 60), take 02 turning out to have 13.4 % stalled frames, the desktop 03 in Downloads turning out to be the 854×480 preview, and one confident recommendation to cut 54 frames that should have been 0.

**ENCODE, the next day.** The stitched clip — 1792×3184, 19 Mbps — went into the site's mobile rotation at native size; the commit said the resolution standard was a floor. CRF 20 made it 11.7 Mbps / 69 MB. The morning after: "It used to autoplay on mobile. Now it just sits there. Is it something on our side or is it my phone?" Then, once the cause was clear: "So I have to re-encode everything on mobile? …no wait, you're the one re-encoding, right?" One file. That exchange is the spec: one command, no decisions.

**VERIFY, the same morning.** The fix went live at 04:47. Then: "still doesn't autoplay on my phone" — "I see a play button" — "mobile Chrome app" — "Safari is fine" — "in Chrome even tapping play does nothing…" — "never mind" — "it suddenly works." Twenty minutes; the bug was a Chrome tab still running yesterday's page. Meanwhile an iOS Simulator had already cold-loaded the site, switched apps and back, and proven the page autoplayed and resumed. Nobody "fixed" the visibility logic that was never broken, and the checklist got its two most useful lines: ask them to close the tab first, and never overwrite a live clip under the same name.

<br>

<p align="center"><sub>Made by <a href="https://alchemint.xyz">Alchemint</a> · every rule here was paid for once already</sub></p>
