import multiprocessing as mp
import time
import sys

def worker(args):
    start, end = args
    total = 0
    for i in range(start, end):
        total += (i * i + 3 * i + 7) % 1000003
    return total

def benchmark(n_threads):
    total_work = 20_000_000
    chunk = total_work // n_threads
    jobs = []

    for i in range(n_threads):
        start = i * chunk
        end = total_work if i == n_threads - 1 else (i + 1) * chunk
        jobs.append((start, end))

    start_time = time.perf_counter()
    with mp.Pool(processes=n_threads) as pool:
        results = pool.map(worker, jobs)
    elapsed = time.perf_counter() - start_time

    print(f"Threads: {n_threads}")
    print(f"Time: {elapsed:.4f} seconds")
    print(f"Result: {sum(results)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python benchmark.py THREADS")
        sys.exit(1)

    mp.freeze_support()
    benchmark(int(sys.argv[1]))
