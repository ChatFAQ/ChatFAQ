from back.config.celery import app as celery_app


def ensure_worker_queues():
    c = celery_app.control
    i = c.inspect()
    active_queues_info = i.active_queues()

    if active_queues_info is None:
        # Handle the case where no queue information is returned
        return []

    active_queues = set()
    for key in active_queues_info:
        for queue in active_queues_info[key]:
            active_queues.add(queue["name"])

    workers = i.stats().keys()
    worker_queues = []
    for worker in workers:
        q_name = f"queue-{worker}"
        if q_name not in active_queues:
            c.add_consumer(q_name, reply=True, destination=[worker])
        worker_queues.append(q_name)
    return worker_queues



def recache_models(log_caller=None):
    from back.apps.language_model.tasks import llm_query_task

    worker_queues = ensure_worker_queues()
    for worker_queue in worker_queues:
        llm_query_task.apply_async(queue=worker_queue, kwargs={"recache_models": True, "log_caller": log_caller})
