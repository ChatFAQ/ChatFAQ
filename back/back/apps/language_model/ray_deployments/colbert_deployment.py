from typing import List
import os
import ray
from ray import serve

from ragatouille import RAGPretrainedModel
from back.apps.language_model.ray_tasks import get_filesystem
from chat_rag.inf_retrieval.reference_checker import clean_relevant_references


@serve.deployment(
    name="colbert_deployment",
    ray_actor_options={
        "num_cpus": 1,
        "resources": {
            "rags": 1,
        },
    },
)
class ColBERTDeployment:
    """
    ColBERTDeployment class for serving the a ColBERT retriever in a Ray Serve deployment in a Ray cluster.
    """

    def __init__(self, index_path, remote_ray_cluster, storages_mode):
        print(f"Initializing ColBERTDeployment")

        index_path = self._read_index(index_path, remote_ray_cluster, storages_mode)

        self.retriever = RAGPretrainedModel.from_index(index_path)

        # Test query for loading the searcher for the first time
        self.retriever.search("test query", k=1)
        print(f"ColBERTDeployment initialized with index_path={index_path}")

    def _read_index(self, index_path, remote_ray_cluster, storages_mode):
        """
        If the index_path is an S3 path, read the index from object storage and write it to the local storage.
        """
        fs_ref = get_filesystem.remote(storages_mode)

        from tqdm import tqdm

        def write_file(row, base_path):
            # Extract bytes and path from the row
            content, file_path = row["bytes"], row["path"]

            file_name = os.path.basename(file_path)

            # Combine the base path with the original file path
            full_path = os.path.join(base_path, file_name)

            print(f"Writing file to {full_path}")

            # Ensure the directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            # Write the file
            with open(full_path, "wb") as file:
                file.write(content)

        print(f"Reading index from {index_path}")

        if "s3://" in index_path:

            from pyarrow.fs import FileSelector

            fs = ray.get(fs_ref)

            if fs is not None:
                # unwrap the filesystem object
                fs = fs.unwrap()

            files = fs.get_file_info(FileSelector(index_path.split('s3://')[1]))

            file_paths = [file.path for file in files]

            # print total index size in MB
            print(f"Downloading index with size: {sum(file.size for file in files) / 1024 / 1024:.2f} MB")

            index = ray.data.read_parquet_bulk(file_paths, filesystem=fs)
            print(f"Downloaded {index.count()} files from S3")

            index_name = os.path.basename(index_path)
            index_path = os.path.join("indexes", index_name)

            # If remote Ray cluster running on containers
            if remote_ray_cluster:
                index_path = os.path.join("/", index_path)

            # if the directory exists, delete it
            if os.path.exists(index_path):
                print(f"Deleting existing index at {index_path}")
                import shutil
                shutil.rmtree(index_path)

            print(f"Writing index to {index_path}")
            for row in tqdm(index.iter_rows()):
                write_file(row, index_path)
        return index_path

    @serve.batch(max_batch_size=5, batch_wait_timeout_s=0.2)
    async def batch_handler(self, queries: List[str], top_ks: List[int]):
        """
        Batch handler for the retriever model. This method is called by Ray Serve when a batch of requests is received.
        It creates the query embeddings, sends them to a pgvector backend endpoint for retrieval asynchronously and returns the results.
        """

        queries_results = self.retriever.search(queries, k=max(top_ks))

        # For normalizing the scores
        query_maxlen = self.retriever.model.model_index.searcher.config.query_maxlen

        # If only one query was passed, the result is not a list
        queries_results = [queries_results] if len(queries) == 1 else queries_results

        results = []
        for query_results, top_k in zip(queries_results, top_ks):
            for result in query_results:
                result["similarity"] = result["score"] / query_maxlen

            # Filter out results not relevant to the query
            query_results = clean_relevant_references(query_results)

            # only keep k_item_id, content and similarity
            query_results = [
                {
                    "k_item_id": int(result["document_id"]),
                    "similarity": result["similarity"],
                    "content": result["content"],
                }
                for result in query_results
            ]

            results.append(query_results[:top_k])

        return results

    def update_batch_params(self, max_batch_size, batch_wait_timeout_s):
        self.batch_handler.set_max_batch_size(max_batch_size)
        self.batch_handler.set_batch_wait_timeout_s(batch_wait_timeout_s)

    async def __call__(self, query: str, top_k: int):
        return await self.batch_handler(query, top_k)


def construct_index_path(index_path: str, storages_mode, remote_ray_cluster: bool):
    """
    Construct the index path based on the STORAGES_MODE environment variable.
    """

    if storages_mode == "local":
        if remote_ray_cluster:
            return os.path.join(
                "/", index_path
            )  # In the ray containers we mount local_storage/indexes/ as /indexes/
        else:
            return os.path.join("back", "back", "local_storage", index_path)
    elif storages_mode in ["s3", "do"]:
        bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME")
        return f"s3://{bucket_name}/{index_path}"


def launch_colbert(retriever_deploy_name, index_path):
    print(f"Launching ColBERT deployment with name: {retriever_deploy_name}")

    storages_mode = os.environ.get("STORAGES_MODE", "local")
    remote_ray_cluster = os.getenv("RAY_CLUSTER", "False") == "True"

    index_path = construct_index_path(index_path, storages_mode, remote_ray_cluster)
    retriever_handle = ColBERTDeployment.options(
        name=retriever_deploy_name,
    ).bind(index_path, remote_ray_cluster, storages_mode)
    print(f"Launched ColBERT deployment with name: {retriever_deploy_name}")
    return retriever_handle
