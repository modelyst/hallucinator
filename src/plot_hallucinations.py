import os
import json
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Increase the default font size
plt.rcParams.update({"font.size": 30})


def plot_spectra_from_folder(folder):
    # Get the list of composition files in the folder
    composition_files = sorted(
        [
            f
            for f in os.listdir(folder)
            if f.startswith("spectra_") and f.endswith(".json")
        ]
    )

    # Create the figure and axes for the plot
    fig, ax = plt.subplots(figsize=(20, 20))
    plt.subplots_adjust(left=0.25, bottom=0.25)

    # Set the initial composition index and load the corresponding spectrum data
    initial_index = 0
    composition_file = os.path.join(folder, composition_files[initial_index])
    with open(composition_file, "r") as f:
        composition_data = json.load(f)
    spectrum_file = os.path.join(folder, f"spectra_{initial_index}.json")
    with open(spectrum_file, "r") as f:
        spectrum_data = json.load(f)

    # Plot the initial spectrum
    wavelength = spectrum_data["wavelengths"]
    amplitude = spectrum_data["amplitude"]
    (line,) = ax.plot(wavelength, amplitude)

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
    def update(val):
        index = int(slider.val)
        composition_file = os.path.join(folder, composition_files[index])
        with open(composition_file, "r") as f:
            composition_data = json.load(f)
        spectrum_file = os.path.join(folder, f"spectra_{index}.json")
        with open(spectrum_file, "r") as f:
            spectrum_data = json.load(f)
        wavelength = spectrum_data["wavelengths"]
        amplitude = spectrum_data["amplitude"]
        line.set_data(wavelength, amplitude)
        ax.set_title(composition_data["label"])
        fig.canvas.draw_idle()

    # Connect the slider to the update function
    slider.on_changed(update)

    # Set the plot title and axis labels
    ax.set_title(composition_data["label"])
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Amplitude")
    ax.set_ylim(0, 15)
    ax.set_xlim(300, 1100)
    # Slant the x-axis labels
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment("right")

    # Show the plot
    plt.show()


if __name__ == "__main__":
    plot_spectra_from_folder("output/hallucination_spectra")
