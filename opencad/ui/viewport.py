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
import numpy as np
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget
from opencad.geometry.mesh import TriangleMesh

class MeshViewport(QWidget):
    """Bootstrap 3D viewport; exact geometry stays in OCCT B-Rep form."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 350)
        self.setMouseTracking(True)
        self._items = ()
        self._yaw = math.radians(42)
        self._pitch = math.radians(28)
        self._zoom = 1.0
        self._last = None

    def set_items(self, items):
        self._items = tuple(items)
        self.update()

    def fit_view(self):
        self._zoom = 1.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#171c24"))
        painter.setPen(QPen(QColor(255, 255, 255, 13), 1))
        for x in range(0, self.width(), 40): painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 40): painter.drawLine(0, y, self.width(), y)
        items = [(obj, obj.mesh) for obj in self._items if isinstance(obj.mesh, TriangleMesh)]
        if not items:
            painter.setPen(QColor("#aab6c5"))
            painter.setFont(QFont("Sans Serif", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "OpenCAD\n\nCreate a Box, Cylinder or Sphere")
            painter.end()
            return
        points = np.concatenate([mesh.vertices for _, mesh in items])
        center = (points.min(axis=0) + points.max(axis=0)) / 2
        span = max(float(np.max(points.max(axis=0)-points.min(axis=0))), 1e-9)
        scale = min(self.width(), self.height()) * .68 / span * self._zoom
        cy, sy = math.cos(self._yaw), math.sin(self._yaw)
        cp, sp = math.cos(self._pitch), math.sin(self._pitch)
        queue = []
        for obj, mesh in items:
            p = mesh.vertices - center
            x = p[:,0]*cy - p[:,1]*sy
            y = p[:,0]*sy + p[:,1]*cy
            z = p[:,2]
            yy = y*cp - z*sp
            depth = y*sp + z*cp
            screen = np.column_stack((self.width()/2+x*scale, self.height()/2-yy*scale))
            camera = np.column_stack((x, yy, depth))
            base = QColor("#58a6d8")
            for tri in mesh.triangles:
                tri3, tri2 = camera[tri], screen[tri]
                normal = np.cross(tri3[1]-tri3[0], tri3[2]-tri3[0])
                length = np.linalg.norm(normal)
                light = .35 if length < 1e-12 else .28 + .72*max(0, float(np.dot(normal/length, [-.35,-.45,.82])))
                color = QColor(int(base.red()*light), int(base.green()*light), int(base.blue()*light))
                queue.append((float(np.mean(tri3[:,2])), tri2, color))
        queue.sort(key=lambda item:item[0])
        painter.setPen(QPen(QColor(8, 13, 20, 110), .7))
        for _, pts, color in queue:
            painter.setBrush(color)
            painter.drawPolygon(QPolygonF([QPointF(float(x),float(y)) for x,y in pts]))
        painter.setPen(QColor("#d2d9e3"))
        painter.setFont(QFont("Sans Serif", 9))
        painter.drawText(12, 22, "Drag: orbit   Wheel: zoom   F: fit")
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._last = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._last is not None and event.buttons() & Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            delta = pos-self._last
            self._last = pos
            self._yaw += delta.x()*.008
            self._pitch = max(-1.48, min(1.48, self._pitch+delta.y()*.008))
            self.update()

    def mouseReleaseEvent(self, event):
        self._last = None
        self.unsetCursor()

    def wheelEvent(self, event):
        self._zoom = max(.05, min(20, self._zoom*(1.12**(event.angleDelta().y()/120))))
        self.update()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F:
            self.fit_view()
            event.accept()
        else:
            super().keyPressEvent(event)
