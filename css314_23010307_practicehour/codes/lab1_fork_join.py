from concurrent.futures import ThreadPoolExecutor
import threading
import time
import os

def worker_task(thread_id, team_size, workload=0):
    native_tid = threading.get_native_id()
    role = "Master" if thread_id == 0 else "Worker"

    # Artificial workload for oversubscription/core-saturation experiments.
    value = 0.0
    for i in range(workload):
        value += (i + 1) ** 0.5

    time.sleep(0.001 * (thread_id % 3))
    return role, thread_id, team_size, native_tid, value

def run_team(num_threads, workload=0):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(worker_task, tid, num_threads, workload)
            for tid in range(num_threads)
        ]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start

    for role, tid, team, native_tid, _ in results:
        print(f"[{role}] Logical Rank: {tid} of {team} | Native OS TID: {native_tid}")
    print(f"Joined thread team. Time = {elapsed:.6f}s")
    return elapsed

if __name__ == "__main__":
    print("LAB 1: Fork-Join / Thread Team")
    for p in [1, 2, 4, 8, 16, 32, 64]:
        if p <= (os.cpu_count() or 1) * 4:
            print(f"\nThreads = {p}")
            run_team(p)
