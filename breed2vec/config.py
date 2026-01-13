"""
Project-wide configuration.

Centralizes paths and constants so modules don't rely on the working directory.
"""
import os
from pathlib import Path

BASE_URL = "https://www.fci.be/en/nomenclature"

# Path to the *package* directory (…/breedStandards/breed2vec/)
PACKAGE_ROOT = Path(__file__).resolve().parent

# Store data inside the package, at breed2vec/data/fci_cache.db
_default_data_dir = PACKAGE_ROOT / "data"
_env_db_path = os.environ.get("BREED2VEC_DB_PATH")
_env_data_dir = os.environ.get("BREED2VEC_DATA_DIR")

if _env_db_path:
    DB_PATH = Path(_env_db_path).expanduser().resolve()
    DATA_DIR = DB_PATH.parent
else:
    DATA_DIR = Path(_env_data_dir).expanduser().resolve() if _env_data_dir else _default_data_dir
    DB_PATH = DATA_DIR / "fci_cache.db"

PDF_DIR = DATA_DIR / "pdfs"
LAYOUT_DIR = DATA_DIR / "layout"
