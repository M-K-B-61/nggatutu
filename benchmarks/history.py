"""Benchmark history - storage, comparison, trend analysis."""
import json
import os
from datetime import datetime


HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "benchmark_history")


def _ensure_history_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)


def save_result(results, system_info=None):
    """Save benchmark result to history."""
    _ensure_history_dir()

    entry = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "system_info": system_info,
    }

    filename = f"result_{entry['id']}.json"
    filepath = os.path.join(HISTORY_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(entry, f, indent=2)

    return entry["id"]


def load_history(limit=50):
    """Load recent benchmark history."""
    _ensure_history_dir()
    entries = []

    if not os.path.exists(HISTORY_DIR):
        return entries

    files = sorted(
        [f for f in os.listdir(HISTORY_DIR) if f.startswith("result_") and f.endswith(".json")],
        reverse=True,
    )

    for filename in files[:limit]:
        filepath = os.path.join(HISTORY_DIR, filename)
        try:
            with open(filepath, "r") as f:
                entry = json.load(f)
                entries.append(entry)
        except Exception:
            continue

    return entries


def get_latest():
    """Get the most recent benchmark result."""
    history = load_history(limit=1)
    return history[0] if history else None


def compare_results(result_a, result_b):
    """Compare two benchmark results."""
    scores_a = _extract_scores(result_a)
    scores_b = _extract_scores(result_b)

    comparison = {}
    for key in scores_a:
        if key in scores_b:
            val_a = scores_a[key]
            val_b = scores_b[key]
            diff = val_b - val_a
            pct = (diff / val_a * 100) if val_a > 0 else 0
            comparison[key] = {
                "previous": val_a,
                "current": val_b,
                "diff": round(diff, 1),
                "pct_change": round(pct, 1),
            }

    return comparison


def _extract_scores(result_entry):
    """Extract component scores from a result entry."""
    results = result_entry.get("results", {})
    scores = {}
    scores["cpu"] = results.get("cpu", {}).get("final_score", 0)
    scores["gpu"] = results.get("gpu", {}).get("score", 0)
    scores["ram"] = results.get("memory", {}).get("final_score", 0)
    scores["disk"] = results.get("disk", {}).get("final_score", 0)
    scores["overall"] = (scores["cpu"] + scores["gpu"] + scores["ram"] + scores["disk"]) / 4
    return scores


def format_history(history):
    """Format history for display."""
    lines = []
    lines.append("=" * 55)
    lines.append("  BENCHMARK HISTORY")
    lines.append("=" * 55)

    for entry in history:
        ts = entry.get("timestamp", "Unknown")
        try:
            dt = datetime.fromisoformat(ts)
            date_str = dt.strftime("%d %b %Y, %H:%M")
        except Exception:
            date_str = ts

        scores = _extract_scores(entry)
        overall = scores.get("overall", 0)

        lines.append(f"\n  {date_str}")
        lines.append(f"    Overall: {int(overall):>6}  |  CPU: {int(scores.get('cpu', 0)):>6}  GPU: {int(scores.get('gpu', 0)):>6}")
        lines.append(f"    RAM: {int(scores.get('ram', 0)):>6}  |  SSD: {int(scores.get('disk', 0)):>6}")

    lines.append("\n" + "=" * 55)
    return "\n".join(lines)
