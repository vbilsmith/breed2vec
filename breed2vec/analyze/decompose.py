import csv
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from breed2vec.analyze.viz import plot_cosine_similarity, plot_embedding_scatter

import numpy as np
import pandas as pd

def pairwise_cosine_table(sim, labels, decimals=3):
    sim = np.asarray(sim)
    labels = list(labels)
    n = sim.shape[0]

    rows = []
    for i in range(n):
        for j in range(i + 1, n):
            rows.append({
                "breed_1": labels[i],
                "breed_2": labels[j],
                "cosine_similarity": float(sim[i, j])
            })

    df = pd.DataFrame(rows).sort_values("cosine_similarity", ascending=False)
    df["cosine_similarity"] = df["cosine_similarity"].round(decimals)
    return df


def configure_tfidf(terms, tfidf_matrix, labels, *, out_dir, top_k=10):
    """
    Save top-k TF-IDF terms per document.
    """
    out_path = Path(out_dir) / "tfidf_top_terms.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["breed", "term", "tfidf", "rank"])

        for doc_idx, label in enumerate(labels):
            row = tfidf_matrix[doc_idx].toarray().ravel()
            top_idx = row.argsort()[-top_k:][::-1]

            rank = 1
            for j in top_idx:
                if row[j] <= 0:
                    continue
                writer.writerow([label, terms[j], float(row[j]), rank])
                rank += 1


def save_tfidf_pair_diffs(terms, tfidf_matrix, labels, *, out_dir, top_k=10):
    """
    Save top-k distinguishing terms for each breed pair.
    """
    out_path = Path(out_dir) / "tfidf_pair_diffs.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["breed_a", "breed_b", "term", "delta", "rank", "direction"])

        n_docs = tfidf_matrix.shape[0]
        for i in range(n_docs):
            row_i = tfidf_matrix[i].toarray().ravel()
            for j in range(i + 1, n_docs):
                row_j = tfidf_matrix[j].toarray().ravel()
                diff = row_i - row_j

                pos_idx = diff.argsort()[-top_k:][::-1]
                neg_idx = diff.argsort()[:top_k]

                rank = 1
                for k in pos_idx:
                    if diff[k] <= 0:
                        continue
                    writer.writerow(
                        [labels[i], labels[j], terms[k], float(diff[k]), rank, "A_minus_B"]
                    )
                    rank += 1

                rank = 1
                for k in neg_idx:
                    if diff[k] >= 0:
                        continue
                    writer.writerow(
                        [labels[i], labels[j], terms[k], float(-diff[k]), rank, "B_minus_A"]
                    )
                    rank += 1

def nearest_neighbors(sim, labels, top_k=1):
    sim = np.asarray(sim)
    labels = list(labels)
    n = sim.shape[0]

    out = []
    for i in range(n):
        order = np.argsort(sim[i])
        order = [j for j in order if j != i]
        top = order[-top_k:][::-1]
        for rank, j in enumerate(top, start=1):
            out.append((labels[i], labels[j], float(sim[i, j]), rank))
    return out

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


def analyze_standards(doc_dict, *, out_dir=None):
    labels = list(doc_dict.keys())
    docs = list(doc_dict.values())

    print("n_docs =", len(docs))

    terms, tfidf_matrix, E, sim = find_representations(docs)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\nTop TF-IDF terms per doc:")
    configure_tfidf(terms, tfidf_matrix, labels, out_dir=out_dir, top_k=10)
    save_tfidf_pair_diffs(terms, tfidf_matrix, labels, out_dir=out_dir, top_k=10)

    print("\nCosine similarity between docs (SentenceTransformer):")
    print(sim)

    plot_cosine_similarity(sim, labels, out_dir=out_dir)
    plot_embedding_scatter(E, labels, out_dir=out_dir)

    df_pairs = pairwise_cosine_table(sim, labels)
    print(df_pairs.to_string(index=False))
    df_pairs.to_csv(out_dir / "cosine_similarity_pairs.csv", index=False)

    matrix_path = out_dir / "cosine_similarity_matrix.csv"
    with matrix_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["breed"] + labels)
        for label, row in zip(labels, sim):
            writer.writerow([label] + [f"{v:.6f}" for v in row])

    nn_rows = list(nearest_neighbors(sim, labels, top_k=3))
    for a, b, s, rank in nn_rows:
        print(f"{a} → {b} ({s:.3f})")

    nn_path = out_dir / "nearest_neighbors.csv"
    with nn_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["breed", "neighbor", "similarity", "rank"])
        for a, b, s, rank in nn_rows:
            writer.writerow([a, b, f"{s:.6f}", rank])

    return terms, tfidf_matrix, E, sim
