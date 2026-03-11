"""FFmpeg audio layer mixing with volume control and fade-out."""

import subprocess
from pathlib import Path


def mix_audio(
    layers: list[dict],
    output_path: Path,
    duration: float,
    fade_out_seconds: float = 3.0,
) -> Path:
    """Mix multiple audio layers into a single audio file.

    Each layer is a dict with 'file' (str path) and 'volume' (float 0-1).
    Audio files shorter than duration are looped.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not layers:
        raise ValueError("No audio layers provided.")

    # Build ffmpeg command with individual volume control and looping
    cmd = ["ffmpeg", "-y"]
    filter_parts = []

    for i, layer in enumerate(layers):
        file_path = layer["file"]
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        cmd.extend(["-stream_loop", "-1", "-i", file_path])
        vol = layer.get("volume", 1.0)
        filter_parts.append(f"[{i}:a]volume={vol}[a{i}]")

    # Mix all layers together
    layer_labels = "".join(f"[a{i}]" for i in range(len(layers)))
    filter_parts.append(
        f"{layer_labels}amix=inputs={len(layers)}:duration=longest[mixed]"
    )

    # Apply fade-out and trim to duration
    fade_start = max(0, duration - fade_out_seconds)
    filter_parts.append(
        f"[mixed]afade=t=out:st={fade_start}:d={fade_out_seconds},"
        f"atrim=0:{duration}[out]"
    )

    filter_complex = ";".join(filter_parts)
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Install it: apt install ffmpeg / brew install ffmpeg")
    if result.returncode != 0:
        stderr = result.stderr
        if "Invalid data found" in stderr:
            raise RuntimeError(f"Corrupted audio file — check your input files.\n{stderr}")
        raise RuntimeError(f"FFmpeg audio mixing failed:\n{stderr}")

    return output_path
