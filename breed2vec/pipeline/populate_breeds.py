from breed2vec.db.schema import init_schema
from breed2vec.db.breed_groups import insert_breed_group, iter_breed_groups   # you should have this already
from breed2vec.db.breed_info import upsert_breeds_with_varieties

from breed2vec.config import BASE_URL
from breed2vec.scrape.fci_breeds import scrape_recognized_breeds_for_group
from breed2vec.scrape.fci_provisional import scrape_provisional_breeds

def build_breeds(reset: bool = False):
    init_schema(reset=reset)
    for group_num, group_url in iter_breed_groups():
        records = scrape_recognized_breeds_for_group(group_num, group_url)
        n = upsert_breeds_with_varieties(records)
        print(f"{group_num}: stored/updated {n} rows")

    provisional_group_num = "P"
    insert_breed_group(provisional_group_num, "Provisional", BASE_URL)
    provisional_records = scrape_provisional_breeds(provisional_group_num)
    n = upsert_breeds_with_varieties(provisional_records)
    print(f"provisional: stored/updated {n} rows")


def main():
    build_breeds()


if __name__ == "__main__":
    main()
