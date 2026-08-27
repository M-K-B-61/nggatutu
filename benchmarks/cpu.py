import math
import time
import hashlib
import zlib
from concurrent.futures import ThreadPoolExecutor
import os


def benchmark_prime_sieve(limit=50_000_000):
    """Sieve of Eratosthenes - 50M limit."""
    start = time.perf_counter()
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(math.isqrt(limit)) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    count = sum(sieve)
    elapsed = time.perf_counter() - start
    return count, elapsed


def benchmark_matrix_multiply(size=1000):
    """Matrix multiplication - 1000x1000 x5."""
    import numpy as np
    A = np.random.rand(size, size).astype(np.float64)
    B = np.random.rand(size, size).astype(np.float64)
    start = time.perf_counter()
    for _ in range(5):
        C = np.dot(A, B)
    elapsed = time.perf_counter() - start
    return elapsed / 5, C.sum()


def benchmark_crypto(iterations=5_000_000):
    """SHA256 hashing - 5M chained hashes."""
    data = b"benchmark test data payload for hashing benchmark"
    start = time.perf_counter()
    h = hashlib.sha256(data)
    for _ in range(iterations):
        h = hashlib.sha256(h.digest())
    elapsed = time.perf_counter() - start
    return iterations / elapsed


def benchmark_compression(iterations=300):
    """zlib compression - 8MB x300."""
    data = os.urandom(8 * 1024 * 1024)
    start = time.perf_counter()
    for _ in range(iterations):
        zlib.compress(data, 6)
    elapsed = time.perf_counter() - start
    return iterations * 8 / elapsed


def benchmark_pi_digits(digits=50_000_000):
    """Pi calculation - 50M digits single core."""
    start = time.perf_counter()
    pi = 0.0
    for i in range(digits):
        pi += ((-1) ** i) / (2 * i + 1)
    pi *= 4
    elapsed = time.perf_counter() - start
    return elapsed, pi


def benchmark_multi_core_stress(duration=12):
    """Multi-core stress - 12s all cores maxed."""
    cores = os.cpu_count() or 4

    def worker(stop_time):
        total = 0.0
        while time.perf_counter() < stop_time:
            total += math.sqrt(abs(total) + 1)
            total += math.sin(total) * math.cos(total)
            total += math.atan2(total, 1.0)
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
    print("  CPU BENCHMARK - EXTREME STRESS")
    print("=" * 55, flush=True)

    scores = {}

    print("\n[1/6] Prime Sieve (50M)...   ", end="", flush=True)
    primes, t1 = benchmark_prime_sieve()
    scores["prime"] = primes / t1 / 1000
    print(f"{t1:.2f}s | {primes} primes | Score: {scores['prime']:.0f}", flush=True)

    print("[2/6] Matrix (1000x1000 x5).", end="", flush=True)
    t2, _ = benchmark_matrix_multiply()
    scores["matrix"] = 5000 / t2
    print(f"{t2:.2f}s | Score: {scores['matrix']:.0f}", flush=True)

    print("[3/6] SHA256 (5M hashes)...  ", end="", flush=True)
    hash_rate = benchmark_crypto()
    scores["crypto"] = hash_rate / 100000
    print(f"{hash_rate:.0f} ops/s | Score: {scores['crypto']:.0f}", flush=True)

    print("[4/6] Compression (8MB x300).", end="", flush=True)
    comp_speed = benchmark_compression()
    scores["compression"] = comp_speed / 100
    print(f"{comp_speed:.0f} MB/s | Score: {scores['compression']:.0f}", flush=True)

    print("[5/6] Pi (50M digits)...      ", end="", flush=True)
    t5, pi_val = benchmark_pi_digits()
    scores["pi"] = 500000 / t5
    print(f"{t5:.2f}s | Score: {scores['pi']:.0f}", flush=True)

    print("[6/6] Multi-Core (12s)...     ", end="", flush=True)
    t6, _ = benchmark_multi_core_stress(12)
    scores["multicore"] = t6 * 30
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
