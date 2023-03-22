from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import List, Optional

from hallucinator.hallucinate import ELEMENTS, LOWER_WAVELENGTH_RANGE, UPPER_WAVELENGTH_RANGE


DEFAULTS = {
    "num_spectra": 1000,
    "wavelength_min": LOWER_WAVELENGTH_RANGE,
    "wavelength_max": UPPER_WAVELENGTH_RANGE,
    "num_points": 1000,
    "elements": ELEMENTS,
    "max_fraction": 1.0,
    "min_elements": 1,
    "max_elements": 4,
    "peak_position_spread": 200,
    "peak_width": 20,
    "background_width": 1000,
    "background_center": 500,
    "background_level": 2,
    "noise_level": 0.1,
    "seed": None,
}


@dataclass
class Config:
    """Configuration for the hallucinator"""

    num_spectra: int = DEFAULTS["num_spectra"]
    wavelength_min: float = DEFAULTS["wavelength_min"]
    wavelength_max: float = DEFAULTS["wavelength_max"]
    num_points: int = DEFAULTS["num_points"]
    elements: List[str] = field(default_factory=lambda: DEFAULTS["elements"])
    max_fraction: float = DEFAULTS["max_fraction"]
    min_elements: int = DEFAULTS["min_elements"]
    max_elements: Optional[int] = DEFAULTS["max_elements"]
    peak_position_spread: float = DEFAULTS["peak_position_spread"]
    peak_width: float = DEFAULTS["peak_width"]
    background_width: float = DEFAULTS["background_width"]
    background_center: float = DEFAULTS["background_center"]
    background_level: float = DEFAULTS["background_level"]
    noise_level: float = DEFAULTS["noise_level"]
    seed: Optional[int] = DEFAULTS["seed"]

    @classmethod
    def from_file(cls, filename: Path):
        with open(filename, "r") as f:
            config = json.load(f)
        return cls(**config)

    def to_file(self, filename: Path):
        with open(filename, "w") as f:
            json.dump(self.__dict__, f, indent=4)
