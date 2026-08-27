# Ngga Tutu

Real performance benchmark tool. Stresses your PC and gives a score.

## Features

- **CPU** - Prime sieve, matrix multiply, SHA256, compression, multi-core stress
- **Memory** - Sequential/random read/write, copy speed, latency
- **Disk** - Sequential/random 4K, mixed workload
- **GPU** - 3D rendering with FPS counter
- **GUI** - Dark theme with animated score gauge and bar charts

## Requirements

- Python 3.8+
- PySide6 (`pip install PySide6`)
- pygame (`pip install pygame`)
- numpy (`pip install numpy`)

## Installation

```bash
git clone https://github.com/M-K-B-61/nggatutu.git
cd nggatutu
pip install PySide6 pygame numpy
```

## Usage

```bash
# Launch GUI
python main.py

# CLI mode
python main.py cli

# Individual tests
python main.py cpu
python main.py memory
python main.py disk
python main.py gpu

# System info
python main.py info
```

## License

MIT
