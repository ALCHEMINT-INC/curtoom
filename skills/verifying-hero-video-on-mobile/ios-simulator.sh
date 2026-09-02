#!/bin/sh
# Does a page's hero video autoplay on iOS, and resume after switching apps? No iPhone needed.
# Usage: ios-simulator.sh URL ["iPhone 17"]   (needs Xcode; output PNGs land in $TMPDIR)
# A simulator has no Low Power Mode, so: plays here but not on the user's phone = device state;
# does not play here = the page's problem (WebKit autoplay / visibility / focus logic).
URL="$1"; DEV="${2:-iPhone 17}"; OUT="${TMPDIR:-/tmp}/sim-hero/$(date +%H%M%S)"; mkdir -p "$OUT"
[ -n "$URL" ] || { echo "usage: $0 URL [device]"; exit 1; }
python3 -c "import PIL" 2>/dev/null || { echo "needs Pillow: python3 -m pip install pillow"; exit 1; }
UDID=$(xcrun simctl list devices available | grep "$DEV (" | head -1 | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')
[ -n "$UDID" ] || { echo "no simulator named '$DEV'"; exit 1; }
xcrun simctl boot "$UDID" 2>/dev/null; xcrun simctl bootstatus "$UDID" -b >/dev/null 2>&1
for i in 1 2 3 4; do xcrun simctl openurl "$UDID" "$URL" 2>/dev/null && break; sleep 8; done  # first launch times out once
diff_frames() { # $1 label: two shots 6 s apart, mean pixel difference in the middle of the screen
  sleep "${3:-15}"; xcrun simctl io "$UDID" screenshot "$OUT/$1-a.png" >/dev/null 2>&1
  sleep 6;         xcrun simctl io "$UDID" screenshot "$OUT/$1-b.png" >/dev/null 2>&1
  python3 -W ignore -c "
from PIL import Image, ImageChops
a=Image.open('$OUT/$1-a.png').convert('RGB'); b=Image.open('$OUT/$1-b.png').convert('RGB')
c=ImageChops.difference(a,b).crop((0,200,a.width,a.height-300)).convert('L')
m=sum(c.getdata())/(c.width*c.height); print('$2: mean diff %.1f -> %s' % (m, 'PLAYING' if m>5 else 'FROZEN / not playing'))"
}
diff_frames load "cold load" 20
xcrun simctl launch "$UDID" com.apple.Preferences >/dev/null 2>&1; sleep 6
xcrun simctl launch "$UDID" com.apple.mobilesafari >/dev/null 2>&1
diff_frames back "after app switch" 8
echo "screenshots: $OUT (look for a ▶ overlay = autoplay refused)"
xcrun simctl shutdown "$UDID" >/dev/null 2>&1
