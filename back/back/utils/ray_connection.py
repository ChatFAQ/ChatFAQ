import os
import random
from contextlib import contextmanager
from logging import getLogger
from time import sleep
import subprocess


import ray
from django.core.exceptions import ImproperlyConfigured
from ray import serve

logger = getLogger(__name__)

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
        result = ray.init(address="auto", ignore_reinit_error=True)
        logger.info(f'Connected to Ray cluster as a driver {n} {type(result)}')
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
        exists_ray_cluster = (os.getenv('RAY_CLUSTER', 'False') == 'True')
        print(f"exists_ray_cluster: {exists_ray_cluster} {os.getenv('RAY_CLUSTER')}")
        if exists_ray_cluster:
            if not check_remote_ray_cluster():
                logger.error(f"You provided a remote Ray Cluster address but the connection failed, these could be because of three reasons: ")
                # logger.error(f"1. The provided address is incorrect: {RAY_ADDRESS}")
                logger.error(f"2. You forgot to start a local ray process with the django command: python manage.py rayconnect")
                logger.error(f"3. The remote Ray cluster is not running")
                raise ImproperlyConfigured("Unable to connect to the Ray cluster after multiple attempts.")
        else:
            initialize_ray_locally()

