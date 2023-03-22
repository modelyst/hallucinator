import json
import os
from pathlib import Path
import random

import matplotlib.pyplot as plt
import numpy as np
from torch import rand

UPPER_RANGE = 1100
LOWER_RANGE = 300
ELEMENTS = [
    "H",
    "He",
    "Li",
    "Be",
    "B",
    "C",
    "N",
    "O",
    "F",
    "Ne",
    "Na",
    "Mg",
    "Al",
    "Si",
    "P",
    "S",
    "Cl",
    "Ar",
    "K",
    "Ca",
    "Sc",
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Cu",
    "Zn",
    "Ga",
    "Ge",
    "As",
    "Se",
    "Br",
    "Kr",
    "Rb",
    "Sr",
    "Y",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Ag",
    "Cd",
    "In",
    "Sn",
    "Sb",
    "Te",
    "I",
    "Xe",
    "Cs",
    "Ba",
    "La",
    "Ce",
    "Pr",
    "Nd",
    "Pm",
    "Sm",
    "Eu",
    "Gd",
    "Tb",
    "Dy",
    "Ho",
    "Er",
    "Tm",
    "Yb",
    "Lu",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
    "Au",
    "Hg",
    "Tl",
    "Pb",
    "Bi",
    "Th",
    "Pa",
    "U",
    "Np",
    "Pu",
    "Am",
    "Cm",
    "Bk",
    "Cf",
    "Es",
    "Fm",
    "Md",
    "No",
    "Lr",
]


def generate_peak_positions(seed):
    np.random.seed(seed)
    atomic_numbers = list(range(1, len(ELEMENTS) + 1))
    expected_peak_positions = np.random.normal(
        loc=(UPPER_RANGE + LOWER_RANGE) / 2, scale=300, size=len(atomic_numbers)
    )
    peak_positions = {
        element: (
            expected_peak_positions[atomic_numbers.index(atomic_number)],
            np.random.normal(10, scale=3),
        )
        for element, atomic_number in zip(ELEMENTS, atomic_numbers)
    }
    return peak_positions


def hallucinator(
    wavelengths,
    composition,
    peak_positions,
    peak_width=0.5,
    noise_level=0.05,
    background_center=None,
    background_level=0.01,
    background_width=100,
):
    amplitudes = np.zeros_like(wavelengths)
    for elem in composition:
        peak_pos, peak_height = peak_positions.get(elem, (None, None))
        if peak_pos is not None and peak_height is not None:
            amplitude = peak_height * np.exp(
                -((wavelengths - peak_pos) ** 2) / (2 * peak_width**2)
            )
            amplitude += np.random.normal(0, noise_level, size=amplitude.shape)
            amplitudes += composition[elem] * amplitude

    # Generate background component
    background_center = background_center or np.random.normal(
        np.mean(wavelengths), scale=200
    )
    background = background_level * np.exp(
        -((wavelengths - background_center) ** 2) / (2 * background_width**2)
    )
    background += np.random.normal(0, noise_level, size=background.shape)
    amplitudes += background

    # amplitudes = np.clip(amplitudes, 0, 20)
    return amplitudes


def stringify_composition(composition):
    elements = list(composition.keys())
    fractions = [f"{fraction:.2f}" for fraction in composition.values()]
    composition_str = ""
    for element, fraction in sorted(zip(elements, fractions)):
        composition_str += "{%s}_{%s} " % (element, fraction)
    composition_str = "$" + composition_str.strip() + "$"
    return composition_str


def generate_hallucination_plots(
    wavelength_min,
    wavelength_max,
    num_points,
    compositions,
    mapping,
    seed=None,
):
    if seed is not None:
        np.random.seed(seed)

    num_compositions = len(compositions)
    num_cols = min(num_compositions, 5)
    num_rows = 1 + (num_compositions - 1) // num_cols

    fig, axs = plt.subplots(
        nrows=num_rows, ncols=num_cols, figsize=(5 * num_cols, 5 * num_rows), hspace=0.4
    )

    for i in range(num_compositions):
        row_idx = i // num_cols
        col_idx = i % num_cols
        composition = compositions[i]
        wavelengths = np.linspace(wavelength_min, wavelength_max, num_points)
        amplitude = hallucinator(
            wavelengths,
            composition,
            mapping,
            peak_width=20,
            background_width=1000,
            background_level=2,
        )
        if num_rows == 1:
            axs[col_idx].plot(wavelengths, amplitude)
            axs[col_idx].set_title(stringify_composition(composition))
            axs[col_idx].set_xlabel("Wavelength (nm)")
            axs[col_idx].set_ylabel("Amplitude")
        else:
            axs[row_idx, col_idx].plot(wavelengths, amplitude)
            axs[row_idx, col_idx].set_title(stringify_composition(composition))
            axs[row_idx, col_idx].set_xlabel("Wavelength (nm)")
            axs[row_idx, col_idx].set_ylabel("Amplitude")

    for i in range(num_compositions, num_rows * num_cols):
        row_idx = i // num_cols
        col_idx = i % num_cols
        if num_rows == 1:
            axs[col_idx].axis("off")
        else:
            axs[row_idx, col_idx].axis("off")

    plt.tight_layout()
    plt.show()


def generate_random_composition(
    elements, max_fraction=1.0, min_elements=1, max_elements=None, seed=None
):
    if seed is not None:
        random.seed(seed)
    if max_elements is None:
        max_elements = len(elements)
    num_elements = random.randint(min_elements, max_elements)
    elements = random.sample(elements, num_elements)
    fractions = [random.uniform(0, max_fraction) for _ in range(num_elements)]
    total_fraction = sum(fractions)
    fractions = [fraction / total_fraction for fraction in fractions]
    composition = {element: fraction for element, fraction in zip(elements, fractions)}
    return composition


def main():
    random.seed(0)
    compositions = [
        generate_random_composition(
            ELEMENTS, max_fraction=1.0, min_elements=1, max_elements=4
        )
        for _ in range(25)
    ]
    generate_hallucination_plots(
        wavelength_max=UPPER_RANGE,
        wavelength_min=LOWER_RANGE,
        num_points=1000,
        compositions=compositions,
        mapping=generate_peak_positions(0),
    )


def save_hallucination_spectra(
    output_dir,
    num_spectra,
    wavelength_min,
    wavelength_max,
    num_points,
    elements,
    max_fraction,
    min_elements,
    max_elements,
    mapping,
    background_width=100,
    background_center=None,
    seed=None,
):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    os.makedirs(output_dir, exist_ok=True)

    for i in range(num_spectra):
        composition = generate_random_composition(
            elements, max_fraction, min_elements, max_elements
        )
        wavelengths = np.linspace(wavelength_min, wavelength_max, num_points)
        amplitude = hallucinator(
            wavelengths,
            composition,
            mapping,
            peak_width=20,
            background_center=background_center,
            background_width=background_width,
            background_level=2,
            noise_level=0.1,
        )
        spectra_data = {
            "compositition": composition,
            "label": stringify_composition(
                composition,
            ),
            "wavelengths": wavelengths.tolist(),
            "amplitude": amplitude.tolist(),
        }
        spectra_path = os.path.join(output_dir, f"spectra_{i}.json")
        with open(spectra_path, "w") as f:
            json.dump(spectra_data, f, indent=4)


def plot_spectra_file(path: Path):
    with open(path, "r") as f:
        data = json.load(f)
    wavelengths = np.array(data["wavelengths"])
    amplitudes = np.array(data["amplitude"])
    plt.plot(wavelengths, amplitudes)
    plt.title(data["label"])
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Amplitude")
    plt.show()


if __name__ == "__main__":

    # plot_spectra_file(Path("data/hallucination_spectra/spectra_0.json"))
    config = {
        "output_dir": "output/hallucination_spectra",
        "num_spectra": 1000,
        "wavelength_min": LOWER_RANGE,
        "wavelength_max": UPPER_RANGE,
        "num_points": 1000,
        "elements": ELEMENTS,
        "max_fraction": 1.0,
        "min_elements": 2,
        "max_elements": 4,
        "mapping": generate_peak_positions(0),
        "background_width": 500,
        "seed": 0,
    }
    save_hallucination_spectra(**config)
    # main()
