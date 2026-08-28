"""Disk benchmark - sequential, random 4K, IOPS, latency, mixed."""
import os
import time
import random
import tempfile


def benchmark_sequential_write(test_file, size_mb=256):
    """Sequential write - large file."""
    chunk_size = 1024 * 1024
    data = os.urandom(chunk_size)
    iterations = size_mb

    start = time.perf_counter()
    with open(test_file, "wb") as f:
        for _ in range(iterations):
            f.write(data)
        f.flush()
        os.fsync(f.fileno())
    elapsed = time.perf_counter() - start
    return size_mb / elapsed


def benchmark_sequential_read(test_file):
    """Sequential read - large file."""
    file_size = os.path.getsize(test_file)
    start = time.perf_counter()
    with open(test_file, "rb") as f:
        while f.read(1024 * 1024):
            pass
    elapsed = time.perf_counter() - start
    return file_size / (1024 * 1024) / elapsed


def benchmark_random_write(test_file, size_mb=128):
    """Random 4K write - IOPS test."""
    chunk_size = 4096
    data = os.urandom(chunk_size)
    file_size = size_mb * 1024 * 1024
    num_chunks = file_size // chunk_size

    with open(test_file, "wb") as f:
        f.write(b"\x00" * file_size)

    start = time.perf_counter()
    with open(test_file, "r+b") as f:
        for _ in range(num_chunks):
            offset = random.randint(0, num_chunks - 1) * chunk_size
            f.seek(offset)
            f.write(data)
        f.flush()
        os.fsync(f.fileno())
    elapsed = time.perf_counter() - start
    return size_mb / elapsed, num_chunks / elapsed


def benchmark_random_read(test_file, size_mb=128):
    """Random 4K read - IOPS test."""
    chunk_size = 4096
    file_size = min(os.path.getsize(test_file), size_mb * 1024 * 1024)
    num_chunks = file_size // chunk_size
    indices = [random.randint(0, num_chunks - 1) for _ in range(num_chunks)]

    start = time.perf_counter()
    with open(test_file, "rb") as f:
        for idx in indices:
            f.seek(idx * chunk_size)
            f.read(chunk_size)
    elapsed = time.perf_counter() - start
    return size_mb / elapsed, num_chunks / elapsed


def benchmark_4k_write(test_file, count=100_000):
    """Pure 4K random write IOPS."""
    chunk = os.urandom(4096)
    file_size = count * 4096

    with open(test_file, "wb") as f:
        f.write(b"\x00" * file_size)

    start = time.perf_counter()
    with open(test_file, "r+b") as f:
        for _ in range(count):
            offset = random.randint(0, count - 1) * 4096
            f.seek(offset)
            f.write(chunk)
        f.flush()
        os.fsync(f.fileno())
    elapsed = time.perf_counter() - start
    iops = count / elapsed
    latency_us = (elapsed / count) * 1_000_000
    return iops, latency_us


def benchmark_4k_read(test_file, count=100_000):
    """Pure 4K random read IOPS."""
    chunk_size = 4096
    file_size = min(os.path.getsize(test_file), count * 4096)
    num_chunks = file_size // chunk_size
    indices = [random.randint(0, num_chunks - 1) for _ in range(count)]

    start = time.perf_counter()
    with open(test_file, "rb") as f:
        for idx in indices:
            f.seek(idx * chunk_size)
            f.read(chunk_size)
    elapsed = time.perf_counter() - start
    iops = count / elapsed
    latency_us = (elapsed / count) * 1_000_000
    return iops, latency_us


def benchmark_mixed_workload(test_file, size_mb=64):
    """Mixed read/write - real world simulation."""
    chunk_size = 4096
    file_size = size_mb * 1024 * 1024
    num_chunks = file_size // chunk_size

    with open(test_file, "wb") as f:
        f.write(os.urandom(file_size))

    start = time.perf_counter()
    with open(test_file, "r+b") as f:
        for _ in range(num_chunks // 2):
            if random.random() < 0.7:
                idx = random.randint(0, num_chunks - 1)
                f.seek(idx * chunk_size)
                f.read(chunk_size)
            else:
                idx = random.randint(0, num_chunks - 1)
                f.seek(idx * chunk_size)
                f.write(os.urandom(chunk_size))
        f.flush()
    elapsed = time.perf_counter() - start
    return size_mb / elapsed


def run_disk_benchmark():
    """Run full disk I/O benchmark suite."""
    print("\n" + "=" * 60)
    print("  DISK I/O BENCHMARK")
    print("=" * 60, flush=True)

    scores = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "benchmark.tmp")

        print("\n[1/8] Sequential Write (256MB)... ", end="", flush=True)
        seq_write = benchmark_sequential_write(test_file)
        scores["seq_write"] = seq_write / 20
        print(f"{seq_write:.0f} MB/s | Score: {scores['seq_write']:.0f}", flush=True)

        print("[2/8] Sequential Read (256MB)...  ", end="", flush=True)
        seq_read = benchmark_sequential_read(test_file)
        scores["seq_read"] = seq_read / 20
        print(f"{seq_read:.0f} MB/s | Score: {scores['seq_read']:.0f}", flush=True)

        print("[3/8] Random Write 4K (128MB)... ", end="", flush=True)
        rand_write, rand_write_iops = benchmark_random_write(test_file)
        scores["rand_write"] = rand_write / 10
        print(f"{rand_write:.0f} MB/s | Score: {scores['rand_write']:.0f}", flush=True)

        print("[4/8] Random Read 4K (128MB)...  ", end="", flush=True)
        rand_read, rand_read_iops = benchmark_random_read(test_file)
        scores["rand_read"] = rand_read / 10
        print(f"{rand_read:.0f} MB/s | Score: {scores['rand_read']:.0f}", flush=True)

        print("[5/8] 4K Write IOPS...           ", end="", flush=True)
        iops_4k_write, lat_4k_write = benchmark_4k_write(test_file)
        scores["iops_write"] = iops_4k_write / 1000
        print(f"{iops_4k_write:.0f} IOPS | {lat_4k_write:.1f} us | Score: {scores['iops_write']:.0f}", flush=True)

        print("[6/8] 4K Read IOPS...            ", end="", flush=True)
        iops_4k_read, lat_4k_read = benchmark_4k_read(test_file)
        scores["iops_read"] = iops_4k_read / 1000
        print(f"{iops_4k_read:.0f} IOPS | {lat_4k_read:.1f} us | Score: {scores['iops_read']:.0f}", flush=True)

        print("[7/8] Mixed Workload (64MB)...   ", end="", flush=True)
        mixed = benchmark_mixed_workload(test_file)
        scores["mixed"] = mixed / 5
        print(f"{mixed:.0f} MB/s | Score: {scores['mixed']:.0f}", flush=True)

        print("[8/8] Latency Benchmark...       ", end="", flush=True)
        avg_latency = (lat_4k_read + lat_4k_write) / 2
        scores["latency"] = max(0, 1000 - avg_latency / 10)
        print(f"Read: {lat_4k_read:.1f}us Write: {lat_4k_write:.1f}us | Score: {scores['latency']:.0f}", flush=True)

    final_score = sum(scores.values()) / len(scores)

    print("\n" + "-" * 60)
    print(f"  DISK SCORE: {final_score:.0f}")
    print(f"  Seq R/W: {seq_read:.0f}/{seq_write:.0f} MB/s")
    print(f"  4K IOPS: R={iops_4k_read:.0f} W={iops_4k_write:.0f}")
    print(f"  Latency: R={lat_4k_read:.1f}us W={lat_4k_write:.1f}us")
    print("-" * 60, flush=True)

    return {
        "scores": scores,
        "final_score": final_score,
        "seq_write": seq_write,
        "seq_read": seq_read,
        "rand_write": rand_write,
        "rand_read": rand_read,
        "mixed": mixed,
        "iops_read": iops_4k_read,
        "iops_write": iops_4k_write,
        "latency_read_us": lat_4k_read,
        "latency_write_us": lat_4k_write,
    }
