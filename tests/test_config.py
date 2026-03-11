"""Tests for recipe loading and configuration."""

from ambigen.config import load_recipe


def test_loads_preset():
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert recipe.name == "Cozy Tavern"
    assert recipe.duration_hours == 3


def test_duration_seconds():
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert recipe.duration_seconds == 10800


def test_safe_name():
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert recipe.safe_name == "cozy_tavern"


def test_image_config():
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert recipe.image.width == 3840
    assert recipe.image.height == 2160
    assert "tavern" in recipe.image.prompt.lower()


def test_animation_config():
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert recipe.animation.duration_seconds == 30
    assert recipe.animation.easing == "ease_in_out"
    assert recipe.animation.zoom_range == (1.0, 1.25)


def test_audio_layers():
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert len(recipe.audio.layers) == 2
    assert recipe.audio.layers[0].volume == 0.8


def test_output_resolution():
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert recipe.output_resolution == (1920, 1080)
