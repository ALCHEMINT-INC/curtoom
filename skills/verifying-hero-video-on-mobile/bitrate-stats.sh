#!/bin/sh
# Per-second video bitrate of an mp4: average, p95 and peak in Mbps, plus stream facts.
# Usage: bitrate-stats.sh file.mp4
f="$1"; [ -f "$f" ] || { echo "usage: $0 file.mp4" >&2; exit 1; }
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,profile,level,width,height,r_frame_rate,bit_rate -of default=nw=1 "$f"
ffprobe -v error -select_streams v:0 -show_entries packet=pts_time,size -of csv=p=0 "$f" | python3 -c '
import sys, collections
b = collections.Counter()
for line in sys.stdin:
    t, s = line.strip().split(",")[:2]; b[int(float(t))] += int(s)
v = sorted(b.values())
print("per-second Mbps: avg %.1f  p95 %.1f  max %.1f  (phones: avg <= 6, p95 <= 8)" % (
    sum(v) / len(v) * 8 / 1e6, v[int(len(v) * 0.95)] * 8 / 1e6, v[-1] * 8 / 1e6))'
