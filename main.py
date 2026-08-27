#!/usr/bin/env python3
"""Ngga Tutu - Real Benchmark Tool"""

import sys
import platform
import json
import os
import math
import subprocess
from datetime import datetime


REQUIRED_MODULES = {
    "PySide6": "PySide6",
    "pygame": "pygame",
    "numpy": "numpy",
}


def check_and_install_modules():
    missing = []
    for module_name, pip_name in REQUIRED_MODULES.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"Installing missing modules: {', '.join(missing)}", flush=True)
        for pkg in missing:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        print("Done!\n", flush=True)


check_and_install_modules()

from benchmarks.cpu import run_cpu_benchmark
from benchmarks.memory import run_memory_benchmark
from benchmarks.disk import run_disk_benchmark
from benchmarks.gpu import run_gpu_benchmark

VERSION = "0.3.0"

BANNER = f"""
+-------------------------------------------------------+
|                   Ngga Tutu Benchmark                 |
|                 v{VERSION} - Real Performance Test           |
+-------------------------------------------------------+
"""


def print_usage():
    print("Usage: python main.py <command>\n", flush=True)
    print("Commands:", flush=True)
    print("  (none)    Launch GUI", flush=True)
    print("  cli       Run all benchmarks (CLI)", flush=True)
    print("  cpu       CPU benchmark only", flush=True)
    print("  memory    Memory benchmark only", flush=True)
    print("  disk      Disk benchmark only", flush=True)
    print("  gpu       3D rendering benchmark", flush=True)
    print("  info      System information", flush=True)
    print("  version   Show version", flush=True)
    print("  help      Show this help", flush=True)


def print_system_info():
    print(BANNER, flush=True)
    print("System Information", flush=True)
    print("=" * 55, flush=True)
    print(f"  OS:         {platform.system()} {platform.release()}", flush=True)
    print(f"  Arch:       {platform.machine()}", flush=True)
    print(f"  Python:     {platform.python_version()}", flush=True)
    print(f"  CPU:        {platform.processor() or 'Unknown'}", flush=True)
    print(f"  Time:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(flush=True)


def run_all_cli():
    print(BANNER)
    print("Running full benchmark suite...\n")

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
    results["gpu"] = run_gpu_benchmark(10)

    cpu_s = results["cpu"]["final_score"]
    mem_s = results["memory"]["final_score"]
    disk_s = results["disk"]["final_score"]
    gpu_s = results["gpu"]["score"]
    total = (cpu_s + mem_s + disk_s + gpu_s) / 4

    print("\n" + "=" * 55)
    print("  FINAL RESULTS")
    print("=" * 55)
    print(f"  CPU:      {cpu_s:.0f}")
    print(f"  Memory:   {mem_s:.0f}")
    print(f"  Disk:     {disk_s:.0f}")
    print(f"  GPU:      {gpu_s:.0f}")
    print("-" * 55)
    print(f"  TOTAL:    {total:.0f}")
    print("=" * 55)

    filename = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {filename}")
    return results


def launch_gui():
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTabWidget, QTextEdit, QSplashScreen, QFrame
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve, QSize
    from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPixmap, QLinearGradient

    class BenchmarkWorker(QThread):
        progress = Signal(str)
        result_ready = Signal(str, dict)

        def __init__(self, benchmark_type):
            super().__init__()
            self.benchmark_type = benchmark_type

        def run(self):
            try:
                if self.benchmark_type == "cpu":
                    self.progress.emit("Running CPU stress test...")
                    result = run_cpu_benchmark()
                    self.result_ready.emit("cpu", result)
                elif self.benchmark_type == "memory":
                    self.progress.emit("Running Memory stress test...")
                    result = run_memory_benchmark()
                    self.result_ready.emit("memory", result)
                elif self.benchmark_type == "disk":
                    self.progress.emit("Running Disk stress test...")
                    result = run_disk_benchmark()
                    self.result_ready.emit("disk", result)
                elif self.benchmark_type == "gpu":
                    self.progress.emit("Running 3D rendering test...")
                    result = run_gpu_benchmark(15)
                    self.result_ready.emit("gpu", result)
                elif self.benchmark_type == "all":
                    results = {}
                    self.progress.emit("Running CPU stress test...")
                    results["cpu"] = run_cpu_benchmark()
                    self.progress.emit("Running Memory stress test...")
                    results["memory"] = run_memory_benchmark()
                    self.progress.emit("Running Disk stress test...")
                    results["disk"] = run_disk_benchmark()
                    self.progress.emit("Running 3D rendering test...")
                    results["gpu"] = run_gpu_benchmark(15)
                    self.result_ready.emit("all", results)
            except Exception as e:
                self.progress.emit(f"Error: {e}")

    class SplashScreen:
        def __init__(self):
            self.splash = None
            self.progress_value = 0
            self.dots = 0

        def show(self):
            pixmap = QPixmap(600, 350)
            pixmap.fill(QColor(13, 17, 23))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            gradient = QLinearGradient(0, 0, 600, 350)
            gradient.setColorAt(0, QColor(13, 17, 23))
            gradient.setColorAt(0.5, QColor(22, 27, 34))
            gradient.setColorAt(1, QColor(13, 17, 23))
            painter.fillRect(0, 0, 600, 350, gradient)

            glow = QLinearGradient(200, 100, 400, 100)
            glow.setColorAt(0, QColor(88, 166, 255, 0))
            glow.setColorAt(0.5, QColor(88, 166, 255, 30))
            glow.setColorAt(1, QColor(88, 166, 255, 0))
            painter.fillRect(0, 80, 600, 80, glow)

            painter.setPen(QColor(88, 166, 255))
            font = QFont("Segoe UI", 42, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect().adjusted(0, -50, 0, 0), Qt.AlignmentFlag.AlignCenter, "Ngga Tutu")

            painter.setPen(QColor(139, 148, 158))
            font = QFont("Segoe UI", 13)
            painter.setFont(font)
            painter.drawText(pixmap.rect().adjusted(0, 20, 0, 0), Qt.AlignmentFlag.AlignCenter, "Real Performance Benchmark")

            painter.setPen(QColor(88, 166, 255))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(pixmap.rect().adjusted(0, 50, 0, 0), Qt.AlignmentFlag.AlignCenter, f"v{VERSION}")

            painter.setPen(QColor(40, 45, 55))
            painter.drawRoundedRect(150, 250, 300, 6, 3, 3)

            painter.setPen(QColor(60, 65, 75))
            font = QFont("Segoe UI", 8)
            painter.setFont(font)
            painter.drawText(150, 280, 300, 15, Qt.AlignmentFlag.AlignCenter, "Initializing benchmarks...")

            painter.end()

            self.splash = QSplashScreen(pixmap)
            self.splash.show()

        def set_progress(self, value):
            if not self.splash:
                return
            self.progress_value = min(value, 100)

            pixmap = QPixmap(600, 350)
            pixmap.fill(QColor(13, 17, 23))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            gradient = QLinearGradient(0, 0, 600, 350)
            gradient.setColorAt(0, QColor(13, 17, 23))
            gradient.setColorAt(0.5, QColor(22, 27, 34))
            gradient.setColorAt(1, QColor(13, 17, 23))
            painter.fillRect(0, 0, 600, 350, gradient)

            glow = QLinearGradient(200, 100, 400, 100)
            glow.setColorAt(0, QColor(88, 166, 255, 0))
            glow.setColorAt(0.5, QColor(88, 166, 255, 30))
            glow.setColorAt(1, QColor(88, 166, 255, 0))
            painter.fillRect(0, 80, 600, 80, glow)

            painter.setPen(QColor(88, 166, 255))
            font = QFont("Segoe UI", 42, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect().adjusted(0, -50, 0, 0), Qt.AlignmentFlag.AlignCenter, "Ngga Tutu")

            painter.setPen(QColor(139, 148, 158))
            font = QFont("Segoe UI", 13)
            painter.setFont(font)
            painter.drawText(pixmap.rect().adjusted(0, 20, 0, 0), Qt.AlignmentFlag.AlignCenter, "Real Performance Benchmark")

            painter.setPen(QColor(88, 166, 255))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(pixmap.rect().adjusted(0, 50, 0, 0), Qt.AlignmentFlag.AlignCenter, f"v{VERSION}")

            painter.setPen(QColor(40, 45, 55))
            painter.drawRoundedRect(150, 250, 300, 6, 3, 3)

            bar_width = int(300 * self.progress_value / 100)
            if bar_width > 0:
                bar_gradient = QLinearGradient(150, 0, 450, 0)
                bar_gradient.setColorAt(0, QColor(88, 166, 255))
                bar_gradient.setColorAt(1, QColor(120, 180, 255))
                painter.setBrush(QBrush(bar_gradient))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(150, 250, bar_width, 6, 3, 3)

            self.dots = (self.dots + 1) % 4
            dots_str = "." * self.dots

            status = "Initializing benchmarks" if self.progress_value < 30 else \
                     "Loading CPU tests" if self.progress_value < 50 else \
                     "Loading Memory tests" if self.progress_value < 70 else \
                     "Loading GPU renderer" if self.progress_value < 90 else \
                     "Ready"

            painter.setPen(QColor(100, 110, 120))
            font = QFont("Segoe UI", 9)
            painter.setFont(font)
            painter.drawText(150, 280, 300, 15, Qt.AlignmentFlag.AlignCenter, f"{status}{dots_str}")

            painter.setPen(QColor(139, 148, 158))
            font = QFont("Segoe UI", 8)
            painter.setFont(font)
            painter.drawText(150, 300, 300, 15, Qt.AlignmentFlag.AlignCenter, f"{self.progress_value}%")

            painter.end()
            self.splash.setPixmap(pixmap)

        def close(self):
            if self.splash:
                self.splash.close()
                self.splash = None

    class ScoreGauge(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.score = 0
            self.target_score = 0
            self.label = "SCORE"
            self.sublabel = ""
            self.setFixedSize(220, 220)

        def set_score(self, score, label="TOTAL", sublabel=""):
            self.target_score = min(score, 1000)
            self.label = label
            self.sublabel = sublabel
            self.score = 0
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_score)
            self.timer.start(16)

        def update_score(self):
            if self.score < self.target_score:
                diff = self.target_score - self.score
                self.score += max(1, diff * 0.08)
                if abs(self.score - self.target_score) < 1:
                    self.score = self.target_score
                    self.timer.stop()
            self.update()

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            center = self.rect().center()
            radius = 85

            pen = QPen(QColor(30, 35, 45), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 225 * 16, -270 * 16)

            progress = min(self.score / 1000, 1.0)
            score_angle = int(-270 * progress)

            if self.score >= 700:
                color = QColor(0, 200, 100)
            elif self.score >= 400:
                color = QColor(255, 200, 0)
            else:
                color = QColor(255, 80, 80)

            pen = QPen(color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(center.x() - radius, center.y() - radius, radius * 2, radius * 2, 225 * 16, score_angle * 16)

            painter.setPen(QColor(255, 255, 255))
            font = QFont("Segoe UI", 36, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(0, -15, 0, 0), Qt.AlignmentFlag.AlignCenter, str(int(self.score)))

            painter.setPen(QColor(150, 150, 150))
            font = QFont("Segoe UI", 11)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(0, 35, 0, 0), Qt.AlignmentFlag.AlignCenter, self.label)

            if self.sublabel:
                painter.setPen(QColor(100, 100, 100))
                font = QFont("Segoe UI", 9)
                painter.setFont(font)
                painter.drawText(self.rect().adjusted(0, 55, 0, 0), Qt.AlignmentFlag.AlignCenter, self.sublabel)

    class BarChart(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.data = {}
            self.max_val = 1000
            self.setFixedHeight(160)

        def set_data(self, data, max_val=1000):
            self.data = data
            self.max_val = max(max_val, 100)
            self.update()

        def paintEvent(self, event):
            if not self.data:
                return
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            bar_width = 50
            gap = 25
            n = len(self.data)
            total_width = n * bar_width + (n - 1) * gap
            start_x = (self.width() - total_width) // 2

            colors = [
                QColor(74, 158, 255),
                QColor(0, 200, 100),
                QColor(255, 180, 0),
                QColor(255, 80, 80),
            ]

            for i, (label, value) in enumerate(self.data.items()):
                x = start_x + i * (bar_width + gap)
                bar_height = int((value / self.max_val) * 110)
                y = self.height() - 35 - bar_height

                gradient = QLinearGradient(x, y, x, y + bar_height)
                color = colors[i % len(colors)]
                gradient.setColorAt(0, color)
                gradient.setColorAt(1, QColor(color.red() // 2, color.green() // 2, color.blue() // 2))

                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(x, y, bar_width, bar_height, 6, 6)

                painter.setPen(QColor(200, 200, 200))
                font = QFont("Segoe UI", 9)
                painter.setFont(font)
                painter.drawText(x, self.height() - 18, bar_width, 15, Qt.AlignmentFlag.AlignCenter, label)

                painter.setPen(QColor(255, 255, 255))
                font = QFont("Segoe UI", 10, QFont.Weight.Bold)
                painter.setFont(font)
                painter.drawText(x, y - 22, bar_width, 15, Qt.AlignmentFlag.AlignCenter, str(int(value)))

    class BenchmarkTab(QWidget):
        def __init__(self, name, icon, color, parent=None):
            super().__init__(parent)
            self.name = name
            self.icon = icon
            self.color = color
            self.setup_ui()

        def setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setSpacing(12)

            header = QHBoxLayout()
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet(f"font-size: 28px; color: {self.color};")
            header.addWidget(icon_label)
            title = QLabel(self.name)
            title.setStyleSheet(f"color: {self.color}; font-size: 20px; font-weight: bold;")
            header.addWidget(title)
            header.addStretch()
            layout.addLayout(header)

            desc = QLabel(self._get_description())
            desc.setStyleSheet("color: #8b949e; font-size: 11px;")
            desc.setWordWrap(True)
            layout.addWidget(desc)

            self.run_btn = QPushButton(f"Run {self.name} Test")
            self.run_btn.setFixedHeight(48)
            self.run_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.color}, stop:1 {self.color}dd);
                    color: white; border: none; border-radius: 10px;
                    font-size: 14px; font-weight: bold;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.color}ee, stop:1 {self.color});
                }}
                QPushButton:disabled {{ background-color: #333; color: #666; }}
            """)
            self.run_btn.clicked.connect(self.run_test)
            layout.addWidget(self.run_btn)

            self.output = QTextEdit()
            self.output.setReadOnly(True)
            self.output.setMaximumHeight(180)
            self.output.setStyleSheet("""
                QTextEdit {
                    background-color: #0d1117; color: #0f0;
                    border: 1px solid #21262d; border-radius: 10px;
                    padding: 12px; font-family: 'Cascadia Code', Consolas, monospace;
                    font-size: 11px; line-height: 1.4;
                }
            """)
            layout.addWidget(self.output)
            layout.addStretch()

        def _get_description(self):
            descs = {
                "CPU": "Prime sieve (50M), Matrix (1000x1000), SHA256 (5M), Compression, Pi digits (50M), Multi-core stress",
                "Memory": "Sequential read/write, Random access (2M ops), Memory copy, Latency test",
                "Disk": "Sequential R/W (256MB), Random 4K R/W, Mixed workload simulation",
                "GPU": "1920x1080, 15 objects, 10K particles, Phong lighting, FPS counter",
            }
            return descs.get(self.name, "")

        def run_test(self):
            self.run_btn.setEnabled(False)
            self.run_btn.setText("Running...")
            self.output.clear()
            self.worker = BenchmarkWorker(self.name.lower())
            self.worker.progress.connect(lambda msg: self.output.append(f"> {msg}"))
            self.worker.result_ready.connect(self.on_result)
            self.worker.start()

        def on_result(self, bench_type, result):
            self.run_btn.setEnabled(True)
            self.run_btn.setText(f"Run {self.name} Test")
            self.output.append("\n" + "=" * 45)
            self.output.append(f"  {self.name} RESULTS")
            self.output.append("=" * 45)
            if "scores" in result:
                for k, v in result["scores"].items():
                    self.output.append(f"  {k}: {v:.0f}")
                self.output.append(f"\n  FINAL SCORE: {result['final_score']:.0f}")
            elif "avg_fps" in result:
                self.output.append(f"  Avg FPS: {result['avg_fps']:.1f}")
                self.output.append(f"  Min FPS: {result['min_fps']:.1f}")
                self.output.append(f"  Max FPS: {result['max_fps']:.1f}")
                self.output.append(f"  Triangles: {result.get('total_triangles', 0)}")
                self.output.append(f"\n  FINAL SCORE: {result['score']:.0f}")

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Ngga Tutu Benchmark")
            self.setMinimumSize(950, 680)
            self.results = {}
            self.setup_ui()

        def setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            header = QWidget()
            header.setFixedHeight(80)
            header.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0d1117, stop:1 #161b22);
                    border-bottom: 1px solid #21262d;
                }
            """)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(25, 0, 25, 0)

            title = QLabel("Ngga Tutu")
            title.setStyleSheet("color: #58a6ff; font-size: 26px; font-weight: bold; background: transparent;")
            header_layout.addWidget(title)

            subtitle = QLabel("  Real Performance Benchmark")
            subtitle.setStyleSheet("color: #8b949e; font-size: 13px; background: transparent;")
            header_layout.addWidget(subtitle)
            header_layout.addStretch()

            self.run_all_btn = QPushButton("  RUN ALL TESTS  ")
            self.run_all_btn.setFixedSize(180, 42)
            self.run_all_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #238636, stop:1 #2ea043);
                    color: white; border: none; border-radius: 10px;
                    font-size: 13px; font-weight: bold; letter-spacing: 1px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2ea043, stop:1 #3fb950);
                }
                QPushButton:disabled { background-color: #333; color: #666; }
            """)
            self.run_all_btn.clicked.connect(self.run_all)
            header_layout.addWidget(self.run_all_btn)
            main_layout.addWidget(header)

            content = QWidget()
            content.setStyleSheet("background-color: #0d1117;")
            content_layout = QHBoxLayout(content)
            content_layout.setContentsMargins(20, 15, 20, 15)
            content_layout.setSpacing(20)

            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            left_layout.setContentsMargins(0, 0, 0, 0)
            self.tabs = QTabWidget()
            self.tabs.setStyleSheet("""
                QTabWidget::pane { border: none; background: #0d1117; }
                QTabBar::tab {
                    background: #161b22; color: #8b949e;
                    padding: 10px 18px; margin-right: 2px;
                    border-top-left-radius: 8px; border-top-right-radius: 8px;
                    font-size: 12px; font-weight: bold;
                }
                QTabBar::tab:selected { background: #0d1117; color: #58a6ff; }
                QTabBar::tab:hover { background: #21262d; }
            """)
            self.cpu_tab = BenchmarkTab("CPU", "CPU", "#58a6ff")
            self.mem_tab = BenchmarkTab("Memory", "RAM", "#00c864")
            self.disk_tab = BenchmarkTab("Disk", "SSD", "#ffb400")
            self.gpu_tab = BenchmarkTab("GPU", "3D", "#ff5050")
            self.tabs.addTab(self.cpu_tab, "CPU")
            self.tabs.addTab(self.mem_tab, "Memory")
            self.tabs.addTab(self.disk_tab, "Disk")
            self.tabs.addTab(self.gpu_tab, "GPU")
            left_layout.addWidget(self.tabs)
            content_layout.addWidget(left_panel, 2)

            right_panel = QWidget()
            right_panel.setStyleSheet("background: #161b22; border-radius: 12px;")
            right_layout = QVBoxLayout(right_panel)
            right_layout.setContentsMargins(20, 20, 20, 20)
            right_layout.setSpacing(12)

            result_title = QLabel("Results")
            result_title.setStyleSheet("color: #fff; font-size: 16px; font-weight: bold; background: transparent;")
            right_layout.addWidget(result_title)

            self.gauge = ScoreGauge()
            right_layout.addWidget(self.gauge, alignment=Qt.AlignmentFlag.AlignHCenter)

            self.chart = BarChart()
            right_layout.addWidget(self.chart)

            self.total_label = QLabel("TOTAL SCORE")
            self.total_label.setStyleSheet("color: #58a6ff; font-size: 18px; font-weight: bold; padding: 8px; background: #0d1117; border-radius: 8px;")
            self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(self.total_label)

            self.grade_label = QLabel("")
            self.grade_label.setStyleSheet("color: #8b949e; font-size: 12px; background: transparent;")
            self.grade_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(self.grade_label)

            right_layout.addStretch()
            content_layout.addWidget(right_panel, 1)

            main_layout.addWidget(content)

            self.status_bar = QLabel("Ready")
            self.status_bar.setFixedHeight(32)
            self.status_bar.setStyleSheet("color: #8b949e; padding: 6px 15px; background: #161b22; border-top: 1px solid #21262d; font-size: 11px;")
            main_layout.addWidget(self.status_bar)

        def run_all(self):
            self.run_all_btn.setEnabled(False)
            self.run_all_btn.setText("  RUNNING...  ")
            self.status_bar.setText("Starting full benchmark suite...")
            self.worker = BenchmarkWorker("all")
            self.worker.progress.connect(lambda msg: self.status_bar.setText(msg))
            self.worker.result_ready.connect(self.on_all_done)
            self.worker.start()

        def on_all_done(self, _, results):
            self.run_all_btn.setEnabled(True)
            self.run_all_btn.setText("  RUN ALL TESTS  ")
            self.results = results
            self.status_bar.setText("Benchmark complete!")

            chart_data = {}
            total = 0
            for key in ["cpu", "memory", "disk", "gpu"]:
                if key in results:
                    val = results[key].get("final_score", results[key].get("score", 0))
                    chart_data[key.upper()] = val
                    total += val

            avg = total / max(len(chart_data), 1)

            grade = "S" if avg >= 800 else "A" if avg >= 600 else "B" if avg >= 400 else "C" if avg >= 200 else "D"
            grade_desc = {
                "S": "Outstanding - Top tier performance",
                "A": "Excellent - High performance",
                "B": "Good - Above average",
                "C": "Average - Typical performance",
                "D": "Below average - Needs upgrade",
            }

            self.gauge.set_score(avg, "TOTAL", f"Grade: {grade}")
            self.chart.set_data(chart_data, max(max(chart_data.values()) * 1.2, 100))
            self.total_label.setText(f"TOTAL SCORE: {int(avg)}")
            self.grade_label.setText(f"Grade: {grade} - {grade_desc.get(grade, '')}")

    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow, QWidget { background-color: #0d1117; color: #fff; }")

    splash = SplashScreen()
    splash.show()

    from PySide6.QtCore import QTimer

    window = [None]

    def show_main():
        splash.close()
        window[0] = MainWindow()
        window[0].show()

    progress = [0]
    progress_timer = QTimer()

    def update_progress():
        progress[0] += 3
        splash.set_progress(progress[0])
        if progress[0] >= 100:
            progress_timer.stop()
            show_main()

    progress_timer.timeout.connect(update_progress)
    progress_timer.start(30)

    app.exec()


def main():
    if len(sys.argv) < 2:
        launch_gui()
        return
    cmd = sys.argv[1].lower()
    if cmd == "gui":
        launch_gui()
    elif cmd == "cli":
        run_all_cli()
    elif cmd == "cpu":
        run_cpu_benchmark()
    elif cmd == "memory":
        run_memory_benchmark()
    elif cmd == "disk":
        run_disk_benchmark()
    elif cmd == "gpu":
        run_gpu_benchmark(15)
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
