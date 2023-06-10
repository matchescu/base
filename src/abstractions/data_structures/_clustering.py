from dataclasses import dataclass

from ._generic import FeatureInfo
from ._tabular import Table


@dataclass
class Clustering:
    feature_info: list[tuple[FeatureInfo]]
    clustered_rows: list[tuple[tuple]]

    @classmethod
    def from_tables(cls, *tables: Table) -> "Clustering":
        return Clustering(
            feature_info=[tuple(table.columns) for table in tables],
            clustered_rows=[
                tuple(tuple(table[i].values) for table in tables)
                for i in range(min(map(len, tables)))
            ]
        )

    @classmethod
    def from_nested_lists(cls, input_data: list[list[list]]) -> "Clustering":
        return Clustering(
            feature_info=[],
            clustered_rows=[
                tuple(
                    tuple(cluster) for cluster in row
                )
                for row in input_data
            ]
        )

    def __len__(self):
        return len(self.clustered_rows)