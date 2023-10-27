from typing import List

from sklearn.cluster import HDBSCAN

from chat_rag.inf_retrieval.embedding_models.base_model import BaseModel

def clusterize_text(queries: List[str], embedding_model: BaseModel, batch_size: int = 32, prefix: str = 'query: '):
    """
    Returns the clusters for the queries.
    Parameters
    ----------
    queries : List[str]
        List of queries to be used for clustering.
    embedding_model: BaseModel
        Embedding model to be used for clustering
    batch_size : int, optional
        Batch size for the embedding model, by default 32.
    prefix : str, optional
        Prefix for the queries, by default 'query: '.
    """
    assert prefix in ['query: ', 'passage: '], "prefix must be 'query: ' or 'passage: '"

    queries_embeddings = embedding_model.build_embeddings(queries, batch_size=batch_size, prefix=prefix, disable_progress_bar=True) # specific prefix for e5 models queries

    clusterer = HDBSCAN(min_cluster_size=2, min_samples=1, metric='euclidean')
    clusterer.fit(queries_embeddings)

    return clusterer.labels_
