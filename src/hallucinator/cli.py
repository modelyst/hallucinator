import json
import logging
import random
from pathlib import Path
from typing import List

import numpy as np
import typer
from rich.progress import Progress
from hallucinator.config import DEFAULTS, Config

from hallucinator.hallucinate import (
    generate_peak_positions,
    generate_random_composition,
    hallucinator,
)
from hallucinator.plotter import plot_grid, plot_spectra_from_files
from hallucinator.utilities import console, stringify_composition

app = typer.Typer(
    name="Hallucinator",
    help="Generate hallucinated spectra",
    no_args_is_help=True,
)

logger = logging.getLogger("hallucinator")
state = {"info": 1}


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Disable all logging"),
):
    """Hallucinator: A Python library for generating UVIS hallucinations."""
    if verbose:
        logger.setLevel(logging.DEBUG)
        state["info"] = 2
    elif quiet:
        logger.setLevel(logging.CRITICAL)
        state["info"] = 0
    else:
        logger.setLevel(logging.INFO)


@app.command("plot")
def plot_hallucination_spectra(
    spectra_folder: Path = typer.Argument("output/hallucination_spectra", help="Folder containing spectra"),
    elements: List[str] = typer.Option(None, help="Elements to use", show_default=False),
    files: List[Path] = typer.Option(None, "--file", help="Files to use", show_default=False),
):
    """Plot hallucinated spectra in specified folder"""
    if files:
        status = plot_spectra_from_files(files, elements)
    elif not spectra_folder.exists():
        message = f"Folder {spectra_folder} does not exist. Did you run the `hallucinator generate` command?"
        typer.secho(message, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    else:
        status = plot_spectra_from_files(sorted(spectra_folder.glob("spectra_*.json")), elements)
    if status:
        # Raise an exception if the plotting failed
        message = f"Error plotting spectra from folder {spectra_folder}. No spectra found, did you run the `hallucinator generate` command?"
        typer.secho(message, fg=typer.colors.RED, err=True)
        raise typer.Exit(status)


@app.command("hallucinate")
def hallucinate(
    composition_file: Path = typer.Argument(..., help="File containing composition"),
    mapping_file: Path = typer.Option(..., "--mapping", help="Mapping file", show_default=False),
    config_file: Path = typer.Option(None, help="Configuration file", show_default=False),
    output_path: Path = typer.Option(Path("output/hallucinated_spectra.json"), "--output", help="Output directory"),
):
    """Hallucinate spectra from a composition file"""
    if not composition_file.exists():
        message = f"File {composition_file} does not exist."
        typer.secho(message, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(composition_file) as f:
        composition = json.load(f)

    config = Config.from_file(config_file) if config_file else Config()
    if not mapping_file or not mapping_file.exists():
        mapping = generate_peak_positions(config.seed, config.peak_position_spread, config.peak_position_spread)
    else:
        with open(mapping_file) as f:
            mapping = json.load(f)

    wavelength = np.linspace(config.wavelength_min, config.wavelength_max, config.num_points)
    amplitude = hallucinator(
        wavelength,
        composition,
        peak_positions=mapping,
        peak_width=config.peak_width,
        background_width=config.background_width,
        background_level=config.background_level,
    )
    spectra_data = {
        "random_seed": config.seed,
        "composition": composition,
        "label": stringify_composition(
            composition,
        ),
        "wavelength": wavelength.tolist(),
        "amplitude": amplitude.tolist(),
    }
    # Write output
    with open(output_path, "w") as f:
        json.dump(spectra_data, f, indent=4)
    logger.info(f"Generated hallucinated spectra for {stringify_composition(composition)}")
    logger.info(f"Output written to {output_path}")
    logger.info(f"Please run `hallucinator plot --file {output_path}` to view the generated spectra")


@app.command("compare-spectra")
def compare_plots(
    files: List[Path] = typer.Argument(..., help="Files to compare"),
):
    """Compare plots"""
    files = sorted(filter(lambda x: x.exists(), files))
    if len(files) < 2:
        message = "Please provide at least two files to compare"
        typer.secho(message, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    plot_grid(files)


@app.command("generate")
def generate_hallucinated_spectra(
    output_dir: Path = typer.Option(Path("output/hallucinated_spectra"), "--output", help="Output directory"),
    num_spectra: int = typer.Option(DEFAULTS["num_spectra"], "--num", "-n", help="Number of spectra to generate"),
    wavelength_min: float = typer.Option(DEFAULTS["wavelength_min"], "--upper", help="Minimum wavelength"),
    wavelength_max: float = typer.Option(DEFAULTS["wavelength_max"], "--lower", help="Maximum wavelength"),
    num_points: int = typer.Option(DEFAULTS["num_points"], "--resolution", help="Number of points per spectrum"),
    elements: List[str] = typer.Option(
        DEFAULTS["elements"], "--element", "-e", help="Elements to use", show_default=False
    ),
    max_fraction: float = typer.Option(
        DEFAULTS["max_fraction"], "--max-fraction", help="Maximum fraction of any element"
    ),
    min_elements: int = typer.Option(DEFAULTS["min_elements"], "--max-elem", help="Minimum number of elements"),
    max_elements: int = typer.Option(DEFAULTS["max_elements"], "--min-elem", help="Maximum number of elements"),
    peak_position_spread: float = typer.Option(
        DEFAULTS["peak_position_spread"], "--peak-spread", help="spread of peak positions"
    ),
    peak_width: float = typer.Option(
        DEFAULTS["peak_width"], "--peak-width", help="Standard deviation of element peaks"
    ),
    background_width: float = typer.Option(
        DEFAULTS["background_width"], "-bw", "--background-width", help="Width of background"
    ),
    background_center: float = typer.Option(
        DEFAULTS["background_center"], "-bc", "--background-center", help="Center of background"
    ),
    background_level: float = typer.Option(
        DEFAULTS["background_level"], "-bl", "--background-level", help="Level of background"
    ),
    noise_level: float = typer.Option(DEFAULTS["noise_level"], "--noise", help="Level of noise"),
    seed: int = typer.Option(DEFAULTS["seed"], help="Random seed"),
    config_file: Path = typer.Option(None, "--config", help="Configuration file"),
):
    """
    Generate hallucinated spectra

    The spectra are generated using a Gaussian mixture model with a background
    and noise. The background is a Gaussian with a given width and level. The
    noise is a Gaussian with a given level. The Gaussian mixture model is
    generated using a random number of Gaussian peaks with a given width and
    random centers and amplitudes. The amplitudes are randomly generated from a
    uniform distribution between 0 and 1. The centers are randomly generated
    from a uniform distribution between the minimum and maximum wavelength. The
    number of peaks is randomly generated from a uniform distribution between
    the minimum and maximum number of elements. The elements are randomly
    selected from the list of elements provided. The fractions of each element
    are randomly generated from a uniform distribution between 0 and the
    maximum fraction. The composition is then normalized to sum to 1. The
    spectra are then plotted and saved to a folder.
    """

    # read config file if provided
    if config_file is not None:
        logger.info(f"Reading configuration from {config_file}, ignoring all arguments passed in")
        config = Config.from_file(config_file)
        num_spectra = config.num_spectra
        wavelength_min = config.wavelength_min
        wavelength_max = config.wavelength_max
        num_points = config.num_points
        elements = config.elements
        max_fraction = config.max_fraction
        min_elements = config.min_elements
        max_elements = config.max_elements
        peak_position_spread = config.peak_position_spread
        peak_width = config.peak_width
        background_width = config.background_width
        background_center = config.background_center
        background_level = config.background_level
        noise_level = config.noise_level
        seed = config.seed

    # Set random seed
    if seed is not None:
        logger.debug(f"Setting random seed to {seed}")
        np.random.seed(seed)
        random.seed(seed)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    # Generate peak positions
    mapping = generate_peak_positions(seed=seed, peak_position_spread=peak_position_spread)

    logger.info(f"Generating {num_spectra} hallucinated spectra")
    with Progress(console=console, disable=state["info"] < 1) as progress:
        task = progress.add_task("Generating Spectra", total=num_spectra)
        for i in range(num_spectra):
            composition = generate_random_composition(elements, max_fraction, min_elements, max_elements)
            wavelengths = np.linspace(wavelength_min, wavelength_max, num_points)
            amplitude = hallucinator(
                wavelengths,
                composition,
                mapping,
                peak_width=peak_width,
                background_center=background_center,
                background_width=background_width,
                background_level=background_level,
                noise_level=noise_level,
            )
            spectra_data = {
                "random_seed": seed,
                "composition": composition,
                "label": stringify_composition(
                    composition,
                ),
                "wavelength": wavelengths.tolist(),
                "amplitude": amplitude.tolist(),
            }
            spectra_path = output_dir / f"spectra_{i}.json"
            with open(spectra_path, "w") as f:
                json.dump(spectra_data, f, indent=4)
            progress.update(task, advance=1)

    # Write out the parameters used to generate the spectra
    config_used = Config(
        num_spectra=num_spectra,
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
        num_points=num_points,
        elements=elements,
        max_fraction=max_fraction,
        min_elements=min_elements,
        max_elements=max_elements,
        peak_position_spread=peak_position_spread,
        peak_width=peak_width,
        background_width=background_width,
        background_center=background_center,
        background_level=background_level,
        noise_level=noise_level,
        seed=seed,
    )
    config_used_path = output_dir / "hallucination_parameters.json"
    config_used.to_file(config_used_path)

    # Save mapping used
    mapping_path = output_dir / "mapping.json"
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=4)

    logger.info(f"Generated {num_spectra} hallucinated spectra")
    logger.info(f"Saved hallucinated spectra to {output_dir}")
    command = (
        f"hallucinator plot {output_dir}" if output_dir != Path("output/hallucination_spectra") else "hallucinator plot"
    )
    logger.info(f"Run `{command}` to plot the hallucinated spectra")


if __name__ == "__main__":
    typer.run(app)
