"""Tests for animator zoom/pan expressions."""

from ambigen.animator import build_zoompan_expression


def test_zoompan_expression_default():
    expr = build_zoompan_expression(duration=30, fps=30)
    assert "zoompan" in expr
    assert "1920x1080" in expr


def test_zoompan_expression_sine():
    expr = build_zoompan_expression(duration=30, fps=30, easing="ease_in_out")
    assert "cos" in expr


def test_zoompan_expression_linear():
    expr = build_zoompan_expression(duration=30, fps=30, easing="linear")
    assert "mod" in expr
    assert "cos" not in expr


def test_zoompan_custom_resolution():
    expr = build_zoompan_expression(
        duration=30, fps=30, output_width=3840, output_height=2160
    )
    assert "3840x2160" in expr
