import json
from pathlib import Path
import re

HERE = Path(__file__).parent.parent
DATA_FILES = (HERE / "data" / "raw_data").glob("*.json")
OUTPUT_DIR = Path("output/parsed_raw_data")


def get_wavelength(data):
    """Get the wavelength array from the json data"""
    return data["meta"]["optional"]["wl"]


def get_amplitude(data, key):
    """Get the amplitude array from the json data"""
    return data[key]


def get_id(key):
    """Get the id from the key"""
    return key.split("__")[1]


def main():
    for file_name in DATA_FILES:
        with open(file_name) as f:
            data = json.load(f)
        wavelength = get_wavelength(data)
        for key in data["data"].keys():
            match = re.search(r"idx_(\d+)", key)
            if match:
                amplitude = get_amplitude(data["data"], key)
                id_ = match.group(1)
                # Zip together the wavelength and amplitude arrays into tuples
                print(max(wavelength), min(wavelength))
                if len(wavelength) != len(amplitude):
                    print(f"Lengths do not match for {file_name} {id_}")
                    continue
                new_data = list(zip(wavelength, amplitude))

                new_file_name = f"{id_}.json"
                output_name = (
                    OUTPUT_DIR / file_name.with_suffix("").name / new_file_name
                )
                output_name.parent.mkdir(parents=True, exist_ok=True)
                with open(output_name, "w") as f:
                    json.dump(new_data, f)


if __name__ == "__main__":
    main()
