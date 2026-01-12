"""
Project-wide configuration.

Centralizes paths and constants so modules don't rely on the working directory.
"""
from pathlib import Path

BASE_URL = "https://www.fci.be/en/nomenclature"

# Path to the *package* directory (…/breedStandards/breed2vec/)
PACKAGE_ROOT = Path(__file__).resolve().parent

# Store data inside the package, at breed2vec/data/fci_cache.db
DATA_DIR = PACKAGE_ROOT / "data"
DB_PATH = DATA_DIR / "fci_cache.db"
PDF_DIR = DATA_DIR / "pdfs"
LAYOUT_DIR = DATA_DIR / "layout"
