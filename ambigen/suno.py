"""Suno prompt generation and audio directory scanner."""

from pathlib import Path


def generate_suno_prompt(recipe_name: str, description: str, mood: str = "") -> str:
    """Generate a Suno-friendly prompt for ambient music.

    Since Suno has no API, this generates a text prompt the user can paste
    into Suno's web interface.
    """
    parts = [
        f"Ambient background music for: {recipe_name}.",
        description,
    ]
    if mood:
        parts.append(f"Mood: {mood}.")
    parts.extend([
        "Style: instrumental ambient, no vocals, seamless loop.",
        "Duration: 3-4 minutes.",
        "Should work well looped for hours without becoming repetitive.",
    ])
    return " ".join(parts)


def scan_audio_dir(audio_dir: str | Path = "audio") -> list[Path]:
    """Scan a directory for audio files (.mp3, .wav, .m4a, .ogg)."""
    audio_dir = Path(audio_dir)
    if not audio_dir.exists():
        return []

    extensions = {".mp3", ".wav", ".m4a", ".ogg"}
    files = sorted(
        f for f in audio_dir.iterdir()
        if f.suffix.lower() in extensions
    )
    return files
