OPENMP LAB PRACTICE — PYTHON ONLY

This folder contains Python implementations for Labs 1–5 from the supplied
OpenMP Lab Practice Manual. The manual presents Python equivalents using
ThreadPoolExecutor, Numba/prange, NumPy, and ProcessPoolExecutor.

Install:
    python -m pip install -r requirements.txt

Run:
    python lab1_fork_join.py
    python lab2_pi_reduction.py
    python lab3_mandelbrot_scheduling.py
    python lab4_false_sharing.py
    python lab5_parallel_merge_sort.py

Notes:
- Large benchmark values in the manual are intentionally reduced in some
  scripts so they can be tested on an ordinary student computer.
- Increase ITERATIONS/N_STEPS/N only after confirming that the program works.
- Benchmark results depend on CPU, operating system, background load, and
  Numba configuration.
- Lab 1 uses Python threads; CPU-bound Python bytecode is affected by the GIL,
  while the Numba-based numerical labs use compiled parallel kernels.
