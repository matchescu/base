from dataclasses import dataclass

from ._generic import FeatureInfo
from ._tabular import Table
from ._partitions import extract_partitions
from ..protocols import IndexedIterable


@dataclass
class Clustering:
    feature_info: list[IndexedIterable[FeatureInfo]]
    clustered_rows: IndexedIterable[IndexedIterable[IndexedIterable]]

    @classmethod
    def from_tables(cls, *tables: Table) -> "Clustering":
        info: list[IndexedIterable[FeatureInfo]] = list(
            extract_partitions(table.columns for table in tables)
        )
        return Clustering(
            feature_info=info,
            clustered_rows=[
                list(extract_partitions(
                    table[i].values for table in tables
                ))
                for i in range(min(map(len, tables)))
            ]
        )

    @classmethod
    def from_nested_lists(cls, input_data: list[list[list]]) -> "Clustering":
        return Clustering(
            feature_info=[],
            clustered_rows=[list(extract_partitions(record)) for record in input_data]
        )

    def __len__(self):
        return len(self.clustered_rows)
