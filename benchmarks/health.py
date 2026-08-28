"""System health analysis with thermal throttling detection."""


def analyze_health(benchmark_results, monitor_data=None):
    """Analyze system health from benchmark results."""
    health = {
        "cpu": {"status": "good", "message": "CPU performing normally"},
        "gpu": {"status": "good", "message": "GPU performing normally"},
        "ram": {"status": "good", "message": "RAM performing normally"},
        "disk": {"status": "good", "message": "Disk performing normally"},
        "thermals": {"status": "good", "message": "Thermals within normal range"},
    }

    cpu_scores = benchmark_results.get("cpu", {}).get("scores", {})
    gpu_data = benchmark_results.get("gpu", {})
    ram_scores = benchmark_results.get("memory", {}).get("scores", {})
    disk_scores = benchmark_results.get("disk", {}).get("scores", {})

    # CPU health
    single_core = cpu_scores.get("single_core", 0)
    multi_core = cpu_scores.get("multi_core", 0)
    if single_core < 20:
        health["cpu"] = {"status": "critical", "message": "CPU single-core performance critically low"}
    elif single_core < 50:
        health["cpu"] = {"status": "warning", "message": "CPU single-core performance below average"}
    else:
        health["cpu"] = {"status": "excellent", "message": "CPU performance excellent"}

    # GPU health
    avg_fps = gpu_data.get("avg_fps", 0)
    if avg_fps < 15:
        health["gpu"] = {"status": "critical", "message": "GPU rendering extremely slow"}
    elif avg_fps < 30:
        health["gpu"] = {"status": "warning", "message": "GPU below 30 FPS target"}
    else:
        health["gpu"] = {"status": "excellent", "message": "GPU rendering smoothly"}

    # RAM health
    latency = ram_scores.get("latency", 0)
    if latency < 100:
        health["ram"] = {"status": "warning", "message": "RAM latency higher than expected"}
    elif latency > 500:
        health["ram"] = {"status": "excellent", "message": "RAM latency excellent"}
    else:
        health["ram"] = {"status": "good", "message": "RAM performing normally"}

    # Disk health
    iops_read = disk_scores.get("iops_read", 0)
    if iops_read < 50:
        health["disk"] = {"status": "warning", "message": "Disk IOPS below expected (HDD?)"}
    elif iops_read > 500:
        health["disk"] = {"status": "excellent", "message": "Disk performance excellent (NVMe?)"}
    else:
        health["disk"] = {"status": "good", "message": "Disk performing normally"}

    # Thermal analysis
    if monitor_data:
        cpu_temp = monitor_data.get("cpu", {}).get("temperature")
        gpu_temp = monitor_data.get("gpu", {}).get("temperature")

        if cpu_temp and cpu_temp > 90:
            health["thermals"] = {"status": "critical", "message": f"CPU temperature critical: {cpu_temp}C"}
        elif cpu_temp and cpu_temp > 80:
            health["thermals"] = {"status": "warning", "message": f"CPU temperature elevated: {cpu_temp}C"}
        elif gpu_temp and gpu_temp > 90:
            health["thermals"] = {"status": "critical", "message": f"GPU temperature critical: {gpu_temp}C"}
        elif gpu_temp and gpu_temp > 80:
            health["thermals"] = {"status": "warning", "message": f"GPU temperature elevated: {gpu_temp}C"}

    return health


def detect_throttling(benchmark_results, monitor_history=None):
    """Detect thermal throttling from benchmark data."""
    throttling = {
        "detected": False,
        "cpu_throttling": False,
        "gpu_throttling": False,
        "details": [],
    }

    gpu_data = benchmark_results.get("gpu", {})
    frame_times = gpu_data.get("frame_times", [])

    if frame_times and len(frame_times) > 10:
        first_quarter = frame_times[:len(frame_times) // 4]
        last_quarter = frame_times[-len(frame_times) // 4:]

        avg_first = sum(first_quarter) / len(first_quarter) if first_quarter else 0
        avg_last = sum(last_quarter) / len(last_quarter) if last_quarter else 0

        if avg_last > avg_first * 1.5:
            throttling["gpu_throttling"] = True
            throttling["detected"] = True
            throttling["details"].append("GPU frame times increasing over time (possible throttling)")

    if monitor_history and len(monitor_history) > 10:
        early_temps = [d.get("cpu", {}).get("temperature") for d in monitor_history[:5] if d.get("cpu", {}).get("temperature")]
        late_temps = [d.get("cpu", {}).get("temperature") for d in monitor_history[-5:] if d.get("cpu", {}).get("temperature")]

        if early_temps and late_temps:
            avg_early = sum(early_temps) / len(early_temps)
            avg_late = sum(late_temps) / len(late_temps)
            if avg_late > avg_early + 10:
                throttling["cpu_throttling"] = True
                throttling["detected"] = True
                throttling["details"].append(f"CPU temperature rose {avg_late - avg_early:.0f}C during test")

    cpu_scores = benchmark_results.get("cpu", {}).get("scores", {})
    single = cpu_scores.get("single_core", 0)
    multi = cpu_scores.get("multi_core", 0)
    cores = benchmark_results.get("cpu", {}).get("scores", {}).get("multi_core", 0)
    if single > 0 and multi > 0:
        expected_multi = single * 4
        if multi < expected_multi * 0.5:
            throttling["details"].append("Multi-core scaling below expected (possible power/thermal limit)")

    return throttling


def format_health_report(health, throttling=None):
    """Format health analysis for display."""
    status_icons = {
        "excellent": "EXCELLENT",
        "good": "GOOD",
        "warning": "WARNING",
        "critical": "CRITICAL",
    }

    lines = []
    lines.append("=" * 55)
    lines.append("  SYSTEM HEALTH ANALYSIS")
    lines.append("=" * 55)

    for component in ["cpu", "gpu", "ram", "disk", "thermals"]:
        info = health.get(component, {})
        status = info.get("status", "unknown")
        message = info.get("message", "No data")
        icon = status_icons.get(status, "UNKNOWN")
        lines.append(f"  {component.upper():10s} [{icon:9s}] {message}")

    if throttling and throttling.get("detected"):
        lines.append("")
        lines.append("-" * 55)
        lines.append("  THROTTLING DETECTED")
        lines.append("-" * 55)
        for detail in throttling.get("details", []):
            lines.append(f"  ! {detail}")

    lines.append("=" * 55)
    return "\n".join(lines)
