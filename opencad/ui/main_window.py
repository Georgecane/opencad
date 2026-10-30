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

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QDockWidget, QInputDialog, QLabel, QMainWindow,
    QMessageBox, QTableWidget, QTableWidgetItem, QToolBar, QTreeWidget, QTreeWidgetItem)
from opencad.core.document import Document, DocumentObject
from opencad.core.history import AddObject, History
from opencad.geometry.kernel import OcctKernel
from opencad.geometry.mesh import tessellate
from opencad.ui.viewport import MeshViewport

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCAD")
        self.resize(1440, 900)
        self.document = Document()
        self.kernel = OcctKernel()
        self.history = History()
        self.viewport = MeshViewport(self)
        self.setCentralWidget(self.viewport)
        self._build_panels()
        self._build_actions()
        self._theme()
        self.statusBar().showMessage("Ready | OCCT 8 via nanocct")

    def _build_panels(self):
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Model", "Type"])
        self.tree.itemSelectionChanged.connect(self._selection_changed)
        dock = QDockWidget("Model", self)
        dock.setObjectName("ModelDock")
        dock.setWidget(self.tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        self.props = QTableWidget(0, 2)
        self.props.setHorizontalHeaderLabels(["Property", "Value"])
        self.props.horizontalHeader().setStretchLastSection(True)
        pdock = QDockWidget("Properties", self)
        pdock.setObjectName("PropertiesDock")
        pdock.setWidget(self.props)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, pdock)

    def _build_actions(self):
        file_menu = self.menuBar().addMenu("&File")
        quit_action = QAction("Exit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        edit = self.menuBar().addMenu("&Edit")
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self._undo)
        edit.addAction(self.undo_action)
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self._redo)
        edit.addAction(self.redo_action)
        create = self.menuBar().addMenu("&Create")
        toolbar = QToolBar("Modeling", self)
        toolbar.setObjectName("ModelingToolbar")
        self.addToolBar(toolbar)
        for label, callback in [("Box", self._box), ("Cylinder", self._cylinder), ("Sphere", self._sphere)]:
            action = QAction(label, self)
            action.triggered.connect(callback)
            create.addAction(action)
            toolbar.addAction(action)
        fit = QAction("Fit All", self)
        fit.setShortcut("F")
        fit.triggered.connect(self.viewport.fit_view)
        self.menuBar().addMenu("&View").addAction(fit)
        toolbar.addAction(fit)
        self._history_state()

    def _number(self, title, label, default):
        value, ok = QInputDialog.getDouble(self, title, label, default, .001, 1e9, 3)
        return value if ok else None

    def _box(self):
        vals = [self._number("Box", f"{name} (mm)", default)
                for name, default in [("Width",100),("Depth",80),("Height",50)]]
        if all(v is not None for v in vals):
            self._create("Box", dict(zip(("width","depth","height"), vals)))

    def _cylinder(self):
        vals = [self._number("Cylinder", name, default)
                for name, default in [("Radius (mm)",25),("Height (mm)",70)]]
        if all(v is not None for v in vals):
            self._create("Cylinder", dict(zip(("radius","height"), vals)))

    def _sphere(self):
        radius = self._number("Sphere", "Radius (mm)", 35)
        if radius is not None: self._create("Sphere", {"radius":radius})

    def _create(self, kind, params):
        try:
            if kind == "Box": shape = self.kernel.box(**params)
            elif kind == "Cylinder": shape = self.kernel.cylinder(**params)
            else: shape = self.kernel.sphere(**params)
            mesh = tessellate(shape)
            obj = DocumentObject(f"{kind} {len(self.document.objects)+1:03d}", kind, shape, mesh, params)
            self.history.execute(AddObject(self.document, obj))
            self._refresh(obj.object_id)
            self.statusBar().showMessage(f"Created {obj.name}", 4000)
        except Exception as exc:
            QMessageBox.critical(self, "Geometry operation failed", str(exc))

    def _refresh(self, selected=None):
        self.tree.clear()
        for obj in self.document.objects:
            item = QTreeWidgetItem([obj.name, obj.kind])
            item.setData(0, Qt.ItemDataRole.UserRole, obj.object_id)
            self.tree.addTopLevelItem(item)
            if obj.object_id == selected: self.tree.setCurrentItem(item)
        self.viewport.set_items(self.document.objects)
        self._properties()
        self._history_state()

    def _selection_changed(self):
        self.viewport.setFocus()
        self._properties()

    def _properties(self):
        selected = self.tree.selectedItems()
        obj = None
        if selected:
            try: obj = self.document.get(selected[0].data(0, Qt.ItemDataRole.UserRole))
            except KeyError: pass
        rows = []
        if obj:
            rows = [("Name",obj.name),("Type",obj.kind)]
            rows += [(k, f"{v:g} mm") for k,v in obj.parameters.items()]
        self.props.setRowCount(len(rows))
        for row, (key,value) in enumerate(rows):
            self.props.setItem(row,0,QTableWidgetItem(key))
            self.props.setItem(row,1,QTableWidgetItem(value))

    def _undo(self):
        if self.history.undo(): self._refresh()
    def _redo(self):
        if self.history.redo(): self._refresh()
    def _history_state(self):
        self.undo_action.setEnabled(self.history.can_undo)
        self.redo_action.setEnabled(self.history.can_redo)

    def _theme(self):
        self.setStyleSheet("""
        QMainWindow,QMenuBar,QMenu,QToolBar,QDockWidget {background:#202630;color:#e7edf5}
        QTreeWidget,QTableWidget {background:#202630;color:#e7edf5;gridline-color:#35404e}
        QHeaderView::section,QDockWidget::title {background:#293441;color:#dce5ef;padding:6px}
        QToolButton {background:#2b3542;color:#e7edf5;padding:6px;border:1px solid #3b4858}
        QStatusBar {background:#202630;color:#aeb9c7}
        """)
