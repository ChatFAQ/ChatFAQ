import os
import random
from django.conf import settings
from contextlib import contextmanager
from logging import getLogger
from time import sleep
from ray.util.state import api as ray_api
from datetime import datetime


import ray
from django.core.exceptions import ImproperlyConfigured
from ray import serve

from back.utils.celery import get_celery_tasks

logger = getLogger(__name__)

map_ray_to_celery_status_task = { # SUCCESS, STARTED, WAITING, FAILURE
    "NIL": "PENDING",
    "PENDING_ARGS_AVAIL": "WAITING",
    "PENDING_NODE_ASSIGNMENT": "WAITING",
    "PENDING_OBJ_STORE_MEM_AVAIL": "WAITING",
    "PENDING_ARGS_FETCH": "WAITING",
    "SUBMITTED_TO_WORKER": "WAITING",
    "RUNNING": "STARTED",
    "RUNNING_IN_RAY_GET": "STARTED",
    "RUNNING_IN_RAY_WAIT": "STARTED",
    "FINISHED": "SUCCESS",
    "FAILED": "FAILURE"
}


@contextmanager
def connect_to_ray_cluster(close_serve=False):
    """
    Connect to a Ray cluster as a client or as a driver.
    If the RAY_ADDRESS environment variable is set, connect as a client.
    Otherwise, connect as a driver.
    It's important to disconnect from the cluster after using it, to avoid connection leaks.
    """
    initialized = ray.is_initialized()
    n = random.randint(0, 10000)
    if not initialized:
        # Connect as a driver
        result = ray.init(address="auto", ignore_reinit_error=True, namespace="back-end")
        initialized = ray.is_initialized()
        logger.info(f'Connected to Ray cluster as a driver {n}')
    else:
        logger.info(f'Ray cluster already connected as a driver {n}')
    try:
        yield
    finally:
        if initialized:
            ray.shutdown()
            logger.info(f'Driver disconnected from the Ray cluster {n}')
            if close_serve:
                serve.shutdown()
                logger.info(f'Serve shutdown {n}')
        else:
            logger.info(f'Driver still connected to the Ray cluster {n}')




def check_remote_ray_cluster(retries=3, backoff_factor=2):
    """
    Check if the provided address is a valid Ray cluster.
    """

    for attempt in range(retries):
        try:
            logger.info(f"Attempting to connect to the Ray cluster...")
            result = ray.init(address='auto', ignore_reinit_error=True)
            logger.info(f"Connected to the Ray cluster successfully. {result}")
            log_ray_resources()
            ray.shutdown()
            return True
        except ConnectionError as e:
            logger.error(f"Attempt {attempt + 1} to connect to Ray failed: {e}")
            sleep(backoff_factor ** attempt)  # Exponential backoff
    return False

def initialize_ray_locally():
    """
    Initialize a Ray cluster locally for development purposes.
    """
    try:
        import chat_rag
    except ImportError:
        logger.error("chat-rag package not found, please install it to use a local ray cluster")
        return

    logger.info("Starting Ray locally...")
    resources = {"rags": 100, "tasks": 100}
    ray.init(
        "local",
        ignore_reinit_error=True,
        resources=resources,
        include_dashboard=True,
        dashboard_port=8265,
        namespace="back-end"
    )
    log_ray_resources()

def log_ray_resources():
    logger.info("Available resources:")
    logger.info(ray.available_resources())

def initialize_or_check_ray():
    """
    Initialize a Ray cluster locally or check if a remote Ray cluster is available.
    """
    if not ray.is_initialized():
        remote_ray_cluster = settings.REMOTE_RAY_CLUSTER_ADDRESS_HEAD
        print(f"remote_ray_cluster: {remote_ray_cluster}")
        if remote_ray_cluster:
            if not check_remote_ray_cluster():
                logger.error(f"You provided a remote Ray Cluster address but the connection failed, these could be because of three reasons: ")
                # logger.error(f"1. The provided address is incorrect: {RAY_ADDRESS}")
                logger.error(f"2. You forgot to start a local ray process with the django command: python manage.py rayconnect")
                logger.error(f"3. The remote Ray cluster is not running")
                raise ImproperlyConfigured("Unable to connect to the Ray cluster after multiple attempts.")
        else:
            initialize_ray_locally()


def _ray_to_celery_task(ray_task):
    """
    Convert a Ray task to a Celery task.
    """
    return {
        **ray_task,
        "id": ray_task["task_id"],
        "task_name": ray_task["name"],
        "state": map_ray_to_celery_status_task[ray_task["state"]],
        "worker": ray_task["worker_id"],
        "task_args": ray_task["runtime_env_info"],
        # traceback -> task_log_info + error_message
        "traceback": (ray_task["task_log_info"] or "") + (ray_task["error_message"] or ""),
        # "start_time_ms" -> func date_created
        "date_created": datetime.utcfromtimestamp(ray_task["start_time_ms"] or 0 / 1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
        "date_done": datetime.utcfromtimestamp(ray_task["end_time_ms"] or 0 / 1000).strftime('%Y-%m-%d %H:%M:%S.%f'),
        "periodic_task_name": None,
        "task_kwargs": None,
        "content_type": None,
        "content_encoding": None,
        "meta": {},
    }


def get_ray_tasks(add_celery_fields=False):
    """
    Get the number of Ray tasks that are currently running or has been run.
    """
    task_types = ["generate_embeddings", "parse_pdf", "generate_titles", "get_filesystem", "create_colbert_index", "test_task", "get_filesystem"]
    tasks = []
    for task_type in task_types:
        tasks += [j.__dict__ for j in ray_api.list_tasks(filters=[("func_or_class_name", "=", task_type)])]
    if add_celery_fields:
        tasks = [_ray_to_celery_task(task) for task in tasks]
    return tasks
