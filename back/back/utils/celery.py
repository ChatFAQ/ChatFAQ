from back.config.celery import app as celery_app


def get_worker_names():
    c = celery_app.control
    i = c.inspect()
    if not i.stats():
        return []
    return list(i.stats().keys())


def ensure_worker_queues():
    c = celery_app.control
    i = c.inspect()
    active_queues_info = i.active_queues()

    active_queues_info = [] if active_queues_info is None else active_queues_info

    active_queues = set()
    for key in active_queues_info:
        for queue in active_queues_info[key]:
            active_queues.add(queue["name"])

    workers = i.stats().keys() if i.stats() else []
    worker_queues = []
    for worker in workers:
        q_name = f"queue-{worker}"
        if q_name not in active_queues:
            c.add_consumer(q_name, reply=True, destination=[worker])
        worker_queues.append(q_name)
    return worker_queues


def recache_models(logger_name=None):
    from back.apps.language_model.tasks import llm_query_task

    worker_queues = ensure_worker_queues()
    if len(worker_queues) == 0:
        print("No workers found")
    for worker_queue in worker_queues:
        llm_query_task.apply_async(queue=worker_queue, kwargs={"recache_models": True, "logger_name": logger_name})
