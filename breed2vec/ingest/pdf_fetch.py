import hashlib
import re
from pathlib import Path

import requests

from breed2vec.config import PDF_DIR
from breed2vec.db.breeds import fetch_breeds_for_pdfs


def _sanitize_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return cleaned.strip("_") or "breed"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_pdf(url: str, dest_path: Path) -> dict:
    response = requests.get(url, allow_redirects=True, timeout=30)
    response.raise_for_status()
    data = response.content or b""
    if not data:
        raise ValueError(f"Empty response body for {url}")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(data)
    return {
        "pdfPath": str(dest_path),
        "sha256": _sha256_bytes(data),
    }


def fetch_pdf_to_cache(breed_filter=None):
    rows = fetch_breeds_for_pdfs(breed_filter)
    results = []

    for fci_number, breed_name, pdf_url in rows:
        filename = f"{fci_number}_{_sanitize_filename(breed_name)}.pdf"
        pdf_path = PDF_DIR / filename
        meta = download_pdf(pdf_url, pdf_path)
        results.append(
            {
                "fciNumber": fci_number,
                "breedName": breed_name,
                "standardPdfUrl": pdf_url,
                **meta,
            }
        )

    return results
