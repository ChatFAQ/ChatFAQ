import tracemalloc
import linecache
from rest_framework.views import APIView
from django.http import HttpResponse
from back.utils.initial_snapshot import get_initial_snapshot


def display_top(snapshot, key_type='lineno', limit=10):
    res = ""
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    res += f"<div>[ Top {limit} lines ]</div>\n"
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        res += f"<div>#{index}: {frame.filename}:{frame.lineno}: {stat.size / 1024} KiB</div>\n"
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            res += f"<div>    {line}</div>\n"

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        res += f"<div>{len(other)} other: {size / 1024} KiB</div>\n"
    total = sum(stat.size for stat in top_stats)
    res += f"<div>Total allocated size: {total / 1024} KiB</div>\n"

    return res


class MemoryAPIViewSet(APIView):
    def get(self, request):

        current = tracemalloc.take_snapshot()

        # Compute differences
        top_stats = current.compare_to(get_initial_snapshot(), 'lineno')
        diff_output = "<div>[ Memory Usage Difference ]</div>\n"
        for stat in top_stats[:10]:
            diff_output += f"<div>{stat}</div>\n"

        # Get the traceback of a memory block
        top_stats = current.statistics('traceback')
        # pick the biggest memory block
        stat = top_stats[0]
        diff_output += f"<div>[ Biggest Memory Block ]</div>\n"
        diff_output += f"<div>{stat.count} memory blocks: {stat.size / 1024} KiB</div>\n"
        for line in stat.traceback.format():
            diff_output += f"<div>{line}</div>\n"
        # Pretty top
        diff_output += display_top(current, 'lineno', 10)
        return HttpResponse(diff_output)
