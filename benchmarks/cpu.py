"""CPU benchmark - single core, multi core, AES, integer, floating point, compression, hashing."""
import math
import time
import hashlib
import zlib
import os
from concurrent.futures import ThreadPoolExecutor


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


def benchmark_decompression(iterations=100):
    """Decompression speed."""
    data = os.urandom(8 * 1024 * 1024)
    compressed = zlib.compress(data, 6)
    start = time.perf_counter()
    for _ in range(iterations):
        zlib.decompress(compressed)
    elapsed = time.perf_counter() - start
    return iterations * 8 / elapsed


def benchmark_single_core(duration=8):
    """Single core stress - one thread maxed."""
    start = time.perf_counter()
    stop_time = start + duration
    total = 0.0
    while time.perf_counter() < stop_time:
        total += math.sqrt(abs(total) + 1)
        total += math.sin(total) * math.cos(total)
        total += math.atan2(total, 1.0)
    elapsed = time.perf_counter() - start
    return elapsed, total


def benchmark_multi_core_stress(duration=12):
    """Multi-core stress - all cores maxed."""
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


def benchmark_integer(iterations=100_000_000):
    """Integer arithmetic - heavy integer operations."""
    start = time.perf_counter()
    a = 123456789
    b = 987654321
    result = 0
    for _ in range(iterations):
        result += a * b
        result += a // b if b != 0 else 0
        result ^= a
        result = result & 0xFFFFFFFF
    elapsed = time.perf_counter() - start
    return iterations / elapsed, result


def benchmark_floating_point(iterations=100_000_000):
    """Floating point arithmetic - heavy FP operations."""
    start = time.perf_counter()
    a = 3.141592653589793
    b = 2.718281828459045
    result = 0.0
    for _ in range(iterations):
        result += math.sqrt(a * b)
        result += math.sin(a) * math.cos(b)
        result += math.log(abs(result) + 1)
    elapsed = time.perf_counter() - start
    return iterations / elapsed, result


def benchmark_aes(iterations=2_000_000):
    """AES encryption/decryption - 2M operations."""
    from hashlib import sha256
    key = sha256(b"aes_benchmark_key").digest()
    data = os.urandom(16)

    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        encryptor = cipher.encryptor()
        decryptor = cipher.decryptor()

        start = time.perf_counter()
        for _ in range(iterations):
            ct = encryptor.update(data)
            encryptor.reset()
            pt = decryptor.update(ct)
            decryptor.reset()
        elapsed = time.perf_counter() - start
        return iterations / elapsed
    except ImportError:
        pass

    start = time.perf_counter()
    total = 0
    for _ in range(iterations):
        h = sha256(data).digest()
        total += h[0]
    elapsed = time.perf_counter() - start
    return iterations / elapsed


def benchmark_pi_digits(digits=50_000_000):
    """Pi calculation - 50M digits single core."""
    start = time.perf_counter()
    pi = 0.0
    for i in range(digits):
        pi += ((-1) ** i) / (2 * i + 1)
    pi *= 4
    elapsed = time.perf_counter() - start
    return elapsed, pi


def run_cpu_benchmark():
    """Run full CPU benchmark suite with separate scores."""
    print("\n" + "=" * 60)
    print("  CPU BENCHMARK")
    print("=" * 60, flush=True)

    scores = {}

    print("\n[1/9] Single Core Stress (8s)...  ", end="", flush=True)
    t1, _ = benchmark_single_core(8)
    scores["single_core"] = 1000 / t1 if t1 > 0 else 0
    print(f"{t1:.2f}s | Score: {scores['single_core']:.0f}", flush=True)

    print("[2/9] Multi Core Stress (12s)...  ", end="", flush=True)
    t2, _ = benchmark_multi_core_stress(12)
    cores = os.cpu_count() or 4
    scores["multi_core"] = (t2 * cores * 20) / t2 if t2 > 0 else 0
    print(f"{t2:.2f}s ({cores} cores) | Score: {scores['multi_core']:.0f}", flush=True)

    print("[3/9] Prime Sieve (50M)...        ", end="", flush=True)
    primes, t3 = benchmark_prime_sieve()
    scores["prime"] = primes / t3 / 1000
    print(f"{t3:.2f}s | {primes} primes | Score: {scores['prime']:.0f}", flush=True)

    print("[4/9] Matrix Multiply (1000x1000)..", end="", flush=True)
    t4, _ = benchmark_matrix_multiply()
    scores["matrix"] = 5000 / t4 if t4 > 0 else 0
    print(f"{t4:.2f}s | Score: {scores['matrix']:.0f}", flush=True)

    print("[5/9] Integer Arithmetic (100M)...", end="", flush=True)
    int_ops, t5 = benchmark_integer()
    scores["integer"] = int_ops / 1_000_000
    print(f"{int_ops/1e6:.1f} Mops/s | Score: {scores['integer']:.0f}", flush=True)

    print("[6/9] Floating Point (100M)...    ", end="", flush=True)
    fp_ops, t6 = benchmark_floating_point()
    scores["floating_point"] = fp_ops / 1_000_000
    print(f"{fp_ops/1e6:.1f} Mops/s | Score: {scores['floating_point']:.0f}", flush=True)

    print("[7/9] SHA256 (5M hashes)...       ", end="", flush=True)
    hash_rate = benchmark_crypto()
    scores["crypto"] = hash_rate / 100000
    print(f"{hash_rate:.0f} ops/s | Score: {scores['crypto']:.0f}", flush=True)

    print("[8/9] AES Encryption (2M)...      ", end="", flush=True)
    aes_rate = benchmark_aes()
    scores["aes"] = aes_rate / 100000
    print(f"{aes_rate:.0f} ops/s | Score: {scores['aes']:.0f}", flush=True)

    print("[9/9] Compression (8MB x300)...   ", end="", flush=True)
    comp_speed = benchmark_compression()
    scores["compression"] = comp_speed / 100
    print(f"{comp_speed:.0f} MB/s | Score: {scores['compression']:.0f}", flush=True)

    final_score = sum(scores.values()) / len(scores)

    print("\n" + "-" * 60)
    print(f"  CPU SCORE: {final_score:.0f}")
    print(f"  Single Core: {scores['single_core']:.0f} | Multi Core: {scores['multi_core']:.0f}")
    print("-" * 60, flush=True)

    return {
        "scores": scores,
        "final_score": final_score,
        "single_core_score": scores["single_core"],
        "multi_core_score": scores["multi_core"],
    }
