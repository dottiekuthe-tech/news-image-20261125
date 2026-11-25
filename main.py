"""News Image 20261125: a newspaper front page for 25 November 2026.

Draws a 1024x1024 black-and-white front page of the day's world news
with a hand-written 5x7 bitmap font and a hand-written PNG encoder.
Python 3.13 standard library only: no network, no clock, no randomness,
so two runs write byte-identical output.
"""

import os
import struct
import zlib

W = 1024
H = 1024
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# A 5x7 bitmap font, one glyph per character: 7 rows of 5 cells each,
# "#" is ink and "." is paper. Uppercase letters, digits and the
# punctuation the page needs.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "*": (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
}

# The six stories of Wednesday 25 November 2026, in my own words.
LEAD = (
    "MIDDLE EAST",
    "RIYADH TOWER HIT AGAIN",
    "Houthi forces struck the capital's tallest tower for the second "
    "time in a week, injuring 11 people, officials said.",
)
LEFT_COLUMN = [
    (
        "CRIME",
        "CARTAGENA HOSTAGES FREED",
        "About 30 people held in a supermarket standoff were all freed "
        "unharmed, police said.",
    ),
    (
        "POLITICS",
        "SHANGHAI BOSS UNDER PROBE",
        "China opened an investigation into Shanghai party chief Chen "
        "Jining, the party said.",
    ),
]
RIGHT_COLUMN = [
    (
        "SPACE",
        "FIRST PAKISTANI IN SPACE",
        "Pakistan's first astronaut reached China's space station aboard "
        "the Shenzhou-24 crew ship.",
    ),
    (
        "JUSTICE",
        "US SOLDIER SOLD SECRETS",
        "US soldier Jian Zhao admitted selling military secrets to China, "
        "prosecutors said.",
    ),
]
ECONOMY = (
    "ECONOMY",
    "BANGLADESH RAISES PAY 36%",
    "Bangladesh raised the garment minimum wage by 36 percent, the "
    "government said.",
)


class Page:
    """A plain RGB canvas with a few drawing helpers."""

    def __init__(self):
        self.buf = bytearray(W * H * 3)
        for i in range(0, len(self.buf), 3):
            self.buf[i] = 255
            self.buf[i + 1] = 255
            self.buf[i + 2] = 255

    def pixel(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            off = (y * W + x) * 3
            self.buf[off] = color[0]
            self.buf[off + 1] = color[1]
            self.buf[off + 2] = color[2]

    def rect(self, x, y, w, h, color=BLACK):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.pixel(xx, yy, color)

    def rule(self, x, y, w, thickness=1):
        self.rect(x, y, w, thickness, BLACK)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, color=BLACK):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines fitting max_width."""
        lines = []
        current = ""
        for word in text.split(" "):
            trial = word if not current else current + " " + word
            if self.text_width(trial, scale) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_body(self, x, y, text, max_width, scale, line_h):
        for line in self.wrap(text, max_width, scale):
            self.draw_text(x, y, line, scale)
            y += line_h
        return y

    def skyline(self, x0, baseline, towers):
        """A city skyline: black towers with lit windows."""
        for (dx, w, h) in towers:
            self.rect(x0 + dx, baseline - h, w, h, BLACK)
            for wy in range(baseline - h + 8, baseline - 6, 12):
                for wx in range(x0 + dx + 6, x0 + dx + w - 4, 10):
                    self.rect(wx, wy, 3, 4, WHITE)

    def bars(self, x_before, x_after, baseline, w, h_before, h_after):
        self.rect(x_before, baseline - h_before, w, h_before, BLACK)
        self.rect(x_after, baseline - h_after, w, h_after, BLACK)


def draw_page():
    p = Page()
    # Masthead.
    p.rule(36, 28, 952, 2)
    title = "THE WORLD TODAY"
    p.draw_text((W - p.text_width(title, 8)) // 2, 44, title, 8)
    date = "WEDNESDAY, 25 NOVEMBER 2026"
    p.draw_text((W - p.text_width(date, 3)) // 2, 112, date, 3)
    p.rule(36, 146, 952, 3)
    p.rule(36, 152, 952, 1)

    # Lead story, with a skyline on its right.
    kicker, headline, body = LEAD
    p.draw_text(36, 168, kicker, 2)
    p.draw_text(36, 190, headline, 5)
    p.draw_body(36, 238, body, 640, 2, 20)
    p.skyline(720, 298, [(0, 40, 55), (48, 36, 80), (92, 44, 64),
                         (144, 38, 95), (190, 42, 70), (240, 28, 48)])
    p.rect(720 + 144 + 17, 298 - 95 - 12, 4, 12, BLACK)
    p.rule(36, 316, 952, 2)

    # Two columns of two stories each.
    p.rule(510, 334, 1, 310)
    for col_x, stories in ((36, LEFT_COLUMN), (532, RIGHT_COLUMN)):
        y = 334
        for kicker, headline, body in stories:
            p.draw_text(col_x, y, kicker, 2)
            p.draw_text(col_x, y + 24, headline, 3)
            p.draw_body(col_x, y + 54, body, 456, 2, 20)
            y += 152
            if stories.index((kicker, headline, body)) == 0:
                p.rule(col_x, y, 456, 1)
                y += 18

    # Economy strip with a before/after bar chart.
    # Revision: shifted the strip and footer down so the page fills its
    # full height instead of leaving a wide blank band at the bottom.
    p.rule(36, 676, 952, 2)
    kicker, headline, body = ECONOMY
    p.draw_text(36, 694, kicker, 2)
    p.draw_text(36, 718, headline, 3)
    p.draw_body(36, 748, body, 620, 2, 20)
    p.bars(740, 860, 824, 80, 64, 88)
    p.draw_text(877, 712, "+36%", 2)
    p.draw_text(740, 832, "BEFORE", 2)
    p.draw_text(860, 832, "AFTER", 2)

    # Footer.
    p.rule(36, 860, 952, 2)
    foot1 = "MIDDLE EAST | CRIME | SPACE | POLITICS | JUSTICE | ECONOMY"
    p.draw_text((W - p.text_width(foot1, 2)) // 2, 876, foot1, 2)
    foot2 = "THE WORLD TODAY - WEDNESDAY 25 NOVEMBER 2026"
    p.draw_text((W - p.text_width(foot2, 2)) // 2, 902, foot2, 2)
    return p


def write_png(page, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += page.buf[y * W * 3:(y + 1) * W * 3]
    data = zlib.compress(bytes(raw), 9)

    def chunk(kind, payload):
        out = struct.pack(">I", len(payload)) + kind + payload
        out += struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    page = draw_page()
    write_png(page, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
