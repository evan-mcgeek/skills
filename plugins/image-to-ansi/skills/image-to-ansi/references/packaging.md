# Packaging templates

Adapt these to the user's environment. Keep the raw ESC byte as the language's
escape form; do not "clean up" the sequences.

## 1. Raw file

Just the renderer output redirected to `name.ansi` (or `.ans` / `.txt`).
Tell the user: `cat name.ansi`. On Windows `cmd`, `type name.ansi` (needs
`VirtualTerminalLevel` enabled) or PowerShell `Get-Content name.ansi`.

## 2. Self-printing script (fixed art)

```sh
#!/bin/sh
# banner.sh — print the pre-rendered banner
exec cat "$(dirname "$0")/banner.ansi"
```

`chmod +x banner.sh`.

## 3. Self-rendering script (responsive, preferred for interactive use)

```sh
#!/bin/sh
# banner.sh — render banner.png to fit the current terminal on every run
here=$(dirname "$0")
cols=$(tput cols 2>/dev/null || echo 80)
# leave a small margin so it never wraps
cols=$((cols > 4 ? cols - 2 : cols))
if command -v chafa >/dev/null 2>&1; then
  exec chafa --size "${cols}x" --animate off --relative off "$here/banner.png"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 "$here/img2ansi.py" "$here/banner.png" -w "$cols"
else
  exec cat "$here/banner.ansi"   # last-resort static fallback
fi
```

Ship `banner.png` (and optionally a static `banner.ansi`) next to the script.

## 4. Size-ladder selector (responsive without a renderer at runtime)

Pre-render `banner-60.ansi`, `banner-80.ansi`, `banner-100.ansi`,
`banner-120.ansi`, then:

```sh
#!/bin/sh
here=$(dirname "$0")
cols=$(tput cols 2>/dev/null || echo 80)
for w in 120 100 80 60; do
  if [ "$cols" -ge "$w" ]; then cat "$here/banner-$w.ansi"; exit 0; fi
done
cat "$here/banner-60.ansi"
```

## 5. Language string literals

The escape byte is 0x1B. Use each language's own form so the literal is
copy-paste safe.

### Python
```python
BANNER = (
    "\x1b[38;2;250;132;69m\x1b[48;2;244;150;83m▀▀▀\x1b[0m\n"
    # ...one line per row, ending each with \x1b[0m\n
)
print(BANNER, end="")
```
For anything more than a few lines, prefer reading a bundled `.ansi` file with
`importlib.resources` rather than a giant literal.

### Go
```go
// Use a raw string literal; put a real ESC in via \x1b in a normal string,
// or keep the .ansi file embedded:
import _ "embed"

//go:embed banner.ansi
var Banner string

fmt.Print(Banner)
```

### Rust
```rust
// Embed the file at compile time — cleaner than a string full of \u{1b}.
const BANNER: &str = include_str!("banner.ansi");
print!("{BANNER}");
```

### JavaScript / Node
```js
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
const banner = readFileSync(new URL("./banner.ansi", import.meta.url), "utf8");
process.stdout.write(banner);
```
Inline form uses `\x1b`:
```js
const BANNER = "\x1b[38;2;250;132;69m▀\x1b[0m\n";
```

### C
```c
/* xxd -i banner.ansi > banner.h  →  embeds as a byte array */
#include "banner.h"
fwrite(banner_ansi, 1, banner_ansi_len, stdout);
```

## 6. TUI framework integration

Render at panel size, cache per width. Sketch (Go / Bubble Tea):

```go
func (m model) renderLogo(width int) string {
    if s, ok := m.logoCache[width]; ok {
        return s
    }
    out, _ := exec.Command("chafa",
        "--size", fmt.Sprintf("%dx", width),
        "--animate", "off", "--relative", "off",
        m.logoPath).Output()
    m.logoCache[width] = string(out)
    return string(out)
}
```

Recompute on the framework's resize event; never store a single fixed-width
blob in a pane the user can resize.

## Notes

- Keep a trailing newline after the final `\x1b[0m` so the shell prompt starts
  on its own line.
- If the art will print at the very top of a cleared screen, prepend
  `\x1b[2J\x1b[H` deliberately — but never leave that in a literal meant to be
  concatenated with other output.
- Strip a UTF-8 BOM if your editor added one; some terminals print it as a
  visible glyph.
