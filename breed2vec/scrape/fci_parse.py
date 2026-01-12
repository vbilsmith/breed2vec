import re
from urllib.parse import urljoin
from breed2vec.config import BASE_URL  # or BASE_URL

def parse_FCI_breed(link):
    """
    Parse an FCI breed link.

    The link text is typically structured as:
        DOG NAME (###) (OPTIONAL ALT NAME)

    Returns a dict with normalized fields.
    """
    text = link.get_text(strip=True)

    # Extract FCI number in parentheses, e.g. "(122)"
    id_match = re.search(r"\((\d+)\)", text)
    if not id_match:
        raise ValueError(f"Could not parse FCI number from: {text}")

    fci_number = int(id_match.group(1))

    # Breed name = text before the (###)
    breed_name = text[:id_match.start()].strip()

    # Optional synonym after the number, e.g. "(Alt Name)"
    remainder = text[id_match.end():].strip()
    synonym = None
    if remainder.startswith("(") and remainder.endswith(")"):
        synonym = remainder[1:-1].strip()

    return {
        "Breed": breed_name,
        "FCI Number": fci_number,
        "Synonyms": synonym,
        "Source": urljoin(BASE_URL, link["href"]),
    }
