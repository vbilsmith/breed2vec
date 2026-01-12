import json
from pathlib import Path
from breed2vec.ingest.extract_utils import join_spans_with_spaces

import fitz  # PyMuPDF

def iter_lines_with_format(pdf_path: str):
    """
    Yield layout-aware text lines from a PDF.

    Each yielded dict represents one visual line and contains:
      - page        : page number (0-based)
      - bbox        : [x0, y0, x1, y1]
      - text        : concatenated text of the line
      - avg_size    : average font size across spans
      - boldish     : heuristic bold flag
      - caps_ratio  : fraction of uppercase letters
    """
    doc = fitz.open(pdf_path)

    try:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            layout = page.get_text("dict")

            for block in layout.get("blocks", []):
                # type 0 = text; skip images, drawings, etc.
                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue

                    spans = sorted(spans, key=lambda s: s["bbox"][0])  # optional

                    text = join_spans_with_spaces(spans)
                    if not text:
                        continue

                    # Font sizes
                    sizes = [span.get("size", 0.0) for span in spans if span.get("size")]
                    avg_size = sum(sizes) / len(sizes) if sizes else 0.0

                    # Bold heuristic:
                    # - font name contains "Bold"
                    # - OR flags indicate bold (bit 2)
                    boldish = False
                    for span in spans:
                        font = span.get("font", "")
                        flags = span.get("flags", 0)
                        if "Bold" in font or (flags & 2):
                            boldish = True
                            break

                    # Uppercase ratio (ignoring non-letters)
                    letters = [c for c in text if c.isalpha()]
                    caps_ratio = (
                        sum(c.isupper() for c in letters) / len(letters)
                        if letters else 0.0
                    )

                    yield {
                        "page": page_num,
                        "bbox": line.get("bbox"),
                        "text": text,
                        "avg_size": avg_size,
                        "boldish": boldish,
                        "caps_ratio": caps_ratio,
                    }
    finally:
        doc.close()



def write_layout_trace_jsonl(pdf_path: str | Path, out_path: str | Path, *, max_lines: int | None = None):
    """
    Write one JSON record per extracted line with lightweight formatting features.
    JSONL is nice because it's easy to inspect and diff.
    """

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with out_path.open("w", encoding="utf-8") as f:
        for rec in iter_lines_with_format(str(pdf_path)):
            # keep it small: drop spans unless you truly need them
            rec_small = {
                "page": rec.get("page"),
                "bbox": rec.get("bbox"),
                "text": rec.get("text"),
                "avg_size": rec.get("avg_size"),
                "boldish": rec.get("boldish"),
                "caps_ratio": rec.get("caps_ratio"),
            }
            f.write(json.dumps(rec_small, ensure_ascii=False) + "\n")
            n += 1
            if max_lines is not None and n >= max_lines:
                break

    return n

