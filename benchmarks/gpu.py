import time
import math
import os


def run_gpu_benchmark(duration=10):
    """3D rendering benchmark using pygame."""
    print("\n" + "=" * 55)
    print("  3D RENDERING BENCHMARK")
    print("=" * 55, flush=True)

    try:
        import pygame
    except ImportError:
        print("  pygame not available", flush=True)
        return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

    return _run_render_benchmark(pygame, duration)


def _run_render_benchmark(pygame, duration=10):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Ngga Tutu 3D Benchmark")

    fps_list = []
    frame_count = 0
    start = time.perf_counter()
    last_time = start
    angle = 0

    print(f"  Running {duration}s 3D render stress test...", flush=True)

    while time.perf_counter() - start < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

        screen.fill((10, 10, 30))

        size = 150
        cx, cy = 400, 300

        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        cos_b = math.cos(math.radians(angle * 0.7))
        sin_b = math.sin(math.radians(angle * 0.7))

        vertices_3d = [
            (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
        ]

        projected = []
        for x, y, z in vertices_3d:
            x2 = x * cos_a - z * sin_a
            z2 = x * sin_a + z * cos_a
            y2 = y * cos_b - z2 * sin_b
            z3 = y * sin_b + z2 * cos_b
            scale = 3 / (3 + z3)
            px = int(cx + x2 * size * scale)
            py = int(cy + y2 * size * scale)
            projected.append((px, py))

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        for i, (a, b) in enumerate(edges):
            color = (
                int(128 + 127 * math.sin(angle * 0.01 + i)),
                int(128 + 127 * math.cos(angle * 0.01 + i)),
                255
            )
            pygame.draw.line(screen, color, projected[a], projected[b], 2)

        for tri_offset in range(8):
            tri_angle = angle * 0.05 + tri_offset * 45
            tx = cx + 220 * math.cos(math.radians(tri_angle))
            ty = cy + 220 * math.sin(math.radians(tri_angle))
            points = []
            for p in range(3):
                a = tri_angle + p * 120
                points.append((
                    int(tx + 35 * math.cos(math.radians(a))),
                    int(ty + 35 * math.sin(math.radians(a)))
                ))
            color = (
                int(255 * abs(math.sin(tri_offset * 0.8))),
                int(255 * abs(math.cos(tri_offset * 0.8))),
                128
            )
            pygame.draw.polygon(screen, color, points)

        for obj in range(5):
            ox = cx + int(180 * math.cos(math.radians(angle * 0.3 + obj * 72)))
            oy = cy + int(180 * math.sin(math.radians(angle * 0.3 + obj * 72)))
            r = 20 + int(10 * math.sin(angle * 0.02 + obj))
            pygame.draw.circle(screen, (200, 100, 50), (ox, oy), r)
            pygame.draw.circle(screen, (50, 100, 200), (ox, oy), r - 5)

        now = time.perf_counter()
        if now - last_time > 0:
            fps_list.append(1.0 / (now - last_time))
        last_time = now

        font = pygame.font.SysFont(None, 36)
        fps_val = fps_list[-1] if fps_list else 0
        fps_text = font.render(f"FPS: {fps_val:.0f}", True, (0, 255, 0))
        screen.blit(fps_text, (10, 10))

        frame_text = font.render(f"Frame: {frame_count}", True, (255, 255, 0))
        screen.blit(frame_text, (10, 50))

        pygame.display.flip()
        frame_count += 1
        angle += 2

    pygame.quit()

    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0
    min_fps = min(fps_list) if fps_list else 0
    max_fps = max(fps_list) if fps_list else 0
    score = avg_fps * 10

    print(f"  Average FPS: {avg_fps:.1f}", flush=True)
    print(f"  Min FPS:     {min_fps:.1f}", flush=True)
    print(f"  Max FPS:     {max_fps:.1f}", flush=True)
    print(f"  Frames:      {frame_count}", flush=True)
    print("\n" + "-" * 55)
    print(f"  GPU SCORE: {score:.0f}")
    print("-" * 55, flush=True)

    return {
        "avg_fps": avg_fps,
        "min_fps": min_fps,
        "max_fps": max_fps,
        "frames": frame_count,
        "score": score,
    }
