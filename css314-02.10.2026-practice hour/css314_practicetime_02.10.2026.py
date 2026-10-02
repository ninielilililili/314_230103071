"""Runs Challenges 1-3 of the OpenMP/Numba lab and prints Table 1.
Usage:  pip install numpy numba matplotlib   then   python run_lab.py
Keep the laptop plugged in and close other apps first.
"""
import time, platform
import numpy as np
import numba
from numba import njit, prange
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MAXT = numba.config.NUMBA_NUM_THREADS

def best(fn, reps=3):
    """Best-of-N timing: removes cold-start / clock-ramp noise."""
    ts = []
    for _ in range(reps):
        s0 = time.perf_counter(); fn(); ts.append(time.perf_counter() - s0)
    return min(ts)

print(f"CPU: {platform.processor() or platform.machine()} | Hardware threads: {MAXT}")
rows_out = []  # (label, threads, size, time, speedup, eff)


# ---------------- Challenge 1: Monte Carlo ----------------
@njit(parallel=True)
def monte_carlo_pi(n):
    inside = 0
    for i in prange(n):
        x = np.random.uniform(0.0, 1.0)
        y = np.random.uniform(0.0, 1.0)
        if x * x + y * y <= 1.0:
            inside += 1
    return (4.0 * inside) / n

monte_carlo_pi(10_000)
SAMPLES = 120_000_000
counts = sorted({t for t in [1, 2, 4, 8, MAXT] if t <= MAXT})
print("\nChallenge 1")
print(f"{'Threads':<8}|{'Time (s)':<12}|{'Speedup':<10}|{'Eff (%)':<10}")
t1 = None
for t in counts:
    numba.set_num_threads(t)
    e = best(lambda: monte_carlo_pi(SAMPLES))
    if t == 1:
        t1 = e
    sp = t1 / e
    eff = sp / t * 100
    print(f"{t:<8}|{e:<12.4f}|{sp:<10.2f}|{eff:<10.1f}")
    rows_out.append((f"Monte Carlo", t, f"{SAMPLES:,}", e, f"{sp:.2f}x", f"{eff:.1f}%"))
numba.set_num_threads(MAXT)


# ---------------- Challenge 2: Mandelbrot ----------------
@njit(parallel=True)
def mandel_rows(h, w, max_iter):
    img = np.zeros((h, w), dtype=np.int32)
    for r in prange(h):
        cy = -1.2 + (r / h) * 2.4
        for c in range(w):
            cx = -2.0 + (c / w) * 2.5
            zr, zi, it = 0.0, 0.0, 0
            while (zr * zr + zi * zi <= 4.0) and (it < max_iter):
                nr = zr * zr - zi * zi + cx
                zi = 2.0 * zr * zi + cy
                zr = nr
                it += 1
            img[r, c] = it
    return img

@njit(parallel=True)
def mandel_cols(h, w, max_iter):
    img = np.zeros((h, w), dtype=np.int32)
    for c in prange(w):
        cx = -2.0 + (c / w) * 2.5
        for r in range(h):
            cy = -1.2 + (r / h) * 2.4
            zr, zi, it = 0.0, 0.0, 0
            while (zr * zr + zi * zi <= 4.0) and (it < max_iter):
                nr = zr * zr - zi * zi + cx
                zi = 2.0 * zr * zi + cy
                zr = nr
                it += 1
            img[r, c] = it
    return img

mandel_rows(100, 100, 50); mandel_cols(100, 100, 50)
H, W, MAX_IT = 2500, 2500, 1000
grid = mandel_rows(H, W, MAX_IT)
t_rows = best(lambda: mandel_rows(H, W, MAX_IT))
t_cols = best(lambda: mandel_cols(H, W, MAX_IT))
print(f"\nChallenge 2\nRow-parallel: {t_rows:.3f} s | Column-parallel: {t_cols:.3f} s")
plt.figure(figsize=(8, 8))
plt.imshow(grid, cmap="magma", extent=[-2.0, 0.5, -1.2, 1.2])
plt.title(f"Mandelbrot {H}x{W} (Render: {t_rows:.2f}s)")
plt.axis("off")
plt.savefig("mandelbrot_output.png", dpi=300, bbox_inches="tight")
print("Saved image: mandelbrot_output.png")
rows_out.append(("Mandelbrot (Rows)", MAXT, "2500 x 2500", t_rows, "N/A", "N/A"))
rows_out.append(("Mandelbrot (Cols)", MAXT, "2500 x 2500", t_cols, "N/A", "N/A"))


# ---------------- Challenge 3: Heat stencil ----------------
@njit(parallel=True)
def heat_step(u, un, alpha=0.20):
    rows, cols = u.shape
    for i in prange(1, rows - 1):
        for j in range(1, cols - 1):
            un[i, j] = u[i, j] + alpha * (
                u[i + 1, j] + u[i - 1, j] + u[i, j + 1] + u[i, j - 1] - 4.0 * u[i, j])

def run_heat(dtype, threads, N=1500, steps=300):
    numba.set_num_threads(threads)
    u = np.zeros((N, N), dtype=dtype); un = np.zeros_like(u)
    u[0, :] = 100.0; u[:, 0] = 100.0; un[0, :] = 100.0; un[:, 0] = 100.0
    heat_step(u, un)  # warmup (also compiles the float32 specialization)
    best_e = None
    for rep_i in range(3):
        s = time.perf_counter()
        for k in range(steps):
            heat_step(u, un)
            u, un = un, u
        e = time.perf_counter() - s
        best_e = e if best_e is None else min(best_e, e)
    return best_e, N * N * steps / best_e / 1e6

print("\nChallenge 3")
e64, m64 = run_heat(np.float64, MAXT)
e32, m32 = run_heat(np.float32, MAXT)
print(f"float64 ({MAXT} thr): {e64:.3f} s | {m64:.2f} Mcells/s")
print(f"float32 ({MAXT} thr): {e32:.3f} s | {m32:.2f} Mcells/s | float32 is {e64/e32:.2f}x faster")
rows_out.append(("Heat Stencil (f64)", MAXT, "1500x1500x300", e64, "N/A", "N/A"))
eb64, _ = run_heat(np.float64, MAXT, N=6000, steps=30)
eb32, _ = run_heat(np.float32, MAXT, N=6000, steps=30)
print(f"Large grid 6000x6000 (RAM-bound): f64 {eb64:.3f} s | f32 {eb32:.3f} s | f32 is {eb64/eb32:.2f}x faster")
print("\nHeat scaling (float64) - shows the memory-bandwidth wall:")
base = None
for t in counts:
    e, m = run_heat(np.float64, t)
    base = base or e
    print(f"  {t:>3} threads: {e:.3f} s  speedup {base/e:.2f}x  ({m:.1f} Mcells/s)")
numba.set_num_threads(MAXT)


# ---------------- Table 1 ----------------
print("\n=== TABLE 1 ===")
print(f"{'Challenge':<20}{'Threads':<9}{'Size':<16}{'Time (s)':<11}{'Speedup':<10}{'Eff':<8}")
for lab, t, size, e, sp, eff in rows_out:
    print(f"{lab:<20}{t:<9}{size:<16}{e:<11.3f}{sp:<10}{eff:<8}")