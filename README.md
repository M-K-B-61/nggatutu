# Ngga Tutu

Cross-platform system benchmark tool for Windows and Linux. Open source, lightweight, and easy to use.

## Features

- **CPU Benchmark** - Single-core and multi-core performance testing
- **Memory Benchmark** - Read/write speed and random access tests
- **Disk I/O Benchmark** - Sequential and random read/write performance
- **JSON Export** - Save results for comparison

## Requirements

- Python 3.8+
- No external dependencies

## Installation

```bash
git clone https://github.com/M-K-B-61/nggatutu.git
cd nggatutu
```

## Usage

```bash
# Run all benchmarks
python main.py quick

# Run specific benchmark
python main.py cpu
python main.py memory
python main.py disk

# Show system info
python main.py info
```

## Example Output

```
==================================================
  CPU BENCHMARK
==================================================

[1/3] Single Core Integer... 28.05 MOPS
[2/3] Single Core Float...   19.83 MOPS
[3/3] Multi Core...          14.84 MOPS

--------------------------------------------------
  CPU SCORE: 20.91
--------------------------------------------------
```

## License

MIT
