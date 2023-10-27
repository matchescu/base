from networkx import Graph, connected_components


def compute_partition(all_references: list, equivalence: list[tuple]) -> list[list[tuple]]:
    """Partition an input set according to an equivalence relation.

    We use Graphs to find the clusters. Clusters are just the connected
    components of a graph built from an input of pairs.

    :param all_references: all entity references that make up the input domain
    :param equivalence: pairs that define which items are equivalent to other items
    :return: a list of lists of tuples, where:

    * each tuple is an entity reference
    * tuples are grouped in clusters which are represented as lists
    * the final result is a list of clusters
    """
    g = Graph(equivalence)
    clusters = []
    all_matching = set()

    for cluster in connected_components(g):
        clusters.append(cluster)
        for item in cluster:
            all_matching.add(item)

    for item in all_references:
        if item in all_matching:
            continue
        clusters.append(frozenset([item]))

    return clusters
