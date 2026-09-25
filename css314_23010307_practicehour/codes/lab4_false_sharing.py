import time
import numpy as np
from numba import njit, prange, set_num_threads

ITERATIONS = 10_000_000

@njit(parallel=True)
def false_sharing_test(num_threads, iters):
    counters = np.zeros(num_threads, dtype=np.int64)
    for tid in prange(num_threads):
        for _ in range(iters):
            counters[tid] += 1
    return counters

@njit(parallel=True)
def padded_sharing_test(num_threads, iters):
    stride = 8  # 8 int64 values = 64 bytes
    counters = np.zeros(num_threads * stride, dtype=np.int64)
    for tid in prange(num_threads):
        idx = tid * stride
        for _ in range(iters):
            counters[idx] += 1
    return counters

@njit(parallel=True)
def local_accumulator_test(num_threads, iters):
    counters = np.zeros(num_threads, dtype=np.int64)
    for tid in prange(num_threads):
        local = 0
        for _ in range(iters):
            local += 1
        counters[tid] = local
    return counters

def run():
    false_sharing_test(2, 1000)
    padded_sharing_test(2, 1000)
    local_accumulator_test(2, 1000)

    for p in [1, 2, 4, 8, 16]:
        set_num_threads(p)

        t0 = time.perf_counter()
        false_sharing_test(p, ITERATIONS)
        t_false = time.perf_counter() - t0

        t0 = time.perf_counter()
        padded_sharing_test(p, ITERATIONS)
        t_padded = time.perf_counter() - t0

        t0 = time.perf_counter()
        local_accumulator_test(p, ITERATIONS)
        t_local = time.perf_counter() - t0

        print(
            f"P={p:2d} | Unpadded={t_false:.6f}s | "
            f"Padded={t_padded:.6f}s | Local={t_local:.6f}s | "
            f"Padding speedup={t_false/t_padded:.3f}x"
        )

if __name__ == "__main__":
    run()
