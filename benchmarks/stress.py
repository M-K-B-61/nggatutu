"""Stress test - CPU, GPU, Combined with monitoring."""
import time
import math
import os
import threading
from concurrent.futures import ThreadPoolExecutor


def _cpu_stress_worker(stop_event, core_id):
    """Single core CPU stress."""
    total = 0.0
    while not stop_event.is_set():
        total += math.sqrt(abs(total) + 1)
        total += math.sin(total) * math.cos(total)
        total += math.atan2(total, 1.0)
        total += math.log(abs(total) + 1)
    return total


def run_cpu_stress(duration_seconds=300, progress_callback=None):
    """Run CPU stress test for specified duration."""
    cores = os.cpu_count() or 4
    stop_event = threading.Event()
    start_time = time.perf_counter()

    def monitor():
        while not stop_event.is_set():
            elapsed = time.perf_counter() - start_time
            pct = min(100, (elapsed / duration_seconds) * 100)
            if progress_callback:
                progress_callback(pct, elapsed, duration_seconds)
            time.sleep(1.0)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

    with ThreadPoolExecutor(max_workers=cores) as executor:
        futures = [executor.submit(_cpu_stress_worker, stop_event, i) for i in range(cores)]
        stop_event.wait(timeout=duration_seconds)
        stop_event.set()
        for f in futures:
            try:
                f.result(timeout=5)
            except Exception:
                pass

    elapsed = time.perf_counter() - start_time
    return {"type": "cpu", "duration": elapsed, "cores": cores}


def _gpu_stress_worker(stop_event):
    """GPU stress via software rendering."""
    try:
        os.environ["SDL_VIDEODRIVER"] = "windib"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        import pygame
        from pygame.locals import DOUBLEBUF, QUIT
    except ImportError:
        return {"error": "pygame not available"}

    pygame.init()
    screen = pygame.display.set_mode((1280, 720), DOUBLEBUF)
    pygame.display.set_caption("GPU Stress")

    frame_count = 0
    start = time.perf_counter()

    while not stop_event.is_set():
        for event in pygame.event.get():
            if event.type == QUIT:
                stop_event.set()

        screen.fill((2, 2, 2))
        t = time.perf_counter() - start

        for i in range(200):
            x = int(640 + 300 * math.cos(t * 2 + i * 0.1))
            y = int(360 + 200 * math.sin(t * 1.5 + i * 0.15))
            r = int(5 + 3 * math.sin(t + i))
            color = (int(128 + 127 * math.sin(i * 0.5)), int(128 + 127 * math.cos(i * 0.7)), int(128 + 127 * math.sin(i * 1.2)))
            pygame.draw.circle(screen, color, (x, y), max(1, r))

        for i in range(50):
            pts = []
            for j in range(6):
                angle = t * 3 + j * math.pi / 3 + i * 0.3
                px = int(640 + (80 + i) * math.cos(angle))
                py = int(360 + (60 + i * 0.5) * math.sin(angle))
                pts.append((px, py))
            if len(pts) >= 3:
                pygame.draw.polygon(screen, (int(50 + i * 2), int(80 + i), int(120 + i)), pts, 2)

        pygame.display.flip()
        frame_count += 1

    pygame.quit()
    elapsed = time.perf_counter() - start
    avg_fps = frame_count / elapsed if elapsed > 0 else 0
    return {"type": "gpu", "duration": elapsed, "frames": frame_count, "avg_fps": avg_fps}


def run_gpu_stress(duration_seconds=300, progress_callback=None):
    """Run GPU stress test for specified duration."""
    stop_event = threading.Event()
    start_time = time.perf_counter()

    def monitor():
        while not stop_event.is_set():
            elapsed = time.perf_counter() - start_time
            pct = min(100, (elapsed / duration_seconds) * 100)
            if progress_callback:
                progress_callback(pct, elapsed, duration_seconds)
            time.sleep(1.0)
        stop_event.set()

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

    result = _gpu_stress_worker(stop_event)
    return result


def run_combined_stress(duration_seconds=300, progress_callback=None):
    """Run CPU + GPU stress test simultaneously."""
    cores = os.cpu_count() or 4
    stop_event = threading.Event()
    start_time = time.perf_counter()

    def cpu_worker():
        total = 0.0
        while not stop_event.is_set():
            total += math.sqrt(abs(total) + 1)
            total += math.sin(total) * math.cos(total)
            total += math.atan2(total, 1.0)
        return total

    def monitor():
        while not stop_event.is_set():
            elapsed = time.perf_counter() - start_time
            pct = min(100, (elapsed / duration_seconds) * 100)
            if progress_callback:
                progress_callback(pct, elapsed, duration_seconds)
            time.sleep(1.0)
        stop_event.set()

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()

    cpu_thread = threading.Thread(target=lambda: [cpu_worker() for _ in range(cores)])
    cpu_thread.start()

    gpu_result = _gpu_stress_worker(stop_event)

    stop_event.wait(timeout=5)
    cpu_thread.join(timeout=5)

    elapsed = time.perf_counter() - start_time
    return {"type": "combined", "duration": elapsed, "gpu": gpu_result}


def run_stress_test(test_type="cpu", duration_seconds=300, progress_callback=None):
    """Run stress test by type."""
    if test_type == "cpu":
        return run_cpu_stress(duration_seconds, progress_callback)
    elif test_type == "gpu":
        return run_gpu_stress(duration_seconds, progress_callback)
    elif test_type == "combined":
        return run_combined_stress(duration_seconds, progress_callback)
    else:
        raise ValueError(f"Unknown stress test type: {test_type}")
