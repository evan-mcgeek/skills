#!/usr/bin/env python3
"""
ansi2png.py — Rasterise a terminal escape-code string to a PNG.

This is a *preview* tool for the image-to-ansi skill: it lets you (and the user)
see what a `.ansi` / `.ans` file looks like when printed, without needing a
terminal screenshot pipeline (vhs/ttyd/ffmpeg). If `vhs` is available, a real
terminal capture is more faithful — use that. This script is the fallback.

It understands:
  - SGR colour: reset(0), 30-37/40-47, 90-97/100-107, 38;5;n / 48;5;n,
    38;2;r;g;b / 48;2;r;g;b
  - The Block Elements chafa emits: full/half/quadrant/eighth blocks, and
    ░▒▓ shading (rendered as fg/bg blends)
  - `--mode text` to draw ASCII/other glyphs with a monospace font instead of
    as geometric fills (use this for luminance-ramp ASCII art)

Requires Pillow.

Usage:
  ansi2png.py art.ansi -o art.png            # block mode, 8px cells
  ansi2png.py art.ansi -o art.png --scale 12
  ansi2png.py ascii.txt -o ascii.png --mode text
"""

import argparse
import re
import sys

from PIL import Image, ImageDraw, ImageFont

SGR = re.compile(r"\x1b\[([0-9;]*)m")
CSI_ANY = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

BASIC = [
    (0, 0, 0), (170, 0, 0), (0, 170, 0), (170, 85, 0),
    (0, 0, 170), (170, 0, 170), (0, 170, 170), (170, 170, 170),
    (85, 85, 85), (255, 85, 85), (85, 255, 85), (255, 255, 85),
    (85, 85, 255), (255, 85, 255), (85, 255, 255), (255, 255, 255),
]


def xterm256(n):
    if n < 16:
        return BASIC[n]
    if n < 232:
        n -= 16
        r, g, b = n // 36, (n // 6) % 6, n % 6
        lv = [0, 95, 135, 175, 215, 255]
        return (lv[r], lv[g], lv[b])
    v = 8 + (n - 232) * 10
    return (v, v, v)


# glyph -> list of (x0,y0,x1,y1) rectangles in a unit cell that are "fg ink".
# Eighths/quadrants approximate; enough for a legible preview.
def _eighths_lower(k):  # k/8 of the cell filled from the bottom
    return [(0.0, 1 - k / 8, 1.0, 1.0)]


def _eighths_left(k):
    return [(0.0, 0.0, k / 8, 1.0)]


BLOCKS = {
    " ": [], " ": [],
    "█": [(0, 0, 1, 1)],                       # █
    "▀": [(0, 0, 1, 0.5)],                     # ▀
    "▄": [(0, 0.5, 1, 1)],                     # ▄
    "▌": [(0, 0, 0.5, 1)],                     # ▌
    "▐": [(0.5, 0, 1, 1)],                     # ▐
    "▖": [(0, 0.5, 0.5, 1)],                   # ▖
    "▗": [(0.5, 0.5, 1, 1)],                   # ▗
    "▘": [(0, 0, 0.5, 0.5)],                   # ▘
    "▝": [(0.5, 0, 1, 0.5)],                   # ▝
    "▙": [(0, 0, 0.5, 1), (0, 0.5, 1, 1)],     # ▙
    "▛": [(0, 0, 1, 0.5), (0, 0, 0.5, 1)],     # ▛
    "▜": [(0, 0, 1, 0.5), (0.5, 0, 1, 1)],     # ▜
    "▟": [(0.5, 0, 1, 1), (0, 0.5, 1, 1)],     # ▟
    "▚": [(0, 0, 0.5, 0.5), (0.5, 0.5, 1, 1)],  # ▚
    "▞": [(0.5, 0, 1, 0.5), (0, 0.5, 0.5, 1)],  # ▞
}
for i in range(1, 8):
    BLOCKS[chr(0x2580 + 0)] = BLOCKS["▀"]
for i, ch in enumerate("▁▂▃▄▅▆▇", start=1):
    BLOCKS[ch] = _eighths_lower(i)
for i, ch in enumerate("▏▎▍▌▋▊▉", start=1):
    BLOCKS[ch] = _eighths_left(i)
SHADE = {"░": 0.25, "▒": 0.5, "▓": 0.75}


def blend(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def parse_cells(text):
    """Yield rows; each row is a list of (char, fg, bg, inv)."""
    fg, bg = (229, 229, 229), None
    default_fg = fg
    inv = False
    rows = []
    row = []
    i = 0
    while i < len(text):
        m = SGR.match(text, i)
        if m:
            parts = [int(p) if p else 0 for p in m.group(1).split(";")]
            j = 0
            while j < len(parts):
                p = parts[j]
                if p == 0:
                    fg, bg, inv = default_fg, None, False
                elif p == 7:
                    inv = True
                elif p == 27:
                    inv = False
                elif 30 <= p <= 37:
                    fg = BASIC[p - 30]
                elif 90 <= p <= 97:
                    fg = BASIC[p - 90 + 8]
                elif 40 <= p <= 47:
                    bg = BASIC[p - 40]
                elif 100 <= p <= 107:
                    bg = BASIC[p - 100 + 8]
                elif p == 39:
                    fg = default_fg
                elif p == 49:
                    bg = None
                elif p in (38, 48) and j + 1 < len(parts):
                    mode = parts[j + 1]
                    if mode == 5 and j + 2 < len(parts):
                        col = xterm256(parts[j + 2])
                        j += 2
                    elif mode == 2 and j + 4 < len(parts):
                        col = (parts[j + 2], parts[j + 3], parts[j + 4])
                        j += 4
                    else:
                        col = fg
                        j += 1
                    if p == 38:
                        fg = col
                    else:
                        bg = col
                j += 1
            i = m.end()
            continue
        m = CSI_ANY.match(text, i)
        if m:
            i = m.end()
            continue
        ch = text[i]
        i += 1
        if ch == "\n":
            rows.append(row)
            row = []
        elif ch == "\r":
            pass
        else:
            row.append((ch, fg, bg, inv))
    if row:
        rows.append(row)
    return rows


def render(rows, cw, ch, mode, bg_default):
    width = max((len(r) for r in rows), default=1) * cw
    height = len(rows) * ch
    img = Image.new("RGB", (max(width, 1), max(height, 1)), bg_default)
    draw = ImageDraw.Draw(img)
    font = None
    # In text mode, monochrome art carries no fg colour, so the default light
    # grey is invisible on a light page. Pick an ink that contrasts the page.
    light_page = sum(bg_default) > 384
    ink = (20, 20, 20) if light_page else (235, 235, 235)
    if mode == "text":
        for name in ("Menlo.ttc", "DejaVuSansMono.ttf", "Courier New.ttf"):
            try:
                font = ImageFont.truetype(name, ch - 1)
                break
            except OSError:
                continue
        if font is None:
            font = ImageFont.load_default()
    for ry, row in enumerate(rows):
        for cx, (glyph, fg, bg, inv) in enumerate(row):
            if inv:
                fg, bg = (bg if bg is not None else bg_default), fg
            x0, y0 = cx * cw, ry * ch
            if bg is not None:
                draw.rectangle([x0, y0, x0 + cw, y0 + ch], fill=bg)
            if glyph in SHADE:
                base = bg if bg is not None else bg_default
                draw.rectangle([x0, y0, x0 + cw, y0 + ch],
                               fill=blend(base, fg, SHADE[glyph]))
                continue
            if mode == "text":
                if glyph.strip():
                    used = fg if fg != (229, 229, 229) else ink
                    draw.text((x0, y0 - 1), glyph, fill=used, font=font)
                continue
            rects = BLOCKS.get(glyph)
            if rects is None:
                rects = [(0.1, 0.1, 0.9, 0.9)] if glyph.strip() else []
            for (a, b, c, d) in rects:
                draw.rectangle([x0 + a * cw, y0 + b * ch,
                                x0 + c * cw, y0 + d * ch], fill=fg)
    return img


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rasterise ANSI art to PNG.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--mode", choices=["blocks", "text"], default="blocks")
    ap.add_argument("--scale", type=int, default=8,
                    help="cell width in px (height is 2x). Default 8.")
    ap.add_argument("--bg", default="#1e1e1e", help="page background colour")
    args = ap.parse_args(argv)

    text = open(args.input, encoding="utf-8", errors="replace").read()
    rows = parse_cells(text)
    cw = args.scale
    ch = args.scale * 2
    bg = tuple(int(args.bg.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4))
    img = render(rows, cw, ch, args.mode, bg)
    img.save(args.output)
    print(f"wrote {args.output}  ({img.width}x{img.height}px, "
          f"{len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
