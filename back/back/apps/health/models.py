import datetime
from itertools import groupby
from typing import TYPE_CHECKING, Optional

from django.db import models
from django.db.transaction import atomic
from django.utils.timezone import now
from .base import Status
from .itertools2 import n_uple

if TYPE_CHECKING:
    from .resolver import Cause


class EventQuerySet(models.QuerySet):
    """
    Facilitate some operations on events
    """

    def type(self, event_type):
        """
        Filters by a given type

        Parameters
        ----------
        event_type
            Type of event to filter by
        """

        return self.filter(event_type=event_type)

    def within(
        self,
        days=0,
        seconds=0,
        microseconds=0,
        milliseconds=0,
        minutes=0,
        hours=0,
        weeks=0,
    ):
        """
        Returns all events that are within a time window from now. The
        parameters are the ones from timedelta.
        """

        delta = datetime.timedelta(
            days=days,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks,
        )
        deadline = now() - delta

        return self.filter(date_created__gte=deadline)

    def stats(self):
        """
        Computes the number of success/failure/total for all events.
        """

        return self.aggregate(
            total=models.Count("id"),
            success=models.Sum(
                models.Case(
                    models.When(is_success=True, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
            failure=models.Sum(
                models.Case(
                    models.When(is_success=False, then=1),
                    default=0,
                    output_field=models.IntegerField(),
                )
            ),
        )

    def latest(self, event_type):
        """
        Returns the latest event of a given type
        """

        return self.type(event_type).order_by("-date_created").first()


class Event(models.Model):
    """
    This is a model for different parts of the code to be able to store events
    that happen in the system. This is useful for debugging and monitoring.
    For example: last time we connected to a DB, last time we got some
    information, etc.

    Attributes
    ----------
    date_created
        When the event was created
    event_type
        Type of the event. For example: "db_connection", etc. Up
        to the developer to decide what to put here.
    is_success
        Whether the event was successful or not
    data
        Any additional data that might be useful for debugging. In case the
        is_success flag is not enough for what you want to test.
    """

    date_created = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=255)
    is_success = models.BooleanField()
    data = models.JSONField()

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ["-date_created"]
        index_together = (("event_type", "date_created"),)


class StatusHistory(models.Model):
    """
    Gives you the history of health check status changes, so that you can know
    retrospectively what were the errors.
    """

    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=255, choices=Status.choices())
    root_cause_code = models.CharField(max_length=255, blank=True, default="")
    root_cause_message = models.TextField(blank=True, default="")
    root_cause_details = models.TextField(blank=True, default="")

    @property
    def signature(self):
        """
        This tuple allows to identify the current status. We'll create a new
        status if this tuple changes, basically. It can be created either
        from here either from cause_signature() (to compare to current status).
        """

        return (
            self.status,
            self.root_cause_code,
            self.root_cause_message,
            self.root_cause_details,
        )

    @classmethod
    def cause_signature(cls, cause: Optional["Cause"]):
        """
        Returns the signature of a cause, if any
        """

        if cause is None:
            return (Status.OK.name, "", "", "")

        return (
            cause.outcome.status.name,
            cause.code,
            cause.message,
            cause.details,
        )

    @classmethod
    @atomic
    def log_status_change(cls, cause: Optional["Cause"]):
        """
        If the current status is different from the last one in database, then
        we create a new log entry.

        Parameters
        ----------
        cause
            Output from the Resolver.check() method
        """

        current_status = cls.cause_signature(cause)
        last_status = cls.objects.select_for_update().order_by("-date_created").first()

        if last_status is None or last_status.signature != current_status:
            cls.objects.create(
                status=current_status[0],
                root_cause_code=current_status[1],
                root_cause_message=current_status[2],
                root_cause_details=current_status[3],
            )

    @classmethod
    def compute_uptime(
        cls,
        days=0,
        seconds=0,
        microseconds=0,
        milliseconds=0,
        minutes=0,
        hours=0,
        weeks=0,
    ) -> float:
        """
        Computes the uptime for the given time window. The parameters are the
        ones from timedelta.

        We iterate all status changes from now to the past, up to when we go
        further than the given time window.

        If the oldest status update is before the end of the window, we
        replace the end of the window by the date of the oldest status update.

        We're collecting all the ranges of downtimes and then compute how long
        that lasted in comparison to the length of the time window.
        """

        delta = datetime.timedelta(
            days=days,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks,
        )
        fixed_now = now()
        deadline = fixed_now - delta
        downtimes = []

        def yield_statues():
            for date_created, s in (
                cls.objects.filter(date_created__gte=deadline)
                .order_by("-date_created")
                .values_list("date_created", "status")
                .iterator(1000)
            ):
                yield (date_created, s)

                if date_created < deadline:
                    break

        statuses_raw = list(yield_statues())

        if not statuses_raw:
            return 1

        # We add a first status at current date, that has the same status as
        # the earliest status
        statuses_raw.insert(0, (fixed_now, statuses_raw[0][1]))

        # If the oldest status is beyond the deadline, we replace it by a
        # status at the deadline
        if statuses_raw[-1][0] < deadline:
            statuses_raw[-1] = (deadline, statuses_raw[-1][1])

        statuses = []

        for status, items in groupby(statuses_raw, key=lambda x: x[1]):
            items = list(items)
            statuses.append((items[-1][0], status))

        for after, before in n_uple(statuses, 2):
            if before[1] == Status.ERROR.value and after[1] == Status.OK.value:
                downtimes.append((before[0], after[0]))

        real_delta = fixed_now - statuses[-1][0]

        total_downtime = sum(
            (after - before).total_seconds() for before, after in downtimes
        )

        return 1 - total_downtime / real_delta.total_seconds()
