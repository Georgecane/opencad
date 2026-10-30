#      /$$$$$$                                 /$$$$$$   /$$$$$$  /$$$$$$$
#     /$$__  $$                               /$$__  $$ /$$__  $$| $$__  $$
#    | $$  \ $$  /$$$$$$   /$$$$$$  /$$$$$$$ | $$  \__/| $$  \ $$| $$  \ $$
#    | $$  | $$ /$$__  $$ /$$__  $$| $$__  $$| $$      | $$$$$$$$| $$  | $$
#    | $$  | $$| $$  \ $$| $$$$$$$$| $$  \ $$| $$      | $$__  $$| $$  | $$
#    | $$  | $$| $$  | $$| $$_____/| $$  | $$| $$    $$| $$  | $$| $$  | $$
#    |  $$$$$$/| $$$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$/| $$  | $$| $$$$$$$/
#     \______/ | $$____/  \_______/|__/  |__/ \______/ |__/  |__/|_______/
#              | $$
#              | $$
#              |__/

from dataclasses import dataclass, field
from uuid import uuid4
from typing import Any

@dataclass(slots=True)
class DocumentObject:
    name: str
    kind: str
    shape: Any
    mesh: Any
    parameters: dict[str, float] = field(default_factory=dict)
    object_id: str = field(default_factory=lambda: str(uuid4()))

class Document:
    def __init__(self, name: str = "Untitled") -> None:
        self.name = name
        self._objects: dict[str, DocumentObject] = {}
        self.revision = 0

    @property
    def objects(self) -> tuple[DocumentObject, ...]:
        return tuple(self._objects.values())

    def add(self, obj: DocumentObject) -> None:
        if obj.object_id in self._objects:
            raise ValueError("Duplicate document object ID")
        self._objects[obj.object_id] = obj
        self.revision += 1

    def remove(self, object_id: str) -> DocumentObject:
        obj = self._objects.pop(object_id)
        self.revision += 1
        return obj

    def get(self, object_id: str) -> DocumentObject:
        return self._objects[object_id]
