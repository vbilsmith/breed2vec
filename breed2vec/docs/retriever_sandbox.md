# Retriever Sandbox: Domain-grounded validation of text-embedding similarity

## Context
Identification of dog breeds from images is a classic machine learning classification problem.  
However, it is rarely discussed that dog breeds themselves vary in their degree of similarity to one another.

Such relationships are particularly relevant to fine-grained image classification. It has long been hypothesized that high inter-class similarity and high intra-class variation reduce classification accuracy, yet this hypothesis has rarely been tested explicitly.

This project provides an initial sketch of a pipeline that uses text descriptions of dog breeds—prescriptive standards defining conformation—to quantify inter- and intra-breed similarity and variation.
While the project is still under development, the Retriever Sandbox provides a minimal working example demonstrating how breed standards can be used to recover meaningful relationships among a small set of breeds.

## The Breeds
Here, we analyze the FCI breed standards for Newfoundland dogs, Labrador Retrievers, Golden Retrievers, and the Xoloitzcuintle (“Xolo”).

The first three breeds belong to FCI Group 8 (Retrievers, Flushing Dogs, and Water Dogs).  
The Newfoundland dog and Labrador Retriever were both developed in Newfoundland, Canada in the mid-19th century from a now-extinct breed known as the St. John’s Water Dog.  
The Golden Retriever was developed in the United Kingdom, potentially in part from Flat-Coated Retrievers—another breed derived from the St. John’s Water Dog.  
In contrast, the Xoloitzcuintle is an ancient, hairless breed originating in Mesoamerica.

These historical relationships allow us to generate an *a priori* prediction:  
if text embeddings reflect meaningful morphology and history, then breeds with shared origin and function should appear most similar.

## *A priori* prediction

Broad patterns:
- Labrador Retriever and Newfoundland should be closest (shared historical and geographic context)
- Golden Retriever should be nearby but offset (UK development; possible indirect descent)
- Xoloitzcuintle should be clearly distinct (different lineage and morphology)
 
Morphological Distinctions:
- Hair: The Xolo is hairless.
- Size: Newfoundlands are extra-large, Goldens and Labs are large/medium, and the Xolo is much smaller.
- Coloration: Newfoundlands are black or sometimes black and white. Labs can be black, brown, or yellow. Golden Retrievers are yellow.

## Results
We evaluate semantic similarity using SentenceTransformer embeddings of full breed standards.

**PCA of document embeddings** shows Labrador Retriever and Newfoundland clustering closely, with Golden Retriever nearby but offset, and Xolo clearly separated.
For submission-ready figures, copy the latest run outputs into `breed2vec/figures/`:
```
cp breed2vec/data/plots/<run_id>/embeddings_pca.png breed2vec/figures/
```

- **Cosine similarity heatmaps** confirm the same structure in the full embedding space.
```
cp breed2vec/data/plots/<run_id>/cosine_similarity.png breed2vec/figures/
```
 
- **Pairwise cosine similarity values** quantify these relationships numerically.

| Breed A            | Breed B            | Cosine Similarity |
|--------------------|--------------------|-------------------|
| NEWFOUNDLAND       | LABRADOR RETRIEVER | 0.724             |
| GOLDEN RETRIEVER   | LABRADOR RETRIEVER | 0.701             |
| NEWFOUNDLAND       | GOLDEN RETRIEVER   | 0.658             |
| GOLDEN RETRIEVER   | XOLOITZCUINTLE     | 0.629             |
| NEWFOUNDLAND       | XOLOITZCUINTLE     | 0.575             |
| LABRADOR RETRIEVER | XOLOITZCUINTLE     | 0.555             |


## TF-IDF Results
TF-IDF analysis supports *a priori* predictions of major morphological differences between breeds.

**TF-IDF, Xolo vs Retrievers:**

| Term     | Direction        | Interpretation                                                   |
|----------|------------------|------------------------------------------------------------------|
| variety  | Xolo ≫ Retriever | Xolo standard includes varieties, retrievers do not              |
| hairless | Xolo ≫ Retriever | Hairlessness is a core defining morphological feature of Xolo    |
| coated   | Xolo ≫ Retriever | Alternative varieties of Xolo have different coat-related traits |
| skin     | Xolo ≫ Retriever | Xolo skin texture and exposure emphasized due to hairlessness    |

Similarly, the difference in TF-IDF scores between breeds highlights other predicted distinctions.
For example, comparing Newfoundland to each of the other three breeds yields coloration and size differences, as expected:

| Comparison                      | Top term 1 (tfidf diff)     | Top term 2 (tfidf diff)     | Top term 3 (tfidf diff)     |
|---------------------------------|-----------------------------|-----------------------------|-----------------------------|
| Newfoundland vs Golden Retriever | black (0.2466925437)        | newfoundland (0.1906723625) | massive (0.1511523216)      |
| Newfoundland vs Labrador Retriever | black (0.2577011726)      | massive (0.1511523216)      | newfoundland (0.1510010817) |
| Newfoundland vs Xolo            | black (0.2221567123)        | newfoundland (0.1906723625) | massive (0.1511523216)      |

This pattern indicates that textual similarity reflects not only morphology, but also how variability is encoded and regulated within breed standards themselves.

The main terms differentiating Xolo from the retriever breeds is consistent with what we understand about variation within and between these breeds.

## Limitations of this Approach
This project does not allow us to test hypotheses about genetic relatedness or evolutionary history, nor does it capture the full extent of inter- and intra-breed variation.  
Instead, it evaluates similarity on the basis of shared descriptive language in breed standards.

Textual representations therefore offer a complementary perspective on breed relationships alongside genetics and image-based representations.

## Future Directions
- In development: because breed standards are semi-structured, we plan to analyze section-level embeddings (e.g., history, general appearance, temperament/behavior).
- Findings from this project will be integrated with complementary work on images and genetics to develop multimodal perspectives on breed similarity and variability.
