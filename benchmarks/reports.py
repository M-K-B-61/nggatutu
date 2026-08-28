"""Report generation - HTML, JSON export."""
import json
import os
from datetime import datetime


def generate_json_report(benchmark_results, system_info=None, filepath=None):
    """Generate JSON report."""
    report = {
        "app": "Ngga Tutu Benchmark",
        "version": "0.4.0",
        "timestamp": datetime.now().isoformat(),
        "system_info": system_info,
        "results": benchmark_results,
    }

    if filepath is None:
        filepath = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)

    return filepath


def generate_html_report(benchmark_results, system_info=None, filepath=None):
    """Generate HTML report."""
    if filepath is None:
        filepath = f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    cpu = benchmark_results.get("cpu", {})
    gpu = benchmark_results.get("gpu", {})
    memory = benchmark_results.get("memory", {})
    disk = benchmark_results.get("disk", {})

    cpu_score = cpu.get("final_score", 0)
    gpu_score = gpu.get("score", 0)
    ram_score = memory.get("final_score", 0)
    disk_score = disk.get("final_score", 0)
    overall = (cpu_score + gpu_score + ram_score + disk_score) / 4

    cpu_info = system_info.get("cpu", {}) if system_info else {}
    gpu_info = system_info.get("gpu", [{}])[0] if system_info and system_info.get("gpu") else {}
    ram_info = system_info.get("ram", {}) if system_info else {}

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Ngga Tutu Benchmark Report</title>
<style>
body {{ background: #0d1117; color: #e6edf3; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; }}
.container {{ max-width: 900px; margin: 0 auto; }}
h1 {{ color: #58a6ff; text-align: center; font-size: 32px; margin-bottom: 5px; }}
.subtitle {{ text-align: center; color: #8b949e; margin-bottom: 30px; }}
.score-box {{ background: #161b22; border-radius: 16px; padding: 30px; text-align: center; margin-bottom: 20px; border: 1px solid #21262d; }}
.score-big {{ font-size: 72px; font-weight: bold; color: #58a6ff; }}
.grade {{ font-size: 24px; color: #8b949e; margin-top: 10px; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }}
.card {{ background: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #21262d; }}
.card h3 {{ color: #58a6ff; margin-top: 0; font-size: 18px; }}
.stat {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #21262d; }}
.stat:last-child {{ border-bottom: none; }}
.label {{ color: #8b949e; }}
.value {{ color: #e6edf3; font-weight: bold; }}
.bar-container {{ background: #21262d; border-radius: 6px; height: 20px; overflow: hidden; margin-top: 8px; }}
.bar {{ height: 100%; border-radius: 6px; transition: width 0.5s; }}
.bar-cpu {{ background: linear-gradient(90deg, #58a6ff, #79c0ff); }}
.bar-gpu {{ background: linear-gradient(90deg, #ff5050, #ff7875); }}
.bar-ram {{ background: linear-gradient(90deg, #00c864, #3fb950); }}
.bar-disk {{ background: linear-gradient(90deg, #ffb400, #e3b341); }}
.footer {{ text-align: center; color: #484f58; margin-top: 30px; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
<h1>Ngga Tutu Benchmark</h1>
<p class="subtitle">Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}</p>

<div class="score-box">
<div class="score-big">{int(overall)}</div>
<div class="grade">Overall Score</div>
</div>

<div class="grid">
<div class="card">
<h3>CPU</h3>
<div class="stat"><span class="label">Model</span><span class="value">{cpu_info.get('name', 'Unknown')}</span></div>
<div class="stat"><span class="label">Cores</span><span class="value">{cpu_info.get('cores', '?')} / {cpu_info.get('threads', '?')} threads</span></div>
<div class="stat"><span class="label">Score</span><span class="value">{int(cpu_score)}</span></div>
<div class="bar-container"><div class="bar bar-cpu" style="width:{min(100, cpu_score/10)}%"></div></div>
</div>

<div class="card">
<h3>GPU</h3>
<div class="stat"><span class="label">Model</span><span class="value">{gpu_info.get('name', 'Unknown')}</span></div>
<div class="stat"><span class="label">VRAM</span><span class="value">{gpu_info.get('vram_gb', '?')} GB</span></div>
<div class="stat"><span class="label">Score</span><span class="value">{int(gpu_score)}</span></div>
<div class="bar-container"><div class="bar bar-gpu" style="width:{min(100, gpu_score/10)}%"></div></div>
</div>

<div class="card">
<h3>Memory</h3>
<div class="stat"><span class="label">Total</span><span class="value">{ram_info.get('total_gb', '?')} GB</span></div>
<div class="stat"><span class="label">Speed</span><span class="value">{ram_info.get('speed_mhz', '?')} MHz ({ram_info.get('type', '?')})</span></div>
<div class="stat"><span class="label">Score</span><span class="value">{int(ram_score)}</span></div>
<div class="bar-container"><div class="bar bar-ram" style="width:{min(100, ram_score/10)}%"></div></div>
</div>

<div class="card">
<h3>Storage</h3>
<div class="stat"><span class="label">Seq Read</span><span class="value">{int(disk.get('seq_read', 0))} MB/s</span></div>
<div class="stat"><span class="label">Seq Write</span><span class="value">{int(disk.get('seq_write', 0))} MB/s</span></div>
<div class="stat"><span class="label">Score</span><span class="value">{int(disk_score)}</span></div>
<div class="bar-container"><div class="bar bar-disk" style="width:{min(100, disk_score/10)}%"></div></div>
</div>
</div>

<div class="footer">
Ngga Tutu Benchmark v0.4.0 - Real Performance Benchmark
</div>
</div>
</body>
</html>"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    return filepath
