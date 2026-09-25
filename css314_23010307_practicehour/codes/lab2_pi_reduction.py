import math
import os
import time
import numpy as np
from numba import njit, prange, set_num_threads, get_num_threads

@njit
def calc_pi_serial(num_steps):
    step = 1.0 / num_steps
    total_sum = 0.0
    for i in range(num_steps):
        x = (i + 0.5) * step
        total_sum += 4.0 / (1.0 + x * x)
    return total_sum * step

@njit(parallel=True)
def calc_pi_reduction(num_steps):
    step = 1.0 / num_steps
    total_sum = 0.0
    for i in prange(num_steps):
        x = (i + 0.5) * step
        total_sum += 4.0 / (1.0 + x * x)
    return total_sum * step

def benchmark(num_steps=10_000_000, threads_list=(1, 2, 4, 8, 16), trials=3):
    # JIT warm-up
    calc_pi_serial(1000)
    calc_pi_reduction(1000)

    t0 = time.perf_counter()
    serial_pi = calc_pi_serial(num_steps)
    serial_time = time.perf_counter() - t0

    print(f"Serial: Pi={serial_pi:.12f}, Time={serial_time:.6f}s, "
          f"Error={abs(serial_pi-math.pi):.3e}")

    for p in threads_list:
        set_num_threads(p)
        times = []
        values = []
        for _ in range(trials):
            t0 = time.perf_counter()
            value = calc_pi_reduction(num_steps)
            times.append(time.perf_counter() - t0)
            values.append(value)

        avg = sum(times) / len(times)
        speedup = serial_time / avg
        efficiency = speedup / p
        error = abs(values[-1] - math.pi)

        print(
            f"P={p:2d} | Pi={values[-1]:.12f} | "
            f"Avg={avg:.6f}s | Error={error:.3e} | "
            f"Speedup={speedup:.3f}x | Efficiency={efficiency:.3f}"
        )

if __name__ == "__main__":
    print(f"Detected CPUs: {os.cpu_count()}")
    print(f"Numba threads initially: {get_num_threads()}")
    benchmark()
