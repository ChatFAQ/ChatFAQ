import sys

from back.config.celery import app as celery_app


def is_celery_worker():
    """
    There is a more integrated solution although the signal doens't seems to work properly:
    celery.py:

    app.running = False

    @worker_init.connect
    def set_running(*args, **kwargs):
        app.running = True

    tasks.py:
    if app.running:
        # do something
    """
    # checks if the list sys.argv has any string element that contains "celery"
    exists_celery = any("celery" in s for s in sys.argv)
    worker_celery = any("worker" in s for s in sys.argv)
    return exists_celery and worker_celery


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
