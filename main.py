#!/usr/bin/env python3
"""
Ngga Tutu - Cross Platform Benchmark Tool
"""

import sys
import platform
import time
import json
import os
from datetime import datetime

from benchmarks.cpu import run_cpu_benchmark
from benchmarks.memory import run_memory_benchmark
from benchmarks.disk import run_disk_benchmark

VERSION = "0.1.0"

BANNER = f"""
+-----------------------------------------------+
|              Ngga Tutu Benchmark              |
|            v{VERSION} - Cross Platform            |
+-----------------------------------------------+
"""


def print_usage():
    print("Usage: python main.py <command>\n")
    print("Commands:")
    print("  cpu       Run CPU benchmark")
    print("  memory    Run memory benchmark")
    print("  disk      Run disk I/O benchmark")
    print("  quick     Run all benchmarks")
    print("  info      Show system information")
    print("  version   Show version")
    print("  help      Show this help")


def print_system_info():
    print(BANNER)
    print("System Information")
    print("=" * 50)
    print(f"  OS:         {platform.system()} {platform.release()}")
    print(f"  Arch:       {platform.machine()}")
    print(f"  Python:     {platform.python_version()}")
    print(f"  CPU:        {platform.processor() or 'Unknown'}")
    print(f"  Time:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def run_quick_benchmark():
    """Run all benchmarks and save results."""
    print(BANNER)
    print("Running all benchmarks...\n")

    results = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "os": platform.system(),
            "arch": platform.machine(),
            "python": platform.python_version(),
        },
    }

    # Run benchmarks
    results["cpu"] = run_cpu_benchmark()
    results["memory"] = run_memory_benchmark()
    results["disk"] = run_disk_benchmark()

    # Summary
    print("\n" + "=" * 50)
    print("  FINAL RESULTS")
    print("=" * 50)
    print(f"  CPU Score:      {results['cpu']['final_score']:.2f}")
    print(f"  Memory:         {results['memory']['avg_bandwidth']:.2f} MB/s")
    print(f"  Disk Seq:       R {results['disk']['seq_read']:.2f} / W {results['disk']['seq_write']:.2f} MB/s")
    print(f"  Disk Rand:      R {results['disk']['rand_read']:.2f} / W {results['disk']['rand_write']:.2f} MB/s")
    print("=" * 50)

    # Save to file
    filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {filename}")

    return results


def main():
    if len(sys.argv) < 2:
        print(BANNER)
        print_usage()
        return

    cmd = sys.argv[1].lower()

    if cmd == "cpu":
        run_cpu_benchmark()
    elif cmd == "memory":
        run_memory_benchmark()
    elif cmd == "disk":
        run_disk_benchmark()
    elif cmd == "quick":
        run_quick_benchmark()
    elif cmd == "info":
        print_system_info()
    elif cmd == "version":
        print(f"nggatutu v{VERSION}")
    elif cmd in ("help", "-h", "--help"):
        print_usage()
    else:
        print(f"Unknown command: {cmd}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
