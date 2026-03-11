"""YAML recipe loader and configuration dataclasses."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ImageConfig:
    prompt: str = ""
    width: int = 3840
    height: int = 2160
    style: str = "photorealistic"


@dataclass
class AnimationConfig:
    duration_seconds: int = 30
    fps: int = 30
    zoom_range: tuple[float, float] = (1.0, 1.3)
    easing: str = "ease_in_out"


@dataclass
class AudioLayer:
    file: str = ""
    volume: float = 1.0


@dataclass
class AudioConfig:
    layers: list[AudioLayer] = field(default_factory=list)
    fade_out_seconds: float = 3.0


@dataclass
class Recipe:
    name: str = ""
    description: str = ""
    duration_hours: int = 1
    image: ImageConfig = field(default_factory=ImageConfig)
    animation: AnimationConfig = field(default_factory=AnimationConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    output_dir: str = "output"
    output_resolution: tuple[int, int] = (1920, 1080)

    @property
    def duration_seconds(self) -> int:
        return self.duration_hours * 3600

    @property
    def safe_name(self) -> str:
        return self.name.lower().replace(" ", "_")


def load_recipe(path: str | Path) -> Recipe:
    """Load a recipe from a YAML file."""
    path = Path(path)
    with open(path) as f:
        data = yaml.safe_load(f)

    image = ImageConfig(**data.get("image", {}))

    anim_data = data.get("animation", {})
    if "zoom_range" in anim_data:
        anim_data["zoom_range"] = tuple(anim_data["zoom_range"])
    animation = AnimationConfig(**anim_data)

    audio_data = data.get("audio", {})
    layers = [AudioLayer(**layer) for layer in audio_data.get("layers", [])]
    audio = AudioConfig(
        layers=layers,
        fade_out_seconds=audio_data.get("fade_out_seconds", 3.0),
    )

    output_res = data.get("output_resolution", [1920, 1080])

    return Recipe(
        name=data.get("name", path.stem),
        description=data.get("description", ""),
        duration_hours=data.get("duration_hours", 1),
        image=image,
        animation=animation,
        audio=audio,
        output_dir=data.get("output_dir", "output"),
        output_resolution=tuple(output_res),
    )
