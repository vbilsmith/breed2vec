# breed2vec Manifest

This document summarizes what each subfolder handles and the purpose of each file.

## Root
- __main__.py: CLI entrypoint; wires stages (groups, breeds, ingest).
- __init__.py: package marker.
- config.py: shared config/constants (BASE_URL, DB_PATH, PDF_DIR).
- breeds.txt: sample user-provided breed list for ingest.
- breed-standard-dim.ipynb: exploratory notebook for PDF text processing.
- data/: runtime artifacts (sqlite DB and downloaded PDFs).

## db/
Purpose: database connections, schema, and CRUD helpers.
- connection.py: sqlite connection helper with PRAGMA setup.
- schema.py: database DDL (tables, migrations).
- breed_groups.py: CRUD for BreedGroups.
- breed_info.py: upsert logic for BreedInfo and varieties.
- breeds.py: query helpers for BreedInfo (filtering + validation).
- documents.py: CRUD for Documents table (PDF metadata + text).
- sections.py: placeholder for future section storage.
- __init__.py: package marker.

## scrape/
Purpose: fetch and parse FCI web pages into structured records.
- scrape_utils.py: HTTP fetch + text normalization helpers.
- fci_parse.py: parse breed link into normalized fields.
- fci_groups.py: parse and store breed groups.
- fci_breeds.py: scrape recognized breeds by group.
- fci_provisional.py: scrape provisional breeds from nomenclature page.
- __init__.py: package marker.

## pipeline/
Purpose: orchestration of scrape stages and DB population.
- populate_groups.py: build BreedGroups table from FCI site.
- populate_breeds.py: build BreedInfo + varieties and provisional entries.
- ingest_pdfs.py: orchestrate ingest (download PDFs, extract text, store).
- __init__.py: package marker.

## ingest/
Purpose: download PDFs, extract text, and store in Documents.
- pdf_fetch.py: query DB for PDF URLs and download files.
- extract_utils.py: PDF text extraction + formatting-aware iterator.
- pdf_text.py: process local PDFs (extract + upsert Documents).
- define_sections.py: placeholder for section extraction rules.
- __init__.py: package marker.
