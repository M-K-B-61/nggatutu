#!/usr/bin/env python3
"""Ngga Tutu - Benchmark GUI"""

import sys
import time
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFrame, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette

from benchmarks.cpu import run_cpu_benchmark
from benchmarks.memory import run_memory_benchmark
from benchmarks.disk import run_disk_benchmark


class BenchmarkWorker(QThread):
    """Background worker for running benchmarks."""
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


class ResultCard(QFrame):
    """Styled card for displaying benchmark results."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(self)

        self.title = QLabel(title)
        self.title.setStyleSheet("color: #888; font-size: 12px; border: none;")
        layout.addWidget(self.title)

        self.value = QLabel("--")
        self.value.setStyleSheet("color: #fff; font-size: 24px; font-weight: bold; border: none;")
        layout.addWidget(self.value)

        self.unit = QLabel("")
        self.unit.setStyleSheet("color: #666; font-size: 11px; border: none;")
        layout.addWidget(self.unit)

    def set_value(self, value, unit=""):
        self.value.setText(f"{value:.2f}")
        self.unit.setText(unit)


class BenchmarkTab(QWidget):
    """Tab widget for a single benchmark type."""
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

        self.results_area = QVBoxLayout()
        self.results_area.setSpacing(10)
        layout.addLayout(self.results_area)

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
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:pressed {
                background-color: #2a7edf;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.run_btn.clicked.connect(self.run_benchmark)
        layout.addWidget(self.run_btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #333;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #4a9eff;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(150)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #0f0;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.output)

        layout.addStretch()

    def run_benchmark(self):
        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.output.clear()

        self.worker = BenchmarkWorker(self.name.lower())
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, msg):
        self.output.append(msg)

    def on_finished(self, results):
        self.run_btn.setEnabled(True)
        self.progress.setVisible(False)

        if self.name.lower() in results:
            data = results[self.name.lower()]
            self.display_results(data)

    def display_results(self, data):
        self.output.append("\n" + "=" * 40)
        self.output.append(f"  {self.name} RESULTS")
        self.output.append("=" * 40)

        for key, value in data.items():
            if isinstance(value, float):
                self.output.append(f"  {key}: {value:.2f}")
            else:
                self.output.append(f"  {key}: {value}")


class MainWindow(QMainWindow):
    """Main application window."""
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
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        self.run_all_btn.clicked.connect(self.run_all)
        header_layout.addWidget(self.run_all_btn)

        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #888;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #4a9eff;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
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


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #fff;
        }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
