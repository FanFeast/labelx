from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Iterable, List, Tuple, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def map_parallel(func: Callable[[T], R], items: Iterable[T], workers: int = 0) -> List[Tuple[int, R]]:
    seq = list(items)
    if workers in (0, 1):  # run in-process
        return [(i, func(x)) for i, x in enumerate(seq)]
    out: List[Tuple[int, R]] = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(func, x): i for i, x in enumerate(seq)}
        for fut in as_completed(futs):
            out.append((futs[fut], fut.result()))
    out.sort(key=lambda t: t[0])  # deterministic order
    return out

