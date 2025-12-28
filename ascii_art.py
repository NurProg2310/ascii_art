
import sys
import os
import re

BANNER_HEIGHT = 8
FIRST_CHAR_CODE = 32
CHAR_COUNT = 95
RESET = "\033[0m"

BASIC_COLORS = {
    "black":   (0, 0, 0),
    "red":     (255, 0, 0),
    "green":   (0, 128, 0),
    "yellow":  (255, 255, 0),
    "blue":    (0, 0, 255),
    "magenta": (255, 0, 255),
    "cyan":    (0, 255, 255),
    "white":   (255, 255, 255),
    "orange":  (255, 165, 0),
}


def clamp(v, lo=0, hi=255):
    v = int(round(v))
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def hsl_to_rgb(h, s, l):
    h = h % 360
    s = s / 100.0
    l = l / 100.0
    c = (1 - abs(2 * l - 1)) * s
    hp = h / 60.0
    x = c * (1 - abs(hp % 2 - 1))

    if 0 <= hp < 1:
        r1, g1, b1 = c, x, 0
    elif 1 <= hp < 2:
        r1, g1, b1 = x, c, 0
    elif 2 <= hp < 3:
        r1, g1, b1 = 0, c, x
    elif 3 <= hp < 4:
        r1, g1, b1 = 0, x, c
    elif 4 <= hp < 5:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    m = l - c / 2
    r = clamp((r1 + m) * 255)
    g = clamp((g1 + m) * 255)
    b = clamp((b1 + m) * 255)
    return r, g, b


def parse_color_to_rgb(color_str):
    if not color_str:
        return None
    c = color_str.strip().lower()

    if c in BASIC_COLORS:
        return BASIC_COLORS[c]

    if c.startswith("#") and len(c) == 7:
        try:
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            return r, g, b
        except ValueError:
            return None

    m = re.match(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)", c)
    if m:
        r, g, b = (int(m.group(i)) for i in range(1, 4))
        if all(0 <= v <= 255 for v in (r, g, b)):
            return r, g, b
        return None

    m = re.match(r"hsl\(\s*(-?\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*\)", c)
    if m:
        h = int(m.group(1))
        s = int(m.group(2))
        l = int(m.group(3))
        if 0 <= s <= 100 and 0 <= l <= 100:
            return hsl_to_rgb(h, s, l)
        return None

    return None


def make_color_codes(color_str):
    rgb = parse_color_to_rgb(color_str)
    if rgb is None:
        return "", ""
    r, g, b = rgb
    prefix = f"\033[38;2;{r};{g};{b}m"
    return prefix, RESET


def normalize_banner_name(raw):
    if raw in ("standard", "shadow", "thinkertoy"):
        return raw + ".txt"
    return raw


def load_banner(banner_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    banner_path = os.path.join(base_dir, banner_name)

    try:
        with open(banner_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        print(f"Error: banner file '{banner_name}' not found.")
        sys.exit(1)

    total_lines = len(lines)
    stride = BANNER_HEIGHT + 1

    if total_lines < stride * CHAR_COUNT or total_lines % stride != 0:
        stride = BANNER_HEIGHT
        if total_lines < stride * CHAR_COUNT or total_lines % stride != 0:
            print("Error: unexpected banner file format.")
            sys.exit(1)

    banner_map = {}
    idx = 0
    ch_code = FIRST_CHAR_CODE

    while ch_code < FIRST_CHAR_CODE + CHAR_COUNT and idx + BANNER_HEIGHT <= total_lines:
        char_lines = lines[idx: idx + BANNER_HEIGHT]
        banner_map[chr(ch_code)] = char_lines
        idx += stride
        ch_code += 1

    return banner_map


def build_color_mask(text_line, pattern):
    n = len(text_line)
    if pattern is None:
        return [True] * n
    if pattern == "":
        return [False] * n

    mask = [False] * n
    start = 0
    plen = len(pattern)

    while True:
        pos = text_line.find(pattern, start)
        if pos == -1:
            break
        for i in range(pos, min(pos + plen, n)):
            mask[i] = True
        start = pos + plen

    return mask


def print_ascii_line(text_line, banner_map, color_prefix="", color_reset="", pattern=None):
    if not text_line:
        return

    for ch in text_line:
        if ch not in banner_map:
            print(f"Error: unsupported character {repr(ch)}")
            sys.exit(1)

    use_color = bool(color_prefix and color_reset)
    mask = build_color_mask(text_line, pattern) if use_color else [False] * len(text_line)

    for row in range(BANNER_HEIGHT):
        parts = []
        for idx, ch in enumerate(text_line):
            piece = banner_map[ch][row]
            if use_color and mask[idx]:
                parts.append(color_prefix + piece + color_reset)
            else:
                parts.append(piece)
        print("".join(parts))


def print_usage_banner():
    print("Usage: python3 main.py [STRING] [BANNER]\n")
    print("EX: python3 main.py something standard")

def print_usage_color():
    print("Usage: python3 main.py [OPTION] [STRING]\n")
    print('EX: python3 main.py --color=<color> <letters to be colored> "something"')


def parse_args(argv):
    banner_name = "standard.txt"
    color_prefix = ""
    color_reset = ""
    pattern = None
    text = None

    if not argv:
        return banner_name, color_prefix, color_reset, pattern, text

    args = list(argv)

    if args[0].startswith("--"):
        if not args[0].startswith("--color="):
            print_usage_color()
            sys.exit(1)

        color_value = args[0].split("=", 1)[1]
        if not color_value:
            print_usage_color()
            sys.exit(1)

        color_prefix, color_reset = make_color_codes(color_value)
        args = args[1:]

        if len(args) == 0:
            print_usage_color()
            sys.exit(1)

        if len(args) == 1:
            text = args[0]
        elif len(args) == 2:
            pattern = args[0]
            text = args[1]
        elif len(args) == 3:
            pattern = args[0]
            text = args[1]
            banner_name = normalize_banner_name(args[2])
        else:
            print_usage_color()
            sys.exit(1)

    else:
        if len(args) == 1:
            text = args[0]
        elif len(args) == 2:
            text = args[0]
            banner_name = normalize_banner_name(args[1])
        else:
            print_usage_banner()
            sys.exit(1)

    return banner_name, color_prefix, color_reset, pattern, text


def main():
    banner_name, color_prefix, color_reset, pattern, text = parse_args(sys.argv[1:])
    if text is None:
        return

    banner_map = load_banner(banner_name)

    if text == "":
        return

    lines = text.split("\n")

    for i, line in enumerate(lines):
        if line != "":
            print_ascii_line(line, banner_map, color_prefix, color_reset, pattern)
        if line == "" and i < len(lines) - 1:
            print()


if __name__ == "__main__":
    main()
