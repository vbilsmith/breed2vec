from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

from breed2vec.config import DATA_DIR

PLOTS_DIR = DATA_DIR / "plots"

def _resolve_out_dir(out_dir: str | Path | None) -> Path:
    resolved = Path(out_dir) if out_dir else PLOTS_DIR
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def plot_cosine_similarity(
    sim,
    labels=None,
    *,
    out_dir: str | Path | None = None,
    out_path: str | Path | None = None,
):
    """
    sim: (n_docs, n_docs) cosine similarity matrix
    labels: optional list of doc labels (breed names, etc.)
    """
    fig, ax = plt.subplots()
    im = ax.imshow(sim, cmap="Greys")

    ax.set_title("Cosine similarity (SentenceTransformer)")
    ax.set_xlabel("Document")
    ax.set_ylabel("Document")

    if labels:
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)

    fig.colorbar(im, ax=ax, label="cosine similarity")
    plt.tight_layout()
    resolved_dir = _resolve_out_dir(out_dir)
    out_path = Path(out_path) if out_path else resolved_dir / "cosine_similarity.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_embedding_scatter(
    E,
    labels=None,
    *,
    out_dir: str | Path | None = None,
    out_path: str | Path | None = None,
):
    """
    E: (n_docs, dim) embedding matrix
    """
    pca = PCA(n_components=2)
    coords = pca.fit_transform(E)

    fig, ax = plt.subplots()
    ax.scatter(coords[:, 0], coords[:, 1])

    if labels:
        for i, label in enumerate(labels):
            ax.text(coords[i, 0], coords[i, 1], label)

    ax.set_title("Document embeddings (PCA)")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    plt.tight_layout()
    resolved_dir = _resolve_out_dir(out_dir)
    out_path = Path(out_path) if out_path else resolved_dir / "embeddings_pca.png"
    fig.savefig(out_path, dpi=200)
    plt.close(fig)

import matplotlib.pyplot as plt

def plot_pairwise_bars(df_pairs):
    plt.figure()
    x = [f"{a} ↔ {b}" for a, b in zip(df_pairs["breed_1"], df_pairs["breed_2"])]
    y = df_pairs["cosine_similarity"].astype(float).values
    plt.bar(range(len(y)), y)
    plt.xticks(range(len(y)), x, rotation=45, ha="right")
    plt.ylabel("Cosine similarity")
    plt.title("Pairwise cosine similarity (document embeddings)")
    plt.tight_layout()
    plt.show()
