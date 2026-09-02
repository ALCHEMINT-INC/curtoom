#!/usr/bin/env python3
"""素材驗收：容器標記不可信，內容的真實流暢度只能從像素驗。

用法: clip_qc.py <clip1.mp4> [clip2.mp4 ...]

回報三個幀率，它們不是同一件事：
  容器fps  —— mp4 標頭寫的，任何人都能寫任何數字
  幀密度   —— 幀數 ÷ 時長，容器裡真的有這麼多幀
  有效fps  —— 扣掉複製幀後真正在動的幀率，這才是觀眾感受到的流暢度
"""
import subprocess, sys, os, tempfile

THUMB_W, THUMB_H = 56, 32       # 夠判斷動作，不夠認出內容
FS = THUMB_W * THUMB_H
PHASE_RATIO = 3.0               # 相位組間差異超過此倍數 = 幀率灌水
STALL_RATIO = 0.25              # 低於中位數此比例 = 停滯幀


def sh(args):
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()


def probe(path, entries, stream=None):
    args = ["ffprobe", "-v", "error"]
    if stream:
        args += ["-select_streams", stream]
    args += ["-show_entries", entries, "-of", "default=noprint_wrappers=1:nokey=1", path]
    return [x for x in sh(args).split("\n") if x]


def gray_frames(path):
    """全片抽成縮圖灰階。逐幀不取樣——複製幀與停滯幀都得看相鄰幀。"""
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as f:
        raw = f.name
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path,
                    "-vf", f"scale={THUMB_W}:{THUMB_H},format=gray",
                    "-f", "rawvideo", raw], check=True)
    data = open(raw, "rb").read()
    os.unlink(raw)
    return [data[i*FS:(i+1)*FS] for i in range(len(data)//FS)]


def mae(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / FS


def detect_padding(diffs):
    """偵測低幀率內容灌水成高幀率容器。

    為什麼不直接數「diff 為 0 的幀」：複製幀經過重編碼會帶進壓縮雜訊，
    diff 落在 0.02~0.15 而不是 0，任何絕對門檻都會漏報。但灌水必然留下
    週期性的相位結構——每 P 幀裡固定有幾幀沒動——這個簽名壓縮殺不掉。
    回傳 (週期, 動的相位數, 組間比值) 或 None。
    """
    best = None
    for P in range(2, 6):
        groups = [[] for _ in range(P)]
        for i, v in enumerate(diffs):
            groups[i % P].append(v)
        means = [sum(g) / len(g) for g in groups if g]
        if len(means) < P or min(means) <= 0:
            continue
        ratio = max(means) / min(means)
        cut = max(means) * 0.4          # 明顯低於最高組的算「沒動」
        moving = sum(1 for m in means if m >= cut)
        if ratio >= PHASE_RATIO and moving < P and (best is None or ratio > best[2]):
            best = (P, moving, ratio)
    return best


def analyse(path):
    if not os.path.exists(path):
        sys.exit(f"找不到檔案: {path}")
    wh = probe(path, "stream=width,height", "v:0")
    if len(wh) < 2:
        sys.exit(f"讀不到視訊串流（檔案損毀或不是影片）: {path}")
    w, h = wh[:2]
    container_fps = probe(path, "stream=r_frame_rate", "v:0")[0]
    cfps = eval(container_fps) if "/" in container_fps else float(container_fps)
    dur = float(probe(path, "format=duration")[0])

    F = gray_frames(path)
    d = [mae(F[i], F[i - 1]) for i in range(1, len(F))]
    med = sorted(d)[len(d) // 2] if d else 0
    density = len(F) / dur if dur else 0

    pad = detect_padding(d)
    effective = density * pad[1] / pad[0] if pad else density
    stall = 100 * sum(1 for v in d if v < med * STALL_RATIO) / len(d) if d else 0

    return dict(name=os.path.basename(path), w=int(w), h=int(h), cfps=cfps,
                frames=len(F), dur=dur, density=density, effective=effective,
                pad=pad, stall=stall)


def main(paths):
    rows = [analyse(p) for p in paths]
    print(f"{'檔案':<26}{'解析度':<13}{'容器fps':<9}{'幀密度':<9}{'有效fps':<9}{'停滯幀%':<9}{'時長':<7}")
    print("-" * 88)
    for r in rows:
        res = f"{r['w']}x{r['h']}"
        print(f"{r['name']:<26}{res:<13}{r['cfps']:<9.0f}{r['density']:<9.1f}"
              f"{r['effective']:<9.1f}{r['stall']:<9.1f}{r['dur']:<7.2f}")
    print()

    flags = []
    # 串接前提：解析度與有效幀率一致。不一致就得縮放或補幀，兩者都要付畫質代價。
    if len({(r["w"], r["h"]) for r in rows}) > 1:
        flags.append("解析度不一致 —— 多半是有人拿到預覽版而非高清版。回頭重下，別靠放大硬接")
    if len({round(r["effective"] / 6) for r in rows}) > 1:
        flags.append("有效幀率不一致 —— 串接得補幀，畫質會付代價；先確認是不是下錯版本")
    for r in rows:
        if r["pad"]:
            P, moving, ratio = r["pad"]
            flags.append(f"{r['name']}: 幀率灌水 —— 每 {P} 幀只有 {moving} 幀在動"
                         f"（相位差 {ratio:.1f}x）。容器寫 {r['cfps']:.0f}fps，"
                         f"實際只有 {r['effective']:.0f}fps 的流暢度")
        if r["stall"] > 5 and not r["pad"]:
            flags.append(f"{r['name']}: 停滯幀 {r['stall']:.0f}% —— 該段動作會鈍。"
                         f"這是單次生成的隨機瑕疵，重生成該段通常就乾淨了")
    print("\n".join("⚠ " + f for f in flags) if flags else "✓ 規格一致，無異常")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
