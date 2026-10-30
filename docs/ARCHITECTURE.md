# OpenCAD architecture

```mermaid
flowchart TB
 U[User] --> UI[PySide6 UI]
 UI --> APP[Application commands and services]
 APP --> DOC[Document and history]
 APP --> MODEL[Modeling features]
 MODEL --> API[OpenCAD Geometry API]
 API --> ADAPTER[OCCT adapter]
 ADAPTER --> NANO[nanocct]
 NANO --> OCCT[OCCT 8.0.1]
 OCCT --> MESH[Tessellation]
 MESH --> VIEW[Qt viewport]
 DOC --> TREE[Model tree and properties]
```

## Dependency rules
1. UI never imports nanocct.
2. Document stores exact OCCT B-Reps and disposable display meshes.
3. Modeling features call the application-owned Geometry API.
4. Only the geometry adapter imports nanocct.
5. Viewport rendering is independent of B-Rep ownership and can be replaced.
6. Document changes go through reversible commands.

## Renderer
The first nanocct build binds Visualization classes but does not include TKOpenGl. The bootstrap viewport therefore uses Qt painting over OCCT tessellations. It is not the final high-performance renderer.
