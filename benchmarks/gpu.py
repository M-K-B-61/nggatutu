import time
import math
import os
import random


def run_gpu_benchmark(duration=25):
    """Heavy 3D rendering benchmark using pygame."""
    print("\n" + "=" * 55)
    print("  GPU BENCHMARK - MAXIMUM STRESS")
    print("=" * 55, flush=True)

    try:
        import pygame
    except ImportError:
        print("  pygame not available", flush=True)
        return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

    return _run_max_benchmark(pygame, duration)


def _rotate_point(x, y, z, ax, ay, az):
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)
    y1 = y * cx - z * sx
    z1 = y * sx + z * cx
    x1 = x * cy + z1 * sy
    z2 = -x * sy + z1 * cy
    x2 = x1 * cz - y1 * sz
    y2 = x1 * sz + y1 * cz
    return x2, y2, z2


def _project(x, y, z, w, h, fov=600):
    if z <= 0.1:
        z = 0.1
    scale = fov / z
    return int(w / 2 + x * scale), int(h / 2 + y * scale), z


def _generate_ico_sphere(subdivisions=4):
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
        return (v[0] / l, v[1] / l, v[2] / l) if l > 0 else (0, 0, 0)

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
            new_faces.extend([(i, ai, ci), (j, bi, ai), (k, ci, bi), (ai, bi, ci)])
        faces = new_faces
    return vertices, faces


def _generate_torus(R=1.0, r=0.3, segments=20, tubes=12):
    vertices = []
    faces = []
    for i in range(segments):
        theta = 2 * math.pi * i / segments
        for j in range(tubes):
            phi = 2 * math.pi * j / tubes
            x = (R + r * math.cos(phi)) * math.cos(theta)
            y = (R + r * math.cos(phi)) * math.sin(theta)
            z = r * math.sin(phi)
            vertices.append((x, y, z))
    for i in range(segments):
        for j in range(tubes):
            a = i * tubes + j
            b = i * tubes + (j + 1) % tubes
            c = ((i + 1) % segments) * tubes + (j + 1) % tubes
            d = ((i + 1) % segments) * tubes + j
            faces.append((a, b, c, d))
    return vertices, faces


def _run_max_benchmark(pygame, duration=25):
    pygame.init()
    W, H = 1920, 1080
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Ngga Tutu GPU MAXIMUM STRESS")

    sphere_v, sphere_f = _generate_ico_sphere(4)
    torus_v, torus_f = _generate_torus(1.0, 0.35, 24, 16)
    print(f"  Sphere: {len(sphere_v)}v {len(sphere_f)}f | Torus: {len(torus_v)}v {len(torus_f)}f", flush=True)

    particles = []
    for _ in range(10000):
        angle_r = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.3, 5)
        particles.append({
            "x": math.cos(angle_r) * dist,
            "y": random.uniform(-3, 3),
            "z": math.sin(angle_r) * dist,
            "vx": random.uniform(-0.04, 0.04),
            "vy": random.uniform(-0.04, 0.04),
            "vz": random.uniform(-0.04, 0.04),
            "size": random.uniform(1, 4),
            "color": (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255)),
        })

    fps_list = []
    frame_times = []
    frame_count = 0
    start = time.perf_counter()
    last_time = start
    angle = 0

    print(f"  Rendering {duration}s at {W}x{H}...", flush=True)
    print(f"  15 objects + 10000 particles + dual lights + shadows", flush=True)

    while time.perf_counter() - start < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return {"avg_fps": 0, "min_fps": 0, "max_fps": 0, "frames": 0, "score": 0}

        screen.fill((2, 2, 5))

        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))
        cos_b = math.cos(math.radians(angle * 0.35))
        sin_b = math.sin(math.radians(angle * 0.35))

        frame_tris = 0

        light1_x = math.sin(math.radians(angle * 0.4)) * 0.6
        light1_y = 0.6
        light1_z = math.cos(math.radians(angle * 0.4)) * 0.6
        l1_len = math.sqrt(light1_x ** 2 + light1_y ** 2 + light1_z ** 2)
        light1_x /= l1_len
        light1_y /= l1_len
        light1_z /= l1_len

        light2_x = math.cos(math.radians(angle * 0.3)) * 0.5
        light2_y = -0.4
        light2_z = math.sin(math.radians(angle * 0.3)) * 0.5
        l2_len = math.sqrt(light2_x ** 2 + light2_y ** 2 + light2_z ** 2)
        light2_x /= l2_len
        light2_y /= l2_len
        light2_z /= l2_len

        cx, cy = W // 2, H // 2

        objects = []
        for i in range(12):
            orb_r = 2.5
            objects.append({
                "type": "sphere",
                "ox": orb_r * math.cos(math.radians(angle * 0.12 + i * 30)),
                "oy": orb_r * math.sin(math.radians(angle * 0.15 + i * 25)),
                "oz": 4 + 2 * math.sin(math.radians(angle * 0.08 + i * 50)),
                "scale": 70 + 25 * math.sin(angle * 0.025 + i),
                "r": int(100 + 155 * math.sin(i * 1.3)),
                "g": int(100 + 155 * math.sin(i * 1.3 + 2.2)),
                "b": int(100 + 155 * math.sin(i * 1.3 + 4.4)),
                "rot_speed": 0.4 + i * 0.05,
            })

        for i in range(3):
            objects.append({
                "type": "torus",
                "ox": 3.0 * math.cos(math.radians(angle * 0.1 + i * 120)),
                "oy": 1.5 * math.sin(math.radians(angle * 0.08 + i * 120)),
                "oz": 5 + math.sin(math.radians(angle * 0.06 + i * 60)),
                "scale": 40 + 10 * math.sin(angle * 0.03 + i),
                "r": int(200 + 55 * math.sin(i * 2)),
                "g": int(150 + 100 * math.cos(i * 2)),
                "b": int(100 + 100 * math.sin(i * 2 + 1)),
                "rot_speed": 0.3 + i * 0.1,
            })

        for obj in objects:
            vertices_src = sphere_v if obj["type"] == "sphere" else torus_v
            faces_src = sphere_f if obj["type"] == "sphere" else torus_f
            obj_scale = obj["scale"]

            rotated = []
            normals = []
            for vx, vy, vz in vertices_src:
                rx, ry, rz = _rotate_point(vx, vy, vz,
                    math.radians(angle * obj["rot_speed"]),
                    math.radians(angle * obj["rot_speed"] * 0.7),
                    math.radians(angle * obj["rot_speed"] * 0.3))
                px, py, pz = _project(rx * obj_scale + obj["ox"] * 100, ry * obj_scale + obj["oy"] * 100, rz + obj["oz"] * 100, W, H)
                rotated.append((px, py, pz))
                normals.append((rx, ry, rz))

            for face in faces_src:
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

                d1 = max(0, nx * light1_x + ny * light1_y + nz * light1_z)
                d2 = max(0, nx * light2_x + ny * light2_y + nz * light2_z)

                specular1 = 0
                if d1 > 0:
                    rz1 = 2 * d1 * nz - light1_z
                    specular1 = max(0, rz1) ** 20 * 0.4

                specular2 = 0
                if d2 > 0:
                    rz2 = 2 * d2 * nz - light2_z
                    specular2 = max(0, rz2) ** 20 * 0.3

                intensity = 0.1 + d1 * 0.5 + d2 * 0.3 + specular1 + specular2
                fr = max(0, min(255, int(obj["r"] * intensity)))
                fg = max(0, min(255, int(obj["g"] * intensity)))
                fb = max(0, min(255, int(obj["b"] * intensity)))

                try:
                    pygame.draw.polygon(screen, (fr, fg, fb), [(p[0], p[1]) for p in pts])
                    pygame.draw.polygon(screen, (fr // 4, fg // 4, fb // 4), [(p[0], p[1]) for p in pts], 1)
                except Exception:
                    pass
                frame_tris += 1

        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["z"] += p["vz"]
            dist = math.sqrt(p["x"] ** 2 + p["y"] ** 2 + p["z"] ** 2)
            if dist > 5:
                p["vx"] -= p["x"] * 0.002
                p["vy"] -= p["y"] * 0.002
                p["vz"] -= p["z"] * 0.002
            px, py, pz = _project(p["x"] * 100, p["y"] * 100, p["z"] * 100 + 250, W, H)
            if 0 <= px < W and 0 <= py < H:
                brightness = max(0.15, min(1.0, pz / 500))
                cr = max(0, min(255, int(p["color"][0] * brightness)))
                cg = max(0, min(255, int(p["color"][1] * brightness)))
                cb = max(0, min(255, int(p["color"][2] * brightness)))
                r_size = max(1, int(p["size"] * brightness))
                pygame.draw.circle(screen, (cr, cg, cb), (px, py), r_size)

        for ring in range(5):
            ring_r = 120 + ring * 70
            ring_pts = 80
            ring_color = (
                int(40 + 30 * math.sin(angle * 0.015 + ring)),
                int(60 + 40 * math.cos(angle * 0.015 + ring)),
                int(100 + 50 * math.sin(angle * 0.02 + ring))
            )
            for i in range(ring_pts):
                a1 = math.radians(angle * (0.2 + ring * 0.08) + i * (360 / ring_pts))
                a2 = math.radians(angle * (0.2 + ring * 0.08) + (i + 1) * (360 / ring_pts))
                x1 = cx + int(ring_r * math.cos(a1))
                y1 = cy + int(ring_r * math.sin(a1) * 0.35)
                x2 = cx + int(ring_r * math.cos(a2))
                y2 = cy + int(ring_r * math.sin(a2) * 0.35)
                pygame.draw.line(screen, ring_color, (x1, y1), (x2, y2), 2)

        for i in range(500):
            sx = random.randint(0, W - 1)
            sy = random.randint(0, H - 1)
            screen.set_at((sx, sy), (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

        for line_y in range(0, H, 2):
            alpha = int(12 + 8 * math.sin(angle * 0.08 + line_y * 0.04))
            pygame.draw.line(screen, (alpha, alpha, alpha + 8), (0, line_y), (W, line_y))

        now = time.perf_counter()
        if now - last_time > 0:
            fps_list.append(1.0 / (now - last_time))
            frame_times.append(now - last_time)
        last_time = now

        font = pygame.font.SysFont("consolas", 18, bold=True)
        fps_val = fps_list[-1] if fps_list else 0

        hud = [
            f"FPS: {fps_val:.1f}  |  Frame: {frame_count}",
            f"Triangles: {frame_tris}  |  Objects: 15 + 10000 particles",
            f"Resolution: {W}x{H}  |  Dual lighting + specular",
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
        angle += 1.0

    pygame.quit()

    avg_fps = sum(fps_list) / len(fps_list) if fps_list else 0
    min_fps = min(fps_list) if fps_list else 0
    max_fps = max(fps_list) if fps_list else 0

    # 1% low and 0.1% low
    sorted_ft = sorted(frame_times)
    n = len(sorted_ft)
    one_pct_count = max(1, n // 100)
    zero_pct_count = max(1, n // 1000)
    one_pct_low_ft = sorted_ft[-one_pct_count] if sorted_ft else 0
    zero_pct_low_ft = sorted_ft[-zero_pct_count] if sorted_ft else 0
    one_percent_low = 1.0 / one_pct_low_ft if one_pct_low_ft > 0 else 0
    zero_point_one_percent_low = 1.0 / zero_pct_low_ft if zero_pct_low_ft > 0 else 0

    score = avg_fps * 2 + frame_tris / max(frame_count, 1) * 0.05

    print(f"\n  Average FPS:              {avg_fps:.1f}", flush=True)
    print(f"  Min FPS:                  {min_fps:.1f}", flush=True)
    print(f"  Max FPS:                  {max_fps:.1f}", flush=True)
    print(f"  1% Low:                   {one_percent_low:.1f} FPS", flush=True)
    print(f"  0.1% Low:                 {zero_point_one_percent_low:.1f} FPS", flush=True)
    print(f"  Frame Time (avg):         {1000/avg_fps:.1f} ms" if avg_fps > 0 else "  Frame Time: N/A", flush=True)
    print(f"  Total Frames:             {frame_count}", flush=True)
    print(f"  Total Triangles:          {frame_tris}", flush=True)
    print(f"  Triangles/Frame:          {frame_tris // max(frame_count, 1)}", flush=True)
    print("\n" + "-" * 60)
    print(f"  GPU SCORE: {score:.0f}")
    print("-" * 60, flush=True)

    return {
        "avg_fps": avg_fps,
        "min_fps": min_fps,
        "max_fps": max_fps,
        "one_percent_low": one_percent_low,
        "zero_point_one_percent_low": zero_point_one_percent_low,
        "frame_times": frame_times,
        "frames": frame_count,
        "total_triangles": frame_tris,
        "score": score,
    }
