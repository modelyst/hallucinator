# Hallucinator

Hallucinator is a Python package for generating hallucinated spectra using a Gaussian mixture model with a background and noise. The package includes functions for generating random element compositions, generating peak positions for elements, and generating hallucinated spectra.
## Installation

You can install Hallucinator using pip:
```
pip install git+https://github.com/modelyst/hallucinator.git
```
## Usage
### Generating Hallucinated Spectra

To generate hallucinated spectra, you can use the generate command:

```Bash
hallucinator generate --seed 0 -e Ba -e Mg -e Cu -e V --num 1000 --output output/spectra
```

This command will generate 1000 hallucinated spectra and save them to the output/spectra directory. You can specify various options, such as the number of spectra to generate, the output directory, and the elements to use.

### Generating Hallucinated Spectra For A Composition

To generate hallucinated spectra for a given composition, you can use the generate command:

```Bash
hallucinator hallucinate output/composition/test.json --mapping output/spectra/mapping.json
```

### Plotting Spectra

To plot the spectra, you can use the plot command:
```Bash
hallucinator plot output/spectra --elements Ba
```

This command will plot the spectra in the output/spectra directory that match the specified elements.
