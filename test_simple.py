# tests/test_simple.py

from simple import make_hello

def test_make_hello_returns_correct_message():
    result = make_hello("World")
    assert result == "Hello, World!"


def test_make_hello_with_empty_name():
    result = make_hello("")
    assert result == "Hello, !"
