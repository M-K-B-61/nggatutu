import time
import random
import os


def benchmark_sequential_write(size_mb=128):
    """Sequential write - large block."""
    chunk = os.urandom(1024 * 1024)
    start = time.perf_counter()
    data = bytearray()
    for _ in range(size_mb):
        data.extend(chunk)
    elapsed = time.perf_counter() - start
    return size_mb / elapsed


def benchmark_sequential_read(size_mb=128):
    """Sequential read - large block."""
    data = bytearray(os.urandom(size_mb * 1024 * 1024))
    start = time.perf_counter()
    total = 0
    for i in range(0, len(data), 4096):
        total += data[i]
    elapsed = time.perf_counter() - start
    return size_mb / elapsed, total


def benchmark_random_access(size_mb=64, ops=2_000_000):
    """Random access - stress memory controller."""
    data = bytearray(os.urandom(size_mb * 1024 * 1024))
    indices = [random.randint(0, len(data) - 1) for _ in range(ops)]

    start = time.perf_counter()
    total = 0
    for idx in indices:
        total += data[idx]
    elapsed = time.perf_counter() - start
    return ops / elapsed / 1_000_000, total


def benchmark_copy(size_mb=64):
    """Memory copy speed."""
    src = os.urandom(size_mb * 1024 * 1024)
    start = time.perf_counter()
    dst = bytearray(src)
    elapsed = time.perf_counter() - start
    return size_mb / elapsed


def benchmark_latency(iterations=10_000_000):
    """Memory latency test - pointer chasing."""
    size = 1024 * 1024  # 1M entries
    arr = list(range(size))
    random.shuffle(arr)

    start = time.perf_counter()
    idx = 0
    for _ in range(iterations):
        idx = arr[idx]
    elapsed = time.perf_counter() - start

    ns_per_op = elapsed / iterations * 1e9
    return ns_per_op, idx


def run_memory_benchmark():
    """Run full memory benchmark suite."""
    print("\n" + "=" * 55)
    print("  MEMORY BENCHMARK - STRESS TEST")
    print("=" * 55, flush=True)

    scores = {}

    print("\n[1/5] Sequential Write (128MB)... ", end="", flush=True)
    seq_write = benchmark_sequential_write()
    scores["seq_write"] = seq_write / 100
    print(f"{seq_write:.0f} MB/s | Score: {scores['seq_write']:.0f}", flush=True)

    print("[2/5] Sequential Read (128MB)...  ", end="", flush=True)
    seq_read, _ = benchmark_sequential_read()
    scores["seq_read"] = seq_read / 100
    print(f"{seq_read:.0f} MB/s | Score: {scores['seq_read']:.0f}", flush=True)

    print("[3/5] Random Access (2M ops)...  ", end="", flush=True)
    random_mops, _ = benchmark_random_access()
    scores["random"] = random_mops * 10
    print(f"{random_mops:.1f} MOPS | Score: {scores['random']:.0f}", flush=True)

    print("[4/5] Memory Copy (64MB)...      ", end="", flush=True)
    copy_speed = benchmark_copy()
    scores["copy"] = copy_speed / 50
    print(f"{copy_speed:.0f} MB/s | Score: {scores['copy']:.0f}", flush=True)

    print("[5/5] Latency Test...            ", end="", flush=True)
    latency, _ = benchmark_latency()
    scores["latency"] = max(0, 1000 - latency)
    print(f"{latency:.0f} ns | Score: {scores['latency']:.0f}", flush=True)

    final_score = sum(scores.values()) / len(scores)

    print("\n" + "-" * 55)
    print(f"  MEMORY SCORE: {final_score:.0f}")
    print("-" * 55, flush=True)

    return {
        "scores": scores,
        "final_score": final_score,
        "seq_write": seq_write,
        "seq_read": seq_read,
        "random_mops": random_mops,
        "copy_speed": copy_speed,
        "latency_ns": latency,
    }
