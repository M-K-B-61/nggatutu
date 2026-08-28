"""Memory benchmark - sequential, random, copy, bandwidth, latency, cache."""
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
    size = 1024 * 1024
    arr = list(range(size))
    random.shuffle(arr)

    start = time.perf_counter()
    idx = 0
    for _ in range(iterations):
        idx = arr[idx]
    elapsed = time.perf_counter() - start

    ns_per_op = elapsed / iterations * 1e9
    return ns_per_op, idx


def benchmark_bandwidth(size_mb=256):
    """Memory bandwidth test - read + write throughput."""
    data = bytearray(os.urandom(size_mb * 1024 * 1024))

    start = time.perf_counter()
    for i in range(0, len(data), 4096):
        data[i] = 0xFF
    write_elapsed = time.perf_counter() - start
    write_bw = size_mb / write_elapsed if write_elapsed > 0 else 0

    start = time.perf_counter()
    total = 0
    for i in range(0, len(data), 4096):
        total += data[i]
    read_elapsed = time.perf_counter() - start
    read_bw = size_mb / read_elapsed if read_elapsed > 0 else 0

    return (write_bw + read_bw) / 2, write_bw, read_bw


def benchmark_cache(iterations=50_000_000):
    """Cache performance test - L1/L2 access patterns."""
    size = 16 * 1024
    arr = bytearray(os.urandom(size))

    start = time.perf_counter()
    total = 0
    for _ in range(iterations):
        for i in range(0, size, 64):
            total += arr[i]
    elapsed = time.perf_counter() - start

    ops_per_sec = iterations * (size // 64) / elapsed
    return ops_per_sec, total


def run_memory_benchmark():
    """Run full memory benchmark suite."""
    print("\n" + "=" * 60)
    print("  MEMORY BENCHMARK")
    print("=" * 60, flush=True)

    scores = {}

    print("\n[1/7] Sequential Write (128MB)...  ", end="", flush=True)
    seq_write = benchmark_sequential_write()
    scores["seq_write"] = seq_write / 100
    print(f"{seq_write:.0f} MB/s | Score: {scores['seq_write']:.0f}", flush=True)

    print("[2/7] Sequential Read (128MB)...   ", end="", flush=True)
    seq_read, _ = benchmark_sequential_read()
    scores["seq_read"] = seq_read / 100
    print(f"{seq_read:.0f} MB/s | Score: {scores['seq_read']:.0f}", flush=True)

    print("[3/7] Random Access (2M ops)...    ", end="", flush=True)
    random_mops, _ = benchmark_random_access()
    scores["random"] = random_mops * 10
    print(f"{random_mops:.1f} MOPS | Score: {scores['random']:.0f}", flush=True)

    print("[4/7] Memory Copy (64MB)...        ", end="", flush=True)
    copy_speed = benchmark_copy()
    scores["copy"] = copy_speed / 50
    print(f"{copy_speed:.0f} MB/s | Score: {scores['copy']:.0f}", flush=True)

    print("[5/7] Latency Test...              ", end="", flush=True)
    latency, _ = benchmark_latency()
    scores["latency"] = max(0, 1000 - latency)
    print(f"{latency:.0f} ns | Score: {scores['latency']:.0f}", flush=True)

    print("[6/7] Bandwidth Test (256MB)...    ", end="", flush=True)
    bw_avg, bw_write, bw_read = benchmark_bandwidth()
    scores["bandwidth"] = bw_avg / 50
    print(f"R:{bw_read:.0f} W:{bw_write:.0f} MB/s | Score: {scores['bandwidth']:.0f}", flush=True)

    print("[7/7] Cache Performance...         ", end="", flush=True)
    cache_ops, _ = benchmark_cache()
    scores["cache"] = cache_ops / 1_000_000
    print(f"{cache_ops/1e6:.1f} Mops/s | Score: {scores['cache']:.0f}", flush=True)

    final_score = sum(scores.values()) / len(scores)

    print("\n" + "-" * 60)
    print(f"  MEMORY SCORE: {final_score:.0f}")
    print(f"  Read: {seq_read:.0f} MB/s | Write: {seq_write:.0f} MB/s | BW: {bw_avg:.0f} MB/s")
    print(f"  Latency: {latency:.0f} ns | Cache: {cache_ops/1e6:.1f} Mops/s")
    print("-" * 60, flush=True)

    return {
        "scores": scores,
        "final_score": final_score,
        "seq_read": seq_read,
        "seq_write": seq_write,
        "copy_speed": copy_speed,
        "latency_ns": latency,
        "bandwidth": bw_avg,
        "cache_ops": cache_ops,
    }
