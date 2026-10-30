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

from nanocct.BRepCheck import BRepCheck_Analyzer
from opencad.geometry.kernel import OcctKernel
from opencad.geometry.mesh import tessellate

def test_occt_box_and_mesh():
    shape = OcctKernel().box(100, 80, 50)
    assert BRepCheck_Analyzer(shape).IsValid()
    mesh = tessellate(shape)
    assert mesh.vertices.shape[1] == 3
    assert mesh.triangles.shape[1] == 3
    assert len(mesh.triangles) >= 12

def test_invalid_dimensions():
    try: OcctKernel().box(0, 10, 10)
    except ValueError: pass
    else: raise AssertionError("zero width accepted")
