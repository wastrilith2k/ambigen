"""Image generation via Gemini with placeholder fallback."""

import os
from pathlib import Path

from PIL import Image, ImageDraw


def generate_placeholder(width: int, height: int) -> Image.Image:
    """Generate a dark gradient placeholder image."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(20 + 15 * (y / height))
        g = int(15 + 10 * (y / height))
        b = int(30 + 20 * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def generate_image(
    prompt: str,
    width: int = 3840,
    height: int = 2160,
    cache_path: Path | None = None,
) -> Path:
    """Generate an image via Gemini, or fall back to a placeholder."""
    if cache_path and cache_path.exists():
        return cache_path

    if cache_path is None:
        cache_path = Path("cache/generated_bg.png")
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY set — using placeholder image.")
        img = generate_placeholder(width, height)
        img.save(cache_path)
        return cache_path

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.ImageGenerationModel("imagen-3.0-generate-002")
        result = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="16:9",
        )
        # Save the generated image
        result.images[0]._pil_image.save(cache_path)

        # Resize if needed
        img = Image.open(cache_path)
        if img.size != (width, height):
            img = img.resize((width, height), Image.LANCZOS)
            img.save(cache_path)

        return cache_path

    except Exception as e:
        print(f"Gemini generation failed: {e}")
        print("Falling back to placeholder image.")
        img = generate_placeholder(width, height)
        img.save(cache_path)
        return cache_path
