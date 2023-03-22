import logging
from typing import Dict
from rich.logging import RichHandler
from rich.console import Console

console = Console()


def stringify_composition(composition: Dict[str, float]):
    elements = list(composition.keys())
    fractions = [f"{fraction:.2f}" for fraction in composition.values()]
    composition_str = ""
    for element, fraction in sorted(zip(elements, fractions)):
        composition_str += "{%s}_{%s} " % (element, fraction)
    composition_str = "$" + composition_str.strip() + "$"
    return composition_str


def setup_logging():
    # Create a logger for the package
    pkg_logger = logging.getLogger("hallucinator")
    pkg_logger.setLevel(logging.DEBUG)

    # Create STDOUT handler
    stdout_handler = RichHandler(console=console)
    stdout_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to the handlers
    pkg_logger.addHandler(stdout_handler)

    return pkg_logger
