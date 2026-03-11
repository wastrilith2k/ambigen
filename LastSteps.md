# Last Steps — Things You Need To Do

## 1. Install FFmpeg

FFmpeg isn't installed in this environment (no sudo access). You need it for all video/audio operations.

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install ffmpeg
```

## 2. Set your Gemini API key

Free from https://aistudio.google.com/apikey

```bash
export GEMINI_API_KEY="your-key-here"
```

Without it, image generation falls back to a dark gradient placeholder. Everything else still works.

## 3. Add audio files

The recipes reference audio files that don't exist yet. You need to provide them:

```
audio/fireplace_crackle.mp3
audio/tavern_ambience.mp3
audio/rain_on_window.mp3
audio/cafe_ambience.mp3
audio/stream_water.mp3
audio/forest_birds.mp3
audio/gentle_wind.mp3
audio/space_drone.mp3
```

**How to get them:**
- Run `ambigen suno-prompt presets/cozy_tavern.yaml` to generate a Suno prompt
- Paste it into https://suno.ai to generate ambient music
- Download and put the files in `audio/`
- Or grab royalty-free ambient sounds from freesound.org

## 4. Test the full pipeline

Once FFmpeg is installed:

```bash
# Placeholder pipeline (no API key or audio needed)
ambigen generate presets/cozy_tavern.yaml --preview --skip-image --no-audio

# With real Gemini image
ambigen generate presets/cozy_tavern.yaml --preview --no-audio

# Full pipeline with audio
ambigen generate presets/cozy_tavern.yaml --preview
```

## 5. Initialize git repo

```bash
cd ~/projs/ambigen
git init
git add -A
git commit -m "Initial commit: ambigen ambient video generator"
```

## 6. Update README screenshot

Once you've generated a video, grab a screenshot or short GIF and add it to the README.

## 7. Update LICENSE copyright

The LICENSE file has "James" as the copyright holder. Update if needed.
