from dataclasses import dataclass

from ._generic import FeatureInfo
from ._tabular import Table


@dataclass
class Clustering:
    feature_info: list[list[FeatureInfo]]
    clustered_rows: list[list[list]]

    @classmethod
    def from_tables(cls, *tables: Table) -> "Clustering":
        return Clustering(
            feature_info=[table.columns for table in tables],
            clustered_rows=[
                [
                    table[i].values
                    for table in tables
                ]
                for i in range(min(map(len, tables)))
            ]
        )

    @classmethod
    def from_nested_lists(cls, input_data: list[list[list]]) -> "Clustering":
        return Clustering(
            feature_info=[],
            clustered_rows=input_data.copy()
        )

    def __len__(self):
        return len(self.clustered_rows)
