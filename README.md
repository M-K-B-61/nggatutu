# Ngga Tutu

Real performance benchmark tool. Stresses your PC and gives a score.

## Contributors

Thanks to all contributors who helped build this project!

<a href="https://github.com/M-K-B-61/nggatutu/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=M-K-B-61/nggatutu" />
</a>

## Features

- **CPU** - Prime sieve (50M), matrix multiply (1000x1000), SHA256 (5M), compression, multi-core stress
- **Memory** - Sequential/random read/write, copy speed, latency
- **Disk** - Sequential/random 4K, mixed workload
- **GPU** - 1920x1080 3D rendering with Phong lighting, 10K particles, FPS counter
- **GUI** - Dark theme with animated score gauge, bar charts, splash screen
- **Auto-install** - Missing modules installed automatically
- **Grading** - S/A/B/C/D grade system based on performance

## Requirements

- Python 3.8+
- Modules auto-installed on first run (PySide6, pygame, numpy)

## Installation

```bash
git clone https://github.com/M-K-B-61/nggatutu.git
cd nggatutu
python main.py  # Modules install automatically
```

## Usage

```bash
# Launch GUI (default)
python main.py

# CLI mode - run all benchmarks
python main.py cli

# Individual tests
python main.py cpu
python main.py memory
python main.py disk
python main.py gpu

# System info
python main.py info
```

## How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT
