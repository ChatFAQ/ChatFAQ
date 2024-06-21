import logging
import os
from typing import List

import umap
from sklearn.cluster import HDBSCAN # Maybe replace with cuML implementation for speedup when using GPU
from sklearn.feature_extraction.text import TfidfVectorizer

from chat_rag.inf_retrieval.embedding_models import BaseModel, E5Model

logger = logging.getLogger(__name__)

model_dict = {
    "en": "Alibaba-NLP/gte-base-en-v1.5",
    "es": "intfloat/multilingual-e5-large-instruct",
    "fr": "intfloat/multilingual-e5-large-instruct",
    "multilang": "intfloat/multilingual-e5-large-instruct",
}


def generate_embeddings(texts, batch_size, lang, device):
    hf_key = os.environ.get("HUGGINGFACE_API_KEY", None)

    model_name = model_dict[lang] if lang != "multilang" else model_dict["multilang"]
    use_cpu = device == "cpu"

    if lang == "en":
        # for gte maybe set unpad_inputs and use_memory_efficient_attention to true, it would require to install xformers
        embedding_model = BaseModel(model_name, use_cpu, hf_key)
    else:
        embedding_model = E5Model(model_name, use_cpu, hf_key)

    print(f"Generating embeddings for {len(texts)} queries...")
    embeddings = embedding_model.build_embeddings(
        texts, batch_size=batch_size, disable_progress_bar=False
    )

    return embeddings


def vectorize_text(texts: List[str], lang: str = "en"):
    """
    Returns the vectorized representation of the queries using TF-IDF.
    Parameters
    ----------
    texts : List[str]
        List of texts to be vectorized.
    lang : str, optional
        Language of the queries, by default "en".
    """
    stop_words = "english" if lang == "en" else None
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    logger.info("Vectorizing text using TF-IDF")
    vectors = vectorizer.fit_transform(texts)
    return vectors


def do_umap(embeddings, low_resource=False):
    """
    Performs dimensionality reduction using UMAP.
    """
    metric = (
        "hellinger" if low_resource else "euclidean"
    )  # Hellinger for tf-idf, euclidean for embeddings
    n_components = 10 if low_resource else 2  # 10 for tf-idf, 2 for embeddings
    n_neighbors = (
        75 if embeddings.shape[0] > 10000 else 15
    )  # 75 for large datasets to get more global clusters, 15 for smaller datasets

    umap_model = umap.UMAP(
        n_components=n_components,
        random_state=42,
        n_neighbors=n_neighbors,
        metric=metric,
    )
    print("Fitting UMAP model")
    umap_embeddings = umap_model.fit_transform(embeddings)
    return umap_embeddings


def perform_clustering(X):
    """
    Performs clustering on the embeddings using HDBSCAN.
    """
    length = len(X)
    print("Clustering...")
    MIN_CLUSTERS = 3
    max_cluster_size = length // MIN_CLUSTERS  # at least 3 clusters
    max_cluster_size = (
        max_cluster_size if length >= (2 * MIN_CLUSTERS) else None
    )  # if there are less than 6 queries, don't limit the cluster size
    clusterer = HDBSCAN(
        min_cluster_size=2,
        max_cluster_size=max_cluster_size,
        min_samples=1,
        metric="euclidean",
    )
    clusterer.fit(X)
    return clusterer.labels_


def clusterize_text(
    texts: List[str],
    batch_size: int = 32,
    lang: str = "en",
    device: str = "cpu",
    low_resource: bool = True,
):
    """
    Returns the clusters for the queries.
    Parameters
    ----------
    texts : List[str]
        List of texts to be used for clustering.
    batch_size : int, optional
        Batch size for the embedding model, by default 32.
    lang : str, optional
        Language of the queries, by default "en".
    device : str, optional
        Device to use for the embedding model, by default "cpu".
    low_resource : bool, optional
        If True, uses TF-IDF for vectorization, if False, uses embeddings, by default True.
    """

    if low_resource:
        X = vectorize_text(texts, lang)
    else:
        if len(texts) > 50000 and device == "cpu":
            logger.warning(
                "You are using a CPU for generating embeddings for a large number of texts. "
                "This might take a long time. Consider using a GPU for faster processing or using the low_resource option."
            )

        X = generate_embeddings(texts, batch_size, lang, device)

    X = do_umap(X)

    labels = perform_clustering(X)

    return labels
