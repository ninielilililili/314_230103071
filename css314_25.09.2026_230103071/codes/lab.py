import time
import csv
import os
import math
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# CSS314 - THE AMDAHL REALITY GAP
# Python analysis version
# Student ID: 230103071
# ============================================================

STUDENT_ID = 230103071
N = 10_000_000 + (STUDENT_ID % 10_000) * 1_000
MOD = 1_000_000_007


def collatz_steps(n):
    steps = 0

    while n > 1:
        if n & 1:
            n = 3 * n + 1
        else:
            n >>= 1
        steps += 1

    return steps


def sequential(start, end):
    maximum = 0
    checksum = 0
    hits = 0

    for i in range(start, end + 1):
        steps = collatz_steps(i)

        if steps > maximum:
            maximum = steps

        checksum = (checksum + steps) % MOD

        if steps > 100:
            hits += 1

    return maximum, checksum, hits


def parallel_worker(args):
    start, end = args
    return sequential(start, end)


def parallel_run(workers):
    chunk = N // workers
    ranges = []

    for w in range(workers):
        start = w * chunk + 1

        if w == workers - 1:
            end = N
        else:
            end = (w + 1) * chunk

        ranges.append((start, end))

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(parallel_worker, ranges))

    elapsed = time.perf_counter() - start_time

    maximum = max(r[0] for r in results)
    checksum = sum(r[1] for r in results) % MOD
    hits = sum(r[2] for r in results)

    return elapsed, maximum, checksum, hits


print("=" * 65)
print("CSS314 - THE AMDAHL REALITY GAP")
print("PYTHON EXPERIMENT")
print("=" * 65)

print(f"Student ID: {STUDENT_ID}")
print(f"N: {N:,}")
print(f"Python CPU count: {os.cpu_count()}")
print()

# ------------------------------------------------------------
# Sequential baseline
# ------------------------------------------------------------

print("SEQUENTIAL BASELINE")
print("-" * 65)

print("Run 1 - warmup")
r1 = sequential(1, N)

start = time.perf_counter()
r2 = sequential(1, N)
t2 = time.perf_counter() - start

print(f"Run 2: {t2:.6f} s")
print(f"Maximum: {r2[0]}")
print(f"Checksum: {r2[1]}")
print(f"Hits >100: {r2[2]}")

start = time.perf_counter()
r3 = sequential(1, N)
t3 = time.perf_counter() - start

print(f"Run 3: {t3:.6f} s")
print(f"Maximum: {r3[0]}")
print(f"Checksum: {r3[1]}")
print(f"Hits >100: {r3[2]}")

t_seq = (t2 + t3) / 2

print()
print(f"T_seq = {t_seq:.6f} s")
print()

# ------------------------------------------------------------
# Python thread experiments
# ------------------------------------------------------------

thread_counts = [1, 2, 4, 8, 16]

results = []

print("PYTHON THREAD EXPERIMENT")
print("-" * 65)

for workers in thread_counts:

    print(f"\nWorkers = {workers}")

    # Warmup
    parallel_run(workers)

    # Run 2
    run2 = parallel_run(workers)

    # Run 3
    run3 = parallel_run(workers)

    avg = (run2[0] + run3[0]) / 2

    speedup = t_seq / avg

    results.append({
        "threads": workers,
        "run1_cold": "",
        "run2": run2[0],
        "run3": run3[0],
        "avg_time": avg,
        "speedup": speedup,
        "maximum": run2[1],
        "checksum": run2[2],
        "hits": run2[3],
    })

    print(f"Run 2:       {run2[0]:.6f} s")
    print(f"Run 3:       {run3[0]:.6f} s")
    print(f"Average:     {avg:.6f} s")
    print(f"Speedup:     {speedup:.6f}")
    print(f"Maximum:     {run2[1]}")
    print(f"Checksum:    {run2[2]}")
    print(f"Hits >100:   {run2[3]}")

# ------------------------------------------------------------
# Amdahl calculation
# ------------------------------------------------------------

s2 = results[1]["speedup"]

p = 2 * (1 - (1 / s2))

print()
print("=" * 65)
print("AMDAHL CALCULATION")
print("=" * 65)

print(f"S_emp(2) = {s2:.6f}")
print(f"p = {p:.6f}")

for row in results:
    k = row["threads"]

    theoretical = 1 / ((1 - p) + (p / k))
    delta = theoretical - row["speedup"]

    row["theoretical_speedup"] = theoretical
    row["reality_gap"] = delta

    print(
        f"k={k:2d}  "
        f"Empirical={row['speedup']:.6f}  "
        f"Theoretical={theoretical:.6f}  "
        f"Delta={delta:.6f}"
    )

# ------------------------------------------------------------
# Save CSV
# ------------------------------------------------------------

with open("results_python.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Threads",
        "Run 2 (s)",
        "Run 3 (s)",
        "Avg T_k (s)",
        "S_emp(k)",
        "S_theo(k)",
        "Delta(k)",
        "Maximum",
        "Checksum",
        "Hits >100"
    ])

    for row in results:

        writer.writerow([
            row["threads"],
            f"{row['run2']:.6f}",
            f"{row['run3']:.6f}",
            f"{row['avg_time']:.6f}",
            f"{row['speedup']:.6f}",
            f"{row['theoretical_speedup']:.6f}",
            f"{row['reality_gap']:.6f}",
            row["maximum"],
            row["checksum"],
            row["hits"]
        ])

print()
print("Saved: results_python.csv")

# ------------------------------------------------------------
# Graph
# ------------------------------------------------------------

k_values = [r["threads"] for r in results]
empirical = [r["speedup"] for r in results]
theoretical = [r["theoretical_speedup"] for r in results]
ideal = k_values

plt.figure(figsize=(10, 6))

plt.plot(k_values, empirical, marker="o", label="Python empirical")
plt.plot(k_values, theoretical, marker="o", label="Amdahl theoretical")
plt.plot(k_values, ideal, marker="o", label="Linear ideal")

plt.xlabel("Number of workers")
plt.ylabel("Speedup")
plt.title("Amdahl Reality Gap - Python Experiment")
plt.xticks(k_values)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig("speedup_plot_python.png", dpi=300)

print("Saved: speedup_plot_python.png")

print()
print("=" * 65)
print("DONE")
print("=" * 65)