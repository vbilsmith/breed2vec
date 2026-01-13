# breed2vec/__main__.py
"""
breed2vec CLI entrypoint.

Run examples:
  python -m breed2vec groups
  python -m breed2vec breeds
  python -m breed2vec all
"""
# breed2vec/__main__.py
import argparse
import os

def read_breeds_file(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="breed2vec")
    parser.add_argument(
        "stage",
        choices=["groups", "breeds", "all", "ingest", "analyze"],
        nargs="?",
        default="all",
        help="Which pipeline stage to run (default: all).",
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Drop and recreate database tables before running.",
    )
    parser.add_argument(
        "--breeds",
        type=str,
        metavar="PATH",
        help="Optional file containing one breed name or FCI number per line. "
             "If omitted, all breeds in the database are processed."
    )
    parser.add_argument(
        "--outdir",
        type=str,
        metavar="PATH",
        help="Output directory for analysis plots. "
             "Default: breed2vec/data/plots/<run_id>.",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        metavar="PATH",
        help="Path to a cached sqlite DB (overrides default and --data-dir).",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        metavar="PATH",
        help="Path to a cached data directory (contains fci_cache.db, pdfs/, layout/).",
    )

    args = parser.parse_args(argv)

    if args.db_path and args.data_dir:
        print("Note: --db-path overrides --data-dir; using --db-path.")

    if args.db_path:
        os.environ["BREED2VEC_DB_PATH"] = args.db_path
    if args.data_dir:
        os.environ["BREED2VEC_DATA_DIR"] = args.data_dir

    from breed2vec.config import PACKAGE_ROOT
    from breed2vec.pipeline.populate_groups import build_groups
    from breed2vec.pipeline.populate_breeds import build_breeds
    from breed2vec.pipeline.ingest_pdfs import ingest_breed_pdfs
    from breed2vec.pipeline.analyze_pdfs import analyze_pdfs

    if args.stage in ("groups", "all"):
        build_groups(reset=args.reset_db)

    if args.stage in ("breeds", "all"):
        # Only reset once at the beginning
        build_breeds(reset=args.reset_db and args.stage != "groups")

    breed_filter = None
    if args.breeds:
        breed_filter = read_breeds_file(args.breeds)
    else:
        default_breeds = PACKAGE_ROOT / "breeds.txt"
        if default_breeds.exists():
            breed_filter = read_breeds_file(str(default_breeds))

    if args.stage in ("ingest", "all"):
        ingest_breed_pdfs(breed_filter)

    if args.stage in ("analyze", "all"):
        analyze_pdfs(breed_filter, out_dir=args.outdir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
