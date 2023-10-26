from networkx import Graph, connected_components


def compute_partition(a: list, equivalence: set[tuple]) -> frozenset[frozenset[tuple]]:
    """Partition an input set according to an equivalence relation.

    The algorithm is available `here<https://doi.org/10.1007/978-3-319-21840-3_36>`_.

    :param partition: buffer variable that contains the output
    :param a: input set of items to partition
    :param equivalence: pairs that define which items are equivalent to other items
    """
    g = Graph(equivalence)
    clusters = []
    all_matching = set()

    for cluster in connected_components(g):
        clusters.append(frozenset(cluster))
        for item in cluster:
            all_matching.add(item)

    for item in a:
        if item in all_matching:
            continue
        clusters.append(frozenset([item]))

    return frozenset(clusters)
