from typing import TypeVar, Iterable, Generator

from abstractions.protocols import IndexedIterable


_T = TypeVar("_T")


# TODO: https://arxiv.org/pdf/1902.00133.pdf, https://sci-hub.ru/downloads/2020-10-10/de/qiao2020.pdf
def extract_partitions(grouped_data: Iterable[IndexedIterable[_T]]) -> Generator[IndexedIterable[_T], None, None]:
    union = set()
    for group in grouped_data:
        result = []
        for value in group:
            if value in union:
                continue
            result.append(value)
            union.add(value)
        if len(result) < 1:
            continue
        yield result
