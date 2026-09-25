import time
import csv
import os

# ============================================================
# CSS314 - Parallel Computing
# Student ID: 230103071
# Python analysis / verification version
# ============================================================

STUDENT_ID = 230103071

# Worksheet formula:
# N = 10,000,000 + (last 4 digits × 1,000)
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


def sequential_run():
    max_steps = 0
    checksum = 0

    start = time.perf_counter()

    for i in range(1, N + 1):
        steps = collatz_steps(i)

        if steps > max_steps:
            max_steps = steps

        checksum = (checksum + steps) % MOD

    elapsed = time.perf_counter() - start

    return elapsed, max_steps, checksum


print("=" * 60)
print("CSS314 - THE AMDAHL REALITY GAP")
print("=" * 60)

print(f"Student ID : {STUDENT_ID}")
print(f"Workload N : {N:,}")
print(f"CPU logical processors visible to Python: {os.cpu_count()}")
print()

print("Starting sequential Python calculation...")
print("This may take some time.")
print()

# Run 1 = warmup
print("Run 1 (warmup)...")
warmup = sequential_run()

print(f"Warmup time: {warmup[0]:.4f} seconds")
print()

# Run 2
print("Run 2...")
run2 = sequential_run()

print(f"Run 2 time: {run2[0]:.4f} seconds")
print(f"Maximum stopping time: {run2[1]}")
print(f"Checksum: {run2[2]}")
print()

# Run 3
print("Run 3...")
run3 = sequential_run()

print(f"Run 3 time: {run3[0]:.4f} seconds")
print()

# Average according to worksheet
t_seq = (run2[0] + run3[0]) / 2

print("=" * 60)
print("RESULT")
print("=" * 60)
print(f"N                    = {N:,}")
print(f"Run 2                = {run2[0]:.6f} s")
print(f"Run 3                = {run3[0]:.6f} s")
print(f"T_seq                = {t_seq:.6f} s")
print(f"Maximum steps        = {run2[1]}")
print(f"Checksum             = {run2[2]}")
print("=" * 60)

# Save initial result
with open("python_sequential_result.txt", "w") as f:
    f.write("CSS314 Python Sequential Result\n")
    f.write(f"Student ID: {STUDENT_ID}\n")
    f.write(f"N: {N}\n")
    f.write(f"Run 1 warmup: {warmup[0]:.6f}\n")
    f.write(f"Run 2: {run2[0]:.6f}\n")
    f.write(f"Run 3: {run3[0]:.6f}\n")
    f.write(f"T_seq: {t_seq:.6f}\n")
    f.write(f"Maximum stopping time: {run2[1]}\n")
    f.write(f"Checksum: {run2[2]}\n")

print()
print("Saved: python_sequential_result.txt")