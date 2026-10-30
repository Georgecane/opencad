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
import numpy as np

@dataclass(frozen=True, slots=True)
class TriangleMesh:
    vertices: np.ndarray
    triangles: np.ndarray
    def __post_init__(self):
        v = np.ascontiguousarray(self.vertices, dtype=np.float64).copy()
        t = np.ascontiguousarray(self.triangles, dtype=np.int64).copy()
        if v.ndim != 2 or v.shape[1] != 3 or t.ndim != 2 or t.shape[1] != 3:
            raise ValueError("Expected vertices (N,3) and triangles (M,3)")
        if t.size and (t.min() < 0 or t.max() >= len(v)):
            raise ValueError("Triangle index out of bounds")
        v.setflags(write=False); t.setflags(write=False)
        object.__setattr__(self, "vertices", v)
        object.__setattr__(self, "triangles", t)

def tessellate(shape, linear_deflection: float = 0.25, angular_deflection: float = 0.35) -> TriangleMesh:
    from nanocct import BRep, BRepMesh, TopAbs, TopExp, TopLoc, TopoDS
    if linear_deflection <= 0 or angular_deflection <= 0:
        raise ValueError("Deflections must be positive")
    mesher = BRepMesh.BRepMesh_IncrementalMesh(shape, linear_deflection, False, angular_deflection, True)
    vertices, triangles, offset = [], [], 0
    explorer = TopExp.TopExp_Explorer(shape, TopAbs.TopAbs_ShapeEnum.TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face(explorer.Current())
        location = TopLoc.TopLoc_Location()
        tri = BRep.BRep_Tool.Triangulation_s(face, location)
        explorer.Next()
        if tri is None or tri.NbNodes() == 0: continue
        nodes = np.asarray(tri.InternalNodes(), dtype=np.float64).copy()
        indices = np.asarray(tri.InternalTriangles(), dtype=np.int64).copy() - 1
        trsf = location.Transformation()
        matrix = np.eye(4)
        for r in range(1, 4):
            for c in range(1, 5): matrix[r-1, c-1] = trsf.Value(r, c)
        nodes = nodes @ matrix[:3, :3].T + matrix[:3, 3]
        indices = indices[np.all((indices >= 0) & (indices < len(nodes)), axis=1)]
        if not len(indices): continue
        vertices.append(nodes); triangles.append(indices + offset); offset += len(nodes)
    if not vertices: raise RuntimeError("OCCT tessellation returned no triangles")
    return TriangleMesh(np.concatenate(vertices), np.concatenate(triangles))
