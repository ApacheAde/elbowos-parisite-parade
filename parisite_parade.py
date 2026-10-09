#!/usr/bin/env python3
"""Parisite Parade — full-colour Python 3 neon lane-float arcade for ElbowOS.

Steer a baton across three parade lanes. Catch rose, lime, cyan and gold
lanterns as the floats rush the camera. Dodge sour drums.
A/D or arrows change lane. Space is a flourish (no effect on score).
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/PARISITE_PARADE_ElbowOS.mp4")
TITLE, HANDLE = "PARISITE PARADE", "x.com/ElbowOS"
LANES = (250, 540, 830)
GOOD = ((255, 72, 156), (150, 255, 90), (70, 236, 255), (255, 214, 72))
DRUM = (255, 64, 72)
INK = (14, 4, 28)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("dejavusans", 64, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.lane = 1
        self.score = 0
        self.combo = 0
        self.t = 0
        self.floats = []
        self.confetti = []
        self.flash = 0
        self.banner = ""
        self.spawn = 0
        random.seed(11)

    def spawn_float(self):
        bad = random.random() < 0.28
        self.floats.append({
            "lane": random.randrange(3),
            "z": 0.02,
            "bad": bad,
            "col": DRUM if bad else random.choice(GOOD),
            "spin": random.random() * 6.28,
        })

    def auto(self):
        near = [f for f in self.floats if 0.42 < f["z"] < 0.92]
        near.sort(key=lambda f: -f["z"])
        if not near:
            if self.t % 40 == 0:
                self.lane = (self.lane + 1) % 3
            return
        lead = near[0]
        if lead["bad"]:
            if self.lane == lead["lane"]:
                self.lane = (lead["lane"] + 1) % 3
        else:
            self.lane = lead["lane"]

    def step(self, keys=None):
        self.t += 1
        if keys:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.t % 8 == 1:
                    self.lane = max(0, self.lane - 1)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.t % 8 == 1:
                    self.lane = min(2, self.lane + 1)
        else:
            self.auto()
        self.spawn += 1
        gap = 16 if self.t < 200 else 13
        if self.spawn >= gap:
            self.spawn = 0
            self.spawn_float()
        speed = 0.012 + min(self.t, 360) * 0.00002
        kept = []
        for f in self.floats:
            f["z"] += speed
            f["spin"] += 0.08
            if f["z"] >= 1.0:
                if f["lane"] == self.lane and not f["bad"]:
                    self.combo += 1
                    self.score += 100 + 25 * min(self.combo, 8)
                    self.flash = 8
                    self.banner = "CATCH"
                    self.burst(LANES[f["lane"]], 1460, f["col"])
                elif f["lane"] == self.lane and f["bad"]:
                    self.combo = 0
                    self.score = max(0, self.score - 80)
                    self.flash = 10
                    self.banner = "SOUR"
                else:
                    if not f["bad"]:
                        self.combo = 0
                continue
            kept.append(f)
        self.floats = kept
        if self.flash:
            self.flash -= 1
        for c in self.confetti:
            c["y"] += c["vy"]
            c["x"] += c["vx"]
            c["life"] -= 1
        self.confetti = [c for c in self.confetti if c["life"] > 0 and c["y"] < H]

    def burst(self, x, y, col):
        for _ in range(14):
            ang = random.random() * 6.28
            sp = random.uniform(2, 9)
            self.confetti.append({
                "x": x, "y": y, "vx": math.cos(ang) * sp,
                "vy": math.sin(ang) * sp - 2, "life": 28, "col": col,
            })

    def project(self, lane, z):
        vanish_y = 430
        base_y = 1580
        y = vanish_y + (base_y - vanish_y) * z
        cx = W / 2 + (LANES[lane] - W / 2) * (0.18 + 0.82 * z)
        scale = 0.22 + 0.95 * z * z
        return cx, y, scale

    def draw(self):
        s = self.screen
        for i in range(16):
            t = i / 15
            col = (int(22 + 40 * t), int(6 + 8 * t), int(40 + 30 * t))
            pygame.draw.rect(s, col, (0, int(i * H / 16), W, H // 16 + 1))
        # street wedge
        road = [(180, 1680), (900, 1680), (620, 460), (460, 460)]
        pygame.draw.polygon(s, (28, 12, 42), road)
        for i, lane in enumerate(LANES):
            a = self.project(i, 0.05)
            b = self.project(i, 1.0)
            pygame.draw.line(s, (90, 40, 110), (a[0], a[1]), (b[0], b[1]), 3)
        # lamp bunting
        for i in range(8):
            x = 80 + i * 130
            yy = 300 + int(12 * math.sin(self.t * 0.08 + i))
            pygame.draw.circle(s, GOOD[i % 4], (x, yy), 14)
            pygame.draw.line(s, (255, 180, 210), (x, yy + 14), (x, yy + 36), 3)
        for f in sorted(self.floats, key=lambda q: q["z"]):
            cx, y, sc = self.project(f["lane"], f["z"])
            bw, bh = int(150 * sc), int(110 * sc)
            body = pygame.Rect(0, 0, bw, bh)
            body.center = (cx, y)
            shade = tuple(max(0, c - 40) for c in f["col"])
            pygame.draw.rect(s, shade, body.inflate(8, 8), border_radius=18)
            pygame.draw.rect(s, f["col"], body, border_radius=16)
            if f["bad"]:
                pygame.draw.circle(s, (40, 8, 16), body.center, max(8, int(28 * sc)))
                pygame.draw.line(s, (255, 220, 220), body.topleft, body.bottomright, 4)
            else:
                pygame.draw.circle(s, (255, 255, 255), (body.centerx, body.centery - int(8 * sc)), max(6, int(16 * sc)))
        # baton
        bx = LANES[self.lane]
        by = 1500
        pygame.draw.circle(s, (255, 190, 230), (bx, by), 54)
        pygame.draw.circle(s, (255, 80, 160), (bx, by), 36)
        pygame.draw.line(s, (255, 245, 220), (bx - 70, by + 40), (bx + 70, by - 50), 10)
        pygame.draw.circle(s, (255, 230, 120), (bx + 70, by - 50), 12)
        for c in self.confetti:
            pygame.draw.circle(s, c["col"], (int(c["x"]), int(c["y"])), 5)
        # HUD
        bar = pygame.Surface((W, 220), pygame.SRCALPHA)
        bar.fill((10, 2, 20, 170))
        s.blit(bar, (0, 0))
        s.blit(self.font.render(TITLE, True, (255, 120, 190)), (48, 36))
        s.blit(self.small.render(f"SCORE {self.score}", True, (255, 236, 140)), (48, 120))
        s.blit(self.small.render(f"COMBO {self.combo}", True, (150, 255, 210)), (520, 120))
        s.blit(self.tiny.render(HANDLE, True, (190, 230, 255)), (48, 172))
        if self.banner and self.flash:
            col = (255, 90, 110) if self.banner == "SOUR" else (255, 240, 160)
            s.blit(self.font.render(self.banner, True, col), (360, 820))
        foot = pygame.Surface((W, 90), pygame.SRCALPHA)
        foot.fill((10, 2, 20, 150))
        s.blit(foot, (0, H - 90))
        s.blit(self.tiny.render("A/D lane   catch lanterns   dodge drums", True, (230, 200, 230)), (70, H - 60))

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
            "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
            "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for _ in range(frames):
                self.step()
                self.draw()
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "replace")
            code = proc.wait(timeout=60)
        except Exception as exc:
            proc.kill()
            raise SystemExit(f"encode failed: {exc}") from exc
        if code != 0:
            raise SystemExit(f"ffmpeg exit {code}\n{err[-800:]}")
        print(OUT)

    def play(self):
        clock = pygame.time.Clock()
        while True:
            keys = pygame.key.get_pressed()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    self.reset()
            self.step(keys)
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    g = Game()
    if PLAY and not RECORD:
        g.play()
    else:
        g.record()
