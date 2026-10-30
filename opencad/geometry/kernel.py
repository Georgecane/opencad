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

import math

class GeometryError(RuntimeError):
    pass

class OcctKernel:
    """Only this module imports nanocct geometry classes."""
    @staticmethod
    def _positive(value: float, label: str) -> float:
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{label} must be finite and greater than zero")
        return value

    @staticmethod
    def _validate(shape):
        from nanocct.BRepCheck import BRepCheck_Analyzer
        if shape is None or shape.IsNull() or not BRepCheck_Analyzer(shape).IsValid():
            raise GeometryError("OCCT produced a null or invalid B-Rep")
        return shape

    def box(self, width: float, depth: float, height: float):
        from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
        return self._validate(BRepPrimAPI_MakeBox(
            self._positive(width, "width"),
            self._positive(depth, "depth"),
            self._positive(height, "height")).Shape())

    def cylinder(self, radius: float, height: float):
        from nanocct.BRepPrimAPI import BRepPrimAPI_MakeCylinder
        return self._validate(BRepPrimAPI_MakeCylinder(
            self._positive(radius, "radius"),
            self._positive(height, "height")).Shape())

    def sphere(self, radius: float):
        from nanocct.BRepPrimAPI import BRepPrimAPI_MakeSphere
        return self._validate(BRepPrimAPI_MakeSphere(
            self._positive(radius, "radius")).Shape())
