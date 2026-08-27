#!/usr/bin/env python3
"""Ngga Tutu - Cross Platform Benchmark Tool"""

import sys
import platform
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
    print("Usage: python main.py <command>\n", flush=True)
    print("Commands:", flush=True)
    print("  (none)    Launch GUI interface", flush=True)
    print("  cli       Run in CLI mode", flush=True)
    print("  cpu       Run CPU benchmark (CLI)", flush=True)
    print("  memory    Run memory benchmark (CLI)", flush=True)
    print("  disk      Run disk I/O benchmark (CLI)", flush=True)
    print("  quick     Run all benchmarks (CLI)", flush=True)
    print("  info      Show system information (CLI)", flush=True)
    print("  version   Show version", flush=True)
    print("  help      Show this help", flush=True)


def print_system_info():
    print(BANNER, flush=True)
    print("System Information", flush=True)
    print("=" * 50, flush=True)
    print(f"  OS:         {platform.system()} {platform.release()}", flush=True)
    print(f"  Arch:       {platform.machine()}", flush=True)
    print(f"  Python:     {platform.python_version()}", flush=True)
    print(f"  CPU:        {platform.processor() or 'Unknown'}", flush=True)
    print(f"  Time:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(flush=True)


def run_quick_benchmark():
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

    results["cpu"] = run_cpu_benchmark()
    results["memory"] = run_memory_benchmark()
    results["disk"] = run_disk_benchmark()

    print("\n" + "=" * 50)
    print("  FINAL RESULTS")
    print("=" * 50)
    print(f"  CPU Score:      {results['cpu']['final_score']:.2f}")
    print(f"  Memory:         {results['memory']['avg_bandwidth']:.2f} MB/s")
    print(f"  Disk Seq:       R {results['disk']['seq_read']:.2f} / W {results['disk']['seq_write']:.2f} MB/s")
    print(f"  Disk Rand:      R {results['disk']['rand_read']:.2f} / W {results['disk']['rand_write']:.2f} MB/s")
    print("=" * 50)

    filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {filename}")
    return results


def launch_gui():
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTabWidget, QFrame, QProgressBar, QTextEdit
    )
    from PySide6.QtCore import Qt, QThread, Signal

    class BenchmarkWorker(QThread):
        progress = Signal(str)
        finished = Signal(dict)

        def __init__(self, benchmark_type):
            super().__init__()
            self.benchmark_type = benchmark_type

        def run(self):
            results = {}
            try:
                if self.benchmark_type in ("cpu", "all"):
                    self.progress.emit("Running CPU benchmark...")
                    results["cpu"] = run_cpu_benchmark()

                if self.benchmark_type in ("memory", "all"):
                    self.progress.emit("Running Memory benchmark...")
                    results["memory"] = run_memory_benchmark()

                if self.benchmark_type in ("disk", "all"):
                    self.progress.emit("Running Disk benchmark...")
                    results["disk"] = run_disk_benchmark()

            except Exception as e:
                self.progress.emit(f"Error: {e}")

            self.finished.emit(results)

    class BenchmarkTab(QWidget):
        def __init__(self, name, benchmark_func, parent=None):
            super().__init__(parent)
            self.name = name
            self.benchmark_func = benchmark_func
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setSpacing(20)

            header = QLabel(self.name)
            header.setStyleSheet("color: #fff; font-size: 20px; font-weight: bold;")
            layout.addWidget(header)

            self.run_btn = QPushButton(f"Run {self.name}")
            self.run_btn.setFixedHeight(45)
            self.run_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a9eff;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #3a8eef; }
                QPushButton:pressed { background-color: #2a7edf; }
                QPushButton:disabled { background-color: #555; color: #888; }
            """)
            self.run_btn.clicked.connect(self.run_benchmark)
            layout.addWidget(self.run_btn)

            self.progress = QProgressBar()
            self.progress.setRange(0, 0)
            self.progress.setVisible(False)
            self.progress.setStyleSheet("""
                QProgressBar {
                    border: none; border-radius: 5px;
                    background-color: #333; height: 8px;
                }
                QProgressBar::chunk {
                    background-color: #4a9eff; border-radius: 5px;
                }
            """)
            layout.addWidget(self.progress)

            self.output = QTextEdit()
            self.output.setReadOnly(True)
            self.output.setMaximumHeight(200)
            self.output.setStyleSheet("""
                QTextEdit {
                    background-color: #1a1a1a; color: #0f0;
                    border: 1px solid #333; border-radius: 8px;
                    padding: 10px; font-family: Consolas, monospace; font-size: 12px;
                }
            """)
            layout.addWidget(self.output)
            layout.addStretch()

        def run_benchmark(self):
            self.run_btn.setEnabled(False)
            self.progress.setVisible(True)
            self.output.clear()
            self.worker = BenchmarkWorker(self.name.lower())
            self.worker.progress.connect(lambda msg: self.output.append(msg))
            self.worker.finished.connect(self.on_finished)
            self.worker.start()

        def on_finished(self, results):
            self.run_btn.setEnabled(True)
            self.progress.setVisible(False)
            if self.name.lower() in results:
                data = results[self.name.lower()]
                self.output.append("\n" + "=" * 40)
                self.output.append(f"  {self.name} RESULTS")
                self.output.append("=" * 40)
                for key, value in data.items():
                    if isinstance(value, float):
                        self.output.append(f"  {key}: {value:.2f}")
                    else:
                        self.output.append(f"  {key}: {value}")

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Ngga Tutu Benchmark")
            self.setMinimumSize(800, 600)
            self.setup_ui()

        def setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)

            header = QWidget()
            header.setFixedHeight(80)
            header.setStyleSheet("background-color: #1a1a1a;")
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(20, 0, 20, 0)

            title = QLabel("Ngga Tutu")
            title.setStyleSheet("color: #4a9eff; font-size: 24px; font-weight: bold;")
            header_layout.addWidget(title)

            subtitle = QLabel("Cross-Platform Benchmark")
            subtitle.setStyleSheet("color: #666; font-size: 14px;")
            header_layout.addWidget(subtitle)
            header_layout.addStretch()

            self.run_all_btn = QPushButton("Run All")
            self.run_all_btn.setFixedSize(120, 40)
            self.run_all_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745; color: white; border: none;
                    border-radius: 8px; font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background-color: #218838; }
                QPushButton:disabled { background-color: #555; }
            """)
            self.run_all_btn.clicked.connect(self.run_all)
            header_layout.addWidget(self.run_all_btn)
            main_layout.addWidget(header)

            self.tabs = QTabWidget()
            self.tabs.setStyleSheet("""
                QTabWidget::pane { border: none; background-color: #1e1e1e; }
                QTabBar::tab {
                    background-color: #2d2d2d; color: #888;
                    padding: 12px 24px; margin-right: 2px;
                    border-top-left-radius: 8px; border-top-right-radius: 8px;
                }
                QTabBar::tab:selected { background-color: #1e1e1e; color: #4a9eff; }
                QTabBar::tab:hover { background-color: #3d3d3d; }
            """)

            self.cpu_tab = BenchmarkTab("CPU", run_cpu_benchmark)
            self.mem_tab = BenchmarkTab("Memory", run_memory_benchmark)
            self.disk_tab = BenchmarkTab("Disk", run_disk_benchmark)

            self.tabs.addTab(self.cpu_tab, "CPU")
            self.tabs.addTab(self.mem_tab, "Memory")
            self.tabs.addTab(self.disk_tab, "Disk")
            main_layout.addWidget(self.tabs)

            self.status_bar = QLabel("Ready")
            self.status_bar.setFixedHeight(30)
            self.status_bar.setStyleSheet("color: #666; padding: 5px 10px; background-color: #1a1a1a;")
            main_layout.addWidget(self.status_bar)

        def run_all(self):
            self.run_all_btn.setEnabled(False)
            self.cpu_tab.run_benchmark()
            self.mem_tab.run_benchmark()
            self.disk_tab.run_benchmark()
            self.run_all_btn.setEnabled(True)

    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow { background-color: #1e1e1e; }
        QWidget { background-color: #1e1e1e; color: #fff; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def cli_mode():
    if len(sys.argv) < 3:
        print("Usage: python main.py cli <command>", flush=True)
        print("Commands: cpu, memory, disk, quick, info", flush=True)
        return

    cmd = sys.argv[2].lower()
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
    else:
        print(f"Unknown command: {cmd}", flush=True)


def main():
    if len(sys.argv) < 2:
        launch_gui()
        return

    cmd = sys.argv[1].lower()

    if cmd == "gui":
        launch_gui()
    elif cmd == "cli":
        cli_mode()
    elif cmd == "cpu":
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
        print(f"nggatutu v{VERSION}", flush=True)
    elif cmd in ("help", "-h", "--help"):
        print_usage()
    else:
        print(f"Unknown command: {cmd}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if os.name == "nt":
            os.system("pause")
