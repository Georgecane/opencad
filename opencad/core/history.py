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

from dataclasses import dataclass
from opencad.core.document import Document, DocumentObject

@dataclass
class AddObject:
    document: Document
    obj: DocumentObject
    @property
    def text(self) -> str:
        return f"Add {self.obj.name}"
    def redo(self) -> None:
        self.document.add(self.obj)
    def undo(self) -> None:
        self.document.remove(self.obj.object_id)

class History:
    def __init__(self) -> None:
        self._undo: list[AddObject] = []
        self._redo: list[AddObject] = []
    @property
    def can_undo(self) -> bool:
        return bool(self._undo)
    @property
    def can_redo(self) -> bool:
        return bool(self._redo)
    def execute(self, command: AddObject) -> None:
        command.redo()
        self._undo.append(command)
        self._redo.clear()
    def undo(self) -> str | None:
        if not self._undo: return None
        cmd = self._undo.pop()
        cmd.undo()
        self._redo.append(cmd)
        return cmd.text
    def redo(self) -> str | None:
        if not self._redo: return None
        cmd = self._redo.pop()
        cmd.redo()
        self._undo.append(cmd)
        return cmd.text
