import math
import time
from concurrent.futures import ThreadPoolExecutor
import os


def benchmark_single_core_int(iterations=10_000_000):
    """Single core integer operations benchmark."""
    start = time.perf_counter()
    total = 0
    for i in range(iterations):
        total += i * i
    elapsed = time.perf_counter() - start
    return iterations / elapsed / 1_000_000, total


def benchmark_single_core_float(iterations=10_000_000):
    """Single core floating point operations benchmark."""
    start = time.perf_counter()
    total = 0.0
    for i in range(iterations):
        total += math.sqrt(float(i))
    elapsed = time.perf_counter() - start
    return iterations / elapsed / 1_000_000, total


def benchmark_multi_core(iterations=5_000_000):
    """Multi core benchmark using all available cores."""
    cores = os.cpu_count() or 4

    def worker(n):
        total = 0.0
        for i in range(n):
            total += math.sqrt(float(i))
        return total

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=cores) as executor:
        futures = [executor.submit(worker, iterations) for _ in range(cores)]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start

    total_ops = iterations * cores
    return total_ops / elapsed / 1_000_000, sum(results)


def run_cpu_benchmark():
    """Run full CPU benchmark suite."""
    print("\n" + "=" * 50, flush=True)
    print("  CPU BENCHMARK", flush=True)
    print("=" * 50, flush=True)

    print("\n[1/3] Single Core Integer... ", end="", flush=True)
    int_score, _ = benchmark_single_core_int()
    print(f"{int_score:.2f} MOPS", flush=True)

    print("[2/3] Single Core Float...   ", end="", flush=True)
    float_score, _ = benchmark_single_core_float()
    print(f"{float_score:.2f} MOPS", flush=True)

    print("[3/3] Multi Core...          ", end="", flush=True)
    multi_score, _ = benchmark_multi_core()
    print(f"{multi_score:.2f} MOPS", flush=True)

    final_score = (int_score + float_score + multi_score) / 3
    print("\n" + "-" * 50, flush=True)
    print(f"  CPU SCORE: {final_score:.2f}", flush=True)
    print("-" * 50, flush=True)

    return {
        "single_int": int_score,
        "single_float": float_score,
        "multi_core": multi_score,
        "final_score": final_score,
    }
