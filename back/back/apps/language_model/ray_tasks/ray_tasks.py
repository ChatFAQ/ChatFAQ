import os
from logging import getLogger

import ray

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


@ray.remote(num_cpus=0.001)
def get_filesystem(storages_mode):
    """
    For Digital Ocean, we need to provide a custom filesystem object to write the index to the cloud storage
    """
    from pyarrow import fs
    from ray.data.datasource import _S3FileSystemWrapper

    if storages_mode == "do":
        
        endpoint_url = f'https://{os.environ.get("DO_REGION")}.digitaloceanspaces.com'
        s3fs = fs.S3FileSystem(
            access_key=os.environ.get("AWS_ACCESS_KEY_ID"),
            secret_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            endpoint_override=endpoint_url,
        )

        # This is a hack to make the S3FileSystem object serializable (https://github.com/ray-project/ray/pull/17103)
        s3fs = _S3FileSystemWrapper(s3fs)

        print("Using Digital Ocean S3 filesystem")

        fs_ref = ray.put(s3fs)
        return fs_ref

    return None


@ray.remote(num_cpus=1, resources={"tasks": 1})
def create_colbert_index(
    colbert_name, bsize, device, s3_index_path, storages_mode, contents_pk, contents
):

    def get_num_gpus():
        try:
            import torch

            return torch.cuda.device_count()
        except:
            return -1

    try:

        from ragatouille import RAGPretrainedModel


        index_root, index_name = os.path.split(s3_index_path)
        print(f'S3 index path: {s3_index_path}')
        print(f"Index root: {index_root}, Index name: {index_name}")

        if "s3://" in index_root:
            # get the index root folder, we don't care about the bucket right now
            _, index_root = os.path.split(index_root)

        n_gpus = -1 if device == "cpu" else get_num_gpus()

        retriever = RAGPretrainedModel.from_pretrained(
            colbert_name, index_root=index_root, n_gpu=n_gpus
        )

        # Update the index path to use the unique index path
        local_index_path = retriever.index(
            index_name=index_name,
            collection=contents,
            document_ids=contents_pk,
            split_documents=True,
            max_document_length=512,
            bsize=bsize,
        )

        print(f"Local index path: {local_index_path}")

        # if cloud storage, then we write the index to the cloud storage
        if "s3://" in s3_index_path:
            # We read the index as binary files into a table with the schema, where each file is a row:
            # Column  Type
            # ------  ----
            # bytes   binary
            # path    string,
            fs_ref = ray.get(get_filesystem.remote(storages_mode))
            fs = ray.get(fs_ref)

            # unwrap the filesystem object
            fs = fs.unwrap()

            print('Reading index from local storage')
            local_index_path = 'local://' + os.path.join(os.getcwd(), local_index_path)
            index = ray.data.read_binary_files(local_index_path, include_paths=True)

            print(f"Writing index to object storage {s3_index_path}")
            # Then we can write the index to the cloud storage
            index.write_parquet(s3_index_path, filesystem=fs)
            print('Index written to object storage')

            # success
            return True

    except Exception as e:
        print(f"Error creating index: {e}")
        # failure
        return False


@ray.remote(num_cpus=1, resources={"tasks": 1})
def test_task(argument_one):
    import time
    print("with arg: ", argument_one, "start")
    time.sleep(5)
    print("with arg: ", argument_one, "finished")

    return 123456789
