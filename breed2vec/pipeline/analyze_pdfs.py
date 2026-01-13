from datetime import datetime

from breed2vec.analyze.decompose import analyze_standards
from breed2vec.config import DATA_DIR
from breed2vec.db.documents import get_pdf_text
from breed2vec.db.schema import init_schema

def analyze_pdfs(breed_filter=None, *, out_dir=None):
    init_schema(reset=False)
    records = get_pdf_text(breed_filter)
    docs = dict()
    for record in records:
        docs[record[1]] = record[2]

    if out_dir is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = DATA_DIR / "plots" / run_id

    analyze_standards(docs, out_dir=out_dir)

