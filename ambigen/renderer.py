"""Final muxing of video + audio, with segment looping for long durations."""

import subprocess
from pathlib import Path


def _run_ffmpeg(cmd: list[str], operation: str) -> None:
    """Run an FFmpeg command with friendly error handling."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Install it: apt install ffmpeg / brew install ffmpeg")
    if result.returncode != 0:
        stderr = result.stderr
        if "Unable to find a suitable output format" in stderr:
            raise RuntimeError(f"Invalid output path — check your output directory.\n{stderr}")
        raise RuntimeError(f"FFmpeg {operation} failed:\n{stderr}")


def loop_video(
    segment_path: Path,
    target_duration: float,
    output_path: Path,
) -> Path:
    """Loop a video segment to reach the target duration."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", str(segment_path),
        "-t", str(target_duration),
        "-c", "copy",
        str(output_path),
    ]

    _run_ffmpeg(cmd, "loop")
    return output_path


def mux(
    video_path: Path,
    audio_path: Path | None,
    output_path: Path,
) -> Path:
    """Mux video and audio into a final MP4."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if audio_path and audio_path.exists():
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path),
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-c:v", "copy",
            "-an",
            str(output_path),
        ]

    _run_ffmpeg(cmd, "mux")
    return output_path


def render(
    segment_path: Path,
    audio_path: Path | None,
    output_path: Path,
    target_duration: float,
    segment_duration: float,
) -> Path:
    """Full render pipeline: loop segment to duration, then mux with audio."""
    if target_duration > segment_duration:
        looped_path = output_path.with_suffix(".looped.mp4")
        loop_video(segment_path, target_duration, looped_path)
    else:
        looped_path = segment_path

    return mux(looped_path, audio_path, output_path)
