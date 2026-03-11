"""FFmpeg zoompan animation — Ken Burns with ping-pong sine motion."""

import subprocess
from pathlib import Path


def build_zoompan_expression(
    duration: int = 30,
    fps: int = 30,
    zoom_min: float = 1.0,
    zoom_max: float = 1.3,
    easing: str = "ease_in_out",
    output_width: int = 1920,
    output_height: int = 1080,
) -> str:
    """Build an FFmpeg zoompan filter expression.

    easing='ease_in_out' uses a sine curve: P = (1-cos(2*PI*t/N))/2
    easing='linear' uses constant motion: P = t/N
    """
    total_frames = duration * fps
    zoom_delta = zoom_max - zoom_min

    if easing == "linear":
        # Linear: progress = on/total_frames, ping-pong via triangle wave
        zoom_expr = (
            f"zoom=if(lt(mod(on\\,{total_frames*2})\\,{total_frames})\\,"
            f"{zoom_min}+{zoom_delta}*(mod(on\\,{total_frames})/{total_frames})\\,"
            f"{zoom_max}-{zoom_delta}*(mod(on\\,{total_frames})/{total_frames}))"
        )
        # Linear pan: move left-to-right then back
        x_expr = (
            f"x=if(lt(mod(on\\,{total_frames*2})\\,{total_frames})\\,"
            f"(iw-iw/zoom)/2*(mod(on\\,{total_frames})/{total_frames})\\,"
            f"(iw-iw/zoom)/2*(1-mod(on\\,{total_frames})/{total_frames}))"
        )
    else:
        # ease_in_out: P = (1 - cos(2*PI*on/N)) / 2  — smooth ping-pong
        progress = f"(1-cos(2*PI*on/{total_frames}))/2"
        zoom_expr = f"zoom={zoom_min}+{zoom_delta}*{progress}"
        x_expr = f"x=(iw-iw/zoom)/2*{progress}"

    y_expr = "y=(ih-ih/zoom)/2"

    filter_str = (
        f"zoompan={zoom_expr}:{x_expr}:{y_expr}"
        f":d={total_frames}:s={output_width}x{output_height}:fps={fps}"
    )
    return filter_str


def animate(
    image_path: Path,
    output_path: Path,
    duration: int = 30,
    fps: int = 30,
    zoom_min: float = 1.0,
    zoom_max: float = 1.3,
    easing: str = "ease_in_out",
    output_width: int = 1920,
    output_height: int = 1080,
) -> Path:
    """Apply Ken Burns animation to a still image via FFmpeg."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    zoompan_filter = build_zoompan_expression(
        duration=duration,
        fps=fps,
        zoom_min=zoom_min,
        zoom_max=zoom_max,
        easing=easing,
        output_width=output_width,
        output_height=output_height,
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", zoompan_filter,
        "-t", str(duration),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Install it: apt install ffmpeg / brew install ffmpeg")
    if result.returncode != 0:
        stderr = result.stderr
        if "No such file or directory" in stderr:
            raise RuntimeError(f"Audio file not found — check paths in your recipe.\n{stderr}")
        if "Invalid data found" in stderr:
            raise RuntimeError(f"Corrupted media file — check your input files.\n{stderr}")
        raise RuntimeError(f"FFmpeg animation failed:\n{stderr}")

    return output_path
