import gc
import json
import os
import uuid
from logging import getLogger

import pandas as pd
import ray
from crochet import setup
from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models import F
from ray import serve
from ray.serve.config import HTTPOptions, ProxyLocation
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

from back.apps.language_model.models.enums import (
    DeviceChoices,
    IndexStatusChoices,
    RetrieverTypeChoices,
)
from back.apps.language_model.ray_deployments import (
    launch_colbert,
    launch_e5,
    launch_rag,
)
from back.apps.language_model.ray_tasks import (
    generate_embeddings as ray_generate_embeddings,
    generate_titles as ray_generate_titles,
    parse_pdf as ray_parse_pdf,
    ColBERTActor,
    test_task as ray_test_task,
)
from back.config.celery import app
from back.utils.celery import is_celery_worker
from back.utils.ray_connection import connect_to_ray_cluster

if is_celery_worker():
    setup()

logger = getLogger(__name__)



def delete_rag_deployment(rag_deploy_name):
    """
    Delete the RAG deployment Ray Serve.
    """
    if serve.status().applications:
        serve.delete(rag_deploy_name)
        try:
            app_handle = serve.get_app_handle(rag_deploy_name)
            # if it doesn't return error it means the deployment is still running
            print(f"{rag_deploy_name} could not be deleted, so it doesn't exist or it is still running.")
        except:
            print(f'{rag_deploy_name} was deleted successfully')

    # When all deployments are deleted, shutdown the serve instance
    if not serve.status().applications:
        serve.shutdown()


@app.task()
def delete_rag_deployment_task(rag_deploy_name):
    with connect_to_ray_cluster(close_serve=True):
        delete_rag_deployment(rag_deploy_name)


def launch_rag_deployment(rag_config_id):
    """
    Launch the RAG deployment using Ray Serve.
    """
    RAGConfig = apps.get_model("language_model", "RAGConfig")

    rag_config = RAGConfig.objects.get(pk=rag_config_id)
    rag_deploy_name = rag_config.get_deploy_name()
        # delete the deployment if it already exists
    delete_rag_deployment(rag_deploy_name)

    if not serve.status().applications:
        http_options = HTTPOptions(host="0.0.0.0", port=settings.RAY_SERVE_PORT)  # Connect to local cluster or to local Ray driver (both by default run in the same addresses)
        proxy_location = ProxyLocation(ProxyLocation.EveryNode)

        serve.start(detached=True, http_options=http_options, proxy_location=proxy_location)

    retriever_type = rag_config.retriever_config.get_retriever_type()
    retriever_deploy_name = f'retriever_{rag_config.retriever_config.name}'

    if retriever_type == RetrieverTypeChoices.E5:
        model_name = rag_config.retriever_config.model_name
        use_cpu = rag_config.retriever_config.get_device() == DeviceChoices.CPU
        lang = rag_config.knowledge_base.get_lang().value
        retriever_handle = launch_e5(retriever_deploy_name, model_name, use_cpu, rag_config_id, lang)

    elif retriever_type == RetrieverTypeChoices.COLBERT:
        retriever_handle = launch_colbert(retriever_deploy_name, rag_config.s3_index_path)

    else:
        raise ValueError(f"Retriever type: {retriever_type.value} not supported.")

    llm_name = rag_config.llm_config.llm_name
    llm_type = rag_config.llm_config.get_llm_type().value
    launch_rag(rag_deploy_name, retriever_handle, llm_name, llm_type)


@app.task()
def launch_rag_deployment_task(rag_config_id):
    with connect_to_ray_cluster(close_serve=True):
        launch_rag_deployment(rag_config_id)


def get_modified_k_items_ids(rag_config):
    """
    Get the ids of the k items that have been modified.
    Parameters
    ----------
    rag_config : RAGConfig
        The RAGConfig object.
    Returns
    -------
    modified_k_item_ids : list
        A list of primary keys of the KnowledgeItem objects.
    """
    Embedding = apps.get_model("language_model", "Embedding")

    modified_k_item_ids = list(
        Embedding.objects.filter(
            rag_config=rag_config,
            updated_date__lt=F("knowledge_item__updated_date"),
        ).values_list("knowledge_item__pk", flat=True)
    )

    return modified_k_item_ids


def generate_embeddings(k_items, rag_config):
    """
    Generate the embeddings for a knowledge base.
    Parameters
    ----------
    ki_ids : list
        A list of primary keys of the KnowledgeItem objects.
    ragconfig_id : int
        The primary key of the RAGConfig object.
    """
    Embedding = apps.get_model("language_model", "Embedding")

    model_name = rag_config.retriever_config.model_name
    batch_size = rag_config.retriever_config.batch_size
    device = rag_config.retriever_config.get_device().value
    logger.info(
        f"Generating embeddings for {k_items.count()} knowledge items. Knowledge base: {rag_config.knowledge_base.name}"
    )
    logger.info(f"Retriever model: {model_name}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Device: {device}")

    contents = [item.content for item in k_items]
    data = {
        "model_name": model_name,
        "device": device,
        "contents": contents,
        "batch_size": batch_size,
    }

    # Submit the task to the Ray cluster
    num_gpus = 1 if device == "cuda" else 0
    task_name = f"generate_embeddings_{rag_config.name}"
    embeddings_ref = ray_generate_embeddings.options(resources={"tasks": 1}, num_gpus=num_gpus, name=task_name).remote(data)
    embeddings = ray.get(embeddings_ref)

    new_embeddings = [
        Embedding(
            knowledge_item=item,
            rag_config=rag_config,
            embedding=embedding,
        )
        for item, embedding in zip(k_items, embeddings)
    ]
    Embedding.objects.bulk_create(new_embeddings)
    logger.info(
        f"Embeddings generated for knowledge base: {rag_config.knowledge_base.name}"
    )


def index_e5(rag_config):
    """
    Generate the embeddings for a knowledge base for the E5 retriever.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    Embedding = apps.get_model("language_model", "Embedding")

    # When a k item is deleted, its embedding is also deleted in cascade, so we need to remove the embeddings of only the modified k items
    # get the modified k items ids
    modified_k_item_ids = get_modified_k_items_ids(rag_config)

    logger.info(f"Number of modified k items: {len(modified_k_item_ids)}")

    # remove the embeddings of the modified k items
    Embedding.objects.filter(knowledge_item__pk__in=modified_k_item_ids).delete()

    # get the k items that have no associated embeddings
    k_items = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).exclude(embedding__rag_config=rag_config)

    generate_embeddings(k_items=k_items, rag_config=rag_config)


def get_indexed_k_items_ids(s3_index_path):

    from back.config.storage_backends import select_private_storage


    if settings.LOCAL_STORAGE:

        print(f"Reading index from local storage: {s3_index_path}")

        index_root, index_name = os.path.split(s3_index_path)

        print(f"Index root: {index_root}, Index name: {index_name}")

        index_path = os.path.join(index_root, 'colbert', 'indexes', index_name)

        print(f"Final index path: {index_path}")

        # get the filename of the pid_docid_map file
        files = os.listdir(index_path)
        filename = [file for file in files if file.startswith('pid_docid_map')][0]
        local_file_path = os.path.join(index_path, filename)

        print(f"Local file path: {local_file_path}")

        # As it is a local storage, we store the files as saved by ColBERT
        with open(local_file_path, "rb") as local_file:
            pid_docid_map = json.loads(local_file.read())

    else:
        private_storage = select_private_storage()

        print(f"Reading index from S3: {s3_index_path}")

        files = private_storage.listdir(s3_index_path)[1]
        local_index_path = f"/tmp/{s3_index_path}"

        print(f"We will download the pid docid map to {local_index_path}")

        filename = [file for file in files if file.startswith('pid_docid_map')][0]

        if not os.path.exists(local_index_path):
            os.makedirs(local_index_path)

        s3_file_path = os.path.join(s3_index_path, filename)

        print(f"Downloading {filename} from {s3_file_path}")

        local_file_path = os.path.join(local_index_path, filename)
        with open(local_file_path, "wb") as local_file:
            local_file.write(private_storage.open(s3_file_path).read())

        print(f"Downloaded {filename} to {local_file_path}")

        df = pd.read_parquet(local_file_path)

        pid_docid_map = json.loads(df['bytes'][0])

    indexed_k_item_ids = [int(id) for id in set(pid_docid_map.values())]

    return indexed_k_item_ids


def modify_index(rag_config):
    """
    Modify the index for a knowledge base. It removes, modifies and adds the k items to an existing index.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """

    from back.apps.language_model.ray_deployments.colbert_deployment import construct_index_path

    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    Embedding = apps.get_model("language_model", "Embedding")

    s3_index_path = rag_config.s3_index_path
    index_path = construct_index_path(rag_config.s3_index_path)
    bsize = rag_config.retriever_config.batch_size
    device = rag_config.retriever_config.get_device().value
    num_gpus = 1 if device == "cuda" else 0
    storages_mode = settings.STORAGES_MODE
    actor_name = f"modify_colbert_index_{rag_config.name}"


    logger.info(f"Index path: {index_path}")
    logger.info(f"Bsize: {bsize}, Device: {device}, Num GPUs: {num_gpus}, Storages Mode: {storages_mode}")

    colbert = ColBERTActor.options(num_gpus=num_gpus, name=actor_name).remote(index_path, device=device, storages_mode=storages_mode)

    logger.info(f"Index path: {index_path}")

    # k items to remove
    current_k_item_ids = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).values_list("pk", flat=True)

    logger.info(f"Length Current k items: {len(current_k_item_ids)}")

    indexed_k_item_ids = get_indexed_k_items_ids(s3_index_path)

    logger.info(f"Length Indexed k items: {len(indexed_k_item_ids)}")

    # Current indexed k items - k items in the database = k items to remove
    k_item_ids_to_remove = set(indexed_k_item_ids) - set(current_k_item_ids)

    logger.info(f"Number of k items to remove: {len(k_item_ids_to_remove)}")

    # modified k items need to be removed from the index also, to detect which k items are modified we check if the k_item embedding updated_date is lower than the k_item updated_date
    modified_k_item_ids = get_modified_k_items_ids(rag_config)

    logger.info(f"Number of modified k items: {len(modified_k_item_ids)}")

    # add the modified k items to the k items to remove
    k_item_ids_to_remove = k_item_ids_to_remove.union(modified_k_item_ids)

    logger.info(f"Number of k items to remove after adding modified k items: {len(k_item_ids_to_remove)}")

    # ids to string
    k_item_ids_to_remove = [str(id) for id in k_item_ids_to_remove]

    if len(k_item_ids_to_remove) > 0:
        # remove the k items from the ColBERT index
        colbert.delete_from_index.remote(k_item_ids_to_remove)
        index_saved = ray.get(colbert.save_index.remote())

    if index_saved:
        # remove the embeddings with the given ids
        Embedding.objects.filter(knowledge_item__pk__in=k_item_ids_to_remove).delete()

    # get the k items that have no associated embeddings
    k_items = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).exclude(embedding__rag_config=rag_config)

    logger.info(f"Number of k items to add: {len(k_items)}")

    contents_to_add = [item.content for item in k_items]
    contents_pk_to_add = [str(item.pk) for item in k_items]

    logger.info(f"Contents to add: {len(contents_to_add)}")
    logger.info(f"Contents PK to add: {len(contents_pk_to_add)}")

    if k_items.count() > 0:
        # add the k items to the ColBERT index
        try:
            colbert.add_to_index.remote(contents_to_add, contents_pk_to_add, bsize)

            del contents_to_add, contents_pk_to_add
            gc.collect()

            index_saved = ray.get(colbert.save_index.remote())

            colbert.exit.remote()

            if index_saved:

                # create an empty embedding for each knowledge item for the given rag config for tracking which items are indexed
                embeddings = [
                    Embedding(
                        knowledge_item=item,
                        rag_config=rag_config,
                    )
                    for item in k_items
                ]
                Embedding.objects.bulk_create(embeddings)

        except Exception as e:
            logger.error(f"Error adding k items to index: {e}")
            logger.info(
                "This error is probably due to too few knowledge items to add to the index."
            )
            logger.info("Rebuilding index from scratch...")
            # remove all embeddings for the given rag config
            Embedding.objects.filter(rag_config=rag_config).delete()
            # indexing starting from scratch
            creates_index(rag_config=rag_config)



def modify_index_deprecated(rag_config):
    """
    Modify the index for a knowledge base. It removes, modifies and adds the k items to an existing index.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """

    from back.apps.language_model.retriever_clients import ColBERTRetriever


    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    Embedding = apps.get_model("language_model", "Embedding")

    retriever = ColBERTRetriever.from_index(rag_config=rag_config)

    # k items to remove
    current_k_item_ids = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).values_list("pk", flat=True)

    indexed_k_item_ids = [
        int(id) for id in retriever.retriever.model.docid_pid_map.keys()
    ]

    # Current indexed k items - k items in the database = k items to remove
    k_item_ids_to_remove = set(indexed_k_item_ids) - set(current_k_item_ids)

    logger.info(f"Number of k items to remove: {len(k_item_ids_to_remove)}")

    # modified k items need to be removed from the index also, to detect which k items are modified we check if the k_item embedding updated_date is lower than the k_item updated_date
    modified_k_item_ids = get_modified_k_items_ids(rag_config)

    logger.info(f"Number of modified k items: {len(modified_k_item_ids)}")

    # add the modified k items to the k items to remove
    k_item_ids_to_remove = k_item_ids_to_remove.union(modified_k_item_ids)

    # ids to string
    k_item_ids_to_remove = [str(id) for id in k_item_ids_to_remove]

    if len(k_item_ids_to_remove) > 0:
        # remove the k items from the ColBERT index
        retriever.delete_from_index(
            rag_config=rag_config, k_item_ids=k_item_ids_to_remove
        )

    # remove the embeddings with the given ids
    Embedding.objects.filter(knowledge_item__pk__in=k_item_ids_to_remove).delete()

    # get the k items that have no associated embeddings
    k_items = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).exclude(embedding__rag_config=rag_config)

    logger.info(f"Number of k items to add: {len(k_items)}")

    if k_items.count() > 0:
        # add the k items to the ColBERT index
        try:
            retriever.add_to_index(rag_config=rag_config, k_items=k_items)

            # create an empty embedding for each knowledge item for the given rag config for tracking which items are indexed
            embeddings = [
                Embedding(
                    knowledge_item=item,
                    rag_config=rag_config,
                )
                for item in k_items
            ]
            Embedding.objects.bulk_create(embeddings)

        except Exception as e:
            logger.error(f"Error adding k items to index: {e}")
            logger.info(
                "This error is probably due to too few knowledge items to add to the index."
            )
            logger.info("Rebuilding index from scratch...")
            # remove all embeddings for the given rag config
            Embedding.objects.filter(rag_config=rag_config).delete()
            # indexing starting from scratch
            creates_index(rag_config=rag_config)


def creates_index(rag_config):
    """
    Build the index for a knowledge base using the ColBERT retriever.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """
    from back.apps.language_model.ray_deployments.colbert_deployment import construct_index_path

    Embedding = apps.get_model("language_model", "Embedding")
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")

    k_items = KnowledgeItem.objects.filter(knowledge_base=rag_config.knowledge_base)

    s3_index_path = rag_config.generate_s3_index_path()

    colbert_name = rag_config.retriever_config.model_name
    bsize = rag_config.retriever_config.batch_size
    device = rag_config.retriever_config.get_device().value
    storages_mode = settings.STORAGES_MODE


    # TODO: Because these lists can be huge, partition them and use ray.put to store each partition in the object store
    # and then pass the object ids to the remote function
    contents = [item.content for item in k_items]
    contents_pk = [str(item.pk) for item in k_items]

    logger.info(
            f"Building index for knowledge base: {rag_config.knowledge_base.name} with colbert model: {colbert_name}"
        )

    actor_name = f"create_colbert_index_{rag_config.name}"

    index_path = construct_index_path(s3_index_path)
    colbert = ColBERTActor.options(name=actor_name).remote(index_path, colbert_name, bsize, device, storages_mode)
    task_ref = colbert.index.remote(contents, contents_pk)

    # Delete all the contents from memory because they are not needed anymore and can be very large
    del contents
    del contents_pk
    gc.collect()

    ray.get(task_ref)
    index_saved = ray.get(colbert.save_index.remote())
    colbert.exit.remote()


    if index_saved:
        # create an empty embedding for each knowledge item for the given rag config for tracking which items are indexed
        embeddings = [
            Embedding(
                knowledge_item=item,
                rag_config=rag_config,
            )
            for item in k_items
        ]
        Embedding.objects.bulk_create(embeddings)

        # save s3 index path
        rag_config.s3_index_path = s3_index_path
        rag_config.save()

    else:
        logger.error(f"Error building index for knowledge base: {rag_config.knowledge_base.name}")


def index_colbert(rag_config):
    """
    Build the index for a knowledge base.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """

    Embedding = apps.get_model("language_model", "Embedding")

    if Embedding.objects.filter(
        rag_config=rag_config
    ).exists():  # if there are embeddings for the given rag config
        modify_index(rag_config)

    else:
        creates_index(rag_config=rag_config)


@app.task()
def index_task(rag_config_id, launch_rag_deploy: bool = False):
    """
    Build the index for a knowledge base.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    launch_rag_deploy : bool
        Whether to launch the RAG deployment after the index is built.
    """

    with connect_to_ray_cluster(close_serve=launch_rag_deploy):

        RAGConfig = apps.get_model("language_model", "RAGConfig")
        rag_config = RAGConfig.objects.get(pk=rag_config_id)

        retriever_type = rag_config.retriever_config.get_retriever_type()

        # if no_index, remove all rag config embeddings for a clean start and no leftovers
        if rag_config.get_index_status() == IndexStatusChoices.NO_INDEX:
            Embedding = apps.get_model("language_model", "Embedding")
            Embedding.objects.filter(rag_config=rag_config).delete()

            # remove the index files from S3
            delete_index_files(rag_config.s3_index_path)

        if retriever_type == RetrieverTypeChoices.E5:
            index_e5(rag_config)
        elif retriever_type == RetrieverTypeChoices.COLBERT:
            index_colbert(rag_config)

        rag_config.index_status = IndexStatusChoices.UP_TO_DATE
        rag_config.save()

        logger.info(f"Index built for knowledge base: {rag_config.knowledge_base.name}")

        # launch rag
        if launch_rag_deploy:
            launch_rag_deployment(rag_config_id)


def delete_index_files(s3_index_path):
    """
    Delete the index files from S3.
    Parameters
    ----------
    s3_index_path : str
        The unique index path.
    """
    from back.config.storage_backends import select_private_storage
    import shutil

    if s3_index_path:

        if settings.LOCAL_STORAGE:
            index_root, index_name = os.path.split(s3_index_path)
            index_path = os.path.join(index_root, 'colbert', 'indexes', index_name)
            print(f'Deleting local index files from {index_path}')
            if os.path.exists(index_path):
                shutil.rmtree(index_path)

        else: # for s3 and do
            private_storage = select_private_storage()
            logger.info(f"Deleting index files from S3: {s3_index_path}")
            # List all files in the unique index path
            _, files = private_storage.listdir(s3_index_path)
            for file in files:
                # Construct the full path for each file
                file_path = os.path.join(s3_index_path, file)
                # Delete the file from S3
                private_storage.delete(file_path)

            logger.info(f"Index files deleted from S3: {s3_index_path}")


@app.task()
def delete_index_files_task(s3_index_path):
    delete_index_files(s3_index_path)


@app.task()
def parse_url_task(ds_id, url):
    """
    Get the html from the url and parse it.
    Parameters
    ----------
    ds_id : int
        The primary key of the data source to which the crawled items will be added.
    url : str
        The url to crawl.
    """
    from back.apps.language_model.scraping.scraping.spiders.generic import (  # CI
        GenericSpider,
    )

    runner = CrawlerRunner(get_project_settings())
    runner.crawl(GenericSpider, start_urls=url, data_source_id=ds_id)
    KnowledgeBase = apps.get_model("language_model", "KnowledgeBase")
    kb = KnowledgeBase.objects.get(pk=ds_id)


@app.task()
def parse_pdf_task(ds_pk):
    """
    Parse a pdf file and return a list of KnowledgeItem objects.
    Parameters
    ----------
    ds_pk : int
        The primary key of the data source to parse.
    Returns
    -------
    k_items : list
        A list of KnowledgeItem objects.
    """


    logger.info("Parsing PDF file...")
    logger.info(f"PDF file pk: {ds_pk}")

    DataSource = apps.get_model("language_model", "DataSource")
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    KnowledgeItemImage = apps.get_model("language_model", "KnowledgeItemImage")
    ds = DataSource.objects.get(pk=ds_pk)
    pdf_file = ds.original_pdf.read()
    strategy = ds.get_strategy().value
    splitter = ds.get_splitter().value
    chunk_size = ds.chunk_size
    chunk_overlap = ds.chunk_overlap

    with connect_to_ray_cluster():
        # Submit the task to the Ray cluster
        logger.info("Submitting the parse_pdf task to the Ray cluster...")
        task_name = f"parse_pdf_{ds_pk}"
        parsed_items_ref = ray_parse_pdf.options(name=task_name).remote(
            pdf_file, strategy, splitter, chunk_size, chunk_overlap
        )

        parsed_items = ray.get(parsed_items_ref)

    with transaction.atomic():
        for item in parsed_items:
            # Create and save the KnowledgeItem instance
            knowledge_item = KnowledgeItem(
                knowledge_base=ds.knowledge_base,
                data_source=ds,
                title=item.title,
                content=item.content,  # alnaf [[Image 0]] a;mda [[Image 2]]
                url=item.url,
                section=item.section,
                page_number=item.page_number,
                metadata=item.metadata,
            )
            knowledge_item.save()

            # For each image in the item, create and save a KnowledgeItemImage instance
            if item.images:
                for index, image in item.images.items():
                    image_instance = KnowledgeItemImage(
                        image_base64=image.image_base64,
                        knowledge_item=knowledge_item,
                        image_caption=image.image_caption,
                    )
                    image_instance.save()

                    # If the image does not have a caption, use a default caption
                    image_caption = (
                        image.image_caption if image.image_caption else f"Image {index}"
                    )

                    # Replace the placeholder image with the actual image markdown
                    knowledge_item.content = knowledge_item.content.replace(
                        f"[[Image {index}]]",
                        f"![{image_caption}]({image_instance.image_file.name})",
                    )
                    knowledge_item.save()


@app.task()
def generate_titles_task(knowledge_base_pk, n_titles=10):
    """
    Generate titles for the knowledge items of a knowledge base.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    n_titles : int
        The number of titles to generate for each knowledge item.
    """

    KnowledgeBase = apps.get_model("language_model", "KnowledgeBase")
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    AutoGeneratedTitle = apps.get_model("language_model", "AutoGeneratedTitle")

    kb = KnowledgeBase.objects.get(pk=knowledge_base_pk)
    k_items = KnowledgeItem.objects.filter(knowledge_base=knowledge_base_pk)

    contents = [item.content for item in k_items]
    with connect_to_ray_cluster():
        # Submit the task to the Ray cluster
        logger.info("Submitting the generate_titles task to the Ray cluster...")
        task_name = f"generate_titles_{kb.name}"
        titles_ref = ray_generate_titles.options(name=task_name).remote(
            contents, n_titles, kb.get_lang().value
        )

        titles = ray.get(titles_ref)

    for item_titles, item in zip(titles, k_items):
        new_titles = [
            AutoGeneratedTitle(
                knowledge_item=item,
                title=title,
            )
            for title in item_titles
        ]
        AutoGeneratedTitle.objects.bulk_create(new_titles)

    logger.info(f"Titles generated for knowledge base: {kb.name}")


def get_similarity_scores(titles, retriever):
    """
    Get the similarity scores for a list of titles.
    Parameters
    ----------
    titles : list
        A list of titles.
    retriever : PGVectorRetriever
        The retriever to use.
    Returns
    -------
    mean_similarity : float
        The mean similarity score.
    std_similarity : float
        The standard deviation of the similarity scores.
    """
    import numpy as np

    results = retriever.retrieve(titles, top_k=1)
    similarities = [item[0]["similarity"] for item in results]
    mean_similarity = np.mean(similarities)
    std_similarity = np.std(similarities)

    return mean_similarity, std_similarity


@app.task()
def generate_suggested_intents_task(knowledge_base_pk, _generate_titles=False):
    """
    Generate new intents from the users' queries.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    """
    if _generate_titles:
        generate_titles_task(knowledge_base_pk)

    from django.db.models import Max

    from back.apps.language_model.prompt_templates import get_queries_out_of_domain
    from back.apps.language_model.retriever_clients import PGVectorRetriever
    from chat_rag.inf_retrieval.embedding_models import E5Model
    from chat_rag.intent_detection import clusterize_text, generate_intents

    logger.info("generate_new_intents_task called")

    RAGConfig = apps.get_model("language_model", "RAGConfig")
    MessageKnowledgeItem = apps.get_model("language_model", "MessageKnowledgeItem")
    Message = apps.get_model("broker", "Message")
    AutoGeneratedTitle = apps.get_model("language_model", "AutoGeneratedTitle")
    Intent = apps.get_model("language_model", "Intent")

    hugginface_key = os.environ.get("HUGGINGFACE_KEY", None)

    # These are in domain titles
    titles_in_domain = AutoGeneratedTitle.objects.filter(
        knowledge_item__knowledge_base=knowledge_base_pk
    )[:100]

    # Get the RAG config that corresponds to the knowledge base
    rag_conf = RAGConfig.objects.filter(knowledge_base=knowledge_base_pk).first()
    if not rag_conf:
        logger.info(f"No RAG config found for knowledge base: {knowledge_base_pk}")
        return
    lang = rag_conf.knowledge_base.get_lang().value

    # if the retriever type is not e5, then return
    if rag_conf.retriever_config.get_retriever_type() != RetrieverTypeChoices.E5:
        logger.info(f"Intent generation is not supported for retriever type: {rag_conf.retriever_config.get_retriever_type().value} right now")
        return

    e5_model = E5Model(
        model_name=rag_conf.retriever_config.model_name,
        use_cpu=rag_conf.retriever_config.get_device() == DeviceChoices.CPU,
        huggingface_key=hugginface_key,
    )

    retriever = PGVectorRetriever(
        embedding_model=e5_model,
        rag_config=rag_conf,
    )

    # Get similarity scores for the in domain titles and the out of domain queries
    mean_sim_in_domain, std_sim_in_domain = get_similarity_scores(
        [title.title for title in titles_in_domain], retriever
    )

    mean_sim_out_domain, std_sim_out_domain = get_similarity_scores(
        get_queries_out_of_domain(lang), retriever
    )

    logger.info(
        f"Mean similarity in domain: {mean_sim_in_domain}, std: {std_sim_in_domain}"
    )
    logger.info(
        f"Mean similarity out domain: {mean_sim_out_domain}, std: {std_sim_out_domain}"
    )

    # The suggested new intents will have a similarity score between the in domain queries and the out of domain queries
    new_intents_thresholds = {
        "max": mean_sim_in_domain - std_sim_in_domain,
        "min": mean_sim_out_domain + std_sim_out_domain,
    }

    logger.info(f"Suggested intents thresholds: {new_intents_thresholds}")

    # check that the max is greater than the min
    if new_intents_thresholds["max"] < new_intents_thresholds["min"]:
        logger.info(
            "Max threshold is lower than min threshold, no new intents will be generated"
        )
        return

    messages = MessageKnowledgeItem.objects.filter(
        knowledge_item__knowledge_base_id=knowledge_base_pk  # Filter by knowledge base
    ).values("message_id").annotate(
        max_similarity=Max("similarity")
    ) #

    logger.info(f"Number of messages: {messages.count()}")

    # filter the results if the max similarity is between the thresholds
    messages = messages.filter(
        max_similarity__lte=new_intents_thresholds["max"],
        max_similarity__gte=new_intents_thresholds["min"],
    )

    logger.info(f"Number of messages after filtering: {messages.count()}")

    if messages.count() == 0:
        logger.info("There are no suggested intents to generate")
        return

    messages_text = [
        Message.objects.get(id=item["message_id"]).stack[0]["payload"]
        for item in messages
    ]

    # get the cluster labels
    labels = clusterize_text(
        messages_text,
        e5_model,
        batch_size=rag_conf.retriever_config.batch_size,
        prefix="query: ",
    )
    k_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    logger.info(f"Number of clusters: {k_clusters}")

    # list of lists of queries associated to each cluster
    clusters = [[] for _ in range(k_clusters)]
    cluster_instances = [[] for _ in range(k_clusters)]
    for label, query, message_instace in zip(labels, messages_text, messages):
        if label != -1:  # -1 is the label for outliers
            clusters[label].append(query)
            cluster_instances[label].append(message_instace)

    # generate the intents
    intents = generate_intents(clusters)

    # save the intents
    new_intents = [
        Intent(
            intent_name=intent,
            auto_generated=True,
            valid=False,
            suggested_intent=True,
        )
        for intent in intents
    ]

    Intent.objects.bulk_create(new_intents)

    logger.info(f"Number of new intents: {len(new_intents)}")

    # add the messages to each intent
    for intent_cluster, intent in zip(cluster_instances, new_intents):
        # get the value of key 'message_id' from each message
        intent_cluster = [item["message_id"] for item in intent_cluster]
        intent.message.add(*intent_cluster)

    logger.info("New intents generated successfully")


@app.task()
def generate_intents_task(knowledge_base_pk, _generate_titles=False):
    """
    Generate existing intents from a knowledge base.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    """
    if _generate_titles:
        generate_titles_task(knowledge_base_pk)

    from back.apps.language_model.models import AutoGeneratedTitle
    from chat_rag.inf_retrieval.embedding_models import E5Model
    from chat_rag.intent_detection import clusterize_text, generate_intents
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")

    Intent = apps.get_model("language_model", "Intent")
    RAGConfig = apps.get_model("language_model", "RAGConfig")
    rag_conf = RAGConfig.objects.filter(knowledge_base=knowledge_base_pk).first()
    if not rag_conf:
        logger.info(f"No RAG config found for knowledge base: {knowledge_base_pk}")
        return

    # if the retriever type is not e5, then return
    if rag_conf.retriever_config.get_retriever_type() != RetrieverTypeChoices.E5:
        logger.info(f"Intent generation is not supported for retriever type: {rag_conf.retriever_config.get_retriever_type().value} right now")
        return

    hugginface_key = os.environ.get("HUGGINGFACE_KEY", None)

    e5_model = E5Model(
        model_name=rag_conf.retriever_config.model_name,
        use_cpu=rag_conf.retriever_config.get_device() == DeviceChoices.CPU,
        huggingface_key=hugginface_key,
    )
    # AutoGeneratedTitle = apps.get_model("language_model", "AutoGeneratedTitle")

    k_items = KnowledgeItem.objects.filter(knowledge_base=knowledge_base_pk)

    logger.info(f"Generating intents for {k_items.count()} knowledge items")

    # These are in domain titles
    autogen_titles = AutoGeneratedTitle.objects.filter(
        knowledge_item__knowledge_base=knowledge_base_pk
    )

    # get as maximum 10 autogen_titles per knowledge item
    final_autogen_titles = []
    for item in k_items:
        titles = autogen_titles.filter(knowledge_item=item)[:10]
        final_autogen_titles.extend(titles)

    logger.info(f"Number of titles: {len(final_autogen_titles)}")

    # get the queries
    queries = [title.title for title in final_autogen_titles]

    # clusterize the queries
    logger.info("Clusterizing queries...")
    labels = clusterize_text(
        queries,
        e5_model,
        batch_size=rag_conf.retriever_config.batch_size,
        prefix="query: ",
    )
    k_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    logger.info(f"Number of clusters: {k_clusters}")

    # list of lists of queries associated to each cluster
    clusters = [[] for _ in range(k_clusters)]
    cluster_instances = [[] for _ in range(k_clusters)]
    for label, query, title_instance in zip(labels, queries, final_autogen_titles):
        if label != -1:  # -1 is the label for outliers
            clusters[label].append(query)
            cluster_instances[label].append(title_instance)

    # generate the intents
    intents = generate_intents(clusters)

    logger.info(f"Number of new intents: {len(intents)} generated")

    # save the intents
    new_intents = [
        Intent(
            intent_name=intent,
            auto_generated=True,
            valid=False,
            suggested_intent=False,
        )
        for intent in intents
    ]

    Intent.objects.bulk_create(new_intents)

    logger.info("Suggested intents saved successfully")

    # add the knowledge items to each intent
    for intent_cluster, intent in zip(cluster_instances, new_intents):
        # get the knowledge items from each title
        intent_cluster = [item.knowledge_item for item in intent_cluster]
        # remove duplicated knowledge items
        intent_cluster = list(set(intent_cluster))
        intent.knowledge_item.add(*intent_cluster)

    logger.info("Knowledge items added to the intents successfully")


@app.task()
def calculate_rag_stats_task(rag_config_id, dates_ranges=[(None, None)]):
    """
    Compute the statistics for a knowledge base.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    dates_ranges : list
        A list of tuples with the start and end dates for the statistics.
    """
    # TODO: add the % of unlabeled knowledge items
    # TODO: add the % of unlabeled responses

    from datetime import datetime

    from back.apps.language_model.stats import (
        calculate_general_rag_stats,
        calculate_response_stats,
        calculate_retriever_stats,
    )

    Message = apps.get_model("broker", "Message")
    AdminReview = apps.get_model("broker", "AdminReview")
    UserFeedback = apps.get_model("broker", "UserFeedback")


    all_retriever_stats = []
    all_quality_stats = []
    all_general_stats = []

    for start_date_str, end_date_str in dates_ranges:

        # else all the messages
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

        logger.info(f"Start date: {start_date}, end date: {end_date}")

        messages = Message.objects.filter(
            stack__contains=[
            {"type": "lm_generated_text", "payload": {"rag_config_id": str(rag_config_id)}}
        ]
        )

        if start_date is not None:  # Apply start_date if not None
            messages = messages.filter(created_date__gte=start_date)

        if end_date is not None:   # Apply end_date if not None
            messages = messages.filter(created_date__lte=end_date)

        ##############################
        # Retriever stats
        ##############################

        admin_reviews = AdminReview.objects.filter(
            message__in=messages,
        )

        ki_review_data_list = [admin_review.ki_review_data for admin_review in admin_reviews]

        logger.info(f"Number of admin reviews: {admin_reviews.count()}")

        retriever_stats = calculate_retriever_stats(ki_review_data_list)

        all_retriever_stats.append(retriever_stats)

        # print retriever stats
        for k, v in retriever_stats.items():
            logger.info(f"{k}: {v:.2f}")

        ##############################
        # Response quality stats
        ##############################

        user_feedbacks = UserFeedback.objects.filter(
            message__in=messages,
            value__isnull=False,
        )

        response_stats = calculate_response_stats(admin_reviews, user_feedbacks)

        for k, v in response_stats.items():
            logger.info(f"{k}: {v:.2f}")

        all_quality_stats.append(response_stats)

        ##############################
        # General RAG stats
        ##############################

        prev_messages_ids = messages.annotate(previous_message_id=F('prev__id'))\
                                    .values('prev_id')\
                                    .filter(previous_message_id__isnull=False)

        prev_messages = Message.objects.filter(id__in=prev_messages_ids)

        general_rag_stats = calculate_general_rag_stats(prev_messages, messages.count())

        for k, v in general_rag_stats.items():
            logger.info(f"{k}: {v:.2f}")

        all_general_stats.append(general_rag_stats)


    # TODO: Return the stats to the frontend


@app.task()
def calculate_usage_stats_task(rag_config_id=None, dates_ranges=[(None, None)]):
    """
    Compute the usage statistics related to the number of messages, conversations, etc.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object to calculate the usage stats for. If None, the stats will be calculated for all the historical data.
    dates_ranges : list
        A list of tuples with the start and end dates for the statistics.
    """

    from datetime import datetime

    from back.apps.language_model.stats import calculate_usage_stats

    Message = apps.get_model("broker", "Message")

    all_usage_stats = []

    for start_date_str, end_date_str in dates_ranges:

        # else all the messages
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

        logger.info(f"Start date: {start_date}, end date: {end_date}")

        messages = Message.objects.all()

        if rag_config_id:
            messages = messages.filter(stack__contains=[
                {"type": "lm_generated_text", "payload": {"rag_config_id": str(rag_config_id)}}
            ])

        if start_date is not None:  # Apply start_date if not None
            messages = messages.filter(created_date__gte=start_date)

        if end_date is not None:   # Apply end_date if not None
            messages = messages.filter(created_date__lte=end_date)

        usage_stats = calculate_usage_stats(messages)

        for k, v in usage_stats.items():
            logger.info(f"{k}: {v}")

        all_usage_stats.append(usage_stats)


@app.task()
def test_task():
    with connect_to_ray_cluster():
        test_task_ref = ray_test_task.options(name="test_task").remote(str(uuid.uuid4()))
        res_test_task = ray.get(test_task_ref)
        return res_test_task
