from breed2vec.db.connection import connect_db
from typing import Iterable, Optional, Sequence, Tuple

DOCUMENT_UPSERT_SQL = """
INSERT INTO Documents(
    fciNumber, breedName, standardPdfUrl, pdfPath, text, sha256, downloadedAt
)
VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
ON CONFLICT(fciNumber) DO UPDATE SET
    breedName=excluded.breedName,
    standardPdfUrl=excluded.standardPdfUrl,
    pdfPath=excluded.pdfPath,
    text=COALESCE(excluded.text, Documents.text),
    sha256=excluded.sha256,
    downloadedAt=datetime('now')
"""


def upsert_document(record):
    with connect_db() as con:
        con.execute(
            DOCUMENT_UPSERT_SQL,
            (
                record["fciNumber"],
                record["breedName"],
                record["standardPdfUrl"],
                record["pdfPath"],
                record.get("text"),
                record.get("sha256"),
            ),
        )


def get_document_sha(fci_number: int) -> str | None:
    with connect_db() as con:
        row = con.execute(
            "SELECT sha256 FROM Documents WHERE fciNumber=?",
            (fci_number,),
        ).fetchone()
    return row[0] if row and row[0] else None

def get_pdf_text(breeds: Optional[Sequence[str]] = None):
    """
    If breeds is None: return all rows.
    If breeds is a non-empty list: return only those breedName/fciNumber values.
    If breeds is an empty list: return no rows.
    """
    base_sql = "SELECT fciNumber, breedName, text FROM Documents"

    if breeds is None:
        sql = base_sql
        params: Tuple[object, ...] = ()
    else:
        entries = [b.strip() for b in breeds if b and b.strip()]
        if not entries:
            return []

        names = [e.lower() for e in entries if not e.isdigit()]
        numbers = [int(e) for e in entries if e.isdigit()]

        clauses = []
        params = []
        if names:
            placeholders = ",".join("?" for _ in names)
            clauses.append(f"lower(breedName) IN ({placeholders})")
            params.extend(names)
        if numbers:
            placeholders = ",".join("?" for _ in numbers)
            clauses.append(f"fciNumber IN ({placeholders})")
            params.extend(numbers)

        sql = base_sql + " WHERE " + " OR ".join(clauses)
        params = tuple(params)

    with connect_db() as con:
        cur = con.execute(sql, params)
        return cur.fetchall()
