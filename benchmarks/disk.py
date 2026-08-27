import os
import time
import random
import tempfile


def benchmark_sequential_write(test_file, size_mb=256):
    """Sequential write benchmark."""
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
    """Sequential read benchmark."""
    file_size = os.path.getsize(test_file)

    start = time.perf_counter()
    with open(test_file, "rb") as f:
        while f.read(1024 * 1024):
            pass
    elapsed = time.perf_counter() - start

    return file_size / (1024 * 1024) / elapsed


def benchmark_random_write(test_file, size_mb=64):
    """Random 4K write benchmark."""
    chunk_size = 4096  # 4KB
    data = os.urandom(chunk_size)
    file_size = size_mb * 1024 * 1024
    num_chunks = file_size // chunk_size

    # Create file first
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


def benchmark_random_read(test_file, size_mb=64):
    """Random 4K read benchmark."""
    chunk_size = 4096  # 4KB
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


def run_disk_benchmark():
    """Run full disk I/O benchmark suite."""
    print("\n" + "=" * 50, flush=True)
    print("  DISK I/O BENCHMARK", flush=True)
    print("=" * 50, flush=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "benchmark.tmp")

        print("\n[1/4] Sequential Write...    ", end="", flush=True)
        seq_write = benchmark_sequential_write(test_file)
        print(f"{seq_write:.2f} MB/s", flush=True)

        print("[2/4] Sequential Read...     ", end="", flush=True)
        seq_read = benchmark_sequential_read(test_file)
        print(f"{seq_read:.2f} MB/s", flush=True)

        print("[3/4] Random Write (4K)...   ", end="", flush=True)
        rand_write = benchmark_random_write(test_file)
        print(f"{rand_write:.2f} MB/s", flush=True)

        print("[4/4] Random Read (4K)...    ", end="", flush=True)
        rand_read = benchmark_random_read(test_file)
        print(f"{rand_read:.2f} MB/s", flush=True)

    print("\n" + "-" * 50, flush=True)
    print(f"  Sequential: R {seq_read:.2f} / W {seq_write:.2f} MB/s", flush=True)
    print(f"  Random:     R {rand_read:.2f} / W {rand_write:.2f} MB/s", flush=True)
    print("-" * 50, flush=True)

    return {
        "seq_read": seq_read,
        "seq_write": seq_write,
        "rand_read": rand_read,
        "rand_write": rand_write,
    }
