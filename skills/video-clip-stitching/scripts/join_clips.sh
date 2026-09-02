#!/usr/bin/env bash
#
# join_clips.sh — 串接三段影片，接縫策略可分別設定
#
# 用法
#   ./join_clips.sh A.mp4 B.mp4 C.mp4 out.mp4
#   CUT_FRAMES=30 ./join_clips.sh A.mp4 B.mp4 C.mp4 out.mp4      # B→C 砍 C 開頭 30 幀
#   SEAM1=xfade ./join_clips.sh A.mp4 B.mp4 C.mp4 out.mp4        # A→B 也用溶接
#
# 參數（先跑 seam_probe.py 決定，別憑感覺填）
#   CUT_FRAMES  砍掉 C 開頭幾幀。0 = 不砍
#   XFADE       交叉溶接秒數
#   SEAM1       A→B 的接法：hard（預設，不同鏡位用）或 xfade（構圖延續用）
#
set -euo pipefail

A="${1:?用法: $0 <clipA> <clipB> <clipC> <output>}"
B="${2:?缺少 clipB}"; C="${3:?缺少 clipC}"; OUT="${4:?缺少 output}"

CUT_FRAMES="${CUT_FRAMES:-0}"
XFADE="${XFADE:-0.1}"
SEAM1="${SEAM1:-hard}"
FPS="${FPS:-60}"
CRF="${CRF:-16}"
PRESET="${PRESET:-fast}"
ABR="${ABR:-192k}"

dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }

# offset 一定要自己算。它是整條鏈裡唯一「算錯也不報錯」的參數——
# ffmpeg 照樣 exit 0，只是把轉場放到錯的時間點，要播出來才發現。
DA=$(dur "$A"); DB=$(dur "$B")
ACUT=$(awk -v f="$CUT_FRAMES" -v r="$FPS" 'BEGIN{printf "%.6f", f/r}')

if [ "$SEAM1" = "xfade" ]; then
  OFF1=$(awk -v a="$DA" -v x="$XFADE" 'BEGIN{printf "%.6f", a-x}')
  V12="[v0][v1]xfade=transition=fade:duration=${XFADE}:offset=${OFF1}[v12]"
  A12="[a0][a1]acrossfade=d=${XFADE}[a12]"
  DAB=$(awk -v a="$DA" -v b="$DB" -v x="$XFADE" 'BEGIN{printf "%.6f", a+b-x}')
else
  V12="[v0][v1]concat=n=2:v=1:a=0,fps=${FPS},settb=AVTB[v12]"
  A12="[a0][a1]concat=n=2:v=0:a=1,asettb=AVTB[a12]"
  DAB=$(awk -v a="$DA" -v b="$DB" 'BEGIN{printf "%.6f", a+b}')
fi
OFF2=$(awk -v d="$DAB" -v x="$XFADE" 'BEGIN{printf "%.6f", d-x}')

echo "A=${DA}s  B=${DB}s  A→B=${SEAM1}  C 砍 ${CUT_FRAMES} 幀 (${ACUT}s)"
echo "B→C xfade offset=${OFF2}s duration=${XFADE}s"

# 三個 ffmpeg 地雷，全在下面這段：
#  1. concat 的輸出接 xfade 前必須 fps+settb=AVTB 正規化 timebase，
#     否則報 "Error reinitializing filters"——訊息完全不提 timebase。
#  2. 音訊每一路都要 aformat 統一取樣格式，否則 AAC 編碼器回 -22 Invalid argument。
#  3. atrim 的秒數必須等於 trim 的幀數 ÷ fps，否則音畫不同步。
AF="aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo"
ffmpeg -y -v error -stats -i "$A" -i "$B" -i "$C" -filter_complex "
[0:v]setsar=1,fps=${FPS},settb=AVTB[v0];
[1:v]setsar=1,fps=${FPS},settb=AVTB[v1];
${V12};
[2:v]trim=start_frame=${CUT_FRAMES},setpts=PTS-STARTPTS,setsar=1,fps=${FPS},settb=AVTB[v2];
[v12][v2]xfade=transition=fade:duration=${XFADE}:offset=${OFF2}[vout];
[0:a]${AF}[a0];
[1:a]${AF}[a1];
${A12};
[2:a]atrim=start=${ACUT},asetpts=PTS-STARTPTS,${AF},asettb=AVTB[a2];
[a12][a2]acrossfade=d=${XFADE}[aout]" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -crf "$CRF" -preset "$PRESET" -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a "$ABR" -movflags +faststart "$OUT"

echo; echo "完成: $OUT"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames \
  -show_entries format=duration,size -of default=noprint_wrappers=1 "$OUT"
