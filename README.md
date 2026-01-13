# breed2vec

**breed2vec** is a lightweight, reproducible pipeline for collecting FCI dog breed standards, extracting text from PDFs, and analyzing semantic similarity between breeds using modern text representations.

The goal of this project is **not** to infer ancestry or biological truth, but to evaluate how well document embeddings recover *known historical, geographic, and morphological relationships* from breed-standard text alone.

The workflow is designed to be transparent and inspectable:

**scrape → store → ingest PDFs → analyze**

## Why This Matters (AI Safety Context)
This project is a small, controlled testbed for evaluating how well text embeddings recover meaningful structure from domain‑specific documents. That style of construct‑validity check is directly relevant to safety‑adjacent evaluation: if embeddings fail on known structure in a narrow domain, they are less trustworthy for high‑stakes interpretability or retrieval settings.

## What This Demo Shows (30-second overview)

Using a small, interpretable set of breeds, the demo illustrates that:

- Breeds with shared geographic and functional history (e.g., Labrador Retriever and Newfoundland) exhibit high semantic similarity.
- Related breeds developed in different contexts (e.g., Golden Retriever) appear nearby but offset.
- Morphologically and historically distinct breeds (e.g., Xoloitzcuintle) separate cleanly.
- These relationships emerge *without* any biological labels—purely from text embeddings of breed standards.

This serves as a construct-validity sanity check for document-level embeddings in a fine-grained biological domain.

## Quickstart for Reviewers
- Read the Retriever Sandbox writeup: `breed2vec/docs/retriever_sandbox.md`.
- Optionally run analysis on the provided breed list:
  ```bash
  python -m breed2vec analyze --breeds breed2vec/breeds.txt
  ```
- To avoid scraping, use a cached DB (see below).

---

## Environment Setup

Create and activate the conda environment:

```bash
conda env create -f environment.yml
conda activate breed2vec
```
(Alternatively, dependencies can be installed via pip; see environment.yml for details.)

## Minimal Working Example

This is the shortest path from scratch to analysis output.

1) Populate FCI group and breed metadata:
```bash
python -m breed2vec groups
python -m breed2vec breeds
```

2) Specify a small list of breeds:
Edit `breed2vec/breeds.txt`, adding one breed per line using official FCI names.

3) Ingest breed standards (PDF download + text extraction):
```bash
python -m breed2vec ingest --breeds breed2vec/breeds.txt
```

Notes:
- Internet access is required to download new PDFs.
- If offline, use a cached DB (see below).

4) Run analysis:
```bash
python -m breed2vec analyze --breeds breed2vec/breeds.txt
```

This produces cosine similarity matrices and low-dimensional visualizations (e.g., PCA) over document embeddings.

## Project Structure (Short)
- `breed2vec/scrape/`: scrape FCI group + breed metadata.
- `breed2vec/db/`: sqlite schema + CRUD.
- `breed2vec/ingest/`: PDF download and text extraction.
- `breed2vec/analyze/`: analysis helpers (TF‑IDF / embeddings).
- `breed2vec/pipeline/`: orchestration entrypoints.

For full detail, see `breed2vec/MANIFEST.md`.

## Using a Cached Database (No Scraping Required)
If you have a cached `fci_cache.db`, you can skip scraping and run ingest/analyze directly.

Option A: environment variables
```bash
export BREED2VEC_DB_PATH="/path/to/fci_cache.db"
python -m breed2vec ingest --breeds breed2vec/breeds.txt
python -m breed2vec analyze --breeds breed2vec/breeds.txt
```

Option B: CLI flags
```bash
python -m breed2vec ingest --db-path /path/to/fci_cache.db --breeds breed2vec/breeds.txt
python -m breed2vec analyze --db-path /path/to/fci_cache.db --breeds breed2vec/breeds.txt
```

If you have a full cached data directory (db + pdfs + layout), use:
```bash
python -m breed2vec analyze --data-dir /path/to/data
```

## Outputs
- `breed2vec/data/fci_cache.db`: sqlite database for breed metadata and documents.
- `breed2vec/data/pdfs/`: downloaded PDF standards.
- `breed2vec/data/layout/`: optional layout traces for section extraction.
- `breed2vec/data/plots/<run_id>/`: analysis outputs (cosine matrix, TF‑IDF tables, plots).

## Notes on Data and Reproducibility
- The FCI site is the source of truth for breed metadata and PDF standards.
- The pipeline is designed to be incremental; re‑ingest re‑downloads PDFs and updates only when hashes change.
- PCA visualizations are used for interpretability, not statistical inference.

## Limitations and Scope

This demo uses a small number of breeds for clarity and interpretability.
Semantic similarity reflects shared descriptive language, not proof of genetic ancestry.
The project is intended as an exploratory and diagnostic tool rather than a benchmark.

## Next Steps (Planned)
- Section extraction from layout traces (history vs morphology vs temperament).
- Structured comparisons across section types.

## Contact
If you are interested in this work, please feel free to reach out for a walkthrough or a curated subset of results.

## Acknowledgements
Development was assisted by OpenAI tools (Codex / ChatGPT) for scaffolding, refactoring, and debugging support.
