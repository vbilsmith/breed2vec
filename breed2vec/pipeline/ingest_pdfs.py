from breed2vec.db.schema import init_schema
from breed2vec.config import LAYOUT_DIR
from breed2vec.ingest.pdf_text import write_layout_trace_jsonl
from breed2vec.ingest.pdf_fetch import fetch_pdf_to_cache
from breed2vec.db.documents import get_document_sha, upsert_document
from breed2vec.ingest.extract_utils import (
    clean_and_fix_pdf_text,
    extract_pdf_text_from_path,
)

def ingest_breed_pdfs(breed_filter=None):
    init_schema(reset=False)
    records = fetch_pdf_to_cache(breed_filter)
    LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
    for record in records:
        status = process_pdf_record(record)
        print(f"{status}: {record['breedName']} ({record['fciNumber']})")

        sha256 = record.get("sha256")
        pdf_path = record.get("pdfPath")
        if sha256 and pdf_path:
            trace_path = LAYOUT_DIR / f"{sha256}.jsonl"
            if not trace_path.exists():
                n_lines = write_layout_trace_jsonl(pdf_path, trace_path, max_lines=None)
                print(f"[trace] wrote {n_lines} layout lines to {trace_path}")
    return records

def process_pdf_record(record):
    existing_sha = get_document_sha(record["fciNumber"])
    if existing_sha and existing_sha == record.get("sha256"):
        record["text"] = None
        upsert_document(record)
        return "unchanged"

    raw_text = extract_pdf_text_from_path(record["pdfPath"])
    record["text"] = clean_and_fix_pdf_text(raw_text)
    upsert_document(record)
    return "updated"
