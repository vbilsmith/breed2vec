# breed2vec/scrape/fci_breeds.py
from collections import OrderedDict
from urllib.parse import urljoin

from breed2vec.config import BASE_URL  # e.g. "https://www.fci.be"
from breed2vec.scrape.scrape_utils import retrieve_html, strip_numbered_list
from breed2vec.scrape.fci_parse import parse_FCI_breed


def scrape_recognized_breeds_for_group(group_num: str, group_url: str):
    """
    Scrape recognized breeds for a given FCI group page.

    Returns a list of dicts:
      {
        fciNumber: int,
        breedName: str,
        country: str | None,
        groupNum: str,
        breedPageUrl: str,
        standardPdfUrl: str | None,
        recognitionStatus: "Definitive",
        varieties: list[str]
      }
    """
    soup = retrieve_html(urljoin(BASE_URL, group_url))
    container = soup.find("div", {"class": "contenu nomenclature"})
    if container is None:
        title = soup.title.get_text(strip=True) if soup.title else "<no title>"
        snippet = soup.get_text(" ", strip=True)[:300]
        raise RuntimeError(
            f"Could not find div.contenu nomenclature on {group_url}\n"
            f"Title: {title}\nSnippet: {snippet}"
        )

    breed_records = []

    for ultag in container.find_all("ul", {"class": "pays"}):
        for litag in ultag.find_all("li"):
            breeds = OrderedDict()

            country_span = litag.find("span")
            if not country_span:
                continue
            country = strip_numbered_list(country_span.get_text(strip=True))

            country_varieties = litag.find("div", {"class": "races"})
            if not country_varieties:
                continue

            for cell in country_varieties.find_all("td"):
                link = cell.find(href=True)

                if link is not None:
                    b = parse_FCI_breed(link)
                    # normalize to your new naming
                    breeds[b["Breed"]] = {
                        "fciNumber": int(b["FCI Number"]),
                        "breedName": b["Breed"],
                        "country": country,
                        "groupNum": group_num,
                        "breedPageUrl": b["Source"],
                        "standardPdfUrl": None,
                        "recognitionDate": None,
                        "recognitionStatus": "Definitive",
                        "varieties": [],
                    }

                    standard_div = cell.find("div", {"class": "standard"})
                    if standard_div:
                        a = standard_div.find("a", href=True)
                        if a:
                            breeds[b["Breed"]]["standardPdfUrl"] = urljoin(BASE_URL, a["href"])

                else:
                    # Varieties belong to most recent breed
                    if not breeds:
                        continue
                    current_breed_key = next(reversed(breeds))
                    for var_td in cell.find_all("td", {"class": "variete"}):
                        var_span = var_td.find("span")
                        if var_span:
                            v = strip_numbered_list(var_span.get_text(strip=True))
                            if v:
                                breeds[current_breed_key]["varieties"].append(v)

            breed_records.extend(breeds.values())

    return breed_records
