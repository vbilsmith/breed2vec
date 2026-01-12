from urllib.parse import urljoin

from breed2vec.config import BASE_URL
from breed2vec.scrape.fci_parse import parse_FCI_breed
from breed2vec.scrape.scrape_utils import retrieve_html


def _find_provisional_table(soup):
    heading = None
    for h2 in soup.find_all("h2", class_="nom"):
        text = h2.get_text(" ", strip=True).lower()
        if "provisional" in text or "provisonal" in text:
            heading = h2
            break

    if heading is None:
        return None

    races_div = heading.find_next("div", class_="races")
    if not races_div:
        return None

    return races_div.find("table")


def scrape_provisional_breeds(group_num: str):
    soup = retrieve_html(BASE_URL)
    prov_table = _find_provisional_table(soup)
    if prov_table is None:
        title = soup.title.get_text(strip=True) if soup.title else "<no title>"
        snippet = soup.get_text(" ", strip=True)[:300]
        raise RuntimeError(
            "Could not find a provisional breeds table on the nomenclature page.\n"
            f"Page title: {title}\n"
            f"Text snippet: {snippet}"
        )

    records = []
    rows = prov_table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        breed_link = cells[0].find("a", class_="nom") or cells[0].find("a", href=True)
        if not breed_link:
            continue

        standard_url = None
        standard_tag = cells[0].find("div", class_="standard")
        if standard_tag:
            standard_link = standard_tag.find("a", href=True)
            if standard_link:
                standard_url = urljoin(BASE_URL, standard_link["href"])

        recognition_date = cells[1].get_text(strip=True) or None

        breed_info = parse_FCI_breed(breed_link)
        records.append(
            {
                "fciNumber": int(breed_info["FCI Number"]),
                "breedName": breed_info["Breed"],
                "country": None,
                "groupNum": group_num,
                "breedPageUrl": breed_info["Source"],
                "standardPdfUrl": standard_url,
                "recognitionDate": recognition_date,
                "recognitionStatus": "Provisional",
                "varieties": [],
            }
        )

    return records
