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

from opencad.core.document import Document, DocumentObject
from opencad.core.history import AddObject, History

def test_add_undo_redo():
    doc = Document()
    obj = DocumentObject("Box", "Box", None, None)
    history = History()
    history.execute(AddObject(doc, obj))
    assert len(doc.objects) == 1
    assert history.undo() == "Add Box"
    assert len(doc.objects) == 0
    assert history.redo() == "Add Box"
    assert len(doc.objects) == 1

def test_duplicate_rejected():
    doc = Document()
    obj = DocumentObject("Box", "Box", None, None)
    doc.add(obj)
    try: doc.add(obj)
    except ValueError: pass
    else: raise AssertionError("duplicate ID accepted")
