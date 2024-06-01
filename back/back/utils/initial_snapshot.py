import tracemalloc

tracemalloc.start()

_initial_snapshot = None


def compute_initial_snapshot():
    return tracemalloc.take_snapshot()


def get_initial_snapshot():
    global _initial_snapshot
    if _initial_snapshot is None:
        print("Computing initial snapshot...")
        _initial_snapshot = compute_initial_snapshot()

    return _initial_snapshot
