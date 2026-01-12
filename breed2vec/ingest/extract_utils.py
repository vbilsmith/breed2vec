import requests
import re

import fitz # for pip, this is pymupdf
from io import BytesIO

_PUNCT_START = set(",.;:!?)]}%")

def extract_pdf_text_with_pymupdf(url):
    """Download a pdf and returns the contents as a string

    Keyword arguments:
    url -- string containing the URL of the PDF
    """
    try:
        response = requests.get(url, allow_redirects=True, timeout=20)
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        print(f"URL invalid: {url}")
        exit(1)
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL,
            ValueError) as e:
        raise ValueError(f"Invalid URL: {url}") from e
    except requests.exceptions.RequestException:
        # includes Timeout, ConnectionError, HTTPError, SSLError, TooManyRedirects, etc.
        raise

    content = response.content or b""
    if not content:
        raise ValueError(f"Empty response body (no PDF bytes) from: {url}")

    # 3) Parse + extract
    doc = None
    text = ""
    try:
        doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")
        for page in doc:
            text += page.get_text()

    finally:
        if doc is not None:
            doc.close()
    return text


def extract_pdf_text_from_path(pdf_path: str) -> str:
    doc = None
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
    finally:
        if doc is not None:
            doc.close()
    return text


def iter_lines_with_format(pdf_path: str):
    """
    Yield layout-aware lines from a PDF.

    Each yielded line contains:
      - text
      - page number
      - bbox (position)
      - avg font size
      - bold-ish flag
      - caps ratio
      - spans (for debugging/fidelity)
    """
    doc = fitz.open(pdf_path)
    try:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            data = page.get_text("dict")
            for block in data.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue

                    text = "".join(s.get("text", "") for s in spans).strip()
                    if not text:
                        continue

                    sizes = [s.get("size", 0.0) for s in spans if s.get("size")]
                    fonts = [s.get("font", "") for s in spans]
                    flags = [s.get("flags", 0) for s in spans]

                    avg_size = sum(sizes) / len(sizes) if sizes else 0.0
                    boldish = any(("Bold" in f) for f in fonts) or any((fl & 2) for fl in flags)

                    letters = [c for c in text if c.isalpha()]
                    caps_ratio = (
                        sum(c.isupper() for c in letters) / len(letters)
                    ) if letters else 0.0

                    yield {
                        "page": page_num,
                        "bbox": line.get("bbox"),
                        "text": text,
                        "avg_size": avg_size,
                        "boldish": boldish,
                        "caps_ratio": caps_ratio,
                        "spans": spans,
                    }
    finally:
        doc.close()


def clean_and_fix_pdf_text(text):
    # This function cleans up breed standard text.

    # Specific to dog breed documents:

    # Remove footer lines like "FCI-St. N° 122 / 30.09.2022"
    text = re.sub(r"FCI-St\.\s+N°\s+\d+\s*/\s*\d{2}\.\d{2}\.\d{4}", "", text)

    # Generally useful:

    # Replace line breaks and tabs
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r' {2,}', ' ', text).strip()
    text = text.lower()

    # Remove all punctuation (preserve spaces and alphanumerics)
    text = re.sub(r'[^\w\s]', '', text)

    return text

import re

def join_spans_with_spaces(spans):
    parts = []
    for span in spans:
        t = span.get("text", "")
        if not t:
            continue
        if not parts:
            parts.append(t)
            continue

        prev = parts[-1]
        # If prev ends with whitespace or t starts with whitespace, just append
        if prev and prev[-1].isspace() or (t and t[0].isspace()):
            parts.append(t)
        # If next starts with punctuation, no space
        elif t and t[0] in _PUNCT_START:
            parts.append(t)
        else:
            parts.append(" " + t)
    out = "".join(parts).strip()

    # Optional: collapse weird multiple spaces
    out = re.sub(r"\s+", " ", out)
    return out
