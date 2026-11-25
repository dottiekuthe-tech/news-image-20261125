"""make.fun bounty entry: news-image-20261125.

Sum up the world's news of Wednesday 25 November 2026 in one image.

The program draws a 1024x1024 newspaper-style front page with a pure-Python
5x7 bitmap font and a hand-written PNG encoder -- standard library only,
no network, no time, no randomness -- so two runs write identical bytes.

Run it like the grader does:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

It writes $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).

News facts are hard-coded below (the grader runs offline). Sources, all
first reported on 25 November 2026:
  * Houthi strike on Riyadh tower -- scmp.com, qatar-tribune.com
  * Cartagena supermarket hostages freed -- scmp.com, horizonapp.link
  * Pakistan's first astronaut aboard Shenzhou-24 -- timesnownews.com,
    qatar-tribune.com
  * China investigates Shanghai party chief Chen Jining -- scmp.com,
    oneturn.news, saachibaat.com
  * US soldier Jian Zhao admits selling secrets -- scmp.com
  * Bangladesh raises garment minimum wage 36% -- horizonapp.link
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows; each row is 5 bits, bit 4 is the
# leftmost pixel. Lowercase sits on the same 7-row grid (descenders use
# the bottom rows). Written out by hand for this entry.

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
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x10, 0x10, 0x11, 0x0E),
    "d": (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x08, 0x1E, 0x08, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0E, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "h": (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    "q": (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1C, 0x08, 0x08, 0x08, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x11, 0x0F),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
}

# ------------------------------------------------------------- canvas


class Canvas:
    """An RGB canvas with rectangle, circle, line, triangle and text drawing."""

    def __init__(self, width, height, bg):
        self.width = width
        self.height = height
        self._bg = bg
        self.px = bytearray(bg * (width * height))

    def _set(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i:i + 3] = colour

    def rect(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + w), min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                self.px[base + (xx - x0) * 3:base + (xx - x0) * 3 + 3] = colour

    def line(self, x0, y0, x1, y1, colour, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(-(thick // 2), thick // 2 + 1):
                for b in range(-(thick // 2), thick // 2 + 1):
                    self._set(x0 + a, y0 + b, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, colour)

    def ring(self, cx, cy, r, thick, colour):
        self.disc(cx, cy, r, colour)
        self.disc(cx, cy, r - thick, self._bg)

    def triangle(self, x0, y0, x1, y1, x2, y2, colour):
        # Scanline fill of a triangle.
        ys = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        for y in range(ay, cy + 1):
            if y < by:
                xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
            else:
                xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
            xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
            lo, hi = sorted((int(xa), int(xb)))
            self.rect(lo, y, hi - lo + 1, 1, colour)

    def text(self, x, y, s, scale, colour):
        """Draw text; returns the width in pixels."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT["?"]
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, colour)
            cx += 6 * scale
        return cx - x

    def text_width(self, s, scale):
        return len(s) * 6 * scale

    def centred(self, y, s, scale, colour):
        w = self.text_width(s, scale)
        self.text((self.width - w) // 2, y, s, scale, colour)

    def wrap(self, s, scale, max_width):
        """Greedy word wrap; returns a list of lines."""
        max_chars = max(1, max_width // (6 * scale))
        lines, cur = [], ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def write_png(canvas, path):
    """Encode the canvas as a true-colour PNG (filter 0 per scanline)."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------------- palette
PAPER = bytes((246, 241, 227))
INK = bytes((27, 27, 27))
BODY = bytes((58, 58, 52))
NAVY = bytes((20, 33, 61))
GOLD = bytes((201, 162, 39))
WHITE = bytes((255, 255, 255))
CARD = bytes((255, 255, 255))
BORDER = bytes((217, 210, 190))
MUTED = bytes((110, 104, 88))

# ------------------------------------------------------------- stories
# Six stories, across regions and fields, each first reported on
# Wednesday 25 November 2026. Headlines are pre-wrapped to two lines;
# bodies must wrap to at most four lines at scale 2 in a 436 px column.

STORIES = [
    {
        "tag": "MIDDLE EAST",
        "colour": bytes((140, 30, 30)),
        "icon": "blast",
        "head": ["HOUTHIS HIT RIYADH TOWER", "AGAIN, 11 ARE INJURED"],
        "body": "Houthi forces hit Riyadh's tallest skyscraper for "
                "the second time in a week. Saudi officials say 11 "
                "were injured.",
    },
    {
        "tag": "CRIME",
        "colour": bytes((180, 83, 9)),
        "icon": "cuffs",
        "head": ["HOSTAGES FREED AFTER", "CARTAGENA SUPERMARKET"],
        "body": "Gunmen held about 30 people in a Cartagena supermarket "
                "after a failed armoured car robbery. Troops stormed in "
                "and freed them all.",
    },
    {
        "tag": "SPACE",
        "colour": bytes((74, 20, 140)),
        "icon": "satellite",
        "head": ["PAKISTAN'S FIRST", "ASTRONAUT IN ORBIT"],
        "body": "Shenzhou-24 carried Muhammad Zeeshan Ali to China's "
                "Tiangong station, the first Pakistani and the first "
                "foreign astronaut aboard.",
    },
    {
        "tag": "POLITICS",
        "colour": bytes((21, 101, 192)),
        "icon": "lens",
        "head": ["CHINA PROBES SHANGHAI", "PARTY CHIEF CHEN"],
        "body": "Beijing put Chen Jining, Shanghai's party chief and "
                "a Politburo member, under investigation for suspected "
                "violations.",
    },
    {
        "tag": "JUSTICE",
        "colour": bytes((123, 45, 38)),
        "icon": "scales",
        "head": ["SOLDIER ADMITS SELLING", "US SECRETS TO CHINA"],
        "body": "Army Sergeant Jian Zhao admitted selling US military "
                "secrets to buyers in China, photographing files and "
                "offering to sell hard drives.",
    },
    {
        "tag": "ECONOMY",
        "colour": bytes((46, 125, 50)),
        "icon": "bars",
        "head": ["BANGLADESH LIFTS GARMENT", "WAGES BY 36 PERCENT"],
        "body": "Bangladesh raised the minimum wage for garment workers "
                "by 36 percent after weeks of protests over the rising "
                "cost of living.",
    },
]

# ------------------------------------------------------------- icons
# Each icon is drawn in white inside a coloured badge circle.


def draw_icon(c, kind, cx, cy, colour):
    if kind == "scales":
        c.line(cx, cy - 16, cx, cy + 14, WHITE, 3)
        c.line(cx - 17, cy - 12, cx + 17, cy - 12, WHITE, 3)
        c.line(cx - 17, cy - 12, cx - 17, cy - 2, WHITE, 2)
        c.line(cx + 17, cy - 12, cx + 17, cy - 2, WHITE, 2)
        c.triangle(cx - 24, cy + 2, cx - 10, cy + 2, cx - 17, cy + 12, WHITE)
        c.triangle(cx + 10, cy + 2, cx + 24, cy + 2, cx + 17, cy + 12, WHITE)
        c.disc(cx, cy - 16, 3, WHITE)
    elif kind == "blast":
        c.disc(cx, cy, 5, WHITE)
        for dx, dy in ((0, -1), (1, -1), (1, 0), (1, 1),
                       (0, 1), (-1, 1), (-1, 0), (-1, -1)):
            c.line(cx + dx * 8, cy + dy * 8, cx + dx * 17, cy + dy * 17,
                   WHITE, 3)
    elif kind == "satellite":
        c.rect(cx - 8, cy - 6, 16, 12, WHITE)
        c.rect(cx - 25, cy - 4, 13, 8, WHITE)
        c.rect(cx + 12, cy - 4, 13, 8, WHITE)
        c.line(cx + 4, cy - 6, cx + 10, cy - 15, WHITE, 2)
        c.disc(cx + 11, cy - 16, 2, WHITE)
        c.disc(cx - 22, cy - 16, 2, WHITE)
        c.disc(cx + 22, cy + 14, 2, WHITE)
    elif kind == "lens":
        c.ring(cx - 3, cy - 3, 12, 3, WHITE)
        c.line(cx + 6, cy + 6, cx + 16, cy + 16, WHITE, 3)
    elif kind == "cuffs":
        c.ring(cx - 11, cy, 10, 4, WHITE)
        c.ring(cx + 11, cy, 10, 4, WHITE)
        c.line(cx - 11, cy - 10, cx + 11, cy - 10, WHITE, 3)
    elif kind == "bars":
        c.rect(cx - 17, cy + 4, 8, 11, WHITE)
        c.rect(cx - 4, cy - 4, 8, 19, WHITE)
        c.rect(cx + 9, cy - 13, 8, 28, WHITE)


# ------------------------------------------------------------- layout


def draw_card(c, x, y, story):
    w, h = 476, 244
    colour = story["colour"]
    c.rect(x, y, w, h, CARD)
    c.rect(x, y, w, 6, colour)
    # Border.
    c.rect(x, y, w, 2, BORDER)
    c.rect(x, y + h - 2, w, 2, BORDER)
    c.rect(x, y, 2, h, BORDER)
    c.rect(x + w - 2, y, 2, h, BORDER)
    # Icon badge.
    bx, by = x + 54, y + 50
    c.disc(bx, by, 34, colour)
    draw_icon(c, story["icon"], bx, by, colour)
    # Category tag.
    c.text(x + 102, y + 42, story["tag"], 2, colour)
    # Headline, two lines at scale 3.
    hy = y + 100
    for i, line in enumerate(story["head"]):
        c.text(x + 20, hy + i * 26, line, 3, INK)
    # Divider.
    c.rect(x + 20, y + 160, w - 40, 2, BORDER)
    # Body, wrapped at scale 2 (436 px column, at most 4 lines).
    lines = c.wrap(story["body"], 2, w - 40)
    for i, line in enumerate(lines[:4]):
        c.text(x + 20, y + 172 + i * 17, line, 2, BODY)


def draw():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    c._bg = PAPER
    # Header band.
    c.rect(0, 0, WIDTH, 150, NAVY)
    c.centred(24, "THE WORLD IN ONE DAY", 4, WHITE)
    c.centred(66, "WEDNESDAY, 25 NOVEMBER 2026", 3, GOLD)
    c.centred(104, "SIX STORIES THAT DEFINED THE DAY", 2, WHITE)
    c.rect(24, 140, WIDTH - 48, 2, GOLD)
    # Section label row.
    c.text(24, 160, "TOP STORIES", 2, INK)
    right = "ALL EVENTS REPORTED 25 NOVEMBER 2026"
    c.text(WIDTH - 24 - c.text_width(right, 2), 160, right, 2, MUTED)
    # Story grid: 2 columns x 3 rows.
    for i, story in enumerate(STORIES):
        x = 24 + (i % 2) * 500
        y = 190 + (i // 2) * 252
        draw_card(c, x, y, story)
    # Footer.
    foot = "SOURCES: SCMP | HORIZON | TIMES NOW | ONETURN - ALL EVENTS REPORTED 25 NOV 2026"
    c.text((WIDTH - c.text_width(foot, 2)) // 2, 962, foot, 2, MUTED)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = draw()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(canvas, path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
