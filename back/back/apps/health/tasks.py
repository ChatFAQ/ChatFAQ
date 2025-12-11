import logging

from procrastinate.contrib.django import app

from .models import Event
from .module_sim import run_module_simulation
from .resolver import build_resolver

logger = logging.getLogger(__name__)


# Schedule tasks for each module
# @app.periodic(cron="0 */6 * * *", queue="health_checks") # Module 1 is not needed for now
@app.task(queue="health_checks")
async def run_module_1_simulation_periodic(timestamp: int):
    logger.info("Scheduling Module 1 simulation task.")
    await run_module_simulation(
        module_number=1,
        module_name="Info2ArticleXia",
        file_name="module1.pdf",
        state_overwrite="M1",
    )

@app.periodic(cron="0 */6 * * *", queue="health_checks")
@app.task(queue="health_checks")
async def run_module_2_simulation_periodic(timestamp: int):
    logger.info("Scheduling Module 2 simulation task.")
    await run_module_simulation(
        module_number=2,
        module_name="TopicsIndexGenXia",
        file_name="module2.sgm",
        state_overwrite="M2",
    )

@app.periodic(cron="0 */6 * * *", queue="health_checks")
@app.task(queue="health_checks")
async def run_module_3_simulation_periodic(timestamp: int):
    logger.info("Scheduling Module 3 simulation task.")
    await run_module_simulation(
        module_number=3,
        module_name="ColAgreeSumXia",
        file_name="module3.xml",
        state_overwrite="M3",
    )

@app.periodic(cron="* * * * *")  # https://crontab.guru/#*_*_*_*_*
@app.task
def log_beat(timestamp: int):
    """
    Log that the beat is running.
    """

    Event.objects.create(
        event_type="beat",
        is_success=True,
        data={},
    )


@app.periodic(cron="0 * * * *")  # https://crontab.guru/#0_*_*_*_*
@app.task
def clear_log(timestamp: int):
    """
    Delete old items from the events log
    """

    Event.objects.exclude(pk__in=Event.objects.within(weeks=1).values("pk")).delete()


@app.task
def log_entry(**kwargs):
    """
    Because sometimes there is no DB access at the time of collecting the log,
    we allow to create them through this task

    Specifically, when we try to create an event while the DB connection to
    TMSA is failing, it seems like the data is never committed. Instead of
    dealing with shenanigans of the ORM, we just send the event through here.

    Parameters
    ----------
    kwargs
        Arguments for log creation
    """

    Event.objects.create(**kwargs)


@app.periodic(cron="* * * * *")  # https://crontab.guru/#0_*_*_*_*
@app.task
def check_status(timestamp: int):
    """
    Periodic check of status to keep track of status history
    """

    resolver = build_resolver()
    resolver.check(stop_on_error=False)
