import json
import logging
from functools import reduce
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Increase the default font size
plt.rcParams.update({"font.size": 30})

logger = logging.getLogger(__name__)


def read_spectra(spectrum_file: Path):
    """Read the spectra from a file"""
    with open(spectrum_file, "r") as f:
        spectrum_data = json.load(f)
    return spectrum_data


def plot_spectra_from_files(composition_files: List[Path], elements: Optional[List[str]] = None):
    """Plot the spectra from a folder"""
    if len(composition_files) == 0:
        logger.error("No composition files found.")
        return 1
    spectra_values = {composition_file: read_spectra(composition_file) for composition_file in composition_files}
    reducer = lambda compare, initial_value: lambda key: reduce(
        lambda prev_val, composition_file: compare(compare(spectra_values[composition_file][key]), prev_val),
        composition_files,
        initial_value,
    )
    # get max y value
    get_max = reducer(max, 0)
    get_min = reducer(min, float("inf"))
    max_x = get_max("wavelength")
    min_x = get_min("wavelength")

    max_y = get_max("amplitude")
    min_y = get_min("amplitude")

    # Get the list of composition files in the folder
    logger.info(f"Found {len(composition_files)} composition files")

    if elements:
        logger.info(f"Filtering composition files by elements: {', '.join(elements)}")
        # Read all the composition files in the folder and only keep the ones with the specified elements
        composition_files = list(
            filter(
                lambda composition_file: all(
                    map(
                        lambda x: x in spectra_values[composition_file]["composition"],
                        elements,
                    )
                ),
                composition_files,
            )
        )
        logger.info(f"Found {len(composition_files)} composition files after filtering")
        if len(composition_files) == 0:
            logger.error("No composition files found after filtering")
            return

    # Create the figure and axes for the plot
    fig, ax = plt.subplots(figsize=(20, 20))
    plt.subplots_adjust(left=0.25, bottom=0.25)

    # Set the initial composition index and load the corresponding spectrum data
    initial_index = 0
    composition_file = composition_files[initial_index]
    spectrum_data = read_spectra(composition_file)
    wavelength = spectrum_data["wavelength"]
    amplitude = spectrum_data["amplitude"]
    label = spectrum_data["label"]
    (line,) = ax.plot(wavelength, amplitude)

    # Create the slider for selecting the composition index
    if len(composition_files) > 1:
        # Create the slider for selecting the composition index
        slider_ax = plt.axes([0.25, 0.1, 0.65, 0.03])
        slider = Slider(
            slider_ax,
            "Spectra Index",
            0,
            len(composition_files) - 1,
            valinit=initial_index,
            valstep=1,
        )

        # Define the update function for the slider
        def update(_val):
            index = int(slider.val)
            composition_file = composition_files[index]
            spectrum_data = spectra_values[composition_file]
            wavelength = spectrum_data["wavelength"]
            amplitude = spectrum_data["amplitude"]
            label = spectrum_data["label"]
            line.set_data(wavelength, amplitude)
            ax.set_title(label)
            fig.canvas.draw_idle()

        # Connect the slider to the update function
        slider.on_changed(update)

    # Set the plot title and axis labels
    ax.set_title(label)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Amplitude")
    ax.set_ylim(min_y, max_y + 1)
    ax.set_xlim(min_x, max_x)
    # Slant the x-axis labels
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment("right")

    # Show the plot
    plt.show()
    return 0


def plot_grid(composition_files: List[Path], elements: Optional[List[str]] = None):
    """Plot the spectra from a folder"""
    if len(composition_files) == 0:
        logger.error("No composition files found.")
        return 1
    spectra_values = {composition_file: read_spectra(composition_file) for composition_file in composition_files}

    reducer = lambda compare, initial_value: lambda key: reduce(
        lambda prev_val, composition_file: compare(compare(spectra_values[composition_file][key]), prev_val),
        composition_files,
        initial_value,
    )
    # get max y value
    get_max = reducer(max, 0)
    get_min = reducer(min, float("inf"))
    max_x = get_max("wavelength")
    min_x = get_min("wavelength")

    max_y = get_max("amplitude")
    min_y = get_min("amplitude")

    # Get the list of composition files in the folder
    logger.info(f"Found {len(composition_files)} composition files")

    if elements:
        logger.info(f"Filtering composition files by elements: {', '.join(elements)}")
        # Read all the composition files in the folder and only keep the ones with the specified elements
        composition_files = list(
            filter(
                lambda composition_file: all(
                    map(
                        lambda x: x in spectra_values[composition_file]["composition"],
                        elements,
                    )
                ),
                composition_files,
            )
        )
        logger.info(f"Found {len(composition_files)} composition files after filtering")
        if len(composition_files) == 0:
            logger.error("No composition files found after filtering")
            return

    # Determine the number of rows and columns in the grid
    num_files = len(composition_files)
    num_cols = min(num_files, 5)
    num_rows = (num_files + num_cols - 1) // num_cols

    # Create the figure and axes for the plot
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(40, 20))
    plt.subplots_adjust(left=0.1, bottom=0.25, right=0.9)

    # Plot each spectrum in the grid
    for i, composition_file in enumerate(composition_files):
        row = i // num_cols
        col = i % num_cols
        ax = axs[row, col] if num_rows > 1 else axs[col]
        spectrum_data = spectra_values[composition_file]
        wavelength = spectrum_data["wavelength"]
        amplitude = spectrum_data["amplitude"]
        label = spectrum_data["label"]
        ax.plot(wavelength, amplitude)
        ax.set_title(f"{composition_file.parent.name}\n{label}")
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Amplitude")
        ax.set_ylim(min_y, max_y + 1)
        ax.set_xlim(min_x, max_x)
        # Slant the x-axis labels
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment("right")

    # Show the plot
    plt.show()
    return 0
