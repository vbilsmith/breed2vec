from breed2vec.db.documents import get_pdf_text
from breed2vec.analyze.decompose import analyze_standards
from breed2vec.db.schema import init_schema

def analyze_pdfs(breed_filter=None):
    init_schema(reset=False)
    records = get_pdf_text(breed_filter)
    docs = dict()
    for record in records:
        docs[record[1]] = record[2]
    analyze_standards(docs)


