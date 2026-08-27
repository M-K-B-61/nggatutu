import time
import random


def benchmark_mem_write(size_mb=64, iterations=10):
    """Memory write benchmark."""
    size_bytes = size_mb * 1024 * 1024
    data = bytearray(size_bytes)

    start = time.perf_counter()
    for _ in range(iterations):
        for i in range(0, size_bytes, 4096):
            data[i] = i & 0xFF
    elapsed = time.perf_counter() - start

    total_mb = size_mb * iterations
    return total_mb / elapsed


def benchmark_mem_read(size_mb=64, iterations=10):
    """Memory read benchmark."""
    size_bytes = size_mb * 1024 * 1024
    data = bytearray(size_bytes)
    for i in range(0, size_bytes, 4096):
        data[i] = i & 0xFF

    start = time.perf_counter()
    total = 0
    for _ in range(iterations):
        for i in range(0, size_bytes, 4096):
            total += data[i]
    elapsed = time.perf_counter() - start

    total_mb = size_mb * iterations
    return total_mb / elapsed, total


def benchmark_mem_random(size_mb=64, iterations=1_000_000):
    """Memory random access benchmark."""
    size_bytes = size_mb * 1024 * 1024
    data = bytearray(size_bytes)
    for i in range(0, size_bytes, 4096):
        data[i] = i & 0xFF

    indices = [random.randint(0, size_bytes - 1) for _ in range(iterations)]

    start = time.perf_counter()
    total = 0
    for idx in indices:
        total += data[idx]
    elapsed = time.perf_counter() - start

    ops_per_sec = iterations / elapsed
    return ops_per_sec / 1_000_000, total


def run_memory_benchmark():
    """Run full memory benchmark suite."""
    print("\n" + "=" * 50)
    print("  MEMORY BENCHMARK")
    print("=" * 50)

    print("\n[1/3] Sequential Write...    ", end="", flush=True)
    write_speed = benchmark_mem_write()
    print(f"{write_speed:.2f} MB/s")

    print("[2/3] Sequential Read...     ", end="", flush=True)
    read_speed, _ = benchmark_mem_read()
    print(f"{read_speed:.2f} MB/s")

    print("[3/3] Random Access...       ", end="", flush=True)
    random_speed, _ = benchmark_mem_random()
    print(f"{random_speed:.2f} MOPS")

    avg_bandwidth = (write_speed + read_speed) / 2
    print("\n" + "-" * 50)
    print(f"  MEMORY BANDWIDTH: {avg_bandwidth:.2f} MB/s")
    print("-" * 50)

    return {
        "write_mbps": write_speed,
        "read_mbps": read_speed,
        "random_mops": random_speed,
        "avg_bandwidth": avg_bandwidth,
    }
