<div align="center">

# Ngga Tutu

### PC Performance Benchmark Suite

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

<br>

Stress test your PC, measure real performance, get a professional grade.

[Installation](#installation) · [Features](#features) · [Usage](#usage) · [Contributing](#how-to-contribute)

</div>

---

## Features

<table>
<tr>
<td width="50%">

### CPU Benchmark
- Prime Sieve (50M numbers)
- Matrix Multiply (1000×1000)
- SHA256 Hashing (5M ops)
- AES Encryption
- Compression (zlib)
- Single & Multi-core tests

</td>
<td width="50%">

### Memory Benchmark
- Sequential Read/Write
- Random Read/Write
- Copy Speed
- Bandwidth Test
- Cache Performance
- Latency Measurement

</td>
</tr>
<tr>
<td>

### Disk Benchmark
- Sequential Read/Write
- Random 4K Read/Write
- IOPS Measurement
- Mixed Workload
- Latency Test

</td>
<td>

### GPU Benchmark
- 1920×1080 3D Rendering
- Phong Lighting + Shadows
- 10,000 Particles
- FPS / 1% Low / 0.1% Low
- Frame Time Analysis
- Real-time HUD

</td>
</tr>
</table>

---

## Score System

Your benchmark results are graded from **S** (best) to **E** (worst):

| Grade | Description |
|:---:|---|
| **S** | Enthusiast / Overkill |
| **A** | High-End |
| **B** | Mid-Range |
| **C** | Entry-Level |
| **D** | Below Average |
| **E** | Needs Upgrade |

---

## Profiles

| Profile | Description |
|---|---|
| `quick` | Fast 30-second test |
| `full` | Complete benchmark suite |
| `gaming` | GPU-focused with CPU/RAM |
| `productivity` | CPU/RAM focused |
| `stress` | Extended 30-minute test |

---

## Installation

```bash
git clone https://github.com/M-K-B-61/nggatutu.git
cd nggatutu
pip install -r requirements.txt
python main.py
```

> Dependencies install automatically on first run.

---

## Usage

```bash
# Launch GUI
python main.py

# CLI — run all benchmarks
python main.py cli

# Individual tests
python main.py cpu
python main.py memory
python main.py disk
python main.py gpu

# System info
python main.py info

# Benchmark profiles
python main.py profiles

# View history
python main.py history

# Version
python main.py version
```

---

## Project Structure

```
nggatutu/
├── main.py                 # GUI + CLI entry point
├── requirements.txt        # Dependencies
├── README.md
├── benchmarks/
│   ├── __init__.py
│   ├── cpu.py              # CPU benchmark suite
│   ├── memory.py           # Memory benchmark suite
│   ├── disk.py             # Disk benchmark suite
│   ├── gpu.py              # GPU benchmark suite
│   ├── system_info.py      # Hardware detection
│   ├── scores.py           # Scoring system
│   ├── history.py          # Result history
│   ├── profiles.py         # Benchmark profiles
│   ├── stress.py           # Stress tests
│   ├── health.py           # System health
│   ├── monitor.py          # Real-time monitoring
│   └── reports.py          # Report generation
└── benchmark_history/      # Saved results
```

---

## How to Contribute

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## Contributors

<a href="https://github.com/M-K-B-61/nggatutu/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=M-K-B-61/nggatutu" />
</a>

---

<div align="center">

Made with Python · PySide6 · NumPy · Pygame

</div>
