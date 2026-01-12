from breed2vec.db.connection import connect_db

BREEDINFO_UPSERT_SQL = """
INSERT INTO BreedInfo(
    fciNumber, breedName, country, groupNum,
    breedPageUrl, standardPdfUrl, recognitionDate, recognitionStatus, lastSeen
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
ON CONFLICT(fciNumber) DO UPDATE SET
    breedName=excluded.breedName,
    country=excluded.country,
    groupNum=excluded.groupNum,
    breedPageUrl=excluded.breedPageUrl,
    standardPdfUrl=excluded.standardPdfUrl,
    recognitionDate=excluded.recognitionDate,
    recognitionStatus=excluded.recognitionStatus,
    lastSeen=datetime('now')
"""

VARIETY_INSERT_SQL = """
INSERT OR IGNORE INTO BreedVarieties(fciNumber, variety)
VALUES (?, ?)
"""

def upsert_breeds_with_varieties(breed_records):
    """
    Insert/update BreedInfo rows and associated BreedVarieties.

    breed_records: list[dict]
      {
        fciNumber: int,
        breedName: str,
        country: str | None,
        groupNum: str,
        breedPageUrl: str,
        standardPdfUrl: str | None,
        recognitionStatus: str,
        varieties: list[str]
      }
    """
    if not breed_records:
        return 0

    with connect_db() as con:
        for r in breed_records:
            con.execute(
                BREEDINFO_UPSERT_SQL,
                (
                    r["fciNumber"],
                    r["breedName"],
                    r.get("country"),
                    r["groupNum"],
                    r["breedPageUrl"],
                    r.get("standardPdfUrl"),
                    r.get("recognitionDate"),
                    r.get("recognitionStatus", "Definitive"),
                ),
            )

            for variety in r.get("varieties", []):
                con.execute(VARIETY_INSERT_SQL, (r["fciNumber"], variety))

    return len(breed_records)
