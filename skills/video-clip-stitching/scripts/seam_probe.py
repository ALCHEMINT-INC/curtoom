#!/usr/bin/env python3
"""接縫診斷：判斷兩段素材該怎麼接，並算出切點。

用法: seam_probe.py <前一段.mp4> <後一段.mp4> [--window 4]

輸出接縫類型與建議的 CUT_FRAMES，附上判斷依據的數字，
好讓你能質疑它——結論若跟眼睛看到的不符，先看證據再改參數。
"""
import subprocess, sys, os, tempfile, argparse

W, H = 56, 32
FS = W * H
WINDOW = 4.0          # 接縫兩側各取幾秒來分析
BASE_SPAN = 36        # 基準運動量取樣幀數（0.6s @60fps）
RELATED = 0.5         # 最佳 MAE 低於對照組中位的此比例 = 構圖有關聯
DRIFT_FRAMES = 15     # 對應位置漂移超過此值 = 真重疊（動作被重演）


def sh(a):
    return subprocess.run(a, capture_output=True, text=True).stdout.strip()


def meta(path):
    fps = sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
              "stream=r_frame_rate", "-of", "csv=p=0", path])
    n = sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
            "stream=nb_frames", "-of", "csv=p=0", path])
    return eval(fps), int(n)


def grab(path, select):
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as f:
        raw = f.name
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-vf",
                    f"select='{select}',scale={W}:{H},format=gray",
                    "-vsync", "0", "-f", "rawvideo", raw], check=True)
    d = open(raw, "rb").read()
    os.unlink(raw)
    return [d[i*FS:(i+1)*FS] for i in range(len(d)//FS)]


def mae(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / FS


def motion(frames):
    return [mae(frames[i], frames[i-1]) for i in range(1, len(frames))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--window", type=float, default=WINDOW)
    args = ap.parse_args()

    fps_a, n_a = meta(args.a)
    fps_b, n_b = meta(args.b)
    span = int(args.window * fps_a)
    start = max(0, n_a - span)

    A = grab(args.a, f"gte(n\\,{start})")
    B = grab(args.b, f"lt(n\\,{int(args.window*fps_b)})")
    print(f"前段 {os.path.basename(args.a)}: {n_a} 幀 @{fps_a:.0f}fps  取尾段 {len(A)} 幀 (n={start}..)")
    print(f"後段 {os.path.basename(args.b)}: {n_b} 幀 @{fps_b:.0f}fps  取頭段 {len(B)} 幀")
    if abs(fps_a - fps_b) > 0.5:
        print("⚠ 兩段幀率不同，切點的幀數換算會失真——先用 clip_qc.py 確認素材版本")
    print()

    # 對照組：任意配對的 MAE，代表「兩幀無關」的量級。沒有它就無從判斷相似度算不算高。
    import random
    random.seed(0)
    ctrl = sorted(mae(B[random.randrange(len(B))], A[random.randrange(len(A))])
                  for _ in range(60))
    ctrl_med = ctrl[len(ctrl)//2]

    # 對應曲線：B 的每一幀最像 A 的哪一幀。
    # 平線 = 構圖延續（B 停在 A 的末畫面上）；斜線 = 真重疊（動作被重演）。
    corr = []
    for k in range(0, min(len(B), 120), 10):
        v, i = min((mae(B[k], A[i]), i) for i in range(len(A)))
        corr.append((k, start + i, v))

    best_mae = corr[0][2]
    related = best_mae < ctrl_med * RELATED
    drift = corr[-1][1] - corr[0][1]

    print("對應曲線（B 的第 k 幀最像 A 的哪一幀）:")
    for k, n, v in corr:
        print(f"   k={k:3d} -> A n={n:5d}  MAE={v:6.2f}")
    print(f"   [對照組] 無關配對 MAE 中位 = {ctrl_med:.2f}")
    print()

    if not related:
        print(f"判定: 【不同鏡位】 最佳 MAE {best_mae:.2f} 接近無關量級 {ctrl_med:.2f}")
        print("處理: 硬切。加轉場是畫蛇添足——換鏡本來就該切得乾脆。")
        print("→ CUT_FRAMES=0，且不要加 xfade")
        return

    if drift > DRIFT_FRAMES:
        print(f"判定: 【真重疊】 對應位置隨 k 前移了 {drift} 幀，B 重演了 A 的動作")
        print(f"處理: 砍掉 B 開頭被重演的部分，約 {corr[-1][0]} 幀起才是新內容。")
        print(f"→ CUT_FRAMES≈{corr[-1][0]}（請目視確認起點畫面）")
        return

    # 構圖延續：真正要決定的是「砍多少」。
    # 判準是接縫後的運動量要接得上接縫前，比值趨近 1。
    # 只看 B 自己的曲線「前低後高」會誤判——B 後段變快可能是動作本來就在加速。
    mA, mB = motion(A), motion(B)
    base = sum(mA[-BASE_SPAN:]) / BASE_SPAN
    print(f"判定: 【構圖延續】 B 的開頭停在 A 的末畫面上（MAE {best_mae:.2f} vs 無關 {ctrl_med:.2f}）")
    print(f"      沒有動作重演，所以要砍的是「死水」不是「重複內容」")
    print()
    print(f"前段接縫前 {BASE_SPAN/fps_a:.1f}s 運動量基準 = {base:.2f}")
    print(f"{'CUT_FRAMES':<12}{'接縫後運動量':<14}{'比值':<8}")
    cands = []
    for cut in range(0, min(121, len(mB) - BASE_SPAN), 6):
        seg = mB[cut:cut + BASE_SPAN]
        m = sum(seg) / len(seg)
        ratio = m / base if base else 0
        cands.append((abs(ratio - 1), cut, m, ratio))
        mark = ""
        if ratio < 0.75:
            mark = "  <= 死水，動作接不上"
        elif ratio > 1.4:
            mark = "  <= 暴衝，砍過頭了"
        print(f"{cut:<12}{m:<14.2f}{ratio:<8.2f}{mark}")
    cands.sort()
    _, cut, m, ratio = cands[0]
    print()
    print(f"→ 建議 CUT_FRAMES={cut}（比值 {ratio:.2f}，最接近 1）")
    if cut == 0:
        print("  不砍就接得上——這一段沒有緩啟動問題，只需要溶接吃掉材質差異")
    print(f"  仍建議 0.1s 交叉溶接：MAE {best_mae:.2f} 不為 0，硬切會閃一下光影/材質")


if __name__ == "__main__":
    main()
