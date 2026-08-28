"""Overall score system with categories."""
import json
import os
from datetime import datetime


CATEGORY_WEIGHTS = {
    "gaming": {"gpu": 0.50, "cpu": 0.25, "ram": 0.15, "disk": 0.10},
    "productivity": {"cpu": 0.35, "ram": 0.30, "disk": 0.25, "gpu": 0.10},
    "compute": {"cpu": 0.45, "gpu": 0.30, "ram": 0.15, "disk": 0.10},
    "storage": {"disk": 0.50, "ram": 0.25, "cpu": 0.15, "gpu": 0.10},
    "overall": {"cpu": 0.30, "gpu": 0.30, "ram": 0.20, "disk": 0.20},
}


def calculate_category_scores(benchmark_results):
    """Calculate scores for each category."""
    scores = {}

    cpu_score = benchmark_results.get("cpu", {}).get("final_score", 0)
    gpu_score = benchmark_results.get("gpu", {}).get("score", 0)
    ram_score = benchmark_results.get("memory", {}).get("final_score", 0)
    disk_score = benchmark_results.get("disk", {}).get("final_score", 0)

    component_scores = {
        "cpu": cpu_score,
        "gpu": gpu_score,
        "ram": ram_score,
        "disk": disk_score,
    }

    for category, weights in CATEGORY_WEIGHTS.items():
        total = 0
        for comp, weight in weights.items():
            total += component_scores.get(comp, 0) * weight
        scores[category] = round(total, 1)

    scores["component_scores"] = component_scores
    return scores


def get_grade(score):
    """Get grade from score."""
    if score >= 900:
        return "S", "Outstanding"
    elif score >= 750:
        return "A", "Excellent"
    elif score >= 600:
        return "B", "Very Good"
    elif score >= 450:
        return "C", "Good"
    elif score >= 300:
        return "D", "Average"
    else:
        return "E", "Below Average"


def get_percentile(score):
    """Estimate percentile rank (approximate)."""
    if score >= 1000:
        return 1
    elif score >= 850:
        return 5
    elif score >= 700:
        return 15
    elif score >= 550:
        return 35
    elif score >= 400:
        return 55
    elif score >= 250:
        return 75
    else:
        return 90


def format_score_report(benchmark_results):
    """Format a complete score report."""
    category_scores = calculate_category_scores(benchmark_results)
    overall = category_scores["overall"]
    grade, grade_desc = get_grade(overall)
    percentile = get_percentile(overall)
    components = category_scores["component_scores"]

    lines = []
    lines.append("=" * 60)
    lines.append("  BENCHMARK RESULTS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  OVERALL SCORE: {int(overall)}")
    lines.append(f"  Grade: {grade} ({grade_desc})")
    lines.append(f"  Top {percentile}%")
    lines.append("")
    lines.append("-" * 60)
    lines.append("  CATEGORY SCORES")
    lines.append("-" * 60)
    for cat in ["gaming", "productivity", "compute", "storage"]:
        val = category_scores[cat]
        bar_len = int(val / 1000 * 30)
        bar = "=" * bar_len + "." * (30 - bar_len)
        lines.append(f"  {cat.upper():12s} [{bar}] {int(val)}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("  COMPONENT SCORES")
    lines.append("-" * 60)
    lines.append(f"  CPU:  {int(components['cpu']):>6}")
    lines.append(f"  GPU:  {int(components['gpu']):>6}")
    lines.append(f"  RAM:  {int(components['ram']):>6}")
    lines.append(f"  SSD:  {int(components['disk']):>6}")
    lines.append("=" * 60)

    return "\n".join(lines)
