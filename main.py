#!/usr/bin/env python3
"""news-image-20261117 - Sum up Tuesday 17 November 2026 world news in one image.

Pure Python 3.13 standard library (zlib + struct only). Draws a 1024x1024
front-page style image with the day's six top stories, each with a kicker,
a big headline, a short subhead and a small drawn scene. Deterministic:
fixed constants, no clock, no randomness, no network. Writes
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Stories (as reported on 17 November 2026):
 1. Ukraine strike collapses a road span of the Kerch Bridge to Crimea;
    Russian missiles hit two bridges over the Dnipro in Kyiv.
 2. Two oil tankers hit mines near the Strait of Hormuz; a third US
    aircraft carrier, USS Theodore Roosevelt, arrives in the Middle East.
 3. Trump arrives in Manila for the ASEAN summit; Xi, Trump and Putin
    are set to meet on Thursday in Shenzhen on the APEC sidelines.
 4. Five EU states (Germany, Denmark, Austria, Greece, Netherlands)
    announce a joint migrant return hub in Rwanda.
 5. A ULA Vulcan rocket fails in flight, destroying 40 Amazon Leo
    internet satellites.
 6. JPMorgan Chase blames a software bug, not a cyberattack, for
    Monday's banking outage (online banking, branches, Zelle).
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 232)
INK = (17, 17, 17)
WHITE = (255, 255, 255)
RED = (180, 35, 24)
BAND = (241, 237, 226)
GREY = (120, 116, 104)

# 5x7 pixel font: each glyph is 7 rows, low 5 bits, bit 4 = leftmost pixel.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
}


class Canvas:
    """A plain RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - t) * (r - t) <= d <= r * r:
                    self.set(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                    (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or yy == ymax and yy == max(ay, by):
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)


def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, c):
    """Draw uppercase text; unknown chars render as blank."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_c(cv, x, y, w, s, scale, c):
    draw_text(cv, x + (w - text_w(s, scale)) // 2, y, s, scale, c)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines = []
    for word in s.split(" "):
        if not lines:
            lines.append(word)
            continue
        trial = lines[-1] + " " + word
        if text_w(trial, scale) <= max_w:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


# ---------------------------------------------------------------- scenes
# Each scene draws inside a 452 x 70 band at (bx, by).

def starburst(cv, cx, cy, r, c):
    for k in range(12):
        ang = k * 30
        # 12 spikes: alternate long and short, drawn as lines.
        import math
        rr = r if k % 2 == 0 else r // 2
        x1 = cx + int(rr * math.cos(math.radians(ang)))
        y1 = cy + int(rr * math.sin(math.radians(ang)))
        cv.line(cx, cy, x1, y1, c, 3)
    cv.disc(cx, cy, r // 3, c)


def scene_bridge(cv, bx, by, accent):
    # Sea, a bridge deck with a collapsed gap, two towers, a falling span.
    cv.rect(bx, by + 52, 452, 18, (64, 120, 160))
    cv.rect(bx, by, 452, 52, (232, 236, 240))
    cv.hline(bx, by + 30, 452, INK, 5)
    cv.hline(bx, by + 14, 452, INK, 2)
    cv.rect(bx + 60, by + 4, 10, 48, INK)
    cv.rect(bx + 380, by + 4, 10, 48, INK)
    cv.line(bx + 65, by + 4, bx + 130, by + 30, INK, 2)
    cv.line(bx + 385, by + 4, bx + 320, by + 30, INK, 2)
    # The gap: deck missing between x 200 and 250.
    cv.rect(bx + 200, by + 30, 50, 5, (232, 236, 240))
    # Falling span, tilted into the sea.
    cv.line(bx + 205, by + 32, bx + 245, by + 52, accent, 6)
    starburst(cv, bx + 225, by + 22, 16, (226, 88, 34))
    cv.disc(bx + 225, by + 22, 5, RED)


def scene_tanker(cv, bx, by, accent):
    # A tanker on waves, a spiked mine, fire on the water.
    cv.rect(bx, by + 48, 452, 22, (44, 110, 150))
    cv.hline(bx, by + 48, 452, WHITE, 2)
    cv.hline(bx, by + 58, 452, WHITE, 2)
    # Hull and containers.
    cv.rect(bx + 60, by + 38, 220, 8, accent)
    cv.tri(bx + 280, by + 38, bx + 300, by + 38, bx + 280, by + 46, accent)
    cv.rect(bx + 60, by + 46, 240, 6, INK)
    cv.rect(bx + 90, by + 14, 34, 24, (200, 60, 40))
    cv.rect(bx + 130, by + 14, 34, 24, (40, 90, 160))
    cv.rect(bx + 170, by + 14, 34, 24, (220, 170, 40))
    cv.rect(bx + 300, by + 8, 10, 38, INK)
    # Mine with spikes, fire beside the hull.
    starburst(cv, bx + 360, by + 40, 14, INK)
    cv.disc(bx + 360, by + 40, 7, INK)
    starburst(cv, bx + 330, by + 30, 12, (226, 88, 34))
    cv.disc(bx + 330, by + 30, 4, RED)


def scene_summit(cv, bx, by, accent):
    # Three flag poles and a globe: a three-way summit.
    cv.disc(bx + 380, by + 35, 26, (64, 120, 160))
    cv.line(bx + 362, by + 18, bx + 398, by + 52, WHITE, 2)
    cv.line(bx + 362, by + 52, bx + 398, by + 18, WHITE, 2)
    for i, cols in enumerate((((200, 60, 40), (255, 255, 255), (40, 60, 160)),
                             ((220, 30, 30), (255, 210, 0), (220, 30, 30)),
                             ((255, 255, 255), (40, 60, 160), (200, 30, 30)))):
        fx = bx + 40 + i * 90
        cv.vline(fx, by + 4, 62, INK, 3)
        for j, col in enumerate(cols):
            cv.rect(fx + 3, by + 6 + j * 10, 56, 10, col)
        cv.frame(fx + 3, by + 6, 56, 30, INK, 1)


def scene_hub(cv, bx, by, accent):
    # A ring of stars, an arrow, and a map pin: a return hub.
    for k in range(8):
        import math
        ang = math.radians(k * 45 - 90)
        sx = bx + 60 + int(30 * math.cos(ang))
        sy = by + 35 + int(30 * math.sin(ang))
        cv.disc(sx, sy, 4, (40, 60, 160))
    cv.disc(bx + 60, by + 35, 8, accent)
    cv.line(bx + 110, by + 35, bx + 250, by + 35, INK, 4)
    cv.tri(bx + 250, by + 35, bx + 228, by + 24, bx + 228, by + 46, INK)
    # Map pin.
    cv.disc(bx + 330, by + 28, 16, RED)
    cv.tri(bx + 314, by + 34, bx + 346, by + 34, bx + 330, by + 62, RED)
    cv.disc(bx + 330, by + 28, 6, WHITE)
    cv.hline(bx + 300, by + 64, 90, INK, 2)


def scene_rocket(cv, bx, by, accent):
    # A rocket climbing on a dashed trail, with falling debris dots.
    cv.rect(bx, by, 452, 70, (24, 32, 54))
    for i in range(9):
        yy = by + 8 + i * 7
        cv.rect(bx + 20, yy, 6, 3, GREY)
    cv.tri(bx + 210, by + 6, bx + 196, by + 30, bx + 224, by + 30, WHITE)
    cv.rect(bx + 196, by + 30, 28, 22, (226, 88, 34))
    cv.rect(bx + 188, by + 44, 8, 14, RED)
    cv.rect(bx + 224, by + 44, 8, 14, RED)
    cv.tri(bx + 204, by + 52, bx + 210, by + 52, bx + 207, by + 66, (255, 210, 0))
    cv.tri(bx + 196, by + 52, bx + 202, by + 52, bx + 199, by + 62, (255, 210, 0))
    cv.tri(bx + 218, by + 52, bx + 224, by + 52, bx + 221, by + 62, (255, 210, 0))
    for (dx, dy) in ((300, 12), (330, 30), (290, 44), (350, 52), (315, 60), (370, 20)):
        cv.disc(bx + dx, by + dy, 3, WHITE)
    draw_text(cv, bx + 396, by + 26, "40", 2, WHITE)


def scene_bank(cv, bx, by, accent):
    # A bank building with columns, cracked by a lightning bolt.
    cv.tri(bx + 140, by + 6, bx + 60, by + 26, bx + 220, by + 26, accent)
    cv.rect(bx + 64, by + 26, 152, 4, INK)
    for i in range(4):
        cv.rect(bx + 74 + i * 38, by + 30, 12, 30, INK)
    cv.rect(bx + 64, by + 60, 152, 6, INK)
    # Lightning bolt crack across the facade.
    cv.line(bx + 300, by + 6, bx + 330, by + 26, (255, 210, 0), 5)
    cv.line(bx + 330, by + 26, bx + 306, by + 26, (255, 210, 0), 5)
    cv.line(bx + 306, by + 26, bx + 336, by + 52, (255, 210, 0), 5)
    cv.line(bx + 336, by + 52, bx + 316, by + 52, (255, 210, 0), 5)
    cv.line(bx + 316, by + 52, bx + 344, by + 68, (255, 210, 0), 5)
    draw_text(cv, bx + 380, by + 26, "BUG", 3, RED)


STORIES = [
    {"kicker": "EUROPE - CONFLICT", "color": (29, 78, 137),
     "head": ["KERCH BRIDGE", "SPAN FALLS"],
     "sub": "UKRAINE STRIKE COLLAPSES A ROAD SPAN; RUSSIA HITS TWO BRIDGES IN KYIV.",
     "scene": scene_bridge},
    {"kicker": "MIDDLE EAST - ENERGY", "color": (14, 124, 107),
     "head": ["TANKERS MINED", "AT HORMUZ"],
     "sub": "TWO TANKERS HIT MINES IN THE STRAIT; A THIRD US CARRIER ARRIVES.",
     "scene": scene_tanker},
    {"kicker": "ASIA - DIPLOMACY", "color": (158, 43, 37),
     "head": ["TRUMP IN MANILA", "SUMMIT THURSDAY"],
     "sub": "ASEAN SUMMIT OPENS; XI, TRUMP AND PUTIN TO MEET THURSDAY IN SHENZHEN.",
     "scene": scene_summit},
    {"kicker": "EUROPE - MIGRATION", "color": (91, 74, 138),
     "head": ["EU-RWANDA", "RETURN HUB"],
     "sub": "FIVE EU STATES PLAN A JOINT HUB FOR REJECTED ASYLUM SEEKERS.",
     "scene": scene_hub},
    {"kicker": "SPACE - TECHNOLOGY", "color": (192, 86, 33),
     "head": ["VULCAN ROCKET", "FAILS IN FLIGHT"],
     "sub": "ULA ROCKET FAILS MINUTES AFTER LAUNCH; 40 AMAZON SATELLITES LOST.",
     "scene": scene_rocket},
    {"kicker": "BUSINESS - TECH", "color": (51, 65, 85),
     "head": ["JPMORGAN", "OUTAGE: A BUG"],
     "sub": "BANKING AND ZELLE SLOWED BY A SOFTWARE BUG, NOT A CYBERATTACK.",
     "scene": scene_bank},
]


# ---------------------------------------------------------------- layout

def build():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    cv.hline(24, 16, 976, RED, 4)
    draw_text_c(cv, 0, 34, W, "THE WORLD IN ONE DAY", 6, INK)
    draw_text_c(cv, 0, 92, W, "TUESDAY 17 NOVEMBER 2026", 5, RED)
    cv.hline(24, 142, 976, RED, 4)
    # Story grid: 2 columns x 3 rows of 480 x 246 panels.
    for i, st in enumerate(STORIES):
        px = 24 + (i % 2) * (480 + 16)
        py = 170 + (i // 2) * (246 + 16)
        cv.rect(px, py, 480, 246, WHITE)
        cv.frame(px, py, 480, 246, INK, 2)
        cv.rect(px, py, 480, 34, st["color"])
        draw_text(cv, px + 14, py + 7, st["kicker"], 3, WHITE)
        draw_text(cv, px + 12, py + 44, st["head"][0], 5, INK)
        draw_text(cv, px + 12, py + 84, st["head"][1], 5, INK)
        sub = wrap(st["sub"], 456, 2)
        draw_text(cv, px + 12, py + 128, sub[0], 2, INK)
        if len(sub) > 1:
            draw_text(cv, px + 12, py + 146, sub[1], 2, INK)
        bx, by = px + 14, py + 168
        cv.rect(bx, by, 452, 70, BAND)
        cv.frame(bx, by, 452, 70, GREY, 1)
        st["scene"](cv, bx, by, st["color"])
    # Footer.
    cv.hline(24, 956, 976, INK, 2)
    draw_text_c(cv, 0, 970, W,
                "SIX STORIES FROM ONE DAY - TUESDAY 17 NOVEMBER 2026", 2, INK)
    return cv


def png_bytes(cv):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
