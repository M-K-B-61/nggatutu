from .cpu import run_cpu_benchmark
from .memory import run_memory_benchmark
from .disk import run_disk_benchmark

__all__ = ["run_cpu_benchmark", "run_memory_benchmark", "run_disk_benchmark"]
