import os
import time
import random
import tempfile


def benchmark_sequential_write(test_file, size_mb=256):
    """Sequential write - large file."""
    chunk_size = 1024 * 1024  # 1MB chunks
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
    return size_mb / elapsed


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
    return size_mb / elapsed


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
    print("\n" + "=" * 55)
    print("  DISK I/O BENCHMARK - STRESS TEST")
    print("=" * 55, flush=True)

    scores = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "benchmark.tmp")

        print("\n[1/5] Sequential Write (256MB)... ", end="", flush=True)
        seq_write = benchmark_sequential_write(test_file)
        scores["seq_write"] = seq_write / 20
        print(f"{seq_write:.0f} MB/s | Score: {scores['seq_write']:.0f}", flush=True)

        print("[2/5] Sequential Read (256MB)...  ", end="", flush=True)
        seq_read = benchmark_sequential_read(test_file)
        scores["seq_read"] = seq_read / 20
        print(f"{seq_read:.0f} MB/s | Score: {scores['seq_read']:.0f}", flush=True)

        print("[3/5] Random Write 4K (128MB)... ", end="", flush=True)
        rand_write = benchmark_random_write(test_file)
        scores["rand_write"] = rand_write / 10
        print(f"{rand_write:.0f} MB/s | Score: {scores['rand_write']:.0f}", flush=True)

        print("[4/5] Random Read 4K (128MB)...  ", end="", flush=True)
        rand_read = benchmark_random_read(test_file)
        scores["rand_read"] = rand_read / 10
        print(f"{rand_read:.0f} MB/s | Score: {scores['rand_read']:.0f}", flush=True)

        print("[5/5] Mixed Workload (64MB)...   ", end="", flush=True)
        mixed = benchmark_mixed_workload(test_file)
        scores["mixed"] = mixed / 5
        print(f"{mixed:.0f} MB/s | Score: {scores['mixed']:.0f}", flush=True)

    final_score = sum(scores.values()) / len(scores)

    print("\n" + "-" * 55)
    print(f"  DISK SCORE: {final_score:.0f}")
    print("-" * 55, flush=True)

    return {
        "scores": scores,
        "final_score": final_score,
        "seq_write": seq_write,
        "seq_read": seq_read,
        "rand_write": rand_write,
        "rand_read": rand_read,
        "mixed": mixed,
    }
