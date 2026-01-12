from breed2vec.db.connection import connect_db

def _parse_breed_filter(breed_filter):
    if not breed_filter:
        return [], []

    names = []
    numbers = []
    for entry in breed_filter:
        cleaned = entry.strip()
        if not cleaned:
            continue
        if cleaned.isdigit():
            numbers.append(int(cleaned))
        else:
            names.append(cleaned.lower())
    return names, numbers


def fetch_breeds_for_pdfs(breed_filter=None):
    names, numbers = _parse_breed_filter(breed_filter)
    params = []
    where_parts = ["standardPdfUrl IS NOT NULL", "standardPdfUrl != ''"]
    match_parts = []

    for name in names:
        match_parts.append("lower(breedName) = ?")
        params.append(name)

    for number in numbers:
        match_parts.append("fciNumber = ?")
        params.append(number)

    where_sql = " AND (" + " OR ".join(match_parts) + ")" if match_parts else ""
    sql = (
        "SELECT fciNumber, breedName, standardPdfUrl "
        "FROM BreedInfo "
        f"WHERE {' AND '.join(where_parts)}{where_sql}"
    )

    with connect_db() as con:
        cur = con.execute(sql, params)
        rows = cur.fetchall()

        if names:
            matched_names = {row[1].lower() for row in rows}
            missing = [name for name in names if name not in matched_names]
            if missing:
                missing_list = ", ".join(missing)
                raise ValueError(f"Unknown breeds in --breeds: {missing_list}")

        if numbers:
            matched_numbers = {row[0] for row in rows}
            missing_nums = [n for n in numbers if n not in matched_numbers]
            if missing_nums:
                missing_list = ", ".join(str(n) for n in missing_nums)
                raise ValueError(f"Unknown FCI numbers in --breeds: {missing_list}")

        return rows
