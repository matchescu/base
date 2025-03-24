from collections.abc import Iterable
from typing import Any, Iterator


class Record:
    def __init__(self, value: Iterable) -> None:
        if isinstance(value, Record):
            self._attr_values = value._attr_values
            self._attr_names = value._attr_names
        else:
            tuples = list(self.__init_data(value))
            self._attr_values = tuple(x[1] for x in tuples)
            self._attr_names = {x[0]: i for i, x in enumerate(tuples)}

    @staticmethod
    def merge(records: Iterable["Record"]) -> "Record":
        merge_record = {}
        for record in records:
            merge_record.update(
                {k: record._attr_values[i] for k, i in record._attr_names.items()}
            )
        return Record(merge_record)

    @staticmethod
    def __get_attr_key(key: str | int) -> str:
        return f"column_{key}" if isinstance(key, int) else key

    def __init_data(self, value: Iterable) -> Iterable[tuple]:
        if isinstance(value, dict):
            return ((self.__get_attr_key(k), v) for k, v in value.items())
        elif isinstance(value, (tuple, list, set)):
            return ((self.__get_attr_key(i), v) for i, v in enumerate(value, start=1))
        raise ValueError(
            f"can't initialize data record from '{type(value).__name__}' values"
        )

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, str):
            return (
                self._attr_values[self._attr_names[key]]
                if key in self._attr_names
                else None
            )
        elif isinstance(key, int):
            return self._attr_values[key]
        raise ValueError(f"can't get data record using '{type(key).__name__}' keys")

    def __getattr__(self, key: str) -> Any:
        if key not in self._attr_names:
            raise AttributeError(f"Record attribute '{key}' not found")
        return self[key]

    def __len__(self) -> int:
        return len(self._attr_values)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._attr_values)
