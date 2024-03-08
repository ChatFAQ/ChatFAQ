import os

import ray


@ray.remote(
    runtime_env={
        "HUGGINGFACE_API_KEY": os.environ.get("HUGGINGFACE_API_KEY", None),
    }
)
def generate_embeddings(data):

    from chat_rag.inf_retrieval.embedding_models import E5Model

    print("Ray: generate_embeddings")
    embedding_model = E5Model(
        model_name=data["model_name"],
        use_cpu=data["device"] == "cpu",
        huggingface_key=os.environ.get("HUGGINGFACE_API_KEY", None),
    )

    embeddings = embedding_model.build_embeddings(
        contents=data["contents"], batch_size=data["batch_size"]
    )

    # from tensor to list
    embeddings = [embedding.tolist() for embedding in embeddings]

    return embeddings
