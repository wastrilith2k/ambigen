# ambigen

Generate YouTube-ready ambient videos from YAML recipes. Define a scene — image prompt, Ken Burns animation, layered audio — and ambigen produces a seamless 1-3 hour video.

## How It Works

```
YAML Recipe → Gemini Image → Ken Burns Animation → Audio Mix → Looped Video
```

1. **Image generation** — Sends the recipe's prompt to Gemini (Imagen 3) to generate a 4K background image. Falls back to a gradient placeholder if no API key is set.
2. **Ken Burns animation** — Applies a zoompan filter via FFmpeg with smooth sine-based ping-pong motion. The 2x resolution source gives headroom for pan/zoom without quality loss.
3. **Audio mixing** — Layers multiple audio files with individual volume control, automatic looping, and fade-out at the end.
4. **Looping** — The animated segment is seamlessly looped to the target duration (hours), then muxed with the mixed audio.

## Installation

```bash
git clone https://github.com/youruser/ambigen.git
cd ambigen
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Requirements:** Python 3.12+, FFmpeg on PATH.

## Usage

### Generate a video

```bash
# Full 3-hour video from a recipe
ambigen generate presets/cozy_tavern.yaml

# Quick 30-second preview, no API calls
ambigen generate presets/cozy_tavern.yaml --preview --skip-image --no-audio

# See what would be generated
ambigen generate presets/cozy_tavern.yaml --dry-run
```

### Other commands

```bash
# Generate all presets in a directory
ambigen batch presets/ --preview --skip-image --no-audio

# Validate a recipe file
ambigen validate presets/cozy_tavern.yaml

# Create a new recipe template
ambigen new-recipe "Mountain Lake"

# Generate a Suno prompt for matching ambient music
ambigen suno-prompt presets/cozy_tavern.yaml
```

## Recipes

Recipes are YAML files that define everything about a video:

```yaml
name: Cozy Tavern
description: A warm medieval tavern with crackling fireplace
duration_hours: 3
image:
  prompt: "Interior of a cozy medieval tavern at night..."
  width: 3840
  height: 2160
animation:
  duration_seconds: 30
  fps: 30
  zoom_range: [1.0, 1.25]
  easing: ease_in_out  # or: linear
audio:
  layers:
    - file: audio/fireplace_crackle.mp3
      volume: 0.8
    - file: audio/tavern_ambience.mp3
      volume: 0.4
  fade_out_seconds: 3.0
output_resolution: [1920, 1080]
```

Four presets are included: `cozy_tavern`, `rainy_cafe`, `forest_stream`, `space_ambient`.

## Audio Workflow

ambigen doesn't generate audio — you provide it. The recommended workflow:

1. Run `ambigen suno-prompt presets/your_recipe.yaml` to get a Suno-friendly prompt
2. Paste it into [Suno](https://suno.ai) to generate ambient music
3. Download the audio files into `audio/`
4. Reference them in your recipe's `audio.layers`

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | No | Gemini API key for image generation. Without it, a placeholder gradient is used. Free from [AI Studio](https://aistudio.google.com/apikey). |

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
