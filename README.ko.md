<p align="center"><a href="https://alchemint.xyz"><img src="assets/banner.svg" alt="cutroom — ffmpeg skills for coding agents, by Alchemint" width="760"></a></p>

<p align="center"><b>ffmpeg 기반 코딩 에이전트 스킬 — 인코딩, 이어 붙이기, 재생 검증을 영상이 실제로 배포되는 방식 그대로.</b></p>

<p align="center">
  <img alt="skills" src="https://img.shields.io/badge/skills-3-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude_Code-ready-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-ready-FDF3D1?style=flat-square&labelColor=05070a">
  <img alt="ffmpeg" src="https://img.shields.io/badge/ffmpeg-required-FDF3D1?style=flat-square&labelColor=05070a">
</p>

<p align="center"><a href="README.md">English</a> &nbsp;·&nbsp; <a href="README.zh-TW.md">繁體中文</a> &nbsp;·&nbsp; <a href="README.zh-CN.md">简体中文</a> &nbsp;·&nbsp; <a href="README.ja.md">日本語</a> &nbsp;·&nbsp; <b>한국어</b></p>

<br>

## 설치

```sh
npx skills add ALCHEMINT-INC/curtoom -g -a claude-code -a codex -y
```

한 줄로 두 에이전트 모두 설치됩니다: 스킬은 `~/.agents/skills`(Codex가 읽음)에 놓이고 `~/.claude/skills`(Claude Code가 읽음)로 심볼릭 링크됩니다. 한쪽만 설치하려면 `-a` 하나를 빼세요. 업데이트는 `npx skills update`. `npx`를 쓰지 않는다면 clone 후 `skills/<name>`을 두 디렉터리에 직접 링크하면 됩니다.

## Skills

| | skill | 언제 쓰는가 |
|:-:|---|---|
| 🎞️ | [`encoding-hero-video-for-mobile`](skills/encoding-hero-video-for-mobile) | 마스터 → 모바일용 9:16 히어로 클립을 명령 하나로: remux/재인코딩 자동 판단, 초당 비트레이트 측정, PASS / FAIL 출력 |
| 📱 | [`verifying-hero-video-on-mobile`](skills/verifying-hero-video-on-mobile) | 배경/히어로 영상이 휴대폰에서 "끊긴다", "자동 재생이 안 된다", "▶가 뜬다"일 때: 비트레이트 상한, Chrome 스로틀링 테스트, iOS 시뮬레이터, 업로드와 CDN 캐시 점검 |
| ✂️ | [`video-clip-stitching`](skills/video-clip-stitching) | AI 생성 클립 여러 개를 하나로: 컷 지점 찾기, 이음새 진단, 생성 소재 규격 검수 |

## 구성

스킬마다 디렉터리 하나 — `skills/<name>/SKILL.md`와 필요한 스크립트. 프로젝트 고유 설정(URL, 버킷, CSP 해시 규칙)은 각 프로젝트의 `CLAUDE.md`/`AGENTS.md`에 두고 여기에는 두지 않습니다. 스킬 본문은 번체 중국어로 작성되어 있습니다.

## 왜 이런 규칙인가

모든 규칙은 실제 운영에서 부딪혀 얻은 것이지 추론한 것이 아닙니다. 숫자 — 비트레이트 상한, 임계값, H.264 level 한계 — 는 각 `SKILL.md`에 기록된 실측값입니다.

<br>

<p align="center"><sub><a href="https://alchemint.xyz">Alchemint</a> 제작 · 여기 있는 규칙은 모두 한 번씩 수업료를 치른 것들</sub></p>
