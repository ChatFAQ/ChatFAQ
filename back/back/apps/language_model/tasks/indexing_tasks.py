import gc
import json
import os
from logging import getLogger

import pandas as pd
import ray
from django.apps import apps
from django.conf import settings
from django.db.models import F

from back.apps.language_model.models.enums import (
    IndexStatusChoices,
    RetrieverTypeChoices,
)


from back.apps.language_model.tasks import (
    generate_embeddings as ray_generate_embeddings,
    ColBERTActor,
)
from back.config.celery import app
from back.utils.ray_connection import connect_to_ray_cluster

logger = getLogger(__name__)


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

    try:
        save_index = False

        # k items to remove
        current_k_item_ids = KnowledgeItem.objects.filter(
            knowledge_base=rag_config.knowledge_base
        ).values_list("pk", flat=True)

        indexed_k_item_ids = get_indexed_k_items_ids(s3_index_path)

        logger.info(f"Number of current k items: {len(current_k_item_ids)}")

        # Current indexed k items - k items in the database = k items to remove
        k_item_ids_to_remove = set(indexed_k_item_ids) - set(current_k_item_ids)

        logger.info(f"Number of k items to remove: {len(k_item_ids_to_remove)}")

        # modified k items need to be removed from the index also
        modified_k_item_ids = get_modified_k_items_ids(rag_config)

        logger.info(f"Number of modified k items: {len(modified_k_item_ids)}")

        # add the modified k items to the k items to remove
        k_item_ids_to_remove = k_item_ids_to_remove.union(modified_k_item_ids)

        logger.info(f"Number of k items to remove after adding modified k items: {len(k_item_ids_to_remove)}")

        # ids to string
        k_item_ids_to_remove = [str(id) for id in k_item_ids_to_remove]

        if k_item_ids_to_remove:
            logger.info("Removing from the index...")
            delete_task_ref = colbert.delete_from_index.remote(k_item_ids_to_remove)
            logger.info("Deleted from the index.")

            save_index = True

            # remove the embeddings with the given ids
            Embedding.objects.filter(knowledge_item__pk__in=k_item_ids_to_remove).delete()

        # get the k items that have no associated embeddings
        k_items = KnowledgeItem.objects.filter(
            knowledge_base=rag_config.knowledge_base
        ).exclude(embedding__rag_config=rag_config)

        logger.info(f"Number of k items to add: {len(k_items)}")

        contents_to_add = [item.content for item in k_items]
        contents_pk_to_add = [str(item.pk) for item in k_items]

        if k_items:
            add_task_ref = colbert.add_to_index.remote(contents_to_add, contents_pk_to_add, bsize)

            # create an empty embedding for each knowledge item for the given rag config for tracking which items are indexed
            embeddings = [
                Embedding(
                    knowledge_item=item,
                    rag_config=rag_config,
                )
                for item in k_items
            ]
            Embedding.objects.bulk_create(embeddings)

        # wait for the tasks to finish to catch any exceptions
        ray.get([delete_task_ref, add_task_ref])

        if save_index:

            new_s3_index_path = rag_config.generate_s3_index_path()
            logger.info(f"New index path: {new_s3_index_path}")

            # Now we save the index only once after all modifications
            index_saved = ray.get(colbert.save_index.remote(
                construct_index_path(new_s3_index_path)
            ))
            rag_config.s3_index_path = new_s3_index_path
            rag_config.save()

            # delete the old index files
            delete_index_files(s3_index_path)

        if not index_saved:
            raise Exception("Failed to save index.")

    except Exception as e:
        logger.error(f"Error modifying index: {e}")
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
    colbert = ColBERTActor.options(name=actor_name).remote(index_path, device=device, colbert_name=colbert_name, storages_mode=storages_mode)
    colbert.index.remote(contents, contents_pk, bsize)

    # Delete all the contents from memory because they are not needed anymore and can be very large
    del contents
    del contents_pk
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

