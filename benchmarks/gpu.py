import time
import math
import os
import random


def run_gpu_benchmark(duration=15):
    """Heavy 3D rendering benchmark using pygame."""
    print("\n" + "=" * 55)
    print("  3D RENDERING BENCHMARK - HEAVY STRESS")
    print("=" * 55, flush=True)

    try:
        import pygame
    except ImportError:
        print("  pygame not available", flush=True)
        return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

    return _run_heavy_benchmark(pygame, duration)


def _project_point(x, y, z, cx, cy, size, cos_a, sin_a, cos_b, sin_b):
    x2 = x * cos_a - z * sin_a
    z2 = x * sin_a + z * cos_a
    y2 = y * cos_b - z2 * sin_b
    z3 = y * sin_b + z2 * cos_b
    scale = 3 / (3 + z3)
    return int(cx + x2 * size * scale), int(cy + y2 * size * scale), z3


def _generate_sphere(segments=12):
    vertices = []
    faces = []
    for i in range(segments + 1):
        phi = math.pi * i / segments
        for j in range(segments):
            theta = 2 * math.pi * j / segments
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)
            vertices.append((x, y, z))

    for i in range(segments):
        for j in range(segments):
            a = i * segments + j
            b = i * segments + (j + 1) % segments
            c = (i + 1) * segments + (j + 1) % segments
            d = (i + 1) * segments + j
            faces.append((a, b, c, d))
    return vertices, faces


def _run_heavy_benchmark(pygame, duration=15):
    pygame.init()
    W, H = 1024, 768
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Ngga Tutu GPU Stress Test")
    clock = pygame.time.Clock()

    sphere_v, sphere_f = _generate_sphere(16)
    particles = []
    for _ in range(2000):
        particles.append({
            "x": random.uniform(-3, 3),
            "y": random.uniform(-3, 3),
            "z": random.uniform(-3, 3),
            "vx": random.uniform(-0.02, 0.02),
            "vy": random.uniform(-0.02, 0.02),
            "vz": random.uniform(-0.02, 0.02),
            "r": random.randint(2, 6),
            "color": (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
        })

    fps_list = []
    frame_count = 0
    start = time.perf_counter()
    last_time = start
    angle = 0
    frame_buffer = pygame.Surface((W, H))

    total_triangles = 0
    total_pixels = 0

    print(f"  Running {duration}s heavy 3D stress...", flush=True)
    print(f"  - {len(sphere_v)} vertices, {len(sphere_f)} faces per sphere x5", flush=True)
    print(f"  - 2000 particles with physics", flush=True)
    print(f"  - Software rasterization + post-processing", flush=True)

    while time.perf_counter() - start < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

        frame_buffer.fill((5, 5, 15))

        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        cos_b = math.cos(math.radians(angle * 0.6))
        sin_b = math.sin(math.radians(angle * 0.6))
        cos_c = math.cos(math.radians(angle * 0.3))
        sin_c = math.sin(math.radians(angle * 0.3))

        cx, cy = W // 2, H // 2

        frame_triangles = 0

        for obj_idx in range(5):
            obj_x = 1.8 * math.cos(math.radians(angle * 0.2 + obj_idx * 72))
            obj_y = 1.2 * math.sin(math.radians(angle * 0.15 + obj_idx * 72))
            obj_z = math.sin(math.radians(angle * 0.1 + obj_idx * 36))
            scale = 120 + 30 * math.sin(angle * 0.02 + obj_idx)

            r = int(200 + 55 * math.sin(obj_idx * 1.2))
            g = int(200 + 55 * math.sin(obj_idx * 1.2 + 2))
            b = int(200 + 55 * math.sin(obj_idx * 1.2 + 4))

            transformed = []
            for vx, vy, vz in sphere_v:
                px, py, pz = _project_point(
                    vx * scale + obj_x * 100, vy * scale + obj_y * 100, vz * scale + obj_z * 100,
                    cx, cy, 1.0, cos_a, sin_a, cos_b, sin_b
                )
                transformed.append((px, py, pz))

            for face in sphere_f:
                pts = [transformed[i] for i in face]
                min_z = min(p[2] for p in pts)
                if min_z > -10:
                    depth = max(0, min(1, (min_z + 3) / 6))
                    fr = max(0, min(255, int(r * depth)))
                    fg = max(0, min(255, int(g * depth)))
                    fb = max(0, min(255, int(b * depth)))
                    try:
                        pygame.draw.polygon(frame_buffer, (fr, fg, fb),
                                           [(p[0], p[1]) for p in pts])
                        pygame.draw.polygon(frame_buffer, (fr // 2, fg // 2, fb // 2),
                                           [(p[0], p[1]) for p in pts], 1)
                    except Exception:
                        pass
                    frame_triangles += 1

        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["z"] += p["vz"]

            if abs(p["x"]) > 3:
                p["vx"] *= -1
            if abs(p["y"]) > 3:
                p["vy"] *= -1
            if abs(p["z"]) > 3:
                p["vz"] *= -1

            px, py, pz = _project_point(
                p["x"] * 80, p["y"] * 80, p["z"] * 80,
                cx, cy, 0.5, cos_a, sin_a, cos_b, sin_b
            )

            if 0 <= px < W and 0 <= py < H:
                brightness = max(0.3, min(1.0, (pz + 3) / 6))
                cr = max(0, min(255, int(p["color"][0] * brightness)))
                cg = max(0, min(255, int(p["color"][1] * brightness)))
                cb = max(0, min(255, int(p["color"][2] * brightness)))
                r_size = max(1, int(p["r"] * brightness))
                pygame.draw.circle(frame_buffer, (cr, cg, cb), (px, py), r_size)

        post_surface = pygame.Surface((W // 2, H // 2))
        pygame.transform.smoothscale(frame_buffer, (W // 2, H // 2), post_surface)
        pygame.transform.scale(post_surface, (W, H), frame_buffer)

        for stripe_y in range(0, H, 4):
            alpha = int(30 + 20 * math.sin(angle * 0.05 + stripe_y * 0.02))
            stripe_color = (alpha, alpha, alpha + 20)
            pygame.draw.line(frame_buffer, stripe_color, (0, stripe_y), (W, stripe_y))

        now = time.perf_counter()
        if now - last_time > 0:
            fps_list.append(1.0 / (now - last_time))
        last_time = now

        font = pygame.font.SysFont("consolas", 20, bold=True)
        fps_val = fps_list[-1] if fps_list else 0

        texts = [
            f"FPS: {fps_val:.0f}",
            f"Frame: {frame_count}",
            f"Triangles: {frame_triangles}",
            f"Particles: {len(particles)}",
            f"Resolution: {W}x{H}",
        ]

        y = 10
        for txt in texts:
            surf = font.render(txt, True, (0, 255, 0))
            bg = pygame.Surface((surf.get_width() + 8, surf.get_height() + 2))
            bg.fill((0, 0, 0))
            bg.set_alpha(150)
            frame_buffer.blit(bg, (8, y - 2))
            frame_buffer.blit(surf, (12, y))
            y += 24

        screen.blit(frame_buffer, (0, 0))
        pygame.display.flip()
        frame_count += 1
        total_triangles += frame_triangles
        angle += 1.5
        clock.tick(0)

    pygame.quit()

    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0
    min_fps = min(fps_list) if fps_list else 0
    max_fps = max(fps_list) if fps_list else 0
    score = avg_fps * 5 + total_triangles / max(frame_count, 1) * 0.5

    print(f"  Average FPS:     {avg_fps:.1f}", flush=True)
    print(f"  Min FPS:         {min_fps:.1f}", flush=True)
    print(f"  Max FPS:         {max_fps:.1f}", flush=True)
    print(f"  Total Frames:    {frame_count}", flush=True)
    print(f"  Total Triangles: {total_triangles}", flush=True)
    print(f"  Triangles/Frame: {total_triangles // max(frame_count, 1)}", flush=True)
    print("\n" + "-" * 55)
    print(f"  GPU SCORE: {score:.0f}")
    print("-" * 55, flush=True)

    return {
        "avg_fps": avg_fps,
        "min_fps": min_fps,
        "max_fps": max_fps,
        "frames": frame_count,
        "total_triangles": total_triangles,
        "score": score,
    }
