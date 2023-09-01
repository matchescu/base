def compute_partition(a: list, equivalence: set[tuple]):
    """Partition an input set according to an equivalence relation.

    :param partition: buffer variable that contains the output
    :param a: input set of items to partition
    :param equivalence: pairs that define which items are equivalent to other items
    """
    r = 0
    n = len(a)
    eq = {}
    neq = {}
    for i in range(n):
        eq[a[i]] = {i}
        neq[a[i]] = set()
    max_class_len = max(map(len, (eq[a[i]] for i in range(n))))
    while r == 0 or max_class_len < (n-1)//r:
        r = r + 1
        for i in range(n):
            union_i = eq[a[i]] | neq[a[i]]
            j = (i + 1) % n
            while j != i:
                if j not in union_i:
                    if (a[i], a[j]) in equivalence or (a[j], a[i]) in equivalence:
                        union_eq = eq[a[i]] | eq[a[j]]
                        union_neq = neq[a[i]] | neq[a[j]]
                        for x in union_eq:
                            eq[a[x]] = union_eq
                            neq[a[x]] = union_neq
                    else:
                        for x in eq[a[i]]:
                            neq[a[x]] |= eq[a[j]]
                        for y in eq[a[j]]:
                            neq[a[y]] |= eq[a[i]]
                j = (j + 1) % n  # wrap around n
        max_class_len = max(map(len, (eq[a[i]] for i in range(n))))

    # convert to frozen sets
    return {frozenset(map(lambda idx: a[idx], eq[key])) for key in eq}

