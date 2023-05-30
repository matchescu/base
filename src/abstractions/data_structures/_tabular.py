from dataclasses import dataclass, field, InitVar
from os import PathLike
from typing import Iterable, Any, Union


@dataclass(repr=True, eq=True, order=True, unsafe_hash=True, frozen=True)
class ColumnInfo:
    name: str = field(init=True, repr=True, hash=True, compare=True)
    index: int = field(init=True, repr=True, hash=True, compare=True)


@dataclass(repr=True, eq=True, order=False, unsafe_hash=True)
class Row:
    _name_to_index_map: dict[str, int] = field(init=False, repr=False, compare=False, hash=False)
    _index_to_name_map: dict[int, str] = field(init=False, repr=False, compare=False, hash=False)

    columns: InitVar[list[ColumnInfo]]
    values: list = field(default_factory=list, init=True, repr=True, compare=False, hash=True)

    def __post_init__(self, columns):
        self._name_to_index_map = {col.name: col.index for col in columns}
        self._index_to_name_map = {col.index: col.name for col in columns}
        self.__index = 0

    def __getitem__(self, item: str | int) -> Any:
        if isinstance(item, str) and item in self._name_to_index_map:
            idx = self._name_to_index_map[item]
            if 0 <= idx < len(self.values):
                return self.values[idx]
        if isinstance(item, int):
            return self.values[item]
        raise ValueError(f"don't know how to get item {item}")

    def __setitem__(self, key: str | int, value: Any) -> None:
        if isinstance(key, str) and key in self._name_to_index_map:
            idx = self._name_to_index_map[key]
            if 0 <= idx < len(self.values):
                self.values[self._name_to_index_map[key]] = value
            else:
                raise ValueError(f"don't know how to set item {key}")
        elif isinstance(key, int):
            self.values[key] = value
        else:
            raise ValueError(f"don't know how to set item {key}")

    def column_name(self, index: int) -> str:
        return self._index_to_name_map[index]

    def sub_row(self, column_info: list[ColumnInfo]) -> "Row":
        return Row(
            column_info,
            [self[col.name] for col in column_info]
        )

    def __iter__(self):
        return iter(self.values)

    def __next__(self):
        if 0 <= self.__index < len(self.values):
            result = self.values[self.__index]
            self.__index += 1
            return result
        raise StopIteration()

    def __len__(self):
        return len(self.values)

    def __str__(self):
        return "[{}]".format(
            ", ".join(f"{self._index_to_name_map[i]}={val}" for i, val in enumerate(self.values))
        )


class Table:
    """Works for small datasets."""

    def __init__(self, *columns: str):
        self.__meta: list[ColumnInfo] = [
            ColumnInfo(name, index) for index, name in enumerate(columns)
        ]
        self.__rows: list[Row] = []

    @property
    def columns(self):
        return self.__meta

    @classmethod
    def load_csv(cls, file_path: Union[str, PathLike]) -> "Table":
        from csv import reader

        with open(file_path, "r") as csv_file:
            lines = csv_file.readlines()

        csv_reader = reader(lines)
        columns = next(csv_reader)
        result = Table(*columns)
        result.load_sequence(csv_reader)
        return result

    def load_sequence(self, input_sequence: Iterable[Iterable]):
        for item in input_sequence:
            self.__rows.append(Row(self.__meta, list(val for val in item)))

    def sub_table(self, *cols: str) -> "Table":
        result = Table(*cols)
        for row in self.__rows:
            result.__rows.append(
                row.sub_row(result.columns)
            )
        return result

    def __getitem__(self, item):
        return self.__rows[item]

    def __repr__(self):
        col_str = ", ".join(map(lambda c: f"{c.index}:{c.name}", self.columns))
        return f"Table[row_count={len(self.__rows)}]({col_str})"
