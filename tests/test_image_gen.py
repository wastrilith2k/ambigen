"""Tests for image generation."""

from ambigen.image_gen import generate_placeholder


def test_placeholder_image():
    img = generate_placeholder(3840, 2160)
    assert img.size == (3840, 2160)


def test_placeholder_image_small():
    img = generate_placeholder(100, 100)
    assert img.size == (100, 100)
    # Should be a dark gradient — check that pixels aren't all black
    pixels = list(img.getdata())
    assert not all(p == (0, 0, 0) for p in pixels)
