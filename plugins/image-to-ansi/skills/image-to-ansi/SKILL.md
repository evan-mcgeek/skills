---
name: image-to-ansi
description: >-
  Convert an image (PNG/JPG/GIF/WebP/SVG/HEIC) into a terminal-renderable string
  built from ANSI colour codes and block/ASCII characters — the kind of
  "terminal graphics" you see in a CLI splash screen, a TUI banner, `neofetch`
  logos, or a login screen. Use this whenever the user hands you an image and
  wants it shown in a terminal, turned into "ANSI art", "terminal art", "TUI
  graphics", a "text-mode" or "escape-code" version of a picture, a colour
  ASCII-art rendering, a banner/logo/splash for a CLI or TUI, or asks to
  `cat` an image, embed a picture in terminal output, or make it look like the
  image "in the console". Also use it when they mention chafa, jp2a, img2sixel,
  viu, timg, half-block rendering, or sixel. Trigger even if they don't say the
  word "ANSI" — "make my logo show up when my script starts" counts. Do NOT use
  it for the reverse direction (rendering ANSI art files to PNG) or for drawing
  diagrams/box-art from scratch with no source image.
---

# image-to-ansi

Turn a source image into a string a terminal can print, matching the original as
closely as the medium allows. The medium is a grid of character cells, each with
one foreground and one background colour — so "as close as possible" means
choosing the right cell resolution, the right character set, and the right
colour depth for where the art will actually be displayed.

## The one thing that trips people up: terminal art does not reflow

A block of ANSI art is rendered at a **fixed** cell width. If the user's
terminal is narrower than the art, every line wraps and the image turns to
confetti. So before rendering anything, you need to know **how wide** the output
may be and **whether the width is knowable ahead of time**. This drives
everything else. See "Responsiveness" below — it is not an afterthought.

## Step 1 — Understand the target

Ask (or infer from context) these, then state your assumptions back before you
build anything:

1. **Where will it be displayed?** This determines the deliverable:
   - *Quick look / one-off* → a `.ans` file they `cat`, plus a preview.
   - *Splash screen in a shell script* → a `.ans` file + a `show.sh` that prints
     it (optionally re-rendering to fit — see Responsiveness).
   - *Embedded in a TUI program's source* → a string literal in their language
     (Python/Go/Rust/JS/C), or better, a call into a rendering library.
   - *Pasted into chat / a README / a comment* → plain output, and consider
     `--mode ascii` so it survives places that strip colour.
2. **Maximum width in columns?** Default to **80**. Ask if a TUI has a known
   panel size. "Responsive / unknown" is a valid answer — handle it per below.
3. **Colour depth of the target terminal?**
   - `truecolor` (24-bit) — modern terminals (iTerm2, kitty, WezTerm, Windows
     Terminal, most Linux terminals). Default.
   - `256` — older/conservative environments, tmux without truecolor passthrough.
   - `16` — maximum portability, TTY consoles, CI logs, `neofetch`-style logos.
   - `none` — monochrome ASCII, for when even colour is unwelcome.
   When unsure, ask, or produce both a truecolor and a 256 version.
4. **Fidelity or character of the result?**
   - *Photographic fidelity* → half-block mode (`▀`), truecolor. Two image
     pixels per cell; this is the closest match.
   - *Retro / "ASCII art" look, or must survive colour-stripping* → ascii mode
     with a luminance ramp. Copy-pasteable anywhere.
   - chafa can also use *sextants/octants/braille* for extra resolution on
     terminals with the fonts for it — mention this only if fidelity is
     paramount and the target terminal is known-modern.

   **Be honest about ASCII's ceiling.** A luminance ramp of ~10 characters on an
   80-column grid holds bold shapes — logos, high-contrast line art, silhouettes,
   a recognisable landmark — and little else. Photographs and anything with fine
   detail come out as noise; if the user hands you a photo and asks for "ASCII
   art", render it, but tell them a half-block version would look far closer and
   show both if you can. `jp2a` is a dedicated ASCII-art tool worth trying as a
   third engine when the bundled ramp disappoints on line art.

## Step 2 — Pick the engine

**Prefer `chafa`.** It has the best symbol selection, dithering, and colour
quantisation, handles every input format, is fast, and is actively maintained.
Check for it:

```bash
chafa --version
```

If it is missing, offer to install it — it is a small, well-known package:

| Platform | Command |
|---|---|
| macOS | `brew install chafa` |
| Debian/Ubuntu | `sudo apt install chafa` |
| Fedora | `sudo dnf install chafa` |
| Arch | `sudo pacman -S chafa` |
| Windows | `scoop install chafa` or `winget install hpjansson.Chafa` |

If the user declines the install or you cannot install, fall back to the
bundled script `scripts/img2ansi.py` (see Step 3b). It is slower and simpler but
needs no system package — it decodes via Pillow if present, otherwise via
ImageMagick or macOS `sips`, and renders half-block or ASCII in any colour depth.

## Step 3a — Render with chafa

chafa's own flags map directly onto the Step 1 answers. Build the command from
this table rather than memorising one incantation:

| Goal | Flags |
|---|---|
| Set width, keep aspect | `--size 80x` (height auto). Use `--size 80x40` to bound both. |
| Highest fidelity, modern terminal | `-c full -f symbols --symbols vhalf+block` |
| 256-colour target | `-c 256` |
| 16-colour / portable logo | `-c 16 --color-space rgb` |
| Monochrome ASCII | `-c none --symbols ascii --fill ascii` |
| Retro colour ASCII | `-c full --symbols ascii+space --fill ascii` |
| Crisp logo/flat art (no dithering) | `--dither none` |
| Photo (smoother gradients) | `--dither ordered` (or `fs` for Floyd–Steinberg) |
| Static block only — no cursor moves, no cursor-hide codes, no sixel surprise | `-f symbols --animate off --relative off --polite on --exact-size off` |
| Transparent PNG, matte onto a solid colour | `--bg '#1e1e2e'` |
| Transparent PNG, let the terminal show through | (no `--bg`) — in `-f symbols` mode chafa just leaves those cells unpainted |

### Transparent PNGs — a decision, not a default

A logo or mascot usually arrives with an alpha channel, and there are two right
answers depending on where it will sit:

- **Matte it** (`--bg <colour>`) when the art will land on a known background —
  a specific TUI panel colour, a docs page, a terminal theme you control. Pick a
  colour that matches. This is also the safe choice when the art has near-black
  or near-white regions that would otherwise vanish (Tux's black body on a dark
  terminal, white line art on a light one).
- **Leave it transparent** (no `--bg`, `-f symbols`) when you *want* it to blend
  with whatever theme the user runs — a startup banner is the classic case.
  chafa leaves the transparent cells unpainted and the terminal background
  shows through cleanly (this is not the "grey haze" — that comes from `-f ansi`
  or a rasteriser, not symbols mode).

For a shipped logo/mascot where you can't know the target, **produce both**: a
transparent version as the default and a matted fallback (`logo-matte.ansi` on a
neutral dark like `#1e1e1e`) for users on the opposite-contrast terminal. Say
which is which.

Write the output to a file:

```bash
chafa -f symbols --size 80x --animate off --relative off --polite on cat.png > cat.ansi
```

Always pass `-f symbols --animate off --relative off --polite on` for a static
deliverable. Without `-f symbols`, chafa auto-detects the output format and can
pick sixel instead of plain character cells when run non-interactively (piped to
a file, or from a script) — a different, wider-support-but-not-universal escape
family than the half-block/ASCII symbols this skill is built around. Without the
other three flags chafa emits cursor-relative moves, multi-frame output, and —
the one that bites — `\x1b[?25l` / `\x1b[?25h` cursor-hide sequences that make
the file unsafe to `cat` (they hide the cursor for the rest of the session, or
corrupt a TUI buffer if parsed). `--polite on` is the flag that suppresses those;
it is easy to forget. Step 5 has you verify it anyway.

For an **animated GIF** the user wants to keep animated, that is a different
artefact — chafa can emit a loop, but usually the right answer is a `show.sh`
that runs `chafa gif_file` live. Confirm with the user.

## Step 3b — Render with the bundled script

```bash
python3 scripts/img2ansi.py IMAGE [options]
```

| Option | Meaning |
|---|---|
| `-w, --width N` | target columns (default 80). `-w auto` = current terminal width. |
| `-H, --height N` | target rows; use instead of or together with width to bound both. |
| `-m, --mode half\|ascii` | `half` = `▀` half-block (default, best fidelity); `ascii` = luminance ramp. |
| `-c, --color truecolor\|256\|16\|none` | colour depth (default truecolor). `none` only with `--mode ascii`. |
| `--ink auto\|dark\|light` | ascii mode: which SOURCE tone becomes the dense ramp characters. `auto` (default) reads the median brightness and inks the *subject* (the minority tone) — correct for line art, logos, and READMEs without any flag. Only reach for `dark`/`light` if auto guesses wrong (rare; usually a near-50/50 image). |
| `--matte R,G,B\|#RRGGBB` | composite transparent pixels onto this colour. Default black — which is right even for ascii (a light subject on a transparent field needs a dark matte to read as a shape; `auto` ink then inks it). |
| `--cell-aspect R` | terminal cell height/width, ascii mode only (default 2.0). |
| `-o, --output FILE` | write to FILE (prints a size summary to stderr) instead of stdout. |

Examples:

```bash
# Photo, fit 100 cols, save
python3 scripts/img2ansi.py photo.jpg -w 100 -o photo.ansi

# Portable 16-colour logo
python3 scripts/img2ansi.py logo.png -w 60 -c 16 -o logo.ansi

# Monochrome ASCII for a README code block (auto ink direction — no flag needed)
python3 scripts/img2ansi.py sketch.png -w 72 -m ascii -c none
```

## Step 4 — Package the deliverable

Match this to the Step 1 answer about where it lives. See
`references/packaging.md` for ready-to-adapt templates of each:

- **Raw file** — `name.ansi`. Tell the user: `cat name.ansi` to view.
- **Self-printing script** — `show.sh` (POSIX) that `cat`s the file, or better,
  a script that re-renders to the current width. Template in packaging.md.
- **Language string literal** — embed the escape codes in a source file. Use the
  language's raw/again-safe string form and keep the `\x1b` as `\x1b` (Python),
  `\033` (C/Go), `\u{1b}` (Rust), `\x1b` (JS). packaging.md has one per language.
- **Responsive regen helper** — ship the *source image* alongside a small script
  that runs chafa/img2ansi at `$(tput cols)` on each run. This is the only way
  to truly fit an unknown terminal; see below.

## Responsiveness

"Make it responsive" means the art should look right regardless of the viewer's
terminal size. ANSI art itself is static, so responsiveness has to come from
*when* you render:

1. **Render at display time (best).** Ship the source image plus a helper:

   ```sh
   #!/bin/sh
   # show.sh — render logo.png to fit the current terminal, every run
   cols=$(tput cols 2>/dev/null || echo 80)
   if command -v chafa >/dev/null 2>&1; then
     chafa --size "${cols}x" --animate off --relative off "$(dirname "$0")/logo.png"
   else
     python3 "$(dirname "$0")/img2ansi.py" "$(dirname "$0")/logo.png" -w "$cols"
   fi
   ```

   Use this for shell prompts, `.bashrc` banners, CLI startup screens, install
   scripts — anything that runs interactively.

2. **Pre-render a size ladder.** When you cannot run a renderer at display time
   (e.g. the art is baked into a compiled binary or a static file), generate a
   few widths — 60, 80, 100, 120 — and have the program pick the largest that
   fits `COLUMNS`. packaging.md has a selector snippet.

3. **Render inside the TUI framework.** If this is going into a Bubble Tea,
   Ratatui, Textual, Ink, etc. app, the layout engine knows the panel size at
   runtime — call chafa as a subprocess (or a libchafa binding) with that
   width when the panel mounts or resizes, and cache the result per size.
   Do not bake a fixed-width blob into a resizable pane.

Always tell the user which strategy you used and how to change the width.

## Step 5 — Verify before handing it over

1. **Dimensions.** Confirm the cell width is ≤ the target. `awk '{ print length }'`
   overcounts (escape codes + multibyte), so instead trust chafa's `--size` or
   the script's stderr summary, and spot-check by printing it in your own
   terminal at that width.
2. **Clean termination.** The output must end with a reset (`\x1b[0m` /
   `\033[0m`) so it does not bleed colour into the following prompt. Both
   engines here do this; verify if you hand-edited.
3. **No stray cursor moves** in a static deliverable (no `\x1b[?25l`,
   `\x1b[<n>A`, `\x1b[2J` unless intended).
4. **Preview it — always, before handing it over.** The user cannot picture an
   escape-code blob; they need to *see* the render next to the source. In order
   of fidelity:
   - `terminal:vhs-cli-demos` skill, if available — a real terminal screenshot.
   - `scripts/ansi2png.py IN -o OUT.png` — bundled rasteriser, no terminal
     capture pipeline needed (needs Pillow). Use `--mode text` for ascii-art
     files, `--mode blocks` (default) for half-block. It understands the
     block-element glyphs chafa emits.
   - Failing both, print it in your own session and paste a trimmed sample.
   Then build a source-vs-render comparison image and send it with
   `SendUserFile`. Do this even for a quick job.
5. **Sanity-check fidelity.** Compare to the source: are the dominant colours
   right, is the subject centred and recognisable, did a transparent background
   turn muddy? If it looks wrong, the usual fixes are: increase width, switch
   dither mode, set an explicit `--bg`, or move from ascii to half-block.

## Notes on getting a closer match

- **Width is resolution.** Doubling the column count roughly doubles detail.
  Encourage the largest width the target can take.
- **Half-block beats ASCII for photos** by 2x vertical resolution and full
  per-cell colour. Only choose ASCII when legibility or paste-safety matters
  more than fidelity.
- **Dithering** trades flat colour for perceived depth — good for photos and
  gradients, bad for logos and text (it fuzzes edges). Default on for photos,
  off for flat art.
- **Transparent PNGs** are a decision — matte onto a known colour, or leave
  transparent to blend with the theme. See "Transparent PNGs" under Step 3a; for
  a shipped logo, produce both.
- **256 vs truecolor** is usually invisible for logos, noticeable for skin tones
  and skies. If the target terminal is unknown, truecolor degrades more
  gracefully than you'd expect on modern setups; 16-colour does not — reserve it
  for genuine TTY/CI targets.
