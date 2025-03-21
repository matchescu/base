from typing import TypeVar, Hashable, Generic


T = TypeVar("T", bound=Hashable)


class EquivalenceClassPartitioner(Generic[T]):
    def __init__(self, items: list[T]):
        self._rank = {item: 0 for item in items}
        self._parent = {item: item for item in items}
        self._items = items

    def _find(self, x: T) -> T:
        if self._parent[x] == x:
            return x
        # path compression
        self._parent[x] = self._find(self._parent[x])
        return self._parent[x]

    def _union(self, x: T, y: T) -> None:
        x_root = self._find(x)
        y_root = self._find(y)

        if x_root == y_root:
            return

        if self._rank[x_root] < self._rank[y_root]:
            self._parent[x_root] = y_root
        elif self._rank[y_root] < self._rank[x_root]:
            self._parent[y_root] = x_root
        else:
            # does not matter which goes where
            # make sure we increase the correct rank
            self._parent[y_root] = x_root
            self._rank[x_root] += 1

    def __call__(self, pairs: list[tuple[T, T]]) -> list[list[T]]:
        for x, y in pairs:
            self._union(x, y)
        classes = {item: dict() for item in self._items}
        for item in self._items:
            classes[self._find(item)][item] = None
        return [list(eq_class) for eq_class in classes.values() if len(eq_class) > 0]


def compute_partition(
    all_references: list, equivalence: list[tuple]
) -> list[list[tuple]]:
    """Partition an input set according to an equivalence relation.

    The algorithm uses the Union-Find or DFU data structure.

    :param all_references: all entity references that make up the input domain
    :param equivalence: pairs that define which items are equivalent to other items
    :return: a list of lists of tuples, where:

    * each tuple is an entity reference
    * tuples are grouped in clusters which are represented as lists
    * the final result is a list of clusters
    """
    partitioner = EquivalenceClassPartitioner(all_references)
    result = partitioner(equivalence)
    return result
