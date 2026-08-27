import math
import time
import hashlib
import zlib
from concurrent.futures import ThreadPoolExecutor
import os


def benchmark_prime_sieve(limit=5_000_000):
    """Sieve of Eratosthenes - heavy CPU test."""
    start = time.perf_counter()
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    count = sum(sieve)
    elapsed = time.perf_counter() - start
    return count, elapsed


def benchmark_matrix_multiply(size=500):
    """Matrix multiplication - heavy FPU test."""
    import numpy as np
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    start = time.perf_counter()
    C = np.dot(A, B)
    elapsed = time.perf_counter() - start
    return elapsed, C.sum()


def benchmark_crypto(iterations=500_000):
    """SHA256 hashing - CPU intensive."""
    data = b"benchmark test data payload for hashing"
    start = time.perf_counter()
    for _ in range(iterations):
        hashlib.sha256(data).digest()
    elapsed = time.perf_counter() - start
    return iterations / elapsed


def benchmark_compression(iterations=100):
    """zlib compression - CPU + memory test."""
    data = os.urandom(1024 * 1024)  # 1MB
    start = time.perf_counter()
    for _ in range(iterations):
        zlib.compress(data, 6)
    elapsed = time.perf_counter() - start
    return iterations * 1024 * 1024 / elapsed / (1024 * 1024)


def benchmark_pi_digits(digits=1_000_000):
    """Pi calculation - single core heavy test."""
    start = time.perf_counter()
    pi = 0.0
    for i in range(digits):
        pi += ((-1) ** i) / (2 * i + 1)
    pi *= 4
    elapsed = time.perf_counter() - start
    return elapsed, pi


def benchmark_multi_core_stress(duration=5):
    """Multi-core stress test for fixed duration."""
    cores = os.cpu_count() or 4

    def worker(stop_time):
        total = 0.0
        while time.perf_counter() < stop_time:
            total += math.sqrt(total + 1)
        return total

    start = time.perf_counter()
    stop_time = start + duration
    with ThreadPoolExecutor(max_workers=cores) as executor:
        futures = [executor.submit(worker, stop_time) for _ in range(cores)]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start
    return elapsed, sum(results)


def run_cpu_benchmark():
    """Run full CPU benchmark suite."""
    print("\n" + "=" * 55)
    print("  CPU BENCHMARK - STRESS TEST")
    print("=" * 55, flush=True)

    scores = {}

    print("\n[1/6] Prime Sieve (5M)...   ", end="", flush=True)
    primes, t1 = benchmark_prime_sieve()
    scores["prime"] = primes / t1 / 1000
    print(f"{t1:.2f}s | {primes} primes | Score: {scores['prime']:.0f}", flush=True)

    print("[2/6] Matrix Multiply...    ", end="", flush=True)
    t2, _ = benchmark_matrix_multiply()
    scores["matrix"] = 1000 / t2
    print(f"{t2:.2f}s | Score: {scores['matrix']:.0f}", flush=True)

    print("[3/6] SHA256 Hashing...     ", end="", flush=True)
    hash_rate = benchmark_crypto()
    scores["crypto"] = hash_rate / 1000
    print(f"{hash_rate:.0f} ops/s | Score: {scores['crypto']:.0f}", flush=True)

    print("[4/6] Compression...        ", end="", flush=True)
    comp_speed = benchmark_compression()
    scores["compression"] = comp_speed / 10
    print(f"{comp_speed:.0f} MB/s | Score: {scores['compression']:.0f}", flush=True)

    print("[5/6] Pi Calculation...     ", end="", flush=True)
    t5, pi_val = benchmark_pi_digits()
    scores["pi"] = 10000 / t5
    print(f"{t5:.2f}s | Score: {scores['pi']:.0f}", flush=True)

    print("[6/6] Multi-Core Stress...  ", end="", flush=True)
    t6, _ = benchmark_multi_core_stress(3)
    scores["multicore"] = t6 * 100
    print(f"{t6:.2f}s | Score: {scores['multicore']:.0f}", flush=True)

    final_score = sum(scores.values()) / len(scores)

    print("\n" + "-" * 55)
    print(f"  CPU SCORE: {final_score:.0f}")
    print("-" * 55, flush=True)

    return {
        "scores": scores,
        "final_score": final_score,
        "prime_count": primes,
        "matrix_time": t2,
        "hash_rate": hash_rate,
        "compression_speed": comp_speed,
        "pi_time": t5,
        "multicore_time": t6,
    }
