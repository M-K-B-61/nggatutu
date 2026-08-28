#!/usr/bin/env python3
import sys
import platform
import json
import os
import subprocess
from datetime import datetime


REQUIRED_MODULES = {
    "PySide6": "PySide6",
    "pygame": "pygame",
    "numpy": "numpy",
    "psutil": "psutil",
}


def check_and_install_modules():
    missing = []
    for module_name, pip_name in REQUIRED_MODULES.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print(f"Installing: {', '.join(missing)}", flush=True)
        for pkg in missing:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        print("Done!\n", flush=True)


check_and_install_modules()

from benchmarks import (
    run_cpu_benchmark, run_memory_benchmark, run_disk_benchmark, run_gpu_benchmark,
    get_all_system_info, print_system_info,
    SystemMonitor,
    run_stress_test,
    calculate_category_scores, get_grade, format_score_report,
    save_result, load_history, format_history,
    analyze_health, detect_throttling, format_health_report,
    list_profiles, format_profiles,
    generate_json_report, generate_html_report,
)

VERSION = "0.4.0"

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
    print("  profiles  Show benchmark profiles", flush=True)
    print("  history   Show benchmark history", flush=True)
    print("  version   Show version", flush=True)
    print("  help      Show this help", flush=True)


def run_all_cli():
    print(BANNER)
    print("Running full benchmark suite...\n")
    results = {
        "timestamp": datetime.now().isoformat(),
        "system": {"os": platform.system(), "arch": platform.machine()},
    }
    results["cpu"] = run_cpu_benchmark()
    results["memory"] = run_memory_benchmark()
    results["disk"] = run_disk_benchmark()
    results["gpu"] = run_gpu_benchmark(15)

    print(format_score_report(results))
    report_id = save_result(results)
    print(f"\nResults saved (ID: {report_id})")
    generate_json_report(results)
    generate_html_report(results)
    return results


def launch_gui():
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTabWidget, QTextEdit, QSplashScreen,
        QScrollArea, QFrame, QProgressBar, QGridLayout, QSplitter,
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPixmap, QLinearGradient

    STYLESHEET = """
    QMainWindow, QWidget { background-color: #0d1117; color: #e6edf3; }
    QTabWidget::pane { border: none; background: #0d1117; }
    QTabBar::tab {
        background: #161b22; color: #8b949e;
        padding: 10px 20px; margin-right: 2px;
        border-top-left-radius: 8px; border-top-right-radius: 8px;
        font-size: 13px; font-weight: bold;
    }
    QTabBar::tab:selected { background: #0d1117; color: #58a6ff; border-bottom: 2px solid #58a6ff; }
    QTabBar::tab:hover { background: #21262d; }
    QPushButton {
        background: #21262d; color: #e6edf3; border: 1px solid #30363d;
        border-radius: 8px; padding: 8px 16px; font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #30363d; border-color: #58a6ff; }
    QPushButton:disabled { background: #161b22; color: #484f58; }
    QTextEdit {
        background: #0d1117; color: #0f0; border: 1px solid #21262d;
        border-radius: 8px; padding: 10px;
        font-family: 'Cascadia Code', Consolas, monospace; font-size: 11px;
    }
    QLabel { background: transparent; }
    QProgressBar {
        background: #21262d; border: none; border-radius: 4px;
        height: 8px; text-align: center;
    }
    QProgressBar::chunk { background: #58a6ff; border-radius: 4px; }
    QScrollArea { border: none; }
    """

    CARD_STYLE = "background: #161b22; border: 1px solid #21262d; border-radius: 12px; padding: 16px;"
    HEADER_STYLE = "color: #58a6ff; font-size: 16px; font-weight: bold;"
    LABEL_STYLE = "color: #8b949e; font-size: 12px;"
    VALUE_STYLE = "color: #e6edf3; font-size: 13px; font-weight: bold;"

    class BenchmarkWorker(QThread):
        progress = Signal(str)
        result_ready = Signal(str, dict)

        def __init__(self, benchmark_type):
            super().__init__()
            self.benchmark_type = benchmark_type

        def run(self):
            try:
                if self.benchmark_type == "cpu":
                    self.progress.emit("Running CPU benchmark...")
                    self.result_ready.emit("cpu", run_cpu_benchmark())
                elif self.benchmark_type == "memory":
                    self.progress.emit("Running Memory benchmark...")
                    self.result_ready.emit("memory", run_memory_benchmark())
                elif self.benchmark_type == "disk":
                    self.progress.emit("Running Disk benchmark...")
                    self.result_ready.emit("disk", run_disk_benchmark())
                elif self.benchmark_type == "gpu":
                    self.progress.emit("Running GPU benchmark...")
                    self.result_ready.emit("gpu", run_gpu_benchmark(15))
                elif self.benchmark_type == "all":
                    results = {}
                    for name, fn in [("cpu", run_cpu_benchmark), ("memory", run_memory_benchmark),
                                     ("disk", run_disk_benchmark)]:
                        self.progress.emit(f"Running {name.upper()} benchmark...")
                        results[name] = fn()
                    self.progress.emit("Running GPU benchmark...")
                    results["gpu"] = run_gpu_benchmark(15)
                    self.result_ready.emit("all", results)
            except Exception as e:
                self.progress.emit(f"Error: {e}")

    class StressWorker(QThread):
        progress = Signal(float, float, float)
        finished = Signal(dict)

        def __init__(self, test_type, duration):
            super().__init__()
            self.test_type = test_type
            self.duration = duration

        def run(self):
            try:
                result = run_stress_test(self.test_type, self.duration, self._on_progress)
                self.finished.emit(result)
            except Exception as e:
                self.finished.emit({"error": str(e)})

        def _on_progress(self, pct, elapsed, total):
            self.progress.emit(pct, elapsed, total)

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
            painter.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
            painter.drawText(pixmap.rect().adjusted(0, -50, 0, 0), Qt.AlignmentFlag.AlignCenter, "Ngga Tutu")
            painter.setPen(QColor(139, 148, 158))
            painter.setFont(QFont("Segoe UI", 13))
            painter.drawText(pixmap.rect().adjusted(0, 20, 0, 0), Qt.AlignmentFlag.AlignCenter, "Real Performance Benchmark")
            painter.setPen(QColor(88, 166, 255))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(pixmap.rect().adjusted(0, 50, 0, 0), Qt.AlignmentFlag.AlignCenter, f"v{VERSION}")
            painter.setPen(QColor(40, 45, 55))
            painter.drawRoundedRect(150, 250, 300, 6, 3, 3)
            painter.setPen(QColor(60, 65, 75))
            painter.setFont(QFont("Segoe UI", 8))
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
            painter.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
            painter.drawText(pixmap.rect().adjusted(0, -50, 0, 0), Qt.AlignmentFlag.AlignCenter, "Ngga Tutu")
            painter.setPen(QColor(139, 148, 158))
            painter.setFont(QFont("Segoe UI", 13))
            painter.drawText(pixmap.rect().adjusted(0, 20, 0, 0), Qt.AlignmentFlag.AlignCenter, "Real Performance Benchmark")
            painter.setPen(QColor(88, 166, 255))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(pixmap.rect().adjusted(0, 50, 0, 0), Qt.AlignmentFlag.AlignCenter, f"v{VERSION}")
            painter.setPen(QColor(40, 45, 55))
            painter.drawRoundedRect(150, 250, 300, 6, 3, 3)
            bar_width = int(300 * self.progress_value / 100)
            if bar_width > 0:
                bar_grad = QLinearGradient(150, 0, 450, 0)
                bar_grad.setColorAt(0, QColor(88, 166, 255))
                bar_grad.setColorAt(1, QColor(120, 180, 255))
                painter.setBrush(QBrush(bar_grad))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(150, 250, bar_width, 6, 3, 3)
            self.dots = (self.dots + 1) % 4
            status = "Initializing" if self.progress_value < 30 else "Loading tests" if self.progress_value < 70 else "Ready"
            painter.setPen(QColor(100, 110, 120))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(150, 280, 300, 15, Qt.AlignmentFlag.AlignCenter, f"{status}{'.' * self.dots}")
            painter.setPen(QColor(139, 148, 158))
            painter.setFont(QFont("Segoe UI", 8))
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
            self._timer = QTimer()
            self._timer.timeout.connect(self._update)
            self._timer.start(16)

        def _update(self):
            if self.score < self.target_score:
                diff = self.target_score - self.score
                self.score += max(1, diff * 0.08)
                if abs(self.score - self.target_score) < 1:
                    self.score = self.target_score
                    self._timer.stop()
            self.update()

        def paintEvent(self, event):
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            c = self.rect().center()
            r = 85
            pen = QPen(QColor(30, 35, 45), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawArc(c.x() - r, c.y() - r, r * 2, r * 2, 225 * 16, -270 * 16)
            prog = min(self.score / 1000, 1.0)
            color = QColor(0, 200, 100) if self.score >= 700 else QColor(255, 200, 0) if self.score >= 400 else QColor(255, 80, 80)
            pen = QPen(color, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawArc(c.x() - r, c.y() - r, r * 2, r * 2, 225 * 16, int(-270 * prog) * 16)
            p.setPen(QColor(255, 255, 255))
            p.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
            p.drawText(self.rect().adjusted(0, -15, 0, 0), Qt.AlignmentFlag.AlignCenter, str(int(self.score)))
            p.setPen(QColor(150, 150, 150))
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(self.rect().adjusted(0, 35, 0, 0), Qt.AlignmentFlag.AlignCenter, self.label)
            if self.sublabel:
                p.setPen(QColor(100, 100, 100))
                p.setFont(QFont("Segoe UI", 9))
                p.drawText(self.rect().adjusted(0, 55, 0, 0), Qt.AlignmentFlag.AlignCenter, self.sublabel)

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
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            bw, gap = 50, 25
            n = len(self.data)
            sx = (self.width() - n * bw - (n - 1) * gap) // 2
            colors = [QColor(74, 158, 255), QColor(255, 80, 80), QColor(0, 200, 100), QColor(255, 180, 0)]
            for i, (label, val) in enumerate(self.data.items()):
                x = sx + i * (bw + gap)
                bh = int((val / self.max_val) * 110)
                y = self.height() - 35 - bh
                grad = QLinearGradient(x, y, x, y + bh)
                c = colors[i % len(colors)]
                grad.setColorAt(0, c)
                grad.setColorAt(1, QColor(c.red() // 2, c.green() // 2, c.blue() // 2))
                p.setBrush(QBrush(grad))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRoundedRect(x, y, bw, bh, 6, 6)
                p.setPen(QColor(200, 200, 200))
                p.setFont(QFont("Segoe UI", 9))
                p.drawText(x, self.height() - 18, bw, 15, Qt.AlignmentFlag.AlignCenter, label)
                p.setPen(QColor(255, 255, 255))
                p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                p.drawText(x, y - 22, bw, 15, Qt.AlignmentFlag.AlignCenter, str(int(val)))

    def make_card(title, content_layout):
        card = QFrame()
        card.setStyleSheet(CARD_STYLE)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)
        t = QLabel(title)
        t.setStyleSheet(HEADER_STYLE)
        card_layout.addWidget(t)
        card_layout.addLayout(content_layout)
        return card

    def make_stat_row(label, value):
        row = QHBoxLayout()
        l = QLabel(label)
        l.setStyleSheet(LABEL_STYLE)
        row.addWidget(l)
        v = QLabel(str(value))
        v.setStyleSheet(VALUE_STYLE)
        v.setAlignment(Qt.AlignmentFlag.AlignRight)
        row.addWidget(v)
        return row

    class DashboardTab(QWidget):
        def __init__(self):
            super().__init__()
            self.results = {}
            self._worker = None
            self._setup_ui()

        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(16)

            top = QHBoxLayout()
            top.setSpacing(16)
            self.gauge = ScoreGauge()
            top.addWidget(self.gauge, alignment=Qt.AlignmentFlag.AlignCenter)

            right = QVBoxLayout()
            right.setSpacing(12)
            self.status_label = QLabel("Ready to benchmark")
            self.status_label.setStyleSheet("color: #8b949e; font-size: 14px;")
            right.addWidget(self.status_label)

            btn_row = QHBoxLayout()
            self.start_btn = QPushButton("  START BENCHMARK  ")
            self.start_btn.setFixedHeight(48)
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #238636, stop:1 #2ea043);
                    color: white; border: none; border-radius: 10px;
                    font-size: 14px; font-weight: bold; letter-spacing: 1px;
                }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ea043, stop:1 #3fb950); }
                QPushButton:disabled { background: #333; color: #666; }
            """)
            self.start_btn.clicked.connect(self._run_all)
            btn_row.addWidget(self.start_btn)
            right.addLayout(btn_row)

            profile_row = QHBoxLayout()
            for name, label in [("quick", "Quick"), ("full", "Full"), ("gaming", "Gaming")]:
                btn = QPushButton(label)
                btn.setFixedHeight(36)
                btn.clicked.connect(lambda checked, n=name: self._run_profile(n))
                profile_row.addWidget(btn)
            right.addLayout(profile_row)
            right.addStretch()

            top.addLayout(right, 1)
            layout.addLayout(top)

            self.chart = BarChart()
            layout.addWidget(self.chart)

            self.grade_label = QLabel("")
            self.grade_label.setStyleSheet("color: #8b949e; font-size: 12px;")
            self.grade_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.grade_label)
            layout.addStretch()

        def _run_all(self):
            self.start_btn.setEnabled(False)
            self.start_btn.setText("  RUNNING...  ")
            self._worker = BenchmarkWorker("all")
            self._worker.progress.connect(lambda msg: self.status_label.setText(msg))
            self._worker.result_ready.connect(self._on_done)
            self._worker.start()

        def _run_profile(self, profile_name):
            self.start_btn.setEnabled(False)
            self.start_btn.setText("  RUNNING...  ")
            profile = get_profile.__wrapped__ if hasattr(get_profile, '__wrapped__') else None
            from benchmarks.profiles import PROFILES
            prof = PROFILES.get(profile_name, PROFILES["full"])
            self._worker = BenchmarkWorker("all")
            self._worker.progress.connect(lambda msg: self.status_label.setText(msg))
            self._worker.result_ready.connect(self._on_done)
            self._worker.start()

        def _on_done(self, _, results):
            self.start_btn.setEnabled(True)
            self.start_btn.setText("  START BENCHMARK  ")
            self.results = results
            self.status_label.setText("Benchmark complete!")

            chart_data = {}
            total = 0
            for key in ["cpu", "memory", "disk", "gpu"]:
                if key in results:
                    val = results[key].get("final_score", results[key].get("score", 0))
                    chart_data[key.upper()] = val
                    total += val

            avg = total / max(len(chart_data), 1)
            grade, grade_desc = get_grade(avg)

            self.gauge.set_score(avg, "TOTAL", f"Grade: {grade}")
            self.chart.set_data(chart_data, max(max(chart_data.values()) * 1.2, 100))
            self.grade_label.setText(f"Grade: {grade} - {grade_desc}")

            try:
                save_result(results, get_all_system_info())
            except Exception:
                pass

    class BenchmarksTab(QWidget):
        def __init__(self):
            super().__init__()
            self._workers = {}
            self._setup_ui()

        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(12)

            self.output = QTextEdit()
            self.output.setReadOnly(True)
            layout.addWidget(self.output)

            btn_row = QHBoxLayout()
            for name, color in [("CPU", "#58a6ff"), ("Memory", "#00c864"), ("Disk", "#ffb400"), ("GPU", "#ff5050")]:
                btn = QPushButton(f"Run {name}")
                btn.setFixedHeight(42)
                btn.setStyleSheet(f"""
                    QPushButton {{ background: {color}; color: white; font-weight: bold; }}
                    QPushButton:hover {{ background: {color}dd; }}
                    QPushButton:disabled {{ background: #333; color: #666; }}
                """)
                btn.clicked.connect(lambda checked, n=name.lower(): self._run_bench(n))
                btn_row.addWidget(btn)
            layout.addLayout(btn_row)

        def _run_bench(self, name):
            self.output.clear()
            self.output.append(f"Running {name.upper()} benchmark...\n")
            worker = BenchmarkWorker(name)
            worker.progress.connect(lambda msg: self.output.append(f"> {msg}"))
            worker.result_ready.connect(self._on_result)
            worker.start()
            self._workers[name] = worker

        def _on_result(self, bench_type, result):
            self.output.append("\n" + "=" * 50)
            self.output.append(f"  {bench_type.upper()} RESULTS")
            self.output.append("=" * 50)
            if "scores" in result:
                for k, v in result["scores"].items():
                    self.output.append(f"  {k:20s} {v:.0f}")
                self.output.append(f"\n  SCORE: {result['final_score']:.0f}")
            elif "avg_fps" in result:
                self.output.append(f"  Avg FPS:           {result['avg_fps']:.1f}")
                self.output.append(f"  Min FPS:           {result['min_fps']:.1f}")
                self.output.append(f"  Max FPS:           {result['max_fps']:.1f}")
                self.output.append(f"  1% Low:            {result.get('one_percent_low', 0):.1f}")
                self.output.append(f"  0.1% Low:          {result.get('zero_point_one_percent_low', 0):.1f}")
                self.output.append(f"  Triangles:         {result.get('total_triangles', 0)}")
                self.output.append(f"\n  SCORE: {result['score']:.0f}")

    class StressTab(QWidget):
        def __init__(self):
            super().__init__()
            self._worker = None
            self._setup_ui()

        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(16)

            for test_name, color in [("CPU", "#58a6ff"), ("GPU", "#ff5050"), ("Combined", "#ffb400")]:
                card = QFrame()
                card.setStyleSheet(CARD_STYLE)
                card_layout = QHBoxLayout(card)
                card_layout.setContentsMargins(16, 12, 16, 12)

                t = QLabel(test_name)
                t.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold; min-width: 80px;")
                card_layout.addWidget(t)

                for dur, label in [(300, "5 min"), (600, "10 min"), (1800, "30 min")]:
                    btn = QPushButton(label)
                    btn.setFixedHeight(36)
                    btn.clicked.connect(lambda checked, n=test_name.lower(), d=dur: self._start_stress(n, d))
                    card_layout.addWidget(btn)

                layout.addWidget(card)

            self.progress_bar = QProgressBar()
            self.progress_bar.setValue(0)
            layout.addWidget(self.progress_bar)

            self.status_label = QLabel("Select a stress test to begin")
            self.status_label.setStyleSheet(LABEL_STYLE)
            layout.addWidget(self.status_label)

            self.output = QTextEdit()
            self.output.setReadOnly(True)
            layout.addWidget(self.output)

            self.stop_btn = QPushButton("Stop")
            self.stop_btn.setFixedHeight(36)
            self.stop_btn.setEnabled(False)
            self.stop_btn.clicked.connect(self._stop)
            layout.addWidget(self.stop_btn)

        def _start_stress(self, test_type, duration):
            self.output.clear()
            self.progress_bar.setValue(0)
            self.stop_btn.setEnabled(True)
            self._worker = StressWorker(test_type, duration)
            self._worker.progress.connect(self._on_progress)
            self._worker.finished.connect(self._on_finished)
            self._worker.start()
            self.status_label.setText(f"Running {test_type} stress test ({duration//60} min)...")

        def _on_progress(self, pct, elapsed, total):
            self.progress_bar.setValue(int(pct))
            m, s = divmod(int(elapsed), 60)
            tm, ts = divmod(int(total), 60)
            self.status_label.setText(f"Elapsed: {m:02d}:{s:02d} / {tm:02d}:{ts:02d} ({pct:.0f}%)")

        def _on_finished(self, result):
            self.stop_btn.setEnabled(False)
            self.progress_bar.setValue(100)
            if "error" in result:
                self.status_label.setText(f"Error: {result['error']}")
            else:
                self.status_label.setText("Stress test complete!")
                self.output.append(f"Type: {result.get('type', 'unknown')}")
                self.output.append(f"Duration: {result.get('duration', 0):.1f}s")
                if "frames" in result:
                    self.output.append(f"Frames: {result['frames']}")
                    self.output.append(f"Avg FPS: {result.get('avg_fps', 0):.1f}")

        def _stop(self):
            if self._worker and self._worker.isRunning():
                self._worker.terminate()

    class HistoryTab(QWidget):
        def __init__(self):
            super().__init__()
            self._setup_ui()

        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(12)

            btn_row = QHBoxLayout()
            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self._load)
            btn_row.addWidget(refresh_btn)
            btn_row.addStretch()
            layout.addLayout(btn_row)

            self.output = QTextEdit()
            self.output.setReadOnly(True)
            layout.addWidget(self.output)

            self._load()

        def _load(self):
            history = load_history()
            if history:
                self.output.setText(format_history(history))
            else:
                self.output.setText("No benchmark history yet.\nRun a benchmark to see results here.")

    class SystemInfoTab(QWidget):
        def __init__(self):
            super().__init__()
            self._setup_ui()

        def _setup_ui(self):
            layout = QVBoxLayout(self)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(12)

            refresh_btn = QPushButton("Refresh")
            refresh_btn.setFixedWidth(100)
            refresh_btn.clicked.connect(self._load)
            layout.addWidget(refresh_btn)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            self.content = QWidget()
            self.content_layout = QVBoxLayout(self.content)
            self.content_layout.setSpacing(12)
            scroll.setWidget(self.content)
            layout.addWidget(scroll)

            self._load()

        def _load(self):
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            try:
                info = get_all_system_info()
            except Exception as e:
                err = QLabel(f"Error loading system info: {e}")
                err.setStyleSheet("color: #ff5050;")
                self.content_layout.addWidget(err)
                return

            cpu = info.get("cpu", {})
            cpu_layout = QVBoxLayout()
            cpu_layout.addLayout(make_stat_row("Model", cpu.get("name", "Unknown")))
            cpu_layout.addLayout(make_stat_row("Manufacturer", cpu.get("manufacturer", "Unknown")))
            cpu_layout.addLayout(make_stat_row("Cores / Threads", f"{cpu.get('cores', '?')} / {cpu.get('threads', '?')}"))
            if cpu.get("base_clock_ghz"):
                cpu_layout.addLayout(make_stat_row("Base Clock", f"{cpu['base_clock_ghz']} GHz"))
            if cpu.get("current_clock_ghz"):
                cpu_layout.addLayout(make_stat_row("Current Clock", f"{cpu['current_clock_ghz']} GHz"))
            self.content_layout.addWidget(make_card("CPU", cpu_layout))

            gpu_list = info.get("gpu", [])
            for i, gpu in enumerate(gpu_list):
                gpu_layout = QVBoxLayout()
                gpu_layout.addLayout(make_stat_row("Model", gpu.get("name", "Unknown")))
                if gpu.get("vram_gb"):
                    gpu_layout.addLayout(make_stat_row("VRAM", f"{gpu['vram_gb']} GB"))
                if gpu.get("driver_version") and gpu["driver_version"] != "Unknown":
                    gpu_layout.addLayout(make_stat_row("Driver", gpu["driver_version"]))
                title = f"GPU" + (f" {i+1}" if len(gpu_list) > 1 else "")
                self.content_layout.addWidget(make_card(title, gpu_layout))

            ram = info.get("ram", {})
            ram_layout = QVBoxLayout()
            ram_layout.addLayout(make_stat_row("Total", f"{ram.get('total_gb', '?')} GB"))
            ram_layout.addLayout(make_stat_row("Used", f"{ram.get('used_gb', '?')} GB ({ram.get('percent_used', '?')}%)"))
            if ram.get("speed_mhz"):
                ram_layout.addLayout(make_stat_row("Speed", f"{ram['speed_mhz']} MHz ({ram.get('type', '?')})"))
            if ram.get("slot_count"):
                ram_layout.addLayout(make_stat_row("Slots", str(ram["slot_count"])))
            self.content_layout.addWidget(make_card("Memory", ram_layout))

            disks = info.get("disks", [])
            if disks:
                disk_layout = QVBoxLayout()
                for d in disks[:4]:
                    disk_layout.addLayout(make_stat_row(
                        f"{d['device']} ({d['mountpoint']})",
                        f"{d['total_gb']} GB [{d['fstype']}]"
                    ))
                self.content_layout.addWidget(make_card("Storage", disk_layout))

            self.content_layout.addStretch()

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Ngga Tutu Benchmark")
            self.setMinimumSize(1000, 700)
            self.setup_ui()

        def setup_ui(self):
            central = QWidget()
            self.setCentralWidget(central)
            main_layout = QVBoxLayout(central)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            header = QWidget()
            header.setFixedHeight(60)
            header.setStyleSheet("""
                QWidget { background: #0d1117; border-bottom: 1px solid #21262d; }
            """)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(25, 0, 25, 0)
            title = QLabel("Ngga Tutu")
            title.setStyleSheet("color: #58a6ff; font-size: 22px; font-weight: bold;")
            header_layout.addWidget(title)
            subtitle = QLabel("  Real Performance Benchmark")
            subtitle.setStyleSheet("color: #8b949e; font-size: 12px;")
            header_layout.addWidget(subtitle)
            header_layout.addStretch()
            ver = QLabel(f"v{VERSION}")
            ver.setStyleSheet("color: #484f58; font-size: 11px;")
            header_layout.addWidget(ver)
            main_layout.addWidget(header)

            tabs = QTabWidget()
            tabs.addTab(DashboardTab(), "Dashboard")
            tabs.addTab(BenchmarksTab(), "Benchmarks")
            tabs.addTab(StressTab(), "Stress Test")
            tabs.addTab(HistoryTab(), "History")
            tabs.addTab(SystemInfoTab(), "System Info")
            main_layout.addWidget(tabs)

            status = QLabel("Ready")
            status.setFixedHeight(28)
            status.setStyleSheet("color: #8b949e; padding: 4px 15px; background: #161b22; border-top: 1px solid #21262d; font-size: 11px;")
            main_layout.addWidget(status)

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    splash = SplashScreen()
    splash.show()

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
    elif cmd == "profiles":
        print(format_profiles())
    elif cmd == "history":
        history = load_history()
        print(format_history(history) if history else "No history yet.")
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
