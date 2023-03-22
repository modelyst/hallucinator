"""Plot the data in a given output file from munge.py"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

DATA = (Path(__file__).parent.parent / "output/parsed_raw_data").glob("**/*.json")


def main():
    for file_name in DATA:
        with open(file_name) as f:
            data = json.load(f)
        wavelength = [x[0] for x in data]
        amplitude = [x[1] for x in data]
        fig, ax = plt.subplots(figsize=(20, 20))
        ax.plot(wavelength, amplitude)
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Amplitude")
        action_id = file_name.parent.name
        plt.title(f"{action_id} - {file_name.stem}")
        plt.show()


if __name__ == "__main__":
    main()
