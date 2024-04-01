import os

import ray

from logging import getLogger

logger = getLogger(__name__)


@ray.remote(num_cpus=1, resources={"tasks": 1})
def generate_embeddings(data):

    from chat_rag.inf_retrieval.embedding_models import E5Model

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


@ray.remote(num_cpus=1, resources={"tasks": 1})
def parse_pdf(pdf_file, strategy, splitter, chunk_size, chunk_overlap):
    from io import BytesIO
    from chat_rag.data.parsers import parse_pdf
    from chat_rag.data.splitters import get_splitter

    pdf_file = BytesIO(pdf_file)

    splitter = get_splitter(splitter, chunk_size, chunk_overlap)

    logger.info(f"Splitter: {splitter}")
    logger.info(f"Strategy: {strategy}")
    logger.info(f"Chunk size: {chunk_size}")
    logger.info(f"Chunk overlap: {chunk_overlap}")

    parsed_items = parse_pdf(file=pdf_file, strategy=strategy, split_function=splitter)

    return parsed_items


@ray.remote(num_cpus=1, resources={"tasks": 1})
def generate_titles(contents, n_titles, lang):
    from chat_rag.inf_retrieval.query_generator import QueryGenerator

    api_key = os.environ.get("OPENAI_API_KEY", None)
    query_generator = QueryGenerator(api_key, lang=lang)

    new_titles = []
    for content in contents:
        titles = query_generator(content, n_queries=n_titles)
        new_titles.append(titles)

    return new_titles
