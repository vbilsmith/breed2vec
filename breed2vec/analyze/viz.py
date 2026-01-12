import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

def plot_cosine_similarity(sim, labels=None):
    """
    sim: (n_docs, n_docs) cosine similarity matrix
    labels: optional list of doc labels (breed names, etc.)
    """
    fig, ax = plt.subplots()
    im = ax.imshow(sim)

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
    plt.show()


def plot_embedding_scatter(E, labels=None):
    """
    E: (n_docs, dim) embedding matrix
    """
    pca = PCA(n_components=2)
    coords = pca.fit_transform(E)

    plt.figure()
    plt.scatter(coords[:, 0], coords[:, 1])

    if labels:
        for i, label in enumerate(labels):
            plt.text(coords[i, 0], coords[i, 1], label)

    plt.title("Document embeddings (PCA)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()
    plt.show()
