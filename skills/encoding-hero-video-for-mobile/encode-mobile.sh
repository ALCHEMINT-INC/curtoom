#!/bin/sh
# Encode (or just remux) a master into a phone-friendly 9:16 hero clip and grade its bitrate.
# Usage: encode-mobile.sh IN.mp4 OUT.mp4 [HEIGHT]   HEIGHT = 2560 (default, 1440x2560) or 1920 (1080x1920)
# Rule: H.264 High, CRF 23, preset slow, audio copied, moov first. Phones need avg <= 6 Mbps, p95 <= 8.
set -e
IN="$1"; OUT="$2"; H="${3:-2560}"; W=$((H * 9 / 16))
[ -f "$IN" ] && [ -n "$OUT" ] || { echo "usage: $0 IN.mp4 OUT.mp4 [2560|1920]" >&2; exit 1; }

# ffprobe prints fields in its own order, not the requested one: read them by key.
V=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,pix_fmt,width,height,bit_rate -of default=nw=1 "$IN")
get() { printf '%s\n' "$V" | sed -n "s/^$1=//p" | head -1; }
CODEC=$(get codec_name); PIX=$(get pix_fmt); SW=$(get width); SH=$(get height); VBR=$(get bit_rate)
case "$VBR" in ''|N/A) VBR=0;; esac
echo "master: $CODEC $PIX ${SW}x${SH} $((VBR / 1000)) kbps"

# Already phone-sized H.264 at a sane bitrate (e.g. a dreamina export): remux only, no generation loss.
if [ "$CODEC" = h264 ] && [ "$PIX" = yuv420p ] && [ "$SH" -le "$H" ] && [ "$VBR" -gt 0 ] && [ "$VBR" -le 6000000 ]; then
  echo "path: remux (already H.264, <= ${W}x${H}, <= 6 Mbps)"
  ffmpeg -y -v error -i "$IN" -map 0:v:0 -map '0:a:0?' -c copy -movflags +faststart "$OUT"
else
  echo "path: encode -> ${W}x${H}, crf 23, preset slow"
  ffmpeg -y -v error -stats -i "$IN" -map 0:v:0 -map '0:a:0?' -vf "scale=${W}:${H}:flags=lanczos" \
    -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT"
  echo
fi

# Grade: per-second video bitrate, moov position, size.
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,profile,level -of default=nw=1 "$OUT" | tr '\n' ' '; echo
python3 - "$OUT" <<'PY'
import sys, struct, subprocess, collections, os
f = sys.argv[1]
boxes = []; pos = 0; n = os.path.getsize(f)
with open(f, 'rb') as fh:
    while pos + 8 <= n:
        fh.seek(pos); size, typ = struct.unpack('>I4s', fh.read(8))
        if size == 1: size, = struct.unpack('>Q', fh.read(8))
        if size == 0: size = n - pos
        boxes.append(typ.decode('latin1')); pos += size
fast = 'moov' in boxes and 'mdat' in boxes and boxes.index('moov') < boxes.index('mdat')
out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'packet=pts_time,size',
                      '-of', 'csv=p=0', f], capture_output=True, text=True).stdout
b = collections.Counter()
for line in out.splitlines():
    t, s = line.split(',')[:2]; b[int(float(t))] += int(s)
v = sorted(b.values()); avg = sum(v) / len(v) * 8 / 1e6; p95 = v[int(len(v) * .95)] * 8 / 1e6; mx = v[-1] * 8 / 1e6
print('size %.1f MB  faststart %s  per-second Mbps: avg %.1f  p95 %.1f  max %.1f' % (n / 1e6, 'yes' if fast else 'NO', avg, p95, mx))
ok = fast and avg <= 6.0 and p95 <= 8.0
print('PASS' if ok else ('FAIL: moov is not first' if not fast else 'FAIL: rerun with 1920'))
sys.exit(0 if ok else 2)
PY
