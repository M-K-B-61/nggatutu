# Ngga Tutu

A cross-platform system benchmark tool for Windows and Linux. Open source, lightweight, and easy to use.

## Features

- **CPU Benchmark** - Single-core and multi-core performance testing
- **Memory Benchmark** - Read/write speed and latency tests
- **Disk I/O Benchmark** - Sequential and random read/write performance
- **Quick Benchmark** - All-in-one test suite

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/M-K-B-61/nggatutu.git
cd nggatutu

# Build (Go required)
go build -o nggatutu
```

### Pre-built Binaries

Download the latest release for your platform from [Releases](https://github.com/M-K-B-61/nggatutu/releases).

| Platform | Architecture | Binary |
|----------|--------------|--------|
| Windows  | x64          | `nggatutu-windows-amd64.exe` |
| Linux    | x64          | `nggatutu-linux-amd64` |
| Linux    | ARM64        | `nggatutu-linux-arm64` |

## Usage

```bash
# Run all benchmarks
./nggatutu

# Run specific benchmark
./nggatutu cpu
./nggatutu memory
./nggatutu disk

# Quick benchmark (all tests, shorter duration)
./nggatutu quick

# Show system info
./nggatutu info
```

## Benchmark Details

### CPU
- Single-thread integer operations
- Single-thread floating-point operations
- Multi-thread performance scaling

### Memory
- Sequential read/write (MB/s)
- Random access latency (ns)

### Disk
- Sequential read/write (MB/s)
- Random 4K read/write (IOPS)

## Examples

```
$ nggatutu quick

╔═══════════════════════════════════════════════╗
║              Ngga Tutu Benchmark              ║
╚═══════════════════════════════════════════════╝

[CPU] Single Core Score: 1234
[CPU] Multi Core Score:  4567
[MEM] Read: 23456 MB/s
[MEM] Write: 18923 MB/s
[DISK] Sequential Read:  3456 MB/s
[DISK] Sequential Write: 2890 MB/s

═══════════════════════════════════════════════
  Results saved to: benchmark_2024-01-15.json
```

## Contributing

Contributions are welcome! Please open an issue first to discuss what you would like to change.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with Go for maximum performance and portability
- Inspired by popular benchmark tools like Geekbench, Cinebench, and CrystalDiskMark
