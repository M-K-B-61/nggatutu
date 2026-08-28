"""Benchmark profiles - Quick, Full, Gaming, Productivity, Stress, Custom."""

PROFILES = {
    "quick": {
        "name": "Quick Test",
        "description": "Fast benchmark (~2 min)",
        "tests": {"cpu": True, "memory": True, "disk": True, "gpu": True},
        "durations": {"cpu": 4, "gpu": 5},
    },
    "full": {
        "name": "Full Benchmark",
        "description": "Complete system test (~10 min)",
        "tests": {"cpu": True, "memory": True, "disk": True, "gpu": True},
        "durations": {"cpu": 12, "gpu": 15},
    },
    "gaming": {
        "name": "Gaming",
        "description": "GPU + FPS focused test",
        "tests": {"cpu": True, "memory": True, "disk": False, "gpu": True},
        "durations": {"cpu": 8, "gpu": 20},
    },
    "productivity": {
        "name": "Productivity",
        "description": "CPU + RAM + Storage focused",
        "tests": {"cpu": True, "memory": True, "disk": True, "gpu": False},
        "durations": {"cpu": 15, "gpu": 0},
    },
    "stress": {
        "name": "Stress Test",
        "description": "Extended stability test (~30 min)",
        "tests": {"cpu": True, "memory": False, "disk": False, "gpu": True},
        "durations": {"cpu": 30, "gpu": 30},
    },
}


def get_profile(name):
    """Get a benchmark profile by name."""
    return PROFILES.get(name, PROFILES["full"])


def list_profiles():
    """List all available profiles."""
    result = []
    for key, profile in PROFILES.items():
        result.append({
            "id": key,
            "name": profile["name"],
            "description": profile["description"],
        })
    return result


def format_profiles():
    """Format profiles for display."""
    lines = []
    lines.append("=" * 55)
    lines.append("  BENCHMARK PROFILES")
    lines.append("=" * 55)
    for key, profile in PROFILES.items():
        tests = [k.upper() for k, v in profile["tests"].items() if v]
        lines.append(f"\n  {profile['name']} ({key})")
        lines.append(f"    {profile['description']}")
        lines.append(f"    Tests: {', '.join(tests)}")
    lines.append("\n" + "=" * 55)
    return "\n".join(lines)
