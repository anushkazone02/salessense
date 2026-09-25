"""
download_dataset.py
----------------------
Downloads the Sample Superstore dataset directly from Kaggle using the
official Kaggle API, and saves it to data/superstore.csv.

This requires a Kaggle account and API credentials (kaggle.json), since
Kaggle does not allow anonymous/unauthenticated downloads. It is NOT run
automatically by the rest of the project -- data/superstore.csv is
already included in this repository -- this script is provided so you
can re-fetch the data yourself directly from the original source if you
want to.

Setup (one-time):
    1. Create a free account at https://www.kaggle.com if you don't have one.
    2. Go to https://www.kaggle.com/settings -> "API" -> "Create New Token".
       This downloads a file called kaggle.json.
    3. Place kaggle.json at:
         Linux/Mac: ~/.kaggle/kaggle.json   (chmod 600 ~/.kaggle/kaggle.json)
         Windows:   C:\\Users\\<You>\\.kaggle\\kaggle.json
    4. pip install kaggle
    5. Run:  python -m src.download_dataset

Dataset source (Kaggle):
    https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
"""

import os
import shutil
import sys

from src.config import DATA_DIR, RAW_DATA_PATH

KAGGLE_DATASET = "vivek468/superstore-dataset-final"
# The file inside that Kaggle dataset is typically named "Sample - Superstore.csv"
KAGGLE_CSV_NAME = "Sample - Superstore.csv"


def download_from_kaggle():
    try:
        import kaggle  # noqa: F401  (import itself validates kaggle.json is present)
    except OSError as e:
        print(
            "Kaggle API credentials not found.\n"
            "Create an API token at https://www.kaggle.com/settings -> API -> "
            "'Create New Token', then place the downloaded kaggle.json at "
            "~/.kaggle/kaggle.json (Linux/Mac) or C:\\Users\\<You>\\.kaggle\\kaggle.json "
            "(Windows), then re-run this script.\n"
            f"Original error: {e}"
        )
        sys.exit(1)
    except ImportError:
        print("The 'kaggle' package is not installed. Run: pip install kaggle")
        sys.exit(1)

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()

    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Downloading dataset '{KAGGLE_DATASET}' from Kaggle ...")
    api.dataset_download_files(KAGGLE_DATASET, path=DATA_DIR, unzip=True)

    downloaded_path = os.path.join(DATA_DIR, KAGGLE_CSV_NAME)
    if os.path.exists(downloaded_path) and downloaded_path != RAW_DATA_PATH:
        shutil.move(downloaded_path, RAW_DATA_PATH)

    if os.path.exists(RAW_DATA_PATH):
        print(f"Dataset saved to: {RAW_DATA_PATH}")
    else:
        print(
            "Download finished but the expected CSV filename wasn't found. "
            f"Check the contents of {DATA_DIR} and rename the CSV to 'superstore.csv' "
            "if needed (the filename inside Kaggle datasets can change over time)."
        )


if __name__ == "__main__":
    download_from_kaggle()
