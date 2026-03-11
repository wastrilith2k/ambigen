"""Click CLI — commands: generate, quick, new-recipe, suno-prompt, suno-link, batch, validate."""

from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ambigen.config import load_recipe

console = Console()


@click.group()
@click.version_option(package_name="ambigen")
def cli():
    """ambigen — Generate ambient YouTube videos from YAML recipes."""


@cli.command()
@click.argument("recipe_path", type=click.Path(exists=True))
@click.option("--preview", is_flag=True, help="Generate a 30-second preview instead of full duration.")
@click.option("--skip-image", is_flag=True, help="Use placeholder image (skip Gemini API call).")
@click.option("--no-audio", is_flag=True, help="Generate video without audio.")
@click.option("--dry-run", is_flag=True, help="Show what would be generated without doing it.")
def generate(recipe_path: str, preview: bool, skip_image: bool, no_audio: bool, dry_run: bool):
    """Generate an ambient video from a YAML recipe."""
    recipe = load_recipe(recipe_path)
    duration = 30 if preview else recipe.duration_seconds
    segment_duration = recipe.animation.duration_seconds

    if dry_run:
        _print_dry_run(recipe, duration)
        return

    console.print(f"[bold]Generating:[/bold] {recipe.name}")
    console.print(f"  Duration: {duration}s ({'preview' if preview else f'{recipe.duration_hours}hr'})")

    # Step 1: Image
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Generating image...", total=None)

        from ambigen.image_gen import generate_image, generate_placeholder

        cache_path = Path(f"cache/{recipe.safe_name}_bg.png")
        if skip_image:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            img = generate_placeholder(recipe.image.width, recipe.image.height)
            img.save(cache_path)
            image_path = cache_path
        else:
            image_path = generate_image(
                prompt=recipe.image.prompt,
                width=recipe.image.width,
                height=recipe.image.height,
                cache_path=cache_path,
            )

    console.print(f"  Image: {image_path}")

    # Step 2: Animate
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Animating (Ken Burns)...", total=None)

        from ambigen.animator import animate

        segment_path = Path(f"cache/{recipe.safe_name}_segment.mp4")
        animate(
            image_path=image_path,
            output_path=segment_path,
            duration=segment_duration,
            fps=recipe.animation.fps,
            zoom_min=recipe.animation.zoom_range[0],
            zoom_max=recipe.animation.zoom_range[1],
            easing=recipe.animation.easing,
            output_width=recipe.output_resolution[0],
            output_height=recipe.output_resolution[1],
        )

    console.print(f"  Segment: {segment_path} ({segment_duration}s)")

    # Step 3: Audio
    audio_path = None
    if not no_audio and recipe.audio.layers:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task("Mixing audio...", total=None)

            from ambigen.audio_mixer import mix_audio

            audio_path = Path(f"cache/{recipe.safe_name}_audio.m4a")
            layers = [{"file": layer.file, "volume": layer.volume} for layer in recipe.audio.layers]
            try:
                mix_audio(
                    layers=layers,
                    output_path=audio_path,
                    duration=duration,
                    fade_out_seconds=recipe.audio.fade_out_seconds,
                )
                console.print(f"  Audio: {audio_path}")
            except (FileNotFoundError, RuntimeError) as e:
                console.print(f"  [yellow]Audio skipped:[/yellow] {e}")
                audio_path = None

    # Step 4: Render
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Rendering final video...", total=None)

        from ambigen.renderer import render

        output_dir = Path(recipe.output_dir)
        suffix = "preview" if preview else f"{recipe.duration_hours}hr"
        output_path = output_dir / f"{recipe.safe_name}_{suffix}.mp4"

        render(
            segment_path=segment_path,
            audio_path=audio_path,
            output_path=output_path,
            target_duration=duration,
            segment_duration=segment_duration,
        )

    console.print(f"\n[bold green]Done![/bold green] {output_path}")


@cli.command()
@click.argument("recipe_path", type=click.Path(exists=True))
def quick(recipe_path: str):
    """Generate a 30-second preview with placeholder image and no audio."""
    from click.testing import CliRunner
    runner = CliRunner()
    runner.invoke(generate, [recipe_path, "--preview", "--skip-image", "--no-audio"])


@cli.command("new-recipe")
@click.argument("name")
@click.option("--output-dir", default="presets", help="Directory to save the recipe.")
def new_recipe(name: str, output_dir: str):
    """Create a new recipe YAML template."""
    import yaml

    safe_name = name.lower().replace(" ", "_")
    path = Path(output_dir) / f"{safe_name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)

    template = {
        "name": name,
        "description": f"Ambient {name} scene",
        "duration_hours": 1,
        "image": {
            "prompt": f"A beautiful {name.lower()} scene, photorealistic, 4K, ambient lighting",
            "width": 3840,
            "height": 2160,
            "style": "photorealistic",
        },
        "animation": {
            "duration_seconds": 30,
            "fps": 30,
            "zoom_range": [1.0, 1.3],
            "easing": "ease_in_out",
        },
        "audio": {
            "layers": [],
            "fade_out_seconds": 3.0,
        },
        "output_resolution": [1920, 1080],
    }

    with open(path, "w") as f:
        yaml.dump(template, f, default_flow_style=False, sort_keys=False)

    console.print(f"Created recipe: {path}")


@cli.command("suno-prompt")
@click.argument("recipe_path", type=click.Path(exists=True))
def suno_prompt(recipe_path: str):
    """Generate a Suno prompt for ambient music matching a recipe."""
    from ambigen.suno import generate_suno_prompt

    recipe = load_recipe(recipe_path)
    prompt = generate_suno_prompt(recipe.name, recipe.description)
    console.print("[bold]Suno prompt:[/bold]")
    console.print(prompt)
    console.print("\n[dim]Copy this into Suno's web interface to generate matching audio.[/dim]")


@cli.command("suno-link")
@click.argument("recipe_path", type=click.Path(exists=True))
@click.argument("audio_dir", type=click.Path(exists=True))
def suno_link(recipe_path: str, audio_dir: str):
    """Scan an audio directory and show files available for a recipe."""
    from ambigen.suno import scan_audio_dir

    recipe = load_recipe(recipe_path)
    files = scan_audio_dir(audio_dir)

    console.print(f"[bold]Audio files for {recipe.name}:[/bold]")
    if files:
        for f in files:
            console.print(f"  {f}")
    else:
        console.print("  [yellow]No audio files found.[/yellow]")


@cli.command()
@click.argument("preset_dir", type=click.Path(exists=True))
@click.option("--preview", is_flag=True, help="Generate 30-second previews.")
@click.option("--skip-image", is_flag=True, help="Use placeholder images.")
@click.option("--no-audio", is_flag=True, help="Skip audio mixing.")
def batch(preset_dir: str, preview: bool, skip_image: bool, no_audio: bool):
    """Generate videos for all recipes in a directory."""
    preset_path = Path(preset_dir)
    yamls = sorted(preset_path.glob("*.yaml"))

    if not yamls:
        console.print(f"[yellow]No .yaml files found in {preset_dir}[/yellow]")
        return

    console.print(f"[bold]Batch generating {len(yamls)} recipes...[/bold]\n")
    for yaml_file in yamls:
        console.print(f"--- {yaml_file.name} ---")
        from click import Context
        ctx = Context(generate)
        ctx.invoke(generate, recipe_path=str(yaml_file), preview=preview, skip_image=skip_image, no_audio=no_audio, dry_run=False)
        console.print()


@cli.command()
@click.argument("recipe_path", type=click.Path(exists=True))
def validate(recipe_path: str):
    """Validate a recipe file and check for issues."""
    recipe = load_recipe(recipe_path)

    console.print(f"[green]\u2713[/green] Recipe: {recipe.name}")
    console.print(f"[green]\u2713[/green] Image prompt: {len(recipe.image.prompt.split())} words")

    for layer in recipe.audio.layers:
        if Path(layer.file).exists():
            console.print(f"[green]\u2713[/green] Audio: {layer.file}")
        else:
            console.print(f"[yellow]\u26a0[/yellow] Audio file not found: {layer.file}")

    total_seconds = recipe.duration_seconds
    w, h = recipe.output_resolution
    console.print(f"[green]\u2713[/green] Output: {total_seconds}s @ {w}x{h}")


def _print_dry_run(recipe, duration):
    """Print what would be generated without doing it."""
    console.print(f"[bold]Recipe:[/bold] {recipe.name}")
    console.print(f"[bold]Duration:[/bold] {recipe.duration_hours} hours ({duration}s)")
    console.print(
        f"[bold]Image:[/bold] {recipe.image.width}x{recipe.image.height}, "
        f"prompt: \"{recipe.image.prompt[:60]}...\""
    )
    console.print(
        f"[bold]Animation:[/bold] Ken Burns, {recipe.animation.duration_seconds}s segment, "
        f"{recipe.animation.easing}"
    )
    for layer in recipe.audio.layers:
        console.print(f"[bold]Audio layer:[/bold] {layer.file} ({layer.volume})")
    output_name = f"{recipe.safe_name}_{recipe.duration_hours}hr.mp4"
    console.print(f"[bold]Output:[/bold] {recipe.output_dir}/{output_name}")
    console.print("\n[dim](dry run — nothing generated)[/dim]")
