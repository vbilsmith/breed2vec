from urllib.parse import urljoin
from breed2vec.config import BASE_URL
from breed2vec.db.schema import init_schema
from breed2vec.scrape.scrape_utils import retrieve_html

def parse_groups(breed_group_info):
    for litag in breed_group_info.find_all("li"):
        link = litag.find("a", href=True)
        span = litag.find("span")
        if not link or not span:
            continue
        group_num_text = link.get_text(strip=True)   # "Group 1"
        group_name = span.get_text(strip=True)
        group_url = urljoin(BASE_URL, link["href"])
        yield group_num_text, group_name, group_url


