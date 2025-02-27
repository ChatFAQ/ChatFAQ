from typing import Iterable, Tuple, TypeVar

T = TypeVar("T")


def n_uple(seq: Iterable[T], n: int = 2) -> Tuple[T, ...]:
    """
    Iterates over the provided iterator and returns n-uples of size n.
    """

    out = []

    for item in seq:
        out.append(item)

        if len(out) == n:
            yield tuple(out)
            out.pop(0)
