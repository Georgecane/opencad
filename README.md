# OpenCAD

Cross-platform, general-purpose CAD application. First development target: Linux.

## Stack
- Python 3.15.2
- OCCT 8.0.1 through nanocct 8.0.1.5
- PySide6 6.12.0
- NumPy 2.x

## Setup
```bash
python3.15 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m opencad
```

## Tests
```bash
QT_QPA_PLATFORM=offscreen python -m pytest -q
python -m compileall -q opencad tests
```

## Current scope
Initial foundation: OCCT-backed Box/Cylinder/Sphere creation, B-Rep validation and tessellation, Qt viewport, model tree, properties, undo/redo. This is an early prototype, not a mature CAD product.

## Renderer limitation
The current nanocct build binds many Visualization classes but does not include TKOpenGl. The initial viewport therefore renders tessellated OCCT geometry using Qt's QPainter. Exact B-Rep remains the source of truth. The renderer is replaceable.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
