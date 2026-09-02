// Paste as the `function` argument of chrome-devtools evaluate_script (waitForStableDom: false).
// Samples every visible/hidden <video> every 3 s for 30 s. Smooth playback: `t` advances 3.00 per
// sample, `ready` stays 4, `buf` (buffered end) keeps pulling ahead of `t`, and `waiting` (from
// test.html's window.__ev, if present) stays at the single initial buffering event.
async () => {
  const vids = [...document.querySelectorAll('video')];
  const snap = () => vids.map((v, i) => ({
    i, src: (v.currentSrc || v.src || '').split('/').pop(), paused: v.paused,
    t: +v.currentTime.toFixed(2), ready: v.readyState,
    buf: v.buffered.length ? +v.buffered.end(v.buffered.length - 1).toFixed(2) : 0,
    err: v.error ? v.error.code : null, opacity: v.style.opacity, w: v.videoWidth, h: v.videoHeight
  }));
  const out = { hidden: document.hidden, hasFocus: document.hasFocus(), ev: window.__ev || null, samples: [] };
  for (let k = 0; k < 10; k++) {
    out.samples.push({ ms: Date.now() - (window.__t0 || 0), v: snap() });
    await new Promise(r => setTimeout(r, 3000));
  }
  return out;
}
// To force a random picker onto one clip, pass this as navigate_page's `initScript` BEFORE the page
// loads and pick the constant from the page's own weights:
//   Math.random = function () { return 0.9; }; window.__t0 = Date.now();
