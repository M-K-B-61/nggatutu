import time
import math
import os
import random


def run_gpu_benchmark(duration=20):
    """Heavy 3D rendering benchmark using pygame."""
    print("\n" + "=" * 55)
    print("  GPU BENCHMARK - EXTREME STRESS")
    print("=" * 55, flush=True)

    try:
        import pygame
    except ImportError:
        print("  pygame not available", flush=True)
        return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

    return _run_extreme_benchmark(pygame, duration)


def _rotate_point(x, y, z, ax, ay, az):
    cx = math.cos(ax)
    sx = math.sin(ax)
    cy = math.cos(ay)
    sy = math.sin(ay)
    cz = math.cos(az)
    sz = math.sin(az)
    y1 = y * cx - z * sx
    z1 = y * sx + z * cx
    x1 = x * cy + z1 * sy
    z2 = -x * sy + z1 * cy
    x2 = x1 * cz - y1 * sz
    y2 = x1 * sz + y1 * cz
    return x2, y2, z2


def _project(x, y, z, w, h, fov=500):
    if z <= 0.1:
        z = 0.1
    scale = fov / z
    return int(w / 2 + x * scale), int(h / 2 + y * scale), z


def _generate_ico_sphere(subdivisions=3):
    t = (1 + math.sqrt(5)) / 2
    vertices = [
        (-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
        (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
        (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)
    ]
    faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
    ]

    def normalize(v):
        l = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
        return (v[0] / l, v[1] / l, v[2] / l)

    def midpoint(a, b):
        return normalize(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2))

    for _ in range(subdivisions):
        new_faces = []
        mid_cache = {}
        for i, j, k in faces:
            a = midpoint(vertices[i], vertices[j])
            b = midpoint(vertices[j], vertices[k])
            c = midpoint(vertices[k], vertices[i])

            def get_idx(p):
                key = (round(p[0], 6), round(p[1], 6), round(p[2], 6))
                if key not in mid_cache:
                    mid_cache[key] = len(vertices)
                    vertices.append(p)
                return mid_cache[key]

            ai, bi, ci = get_idx(a), get_idx(b), get_idx(c)
            new_faces.extend([
                (i, ai, ci), (j, bi, ai), (k, ci, bi), (ai, bi, ci)
            ])
        faces = new_faces

    return vertices, faces


def _run_extreme_benchmark(pygame, duration=20):
    pygame.init()
    W, H = 1280, 720
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Ngga Tutu GPU EXTREME STRESS")

    sphere_v, sphere_f = _generate_ico_sphere(3)
    print(f"  Mesh: {len(sphere_v)} vertices, {len(sphere_f)} faces", flush=True)

    particles = []
    for _ in range(5000):
        angle_r = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.5, 4)
        particles.append({
            "x": math.cos(angle_r) * dist,
            "y": random.uniform(-2, 2),
            "z": math.sin(angle_r) * dist,
            "vx": random.uniform(-0.03, 0.03),
            "vy": random.uniform(-0.03, 0.03),
            "vz": random.uniform(-0.03, 0.03),
            "size": random.uniform(1.5, 5),
            "color": (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            ),
            "life": random.uniform(0.5, 1.0),
        })

    fps_list = []
    frame_count = 0
    start = time.perf_counter()
    last_time = start
    angle = 0

    print(f"  Rendering {duration}s at {W}x{H}...", flush=True)
    print(f"  {len(sphere_f)} faces x 8 objects + 5000 particles + lighting", flush=True)

    while time.perf_counter() - start < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

        screen.fill((2, 2, 8))

        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        cos_b = math.cos(math.radians(angle * 0.4))
        sin_b = math.sin(math.radians(angle * 0.4))

        frame_tris = 0

        light_x = math.sin(math.radians(angle * 0.5)) * 0.5
        light_y = 0.7
        light_z = math.cos(math.radians(angle * 0.5)) * 0.5
        light_len = math.sqrt(light_x ** 2 + light_y ** 2 + light_z ** 2)
        light_x /= light_len
        light_y /= light_len
        light_z /= light_len

        cx, cy = W // 2, H // 2

        for obj_idx in range(8):
            orb_radius = 2.0
            orb_x = orb_radius * math.cos(math.radians(angle * 0.15 + obj_idx * 45))
            orb_y = orb_radius * math.sin(math.radians(angle * 0.2 + obj_idx * 30))
            orb_z = 3 + 2 * math.sin(math.radians(angle * 0.1 + obj_idx * 60))

            obj_scale = 80 + 20 * math.sin(angle * 0.03 + obj_idx)
            base_r = int(127 + 127 * math.sin(obj_idx * 1.1))
            base_g = int(127 + 127 * math.sin(obj_idx * 1.1 + 2.1))
            base_b = int(127 + 127 * math.sin(obj_idx * 1.1 + 4.2))

            rotated = []
            normals = []
            for vx, vy, vz in sphere_v:
                rx, ry, rz = _rotate_point(vx, vy, vz,
                    math.radians(angle * 0.5),
                    math.radians(angle * 0.3 + obj_idx * 45),
                    math.radians(angle * 0.2))
                px, py, pz = _project(rx * obj_scale + orb_x * 100, ry * obj_scale + orb_y * 100, rz + orb_z * 100, W, H)
                rotated.append((px, py, pz))
                normals.append((rx, ry, rz))

            for face in sphere_f:
                pts = [rotated[i] for i in face]
                ns = [normals[i] for i in face]

                avg_z = sum(p[2] for p in pts) / 3
                if avg_z < 1:
                    continue

                nx = sum(n[0] for n in ns) / 3
                ny = sum(n[1] for n in ns) / 3
                nz = sum(n[2] for n in ns) / 3
                nl = math.sqrt(nx * nx + ny * ny + nz * nz)
                if nl > 0:
                    nx /= nl
                    ny /= nl
                    nz /= nl

                dot = max(0, nx * light_x + ny * light_y + nz * light_z)
                ambient = 0.15
                diffuse = dot * 0.7
                specular = 0
                if dot > 0:
                    rz2 = 2 * dot * nz - light_z
                    specular = max(0, rz2) ** 16 * 0.5

                intensity = ambient + diffuse + specular
                fr = max(0, min(255, int(base_r * intensity)))
                fg = max(0, min(255, int(base_g * intensity)))
                fb = max(0, min(255, int(base_b * intensity)))

                try:
                    pygame.draw.polygon(screen, (fr, fg, fb), [(p[0], p[1]) for p in pts])
                    pygame.draw.polygon(screen, (fr // 3, fg // 3, fb // 3), [(p[0], p[1]) for p in pts], 1)
                except Exception:
                    pass
                frame_tris += 1

        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["z"] += p["vz"]
            dist = math.sqrt(p["x"] ** 2 + p["y"] ** 2 + p["z"] ** 2)
            if dist > 4:
                p["vx"] -= p["x"] * 0.001
                p["vy"] -= p["y"] * 0.001
                p["vz"] -= p["z"] * 0.001
            px, py, pz = _project(p["x"] * 100, p["y"] * 100, p["z"] * 100 + 200, W, H)
            if 0 <= px < W and 0 <= py < H:
                brightness = max(0.2, min(1.0, pz / 400))
                cr = max(0, min(255, int(p["color"][0] * brightness * p["life"])))
                cg = max(0, min(255, int(p["color"][1] * brightness * p["life"])))
                cb = max(0, min(255, int(p["color"][2] * brightness * p["life"])))
                r_size = max(1, int(p["size"] * brightness))
                pygame.draw.circle(screen, (cr, cg, cb), (px, py), r_size)

        for ring in range(3):
            ring_radius = 150 + ring * 80
            ring_points = 60
            ring_color = (
                int(50 + 30 * math.sin(angle * 0.02 + ring)),
                int(80 + 40 * math.cos(angle * 0.02 + ring)),
                int(120 + 50 * math.sin(angle * 0.03 + ring))
            )
            for i in range(ring_points):
                a1 = math.radians(angle * (0.3 + ring * 0.1) + i * (360 / ring_points))
                a2 = math.radians(angle * (0.3 + ring * 0.1) + (i + 1) * (360 / ring_points))
                x1 = cx + int(ring_radius * math.cos(a1))
                y1 = cy + int(ring_radius * math.sin(a1) * 0.4)
                x2 = cx + int(ring_radius * math.cos(a2))
                y2 = cy + int(ring_radius * math.sin(a2) * 0.4)
                pygame.draw.line(screen, ring_color, (x1, y1), (x2, y2), 2)

        for i in range(200):
            sx = random.randint(0, W - 1)
            sy = random.randint(0, H - 1)
            screen.set_at((sx, sy), (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255)))

        for line_y in range(0, H, 3):
            alpha = int(15 + 10 * math.sin(angle * 0.1 + line_y * 0.05))
            pygame.draw.line(screen, (alpha, alpha, alpha + 10), (0, line_y), (W, line_y))

        now = time.perf_counter()
        if now - last_time > 0:
            fps_list.append(1.0 / (now - last_time))
        last_time = now

        font = pygame.font.SysFont("consolas", 18, bold=True)
        fps_val = fps_list[-1] if fps_list else 0

        hud = [
            f"FPS: {fps_val:.1f}",
            f"Frame: {frame_count}",
            f"Triangles: {frame_tris}",
            f"Objects: 8 spheres + 5000 particles",
            f"Resolution: {W}x{H}",
            f"Elapsed: {time.perf_counter() - start:.1f}s / {duration}s",
        ]

        y = 8
        for txt in hud:
            surf = font.render(txt, True, (0, 255, 0))
            bg = pygame.Surface((surf.get_width() + 6, surf.get_height() + 2))
            bg.fill((0, 0, 0))
            bg.set_alpha(180)
            screen.blit(bg, (6, y - 1))
            screen.blit(surf, (10, y))
            y += 22

        pygame.display.flip()
        frame_count += 1
        angle += 1.2

    pygame.quit()

    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0
    min_fps = min(fps_list) if fps_list else 0
    max_fps = max(fps_list) if fps_list else 0
    total_tris = frame_tris
    score = avg_fps * 3 + total_tris / max(frame_count, 1) * 0.1

    print(f"  Average FPS:     {avg_fps:.1f}", flush=True)
    print(f"  Min FPS:         {min_fps:.1f}", flush=True)
    print(f"  Max FPS:         {max_fps:.1f}", flush=True)
    print(f"  Total Frames:    {frame_count}", flush=True)
    print(f"  Total Triangles: {total_tris}", flush=True)
    print(f"  Triangles/Frame: {total_tris // max(frame_count, 1)}", flush=True)
    print("\n" + "-" * 55)
    print(f"  GPU SCORE: {score:.0f}")
    print("-" * 55, flush=True)

    return {
        "avg_fps": avg_fps,
        "min_fps": min_fps,
        "max_fps": max_fps,
        "frames": frame_count,
        "total_triangles": total_tris,
        "score": score,
    }
