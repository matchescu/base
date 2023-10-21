from dataclasses import dataclass, field


@dataclass
class EntityResolutionResult:
    """Ground truth is expressed in terms of one or more mathematical models."""

    """Entity resolution result expressed in terms of the Algebraic model.

    The algebraic model for entity resolution views entity resolution as an equivalence algebraic
    relation between elements of the same data source with the properties of reflexivity, symmetry
    and distributivity. Such a relation partitions the original data source in a unique way.
    Therefore, in this model, the entity resolution over a data source is the partitioning of
    equivalent elements over the same data source. This model was proposed by John R. Talburt in
    the book
    `Entity Resolution and Information Quality<https://books.google.ro/books?id=tIB0IZYR8V8C&dq=john+r.+talburt>`_.
    """
    algebraic: list[list[tuple]] = field(default_factory=list, init=False)
    """Entity resolution result in terms of the Fellegi-Sunter probabilistic model.

    The Fellegi-Sunter model is the oldest mathematical model for entity resolution. Its origins
    can be traced back to the paper written by Ivan Fellegi and Alan Sunter:
    `A Theory for Record Linkage<https://www.tandfonline.com/doi/abs/10.1080/01621459.1969.10501049>`_.
    """
    fsm: list[tuple[tuple]] = field(default_factory=list, init=False)
    """Entity resolution result expressed in terms of the SERF functional model.

    The SERF (Standard Entity Resolution Framework) mathematical model proposes a way of looking
    at entity resolution as if it were the result of applying two types of functions (match
    functions and merge functions) over two data sources with unique records (a data set). The model
    builds new information records from pairs of existing information records by using a "domination"
    relationship. The "dominating" information records take the place of the "dominated" information
    records until there aren't any more records in the two data sets that can create new "dominating"
    records. The information records obtained by this process make up a data set that is said to be
    the entity resolution over the two initial data sources. The SERF ground truth depends on which
    ``merge`` function is used.

    It was proposed by Omar Benjelloun et al. in the paper
    `Swoosh: a generic approach to entity resolution<https://link.springer.com/article/10.1007/s00778-008-0098-x>`_.
    """
    serf: list[tuple] = field(default_factory=list, init=False)
