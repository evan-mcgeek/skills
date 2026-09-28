#!/usr/bin/env python3
"""
img2ansi.py — Convert an image to a terminal-renderable escape-code string.

This is the fallback engine for the image-to-ansi skill. Prefer `chafa` when it
is installed (better dithering, symbol selection, and speed); reach for this
script when chafa is unavailable or you need a dependency-light path.

Decoding strategy, in order of preference:
  1. Pillow, if importable.
  2. `magick` / `convert` (ImageMagick) piped to PPM.
  3. `sips` (macOS built-in) -> BMP, parsed here in pure Python.

Rendering modes:
  half   (default) — U+2580 upper half block. Top pixel -> foreground colour,
                     bottom pixel -> background colour. Doubles vertical
                     resolution, so this is the closest-to-the-image option.
  ascii            — luminance ramp, optional colour. The "retro" look; also the
                     right choice when the output must survive being pasted
                     somewhere colour codes get stripped.

Colour depth: truecolor (24-bit), 256, 16, or none (ascii mode only).

The output always ends with a reset (\x1b[0m) and a trailing newline so it is
safe to `cat` or embed.
"""

import argparse
import os
import shutil
import subprocess
import sys

RESET = "\x1b[0m"
UPPER_HALF = "▀"  # ▀
# Dense -> sparse. Leading char is a space (brightest cell prints nothing).
ASCII_RAMP = " .:-=+*#%@"


# --------------------------------------------------------------------------- #
# Image loading. Returns (width, height, pixels) where pixels is a flat list  #
# of (r, g, b) tuples, row-major.                                             #
# --------------------------------------------------------------------------- #

def load_with_pillow(path, matte=(0, 0, 0)):
    from PIL import Image

    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, tuple(matte) + (255,))
        im = Image.alpha_composite(bg, im).convert("RGB")
    else:
        im = im.convert("RGB")
    return im.width, im.height, list(im.getdata())


def load_with_magick(path, matte=(0, 0, 0)):
    exe = shutil.which("magick") or shutil.which("convert")
    if not exe:
        return None
    cmd = [exe] + (["convert"] if exe.endswith("magick") else [])
    cmd += [path, "-background", "#%02x%02x%02x" % tuple(matte),
            "-flatten", "-depth", "8", "ppm:-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return parse_ppm(raw)


def parse_ppm(raw):
    """Parse a binary P6 PPM."""
    if not raw.startswith(b"P6"):
        raise ValueError("not a P6 PPM")
    # header: P6 <w> <h> <maxval>, whitespace-separated, comments start with #
    fields = []
    i = 2
    while len(fields) < 3:
        while i < len(raw) and raw[i:i + 1].isspace():
            i += 1
        if raw[i:i + 1] == b"#":
            while i < len(raw) and raw[i:i + 1] != b"\n":
                i += 1
            continue
        start = i
        while i < len(raw) and not raw[i:i + 1].isspace():
            i += 1
        fields.append(int(raw[start:i]))
    i += 1  # single whitespace after maxval
    w, h, maxval = fields
    data = raw[i:i + w * h * 3]
    scale = 255.0 / maxval if maxval != 255 else 1.0
    if scale == 1.0:
        pixels = [tuple(data[p:p + 3]) for p in range(0, len(data), 3)]
    else:
        pixels = [
            tuple(int(data[p + k] * scale) for k in range(3))
            for p in range(0, len(data), 3)
        ]
    return w, h, pixels


def load_with_sips(path, work_png=None):
    exe = shutil.which("sips")
    if not exe:
        return None
    tmp = path + ".img2ansi.bmp"
    try:
        subprocess.run(
            [exe, "-s", "format", "bmp", path, "--out", tmp],
            capture_output=True, check=True,
        )
        with open(tmp, "rb") as fh:
            return parse_bmp(fh.read())
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def parse_bmp(raw):
    """Parse uncompressed 24/32-bit BITMAPINFOHEADER BMPs (what sips emits)."""
    if raw[:2] != b"BM":
        raise ValueError("not a BMP")
    off = int.from_bytes(raw[10:14], "little")
    hdr = int.from_bytes(raw[14:18], "little")
    w = int.from_bytes(raw[18:22], "little", signed=True)
    h = int.from_bytes(raw[22:26], "little", signed=True)
    bpp = int.from_bytes(raw[28:30], "little")
    compression = int.from_bytes(raw[30:34], "little")
    if compression not in (0, 3):
        raise ValueError("compressed BMP not supported")
    top_down = h < 0
    h = abs(h)
    row_bytes = ((bpp * w + 31) // 32) * 4
    px = bytearray(w * h * 3)
    for row in range(h):
        src_row = row if top_down else h - 1 - row
        base = off + src_row * row_bytes
        for col in range(w):
            p = base + col * (bpp // 8)
            b, g, r = raw[p], raw[p + 1], raw[p + 2]
            d = (row * w + col) * 3
            px[d], px[d + 1], px[d + 2] = r, g, b
    pixels = [tuple(px[p:p + 3]) for p in range(0, len(px), 3)]
    return w, h, pixels


def load_image(path, matte=(0, 0, 0)):
    """Decode `path` to (w, h, [(r,g,b), ...]). Transparent pixels are composited
    onto `matte` — black by default, but callers pass white for ascii/paper
    output. (The `sips` fallback can't honour `matte`; it flattens onto white.)"""
    if not os.path.isfile(path):
        sys.exit(f"No such image: {path}")
    errors = []
    try:
        return load_with_pillow(path, matte)
    except ImportError:
        errors.append("Pillow not installed")
    except Exception as e:  # noqa: BLE001
        errors.append(f"Pillow: {e}")
    for loader in (load_with_magick, load_with_sips):
        try:
            result = loader(path, matte) if loader is load_with_magick \
                else loader(path)
            if result:
                return result
        except Exception as e:  # noqa: BLE001
            errors.append(f"{loader.__name__}: {e}")
    sys.exit(
        "Could not decode image. Tried:\n  - "
        + "\n  - ".join(errors)
        + "\n\nInstall one of: chafa (preferred, use it directly), "
        "Pillow (`pip install pillow`), or ImageMagick (`brew install imagemagick`)."
    )


# --------------------------------------------------------------------------- #
# Resampling (area-average box filter, pure Python).                          #
# --------------------------------------------------------------------------- #

def resize(src_w, src_h, pixels, dst_w, dst_h):
    if (src_w, src_h) == (dst_w, dst_h):
        return pixels
    out = [(0, 0, 0)] * (dst_w * dst_h)
    x_ratio = src_w / dst_w
    y_ratio = src_h / dst_h
    for dy in range(dst_h):
        sy0 = int(dy * y_ratio)
        sy1 = max(sy0 + 1, int((dy + 1) * y_ratio))
        sy1 = min(sy1, src_h)
        for dx in range(dst_w):
            sx0 = int(dx * x_ratio)
            sx1 = max(sx0 + 1, int((dx + 1) * x_ratio))
            sx1 = min(sx1, src_w)
            r = g = b = n = 0
            for sy in range(sy0, sy1):
                row = sy * src_w
                for sx in range(sx0, sx1):
                    pr, pg, pb = pixels[row + sx]
                    r += pr
                    g += pg
                    b += pb
                    n += 1
            if n:
                out[dy * dst_w + dx] = (r // n, g // n, b // n)
    return out


# --------------------------------------------------------------------------- #
# Colour handling.                                                            #
# --------------------------------------------------------------------------- #

def srgb_luma(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def to_256(r, g, b):
    """Nearest xterm-256 index."""
    def cube(v):
        if v < 48:
            return 0
        if v < 115:
            return 1
        return (v - 35) // 40

    ci = 16 + 36 * cube(r) + 6 * cube(g) + cube(b)
    # grey ramp can be closer for near-neutral colours
    grey = round((srgb_luma(r, g, b) - 8) / 10)
    if 0 <= grey <= 23:
        gi = 232 + grey
        cube_levels = [0, 95, 135, 175, 215, 255]
        cr, cg, cb = (cube_levels[cube(x)] for x in (r, g, b))
        gv = 8 + grey * 10
        if (gv - r) ** 2 + (gv - g) ** 2 + (gv - b) ** 2 < \
           (cr - r) ** 2 + (cg - g) ** 2 + (cb - b) ** 2:
            return gi
    return ci


_ANSI16 = [
    (0, 0, 0), (170, 0, 0), (0, 170, 0), (170, 85, 0),
    (0, 0, 170), (170, 0, 170), (0, 170, 170), (170, 170, 170),
    (85, 85, 85), (255, 85, 85), (85, 255, 85), (255, 255, 85),
    (85, 85, 255), (255, 85, 255), (85, 255, 255), (255, 255, 255),
]


def to_16(r, g, b):
    best, bi = 1e18, 7
    for i, (cr, cg, cb) in enumerate(_ANSI16):
        d = (cr - r) ** 2 + (cg - g) ** 2 + (cb - b) ** 2
        if d < best:
            best, bi = d, i
    return bi


def fg_code(rgb, depth):
    r, g, b = rgb
    if depth == "truecolor":
        return f"\x1b[38;2;{r};{g};{b}m"
    if depth == "256":
        return f"\x1b[38;5;{to_256(r, g, b)}m"
    if depth == "16":
        i = to_16(r, g, b)
        return f"\x1b[{90 + i - 8}m" if i >= 8 else f"\x1b[{30 + i}m"
    return ""


def bg_code(rgb, depth):
    r, g, b = rgb
    if depth == "truecolor":
        return f"\x1b[48;2;{r};{g};{b}m"
    if depth == "256":
        return f"\x1b[48;5;{to_256(r, g, b)}m"
    if depth == "16":
        i = to_16(r, g, b)
        return f"\x1b[{100 + i - 8}m" if i >= 8 else f"\x1b[{40 + i}m"
    return ""


# --------------------------------------------------------------------------- #
# Renderers.                                                                  #
# --------------------------------------------------------------------------- #

def render_half(w, h, pixels, depth):
    """Two vertical pixels per character cell via the upper-half block."""
    if h % 2:
        pixels = pixels + pixels[-w:]  # pad to even row count
        h += 1
    lines = []
    for cy in range(0, h, 2):
        top = pixels[cy * w:(cy + 1) * w]
        bot = pixels[(cy + 1) * w:(cy + 2) * w]
        cells = []
        prev = None
        for tp, bp in zip(top, bot):
            code = fg_code(tp, depth) + bg_code(bp, depth)
            if code != prev:
                cells.append(code)
                prev = code
            cells.append(UPPER_HALF)
        lines.append("".join(cells) + RESET)
    return "\n".join(lines) + "\n"


def background_is_bright(pixels):
    """Guess whether the image sits on a light background.

    Uses the median luma: in a picture of a subject on a field, most pixels are
    the field, so the median tracks the background. Dense ramp characters should
    land on the *subject* (the minority tone), keeping the background sparse —
    that reads as the subject drawn in ink regardless of which way round the
    tones are.
    """
    if not pixels:
        return True
    lums = sorted(srgb_luma(*p) for p in pixels)
    return lums[len(lums) // 2] > 128


def render_ascii(w, h, pixels, depth, bright_is_dense):
    lines = []
    for cy in range(h):
        row = pixels[cy * w:(cy + 1) * w]
        cells = []
        prev = None
        for rgb in row:
            lum = srgb_luma(*rgb) / 255.0
            if not bright_is_dense:
                lum = 1.0 - lum
            ch = ASCII_RAMP[min(len(ASCII_RAMP) - 1,
                                int(lum * (len(ASCII_RAMP) - 1) + 0.5))]
            if depth == "none":
                cells.append(ch)
                continue
            code = fg_code(rgb, depth)
            if code != prev:
                cells.append(code)
                prev = code
            cells.append(ch)
        line = "".join(cells)
        lines.append(line + (RESET if depth != "none" else ""))
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Sizing.                                                                     #
# --------------------------------------------------------------------------- #

def target_grid(src_w, src_h, cols, rows, mode, cell_aspect):
    """
    Return (sample_w, sample_h): the pixel grid to resample the image to.

    cols/rows are the character-cell budget. `cell_aspect` is cell height/width
    (~2.0 for typical terminal fonts). In half mode each cell holds 2 stacked
    pixels, so a cell is effectively square and we sample rows*2 pixels tall.
    """
    if cols is None and rows is None:
        cols = 80
    img_aspect = src_h / src_w  # height / width

    if mode == "half":
        if cols and not rows:
            sw = cols
            sh = round(sw * img_aspect)
            if sh % 2:
                sh += 1
            if rows_cap := os.environ.get("IMG2ANSI_MAX_ROWS"):
                sh = min(sh, int(rows_cap) * 2)
        elif rows and not cols:
            sh = rows * 2
            sw = round(sh / img_aspect)
        else:
            sw, sh = cols, rows * 2
            # letterbox to preserve aspect within the box
            box_aspect = sh / sw
            if img_aspect > box_aspect:
                sw = round(sh / img_aspect)
            else:
                sh = round(sw * img_aspect)
                if sh % 2:
                    sh += 1
        return max(1, sw), max(2, sh)

    # ascii: one pixel per cell, so correct for the tall cell
    if cols and not rows:
        sw = cols
        sh = max(1, round(sw * img_aspect / cell_aspect))
    elif rows and not cols:
        sh = rows
        sw = max(1, round(sh * cell_aspect / img_aspect))
    else:
        sw, sh = cols, rows
        box_aspect = (sh * cell_aspect) / sw
        if img_aspect > box_aspect:
            sw = max(1, round(sh * cell_aspect / img_aspect))
        else:
            sh = max(1, round(sw * img_aspect / cell_aspect))
    return sw, sh


def detect_cols():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return int(os.environ.get("COLUMNS", 80))


# --------------------------------------------------------------------------- #
# CLI.                                                                        #
# --------------------------------------------------------------------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Convert an image to a terminal escape-code string.")
    ap.add_argument("image")
    ap.add_argument("-w", "--width", default=None,
                    help="target columns; 'auto' = current terminal width "
                         "(default: 80, or unset if --height given)")
    ap.add_argument("-H", "--height", type=int, default=None,
                    help="target rows (optional; caps/overrides width)")
    ap.add_argument("-m", "--mode", choices=["half", "ascii"], default="half")
    ap.add_argument("-c", "--color",
                    choices=["truecolor", "256", "16", "none"],
                    default="truecolor")
    ap.add_argument("--cell-aspect", type=float, default=2.0,
                    help="terminal cell height/width ratio (ascii mode)")
    ap.add_argument("--ink", choices=["auto", "dark", "light"], default="auto",
                    help="ascii mode: which tone of the SOURCE image becomes the "
                         "dense ramp characters. 'auto' (default) reads the "
                         "median brightness and inks the subject (the minority "
                         "tone) — right for almost everything, including a "
                         "README. 'dark' forces dense-where-source-is-dark, "
                         "'light' dense-where-source-is-bright; use these only "
                         "if auto guesses wrong.")
    ap.add_argument("--matte", default=None, metavar="R,G,B|#RRGGBB",
                    help="composite transparent pixels onto this colour "
                         "(default: black for half mode, and auto for ascii — "
                         "black so a light subject shows as a shape).")
    ap.add_argument("--invert", action="store_true",
                    help="alias for --ink light")
    ap.add_argument("-o", "--output", default=None,
                    help="write here instead of stdout")
    args = ap.parse_args(argv)

    if args.color == "none" and args.mode == "half":
        ap.error("--color none only makes sense with --mode ascii")

    if args.width is None:
        cols = None if args.height else 80
    elif args.width == "auto":
        cols = detect_cols()
    else:
        cols = int(args.width)
    rows = args.height

    if args.matte:
        s = args.matte.lstrip("#")
        if "," in s:
            matte = tuple(int(x) for x in s.split(","))
        else:
            matte = tuple(int(s[k:k + 2], 16) for k in (0, 2, 4))
    else:
        matte = (0, 0, 0)

    src_w, src_h, pixels = load_image(args.image, matte)
    sw, sh = target_grid(src_w, src_h, cols, rows, args.mode, args.cell_aspect)
    pixels = resize(src_w, src_h, pixels, sw, sh)

    if args.mode == "half":
        art = render_half(sw, sh, pixels, args.color)
    else:
        ink = "light" if args.invert else args.ink
        if ink == "auto":
            # Ink the subject (minority tone), leave the background sparse.
            bright_is_dense = not background_is_bright(pixels)
        else:
            bright_is_dense = (ink == "light")
        art = render_ascii(sw, sh, pixels, args.color, bright_is_dense)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(art)
        cell_rows = art.count("\n")
        print(f"wrote {args.output}  ({sw}x{cell_rows} cells, "
              f"{args.mode}/{args.color})", file=sys.stderr)
    else:
        sys.stdout.write(art)


if __name__ == "__main__":
    main()
