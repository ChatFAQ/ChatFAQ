from typing import Any, MutableMapping

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import StatusHistory
from .resolver import build_resolver


def global_status(request: HttpRequest) -> HttpResponse:
    """
    Return the global status of the system.

    Parameters
    ----------
    request
        Django request
    """

    resolver = build_resolver()
    run_all = "run_all" in request.GET
    root_cause = resolver.check(stop_on_error=not run_all)
    status_history = StatusHistory.objects.order_by("-date_created")[0:20]
    uptime_365 = round(100 * StatusHistory.compute_uptime(days=365), 4)
    uptime_30 = round(100 * StatusHistory.compute_uptime(days=30), 4)
    uptime_7 = round(100 * StatusHistory.compute_uptime(days=7), 4)
    uptime_1 = round(100 * StatusHistory.compute_uptime(hours=6), 4)

    return render(
        request,
        "health/status.html",
        context=dict(
            resolver=resolver,
            root_cause=root_cause,
            status_history=status_history,
            uptime_365=uptime_365,
            uptime_30=uptime_30,
            uptime_7=uptime_7,
            uptime_1=uptime_1,
        ),
        status=200 if not root_cause else 418,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def global_status_json(request: HttpRequest) -> HttpResponse:
    """
    Return the global status of the system, in JSON for robots to exploit.
    """

    out: MutableMapping[Any, Any] = {}

    resolver = build_resolver()
    run_all = "run_all" in request.GET
    root_cause = resolver.check(stop_on_error=not run_all)

    if root_cause:
        out["status"] = "error"
        out["outcome"] = {
            "status": root_cause.outcome.status.value,
            "code": root_cause.code,
            "message": root_cause.message,
            "name": root_cause.name,
        }
    else:
        out["status"] = "ok"
        out["outcome"] = {}

    out["checks"] = []

    for cause in resolver.get_all_tests():
        if outcome := cause.outcome:
            status = outcome.status.value
        else:
            status = "UNKNOWN"

        out["checks"].append(
            {
                "status": status,
                "code": cause.code,
                "name": cause.name,
                "message": cause.message,
            }
        )

    return Response(out, status=200 if out["status"] == "ok" else 418)
