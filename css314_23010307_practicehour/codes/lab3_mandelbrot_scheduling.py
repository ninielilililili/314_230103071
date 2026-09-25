import time
import numpy as np
from numba import njit, prange, set_num_threads

WIDTH, HEIGHT, MAX_ITER = 1920, 1080, 1000

@njit
def compute_pixel(px, py, width, height, max_iter):
    x0 = (px - width / 2.0) * 4.0 / width
    y0 = (py - height / 2.0) * 4.0 / height
    x = y = 0.0
    iteration = 0

    while x*x + y*y <= 4.0 and iteration < max_iter:
        xtemp = x*x - y*y + x0
        y = 2.0*x*y + y0
        x = xtemp
        iteration += 1
    return iteration

@njit(parallel=True)
def render_static(width, height, max_iter):
    image = np.zeros((height, width), dtype=np.int32)
    for y in prange(height):
        for x in range(width):
            image[y, x] = compute_pixel(x, y, width, height, max_iter)
    return image

def render_dynamic(width, height, max_iter, threads, chunk):
    # Python implementation of a dynamic work queue.
    # The expensive pixel calculation itself is compiled by Numba.
    from concurrent.futures import ThreadPoolExecutor

    image = np.zeros((height, width), dtype=np.int32)
    next_row = 0
    lock = __import__("threading").Lock()

    def worker():
        nonlocal next_row
        while True:
            with lock:
                start = next_row
                next_row += chunk
            if start >= height:
                return
            end = min(start + chunk, height)
            for y in range(start, end):
                for x in range(width):
                    image[y, x] = compute_pixel(x, y, width, height, max_iter)

    with ThreadPoolExecutor(max_workers=threads) as pool:
        list(pool.map(lambda _: worker(), range(threads)))
    return image

def benchmark():
    # Warm-up
    render_static(100, 100, 100)

    print("Static schedule")
    for p in [2, 4, 8, 16]:
        set_num_threads(p)
        t0 = time.perf_counter()
        image = render_static(WIDTH, HEIGHT, MAX_ITER)
        elapsed = time.perf_counter() - t0
        print(f"P={p:2d} | Time={elapsed:.4f}s | Checksum={int(image.sum())}")

    print("\nDynamic schedule")
    for p in [2, 4, 8, 16]:
        for chunk in [1, 16, 64, 256]:
            t0 = time.perf_counter()
            image = render_dynamic(WIDTH, HEIGHT, MAX_ITER, p, chunk)
            elapsed = time.perf_counter() - t0
            print(
                f"P={p:2d} | Chunk={chunk:3d} | "
                f"Time={elapsed:.4f}s | Checksum={int(image.sum())}"
            )

if __name__ == "__main__":
    benchmark()
