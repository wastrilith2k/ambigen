# ambigen — Claude Code Build Instructions

## What This Is

ambigen is a Python CLI tool that generates YouTube-ready ambient videos from YAML recipes. It generates background images via Gemini, applies Ken Burns pan/zoom animation via FFmpeg, mixes layered audio, and loops segments to create 1-3 hour videos.

**The code is already written.** Your job is to get it running, test it end-to-end, fix any issues, and polish it into a portfolio-ready project.

## Project Location

The complete source is in this directory. Copy it to your working area:

```bash
cp -r /path/to/ambigen ~/projects/ambigen
cd ~/projects/ambigen
```

## Existing File Structure

```
ambigen/
├── ambigen/
│   ├── __init__.py
│   ├── __main__.py       # Entry: python -m ambigen
│   ├── cli.py            # Click CLI — 5 commands: generate, quick, new-recipe, suno-prompt, suno-link
│   ├── config.py         # YAML loader, dataclass config (Recipe, ImageConfig, AnimationConfig, etc.)
│   ├── image_gen.py      # Gemini image generation with placeholder fallback
│   ├── animator.py       # FFmpeg zoompan filter — Ken Burns with ping-pong sine motion
│   ├── audio_mixer.py    # FFmpeg audio layer mixing with volume control + fade-out
│   ├── renderer.py       # Final muxing of video + audio
│   └── suno.py           # Suno prompt generation + audio directory scanner
├── presets/
│   ├── cozy_tavern.yaml
│   ├── rainy_cafe.yaml
│   ├── forest_stream.yaml
│   └── space_ambient.yaml
├── README.md
└── requirements.txt
```

## Prerequisites

- Python 3.12+
- FFmpeg installed and on PATH (`brew install ffmpeg` or `apt install ffmpeg`)
- Gemini API key (free from https://aistudio.google.com/apikey)

---

## Phase 1: Get It Running

### Step 1: Set up the environment

```bash
cd ~/projects/ambigen
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-here"
```

### Step 2: Test the placeholder pipeline (no API key needed)

```bash
python -m ambigen generate presets/cozy_tavern.yaml --preview --skip-image --no-audio
```

This should:
1. Create a dark gradient placeholder image
2. Run the zoompan filter to create a 30-second animated segment
3. Render a final MP4 with no audio

**Expected output:** `output/cozy_tavern_1hr.mp4` (will actually be 30s due to --preview)

**If FFmpeg fails:** Check that `ffmpeg` is on your PATH. The zoompan expressions use inline math — if there's a parsing error, the issue is likely in the expression quoting in `animator.py`.

### Step 3: Test with real image generation

```bash
python -m ambigen generate presets/cozy_tavern.yaml --preview --no-audio
```

This makes one Gemini API call to generate the background image. Expected: 3840x2160 PNG saved to `cache/cozy_tavern_bg.png`.

### Step 4: Test audio mixing

```bash
# First, add some test audio files
mkdir -p audio
# Download or copy any .mp3 files into audio/

python -m ambigen generate presets/cozy_tavern.yaml --preview
```

### Step 5: Full generation

```bash
python -m ambigen generate presets/cozy_tavern.yaml
```

This runs the full pipeline: image → animate → mix audio → loop to target duration → render.

---

## Phase 2: Fix Known Issues

### 1. Add pyproject.toml

The project has `requirements.txt` but no `pyproject.toml`. Add one:

```toml
[project]
name = "ambigen"
version = "0.1.0"
description = "Generate ambient YouTube videos from YAML recipes"
requires-python = ">=3.12"
dependencies = [
  "click>=8.0",
  "google-generativeai>=0.8",
  "pyyaml>=6.0",
  "pillow>=10.0",
]

[project.scripts]
ambigen = "ambigen.cli:cli"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

Then users can install with `pip install -e .` and run `ambigen` directly instead of `python -m ambigen`.

### 2. Fix easing config being ignored

In `animator.py`, check whether the `easing` field from the recipe config is actually being used in the zoompan expression. It's likely the expression uses a hardcoded sine curve regardless of what's in the YAML. Wire it up properly so `easing: linear` produces constant motion and `easing: ease_in_out` produces the sine curve.

### 3. Update README

The README should reflect the actual current state. Update:
- Installation instructions (add the `pip install -e .` approach)
- Usage examples (use real command syntax from `cli.py`)
- Remove any placeholder or aspirational features not yet built

### 4. Add tests

Create `tests/test_config.py`:
```python
def test_loads_preset():
    from ambigen.config import load_recipe
    recipe = load_recipe("presets/cozy_tavern.yaml")
    assert recipe.name == "Cozy Tavern"
    assert recipe.duration_hours == 3

def test_placeholder_image():
    from ambigen.image_gen import generate_placeholder
    img = generate_placeholder(3840, 2160)
    assert img.size == (3840, 2160)
```

Create `tests/test_animator.py`:
```python
def test_zoompan_expression():
    from ambigen.animator import build_zoompan_expression
    expr = build_zoompan_expression(duration=30, fps=30)
    assert "zoompan" in expr
    assert "sin" in expr  # should use sine for smooth motion
```

### 5. Add .gitignore

```gitignore
.venv/
__pycache__/
*.pyc
output/
cache/
audio/
.env
*.mp4
*.png
*.jpg
```

---

## Phase 3: Polish

### Add `--dry-run` flag

```bash
ambigen generate presets/cozy_tavern.yaml --dry-run
# Output:
# Recipe: Cozy Tavern
# Duration: 3 hours (10800s)
# Image: 3840x2160, prompt: "cozy medieval tavern..."
# Animation: Ken Burns, 30s segment, ping-pong sine
# Audio layers: fireplace_crackle.mp3 (0.8), tavern_ambience.mp3 (0.4)
# Output: output/cozy_tavern_3hr.mp4
# Estimated generation time: ~4 minutes
# (dry run — nothing generated)
```

### Add progress bars

Use `rich` or `tqdm` to show progress during long operations:
- Image generation: spinner with "Generating image via Gemini..."
- Animation: progress bar with frame count
- Rendering: progress bar with time elapsed / estimated

### Add a `batch` command

```bash
ambigen batch presets/
# Generates all presets in a directory
```

### Add a `validate` command

```bash
ambigen validate presets/cozy_tavern.yaml
# ✓ Recipe: Cozy Tavern
# ✓ Image prompt: 47 words
# ⚠ Audio file not found: audio/fireplace_crackle.mp3
# ✓ Output: 10800s @ 1920x1080
```

### Better error messages

Parse common FFmpeg failures:
- "No such file or directory" → "Audio file not found: {path}"
- "Invalid data found" → "Corrupted audio file: {path}"
- "Unable to find a suitable output format" → "Invalid output path: {path}"

---

## Phase 4: GitHub-Ready

### Write a solid README

The current one needs:
- A screenshot or GIF of sample output (even a 5-second clip)
- Architecture diagram showing the pipeline
- Comparison of `generate` vs `quick` commands
- Clear note about Suno workflow (two-step: generate prompt → paste into Suno → download → link)

### Add GitHub Actions CI

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: pytest
```

### Add a LICENSE

MIT is fine for a portfolio project.

---

## Architecture Notes for Interview Discussion

1. **Config-driven architecture** — YAML recipes separate content from code. New video styles require zero code changes.

2. **FFmpeg zoompan with ping-pong sine** — The animation uses `P = (1-cos(2πt/N))/2` to ensure the first and last frames are identical. This makes looping seamless without crossfades, which matters for multi-hour videos.

3. **2x resolution generation** — Images are generated at 3840x2160 for 1920x1080 output. This gives the Ken Burns effect headroom to pan and zoom without hitting edges or losing quality.

4. **Differential tool use** — Gemini for images (free tier viable, API available), Suno for audio (no API, so we generate prompts and assist with the manual workflow). The CLI adapts to what's automatable vs. what needs human input.

5. **Subprocess isolation** — FFmpeg runs as a subprocess, not via a Python binding. Clear command-line arguments you can debug independently, no C library dependency issues, and the same commands work if someone wants to run them manually.

6. **Audio mixing architecture** — Individual volume control per layer, automatic looping of short clips, and fade-out at the end. The `amix` filter handles arbitrary layer counts.

