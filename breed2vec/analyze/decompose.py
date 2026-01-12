from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from breed2vec.analyze.viz import plot_cosine_similarity, plot_embedding_scatter
import numpy as np




def configure_tfidf(terms, tfidf_matrix, top_k=10):
    """
    Print top-k TF-IDF terms for each document.
    tfidf_matrix is a scipy sparse matrix: (n_docs, n_terms)
    terms is an array mapping column index -> token
    """
    n_docs = tfidf_matrix.shape[0]

    for doc_idx in range(n_docs):
        print(f"\nDOC {doc_idx}")

        row = tfidf_matrix[doc_idx].toarray().ravel()
        top_idx = row.argsort()[-top_k:][::-1]

        for j in top_idx:
            if row[j] > 0:
                print(terms[j], float(row[j]))


def find_representations(docs):
    """
    Returns:
      terms: vocab tokens (n_terms,)
      tfidf_matrix: sparse TF-IDF matrix (n_docs, n_terms)
      E: dense sentence-transformer embeddings (n_docs, dim), L2-normalized
      sim: cosine similarity matrix (n_docs, n_docs)
    """
    # TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(docs)
    terms = vectorizer.get_feature_names_out()

    # SentenceTransformer embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    E = model.encode(docs, convert_to_numpy=True, normalize_embeddings=True)

    # Cosine similarity (since normalized)
    sim = E @ E.T

    return terms, tfidf_matrix, E, sim


def analyze_standards(doc_dict):
    labels = list(doc_dict.keys())
    docs = list(doc_dict.values())

    print("n_docs =", len(docs))

    terms, tfidf_matrix, E, sim = find_representations(docs)

    print("\nTop TF-IDF terms per doc:")
    configure_tfidf(terms, tfidf_matrix, top_k=10)

    print("\nCosine similarity between docs (SentenceTransformer):")
    print(sim)

    plot_cosine_similarity(sim, labels)
    plot_embedding_scatter(sim, labels)

    return terms, tfidf_matrix, E, sim
