from urllib.parse import urljoin

from breed2vec.config import BASE_URL  # recommended split
from breed2vec.scrape.scrape_utils import retrieve_html
from breed2vec.scrape.fci_groups import parse_groups
from breed2vec.db.schema import init_schema
from breed2vec.db.breed_groups import insert_breed_group


def build_groups(reset: bool = False):
    """Scrape FCI breed groups and store them in BreedGroups."""
    init_schema(reset=reset)

    page = retrieve_html(BASE_URL)
    breed_group_info = page.find("ul", {"class": "grouplist"})
    if breed_group_info is None:
        title = page.title.get_text(strip=True) if page.title else "<no title>"
        snippet = page.get_text(" ", strip=True)[:300]
        raise RuntimeError(
            f"Could not find <ul class='grouplist'> on {BASE_URL}.\n"
            f"Page title: {title}\n"
            f"Text snippet: {snippet}"
        )

    inserted = 0
    for group_num, group_name, group_url in parse_groups(breed_group_info):
        # make sure URL is absolute before storing
        abs_url = urljoin(BASE_URL, group_url)

        ok = insert_breed_group(group_num, group_name, abs_url)
        if ok:
            inserted += 1
            print(f"{group_num} added: {group_name}")
        else:
            print(f"{group_num} skipped (already exists?): {group_name}")

    print(f"Done. Inserted {inserted} groups.")


def main():
    build_groups()


if __name__ == "__main__":
    main()
