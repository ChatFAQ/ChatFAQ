import sys
from logging import getLogger
from ray.util.state import api as ray_api
from datetime import datetime



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


def is_ray_worker():
    """
    Check if the current process is a Ray worker.
    """
    return any("ray" in s for s in sys.argv)



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
    task_types = ["generate_embeddings", "parse_pdf_task", "parse_url_task", "generate_titles_task", "get_filesystem", "create_colbert_index", "test_task", "get_filesystem", "generate_intents", "get_similarity_scores", "clusterize_queries", "generate_intents_task", "generate_suggested_intents_task", ]
    tasks = []
    for task_type in task_types:
        tasks += [j.__dict__ for j in ray_api.list_tasks(filters=[("func_or_class_name", "=", task_type)])]
    if add_celery_fields:
        tasks = [_ray_to_celery_task(task) for task in tasks]
    return tasks
