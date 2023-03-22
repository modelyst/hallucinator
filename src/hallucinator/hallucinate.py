import random
from typing import Dict, List, Optional, Tuple

import numpy as np

UPPER_WAVELENGTH_RANGE = 1100
LOWER_WAVELENGTH_RANGE = 300
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


def generate_peak_positions(
    seed: int,
    peak_mean: Optional[float] = None,
    peak_position_spread: float = 300,
) -> dict:
    """
    Generate the peak positions for the elements.

    Args:
        seed (int): The random seed to use for generating the peak positions.
        peak_mean (float, optional): The mean peak position. If not specified,
            the mean is set to the middle of the wavelength range.
        peak_position_spread (float, optional): The standard deviation of the peak positions.

    Returns:
        dict: A dictionary mapping each element to its peak position, as a tuple of two floats representing
          the mean and amplitude.

    Example:
        >>> generate_peak_positions(seed=42)
        {
            'H': (720.7892917649954, 10.06152364861703),
            'He': (532.3732090136972, 9.090188469221164),
            'Li': (880.2925422806788, 10.047347253058453),
            ...
        }
    """
    np.random.seed(seed)
    peak_mean = peak_mean or (UPPER_WAVELENGTH_RANGE + LOWER_WAVELENGTH_RANGE) / 2
    atomic_numbers = list(range(1, len(ELEMENTS) + 1))
    expected_peak_positions = np.random.normal(
        loc=peak_mean,
        scale=peak_position_spread,
        size=len(atomic_numbers),
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
    wavelengths: np.ndarray,
    composition: Dict[str, float],
    peak_positions: Dict[str, Tuple[float, float]],
    peak_width: float = 0.5,
    noise_level: float = 0.05,
    background_center: Optional[float] = None,
    background_level: float = 0.01,
    background_width: float = 100,
) -> np.ndarray:
    """
    Generate a hallucinated spectrum.

    Args:
        wavelengths (np.ndarray): The wavelengths at which to generate the spectrum.
        composition (Dict[str, float]): A dictionary of element compositions, where each key is an element symbol and
            each value is the fraction of that element in the composition.
        peak_positions (Dict[str, Tuple[float, float]]): A dictionary mapping each element to its peak position and
            height, as a tuple of two floats representing the mean and standard deviation.
        peak_width (float, optional): The standard deviation of the element peaks.
        noise_level (float, optional): The level of Gaussian noise to add to the spectrum.
        background_center (float, optional): The center of the Gaussian background component. If not specified, it is
            set to a random value drawn from a normal distribution with a mean of the mean of the wavelengths and a
            standard deviation of 200.
        background_level (float, optional): The level of the Gaussian background component.
        background_width (float, optional): The width of the Gaussian background component.

    Returns:
        np.ndarray: An array of amplitudes representing the hallucinated spectrum.

    Example:
        >>> wavelengths = np.linspace(300, 1100, 1000)
        >>> composition = {'H': 0.5, 'He': 0.5}
        >>> peak_positions = {'H': (656.3, 1), 'He': (587.6, 1)}
        >>> amplitudes = hallucinator(wavelengths, composition, peak_positions)
    """
    amplitudes = np.zeros_like(wavelengths)
    for elem in composition:
        peak_pos, peak_height = peak_positions.get(elem, (None, None))
        if peak_pos is not None and peak_height is not None:
            amplitude = peak_height * np.exp(-((wavelengths - peak_pos) ** 2) / (2 * peak_width**2))
            amplitude += np.random.normal(0, noise_level, size=amplitude.shape)
            amplitudes += composition[elem] * amplitude

    # Generate background component
    background_center = background_center or np.random.normal(np.mean(wavelengths), scale=200)
    background = background_level * np.exp(-((wavelengths - background_center) ** 2) / (2 * background_width**2))
    background += np.random.normal(0, noise_level, size=background.shape)
    amplitudes += background
    return amplitudes


def generate_random_composition(
    elements: List[str],
    max_fraction: float = 1.0,
    min_elements: int = 1,
    max_elements: Optional[int] = None,
    seed: Optional[int] = None,
) -> Dict[str, float]:
    """
    Generate a random element composition.

    Args:
        elements (List[str]): A list of element symbols to choose from.
        max_fraction (float, optional): The maximum fraction of any element in the composition.
        min_elements (int, optional): The minimum number of elements in the composition.
        max_elements (int, optional): The maximum number of elements in the composition. If not specified, it is set
            to the length of the `elements` list.
        seed (int, optional): The random seed to use for reproducibility.

    Returns:
        Dict[str, float]: A dictionary of element compositions, where each key is an element symbol and each value is
        the fraction of that element in the composition.

    Example:
        >>> elements = ['H', 'He', 'C', 'N', 'O']
        >>> composition = generate_random_composition(elements, max_fraction=0.5, min_elements=2, max_elements=3)
        >>> print(composition)
        {'H': 0.3221916697410883, 'C': 0.05945419863492032, 'N': 0.6183541316249915}
    """
    if seed is not None:
        random.seed(seed)
    if max_elements is None or max_elements > len(elements):
        max_elements = len(elements)
    num_elements = random.randint(min_elements, max_elements)
    elements = random.sample(elements, num_elements)
    fractions = [random.uniform(0, max_fraction) for _ in range(num_elements)]
    total_fraction = sum(fractions)
    fractions = [fraction / total_fraction for fraction in fractions]
    composition = {element: fraction for element, fraction in zip(elements, fractions)}
    return composition
