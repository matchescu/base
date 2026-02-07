from abc import ABCMeta, abstractmethod

import json
import networkx as nx
from matchescu.typing import EntityReference, EntityReferenceIdentifier


class GraphPersistence(metaclass=ABCMeta):
    @abstractmethod
    def load(self) -> nx.Graph:
        pass

    @abstractmethod
    def save(self, g: nx.Graph) -> None:
        pass


class GmlGraphPersistence(GraphPersistence):
    def __init__(self, file_path):
        super().__init__()
        self._path = file_path

    @staticmethod
    def _json_decode(dct: dict):
        obj_type = dct.pop("type", "ref_id")
        if obj_type == "ref":
            ref_id = dct.pop("ref_id")
            ref = EntityReference(ref_id, dct)
            return ref
        if obj_type == "ref_id":
            return EntityReferenceIdentifier(dct.get("label"), dct.get("source"))
        return dct

    def load(self) -> nx.Graph:
        return nx.read_gml(
            self._path,
            destringizer=lambda x: json.loads(x, object_hook=self._json_decode),
        )

    @staticmethod
    def _json_encode(o):
        if isinstance(o, EntityReferenceIdentifier):
            return {"type": "ref_id", "label": o.label, "source": o.source}
        if isinstance(o, EntityReference):
            return {
                "type": "ref",
                "ref_id": {"label": o.id.label, "source": o.id.source},
                **o.as_dict(),
            }
        return o

    def save(self, g: nx.Graph) -> None:
        return nx.write_gml(
            g, self._path, stringizer=lambda x: json.dumps(x, default=self._json_encode)
        )
