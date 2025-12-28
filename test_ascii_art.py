import pytest
import ascii_art

def test_clamp_inside_range():
    assert ascii_art.clamp(100) == 100
    assert ascii_art.clamp(0) == 0
    assert ascii_art.clamp(255) == 255

def test_clamp_below_zero():
    assert ascii_art.clamp(-10) == 0


def test_clamp_above_255():
    assert ascii_art.clamp(300) == 255




def test_hsl_to_rgb_red():
    assert ascii_art.hsl_to_rgb(0, 100, 50) == (255, 0, 0)


def test_hsl_to_rgb_green():
    assert ascii_art.hsl_to_rgb(120, 100, 50) == (0, 255, 0)


def test_hsl_to_rgb_blue():
    assert ascii_art.hsl_to_rgb(240, 100, 50) == (0, 0, 255)

def test_parse_color_basic_names():
    assert ascii_art.parse_color_to_rgb("red") == (255, 0, 0)
    assert ascii_art.parse_color_to_rgb("blue") == (0, 0, 255)

def test_parse_color_hex():
    assert ascii_art.parse_color_to_rgb("#FF0000") == (255, 0, 0)
    assert ascii_art.parse_color_to_rgb("#00FF00") == (0, 255, 0)

def test_parse_color_invalid_hex():
    assert ascii_art.parse_color_to_rgb("#GG0000") is None

def test_parse_color_rgb_function():
    assert ascii_art.parse_color_to_rgb("rgb(255, 0, 0)") == (255, 0, 0)
    assert ascii_art.parse_color_to_rgb("rgb(0,128,255)") == (0, 128, 255)

def test_parse_color_hsl_function():
    assert ascii_art.parse_color_to_rgb("hsl(0,100%,50%)") == (255, 0, 0)
    assert ascii_art.parse_color_to_rgb("hsl(120,100%,50%)") == (0, 255, 0)

def test_parse_color_none_and_empty():
    assert ascii_art.parse_color_to_rgb(None) is None
    assert ascii_art.parse_color_to_rgb("") is None

def test_make_color_codes_valid():
    prefix, reset = ascii_art.make_color_codes("red")

    assert prefix.startswith("\033[38;2;255;0;0m")
    assert reset == ascii_art.RESET

def test_make_color_codes_invalid():
    prefix, reset = ascii_art.make_color_codes("not_a_color")
    assert prefix == ""
    assert reset == ""

def test_normalize_banner_name_predefined():
    assert ascii_art.normalize_banner_name("standard") == "standard.txt"
    assert ascii_art.normalize_banner_name("shadow") == "shadow.txt"
    assert ascii_art.normalize_banner_name("thinkertoy") == "thinkertoy.txt"


def test_normalize_banner_name_custom():
    assert ascii_art.normalize_banner_name("mybanner.txt") == "mybanner.txt"
    assert ascii_art.normalize_banner_name("weird_name") == "weird_name"

def test_build_color_mask_no_pattern():
    mask = ascii_art.build_color_mask("hello", None)
    assert mask == [True, True, True, True, True]

def test_build_color_mask_empty_pattern():
    mask = ascii_art.build_color_mask("hello", "")
    assert mask == [False, False, False, False, False]

def test_build_color_mask_single_occurrence():
    mask = ascii_art.build_color_mask("banana", "ana")

    assert mask == [False, True, True, True, False, False]


def test_build_color_mask_multiple_occurrences():
    mask = ascii_art.build_color_mask("aaaaa", "aa")
    assert mask == [True, True, True, True, False]

def test_print_ascii_line_basic(capsys):
    banner_map = {
        "A": ["AAA"] * ascii_art.BANNER_HEIGHT
    }

    ascii_art.print_ascii_line("A", banner_map)

    captured = capsys.readouterr()
    lines = captured.out.splitlines()

    assert len(lines) == ascii_art.BANNER_HEIGHT
    assert all(line == "AAA" for line in lines)


def test_print_ascii_line_unsupported_char_causes_exit():
    banner_map = {
        "A": ["AAA"] * ascii_art.BANNER_HEIGHT
    }

    with pytest.raises(SystemExit):
        ascii_art.print_ascii_line("B", banner_map)


def test_print_ascii_line_with_color_and_pattern(capsys):
    banner_map = {
        "H": ["H"] * ascii_art.BANNER_HEIGHT,
        "I": ["I"] * ascii_art.BANNER_HEIGHT,
    }

    prefix, reset = ascii_art.make_color_codes("red")
    ascii_art.print_ascii_line("HI", banner_map, prefix, reset, pattern="I")

    captured = capsys.readouterr()
    lines = captured.out.splitlines()

    assert len(lines) == ascii_art.BANNER_HEIGHT

    assert any(prefix in line for line in lines)

def test_parse_args_no_arguments():
    banner, prefix, reset, pattern, text = ascii_art.parse_args([])
    assert banner == "standard.txt"
    assert prefix == ""
    assert reset == ""
    assert pattern is None
    assert text is None


def test_parse_args_text_only():
    banner, prefix, reset, pattern, text = ascii_art.parse_args(["Hello"])
    assert banner == "standard.txt"
    assert text == "Hello"
    assert pattern is None
    assert prefix == ""
    assert reset == ""


def test_parse_args_text_and_banner():
    banner, prefix, reset, pattern, text = ascii_art.parse_args(["Hi", "shadow"])
    assert banner == "shadow.txt"
    assert text == "Hi"
    assert pattern is None


def test_parse_args_color_and_text():
    banner, prefix, reset, pattern, text = ascii_art.parse_args(["--color=red", "Hello"])
    assert banner == "standard.txt"
    assert text == "Hello"
    assert pattern is None
    assert prefix != ""
    assert reset == ascii_art.RESET


def test_parse_args_color_pattern_text_banner():
    banner, prefix, reset, pattern, text = ascii_art.parse_args(
        ["--color=#FF0000", "lo", "Hello", "standard"]
    )
    assert banner == "standard.txt"
    assert text == "Hello"
    assert pattern == "lo"
    assert prefix != ""
    assert reset == ascii_art.RESET

def test_main_no_text_does_not_crash(monkeypatch):
    monkeypatch.setattr("sys.argv", ["ascii_art.py"])
    ascii_art.main()
