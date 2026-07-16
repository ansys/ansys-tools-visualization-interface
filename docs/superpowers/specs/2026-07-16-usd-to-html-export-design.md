# Design: USD-to-HTML Export Feature

**Date:** 2026-07-16
**Repo:** `ansys-tools-visualization-interface`

---

## Overview

Add a `export_usd_to_html()` utility function to `ansys-tools-visualization-interface` that converts
a USD file (or in-memory `pxr.Usd.Stage`) to a self-contained Three.js HTML viewer page.

The feature follows the pattern established by PyPrimeMesh's `export_usd_viewer_html`, but lives
in this shared visualization library so it can be consumed by any PyAnsys project that exports USD
(currently PyPrimeMesh and PyAnsys-Geometry).

---

## Context & Motivation

- **`python-usd-viewer`** already provides `export_viewer_html()` (USD → GLB → Three.js HTML).
- **PyPrimeMesh** wraps that function and adds mesh-edge overlay injection into the HTML JS.
- **PyAnsys-Geometry** exports USD but has no HTML step at all.
- This repo is the right shared home for the HTML export utility, keeping it out of
  `python-usd-viewer` (which has C++ compiled USD dependencies we don't want to proliferate).

---

## Architecture

### New file

```
src/ansys/tools/visualization_interface/backends/usd/html_export.py
```

### Module-level exposure

```python
# src/ansys/tools/visualization_interface/__init__.py
from ansys.tools.visualization_interface.backends.usd.html_export import (
    export_usd_to_html,
)
```

### Internal structure

```
export_usd_to_html(source, output_path, show_mesh_lines, line_color, line_opacity)
  ├── _stage_to_temp_usd(stage)  → writes Stage to a temp .usda, returns path
  └── _inject_mesh_lines(html_path, stage, line_color, line_opacity)
        └── traverse stage via pxr UsdGeomMesh prims
            → extract unique polygon edges (same dedup algorithm as PyPrimeMesh)
            → inject Three.js BufferGeometry + LineSegments into HTML
```

### Dependency strategy

| Package | Import style | Reason |
|---------|-------------|--------|
| `pxr` (from `usd-core`) | Lazy (inside function) | Pure-Python wheel; optional feature |
| `ansys.tools.usdviewer.web.html_export` | Lazy (inside function) | Requires compiled C++ USD; must not break imports of other backends |
| stdlib (`pathlib`, `tempfile`) | Top-level | Always available |

`usd-core` is added as a direct optional dependency in `pyproject.toml` under `[usd]`.

---

## Public API

```python
def export_usd_to_html(
    source: "str | Path | pxr.Usd.Stage",
    output_path: "str | Path | None" = None,
    *,
    show_mesh_lines: bool = True,
    line_color: str = "#ffffff",
    line_opacity: float = 0.9,
) -> Path:
    """Convert a USD asset to a self-contained Three.js HTML viewer.

    Parameters
    ----------
    source : str | Path | pxr.Usd.Stage
        USD file path (.usd / .usda / .usdc / .usdz) or an in-memory USD stage.
    output_path : str | Path | None, default: None
        Destination for the HTML file. When None, placed alongside the source
        as ``{stem}_viewer.html``.
    show_mesh_lines : bool, default: True
        When True, injects Three.js LineSegments derived from polygon edges of
        all UsdGeomMesh prims in the stage for a wireframe overlay.
    line_color : str, default: "#ffffff"
        CSS hex color for the mesh-edge overlay.
    line_opacity : float, default: 0.9
        Opacity of the mesh-edge overlay (0.0 – 1.0).

    Returns
    -------
    pathlib.Path
        Absolute path to the written HTML file.

    Raises
    ------
    ImportError
        If ``ansys-tools-usdviewer`` or ``usd-core`` is not installed.
    FileNotFoundError
        If a file path is given but does not exist.
    ValueError
        If ``line_opacity`` is outside [0.0, 1.0].
    """
```

---

## Behaviour

1. **Input normalisation**: if `source` is a `pxr.Usd.Stage`, export it to a
   `tempfile.NamedTemporaryFile` (`.usda`). Track path for cleanup.
2. **HTML generation**: call `ansys.tools.usdviewer.web.html_export.export_viewer_html(usd_path, output_path)`.
3. **Mesh-line injection** (when `show_mesh_lines=True`):
   - Open (or reuse) the stage via `pxr`.
   - Traverse all `UsdGeomMesh` prims.
   - For each, read `faceVertexCounts` and `faceVertexIndices` and `points`.
   - Build a flat `Float32Array` of line-segment pairs (one per unique polygon edge).
   - Inject a `<script>` block into the HTML before the closing `</body>` that adds a
     `THREE.LineSegments` to the scene after model load.
4. **Cleanup**: delete temp `.usda` if created.
5. **Return**: resolved `Path` to the HTML file.

---

## Error Handling

| Condition | Error |
|-----------|-------|
| `ansys-tools-usdviewer` not installed | `ImportError` with install hint |
| `usd-core` not installed | `ImportError` with install hint |
| File path doesn't exist | `FileNotFoundError` |
| `line_opacity` outside [0, 1] | `ValueError` |
| Unsupported file extension | `ValueError` (from usdviewer) |

---

## Dependency Changes

In `pyproject.toml`, under `[project.optional-dependencies]`:

```toml
usd = [
    "ansys-tools-usdviewer >= 0.1.0,< 1",
    "usd-core >= 24.0",          # <-- NEW: for pxr stage I/O and traversal
]
```

---

## File Changes Summary

| File | Change |
|------|--------|
| `src/.../backends/usd/html_export.py` | **Create** — new module |
| `src/.../backends/usd/__init__.py` | Update exports |
| `src/.../visualization_interface/__init__.py` | Add `export_usd_to_html` import |
| `pyproject.toml` | Add `usd-core` to `[usd]` extra |
| `tests/test_usd_html_export.py` | **Create** — unit + integration tests |
| `doc/source/user_guide/usdviewer.rst` | Update with HTML export example |

---

## Testing Plan

### Unit tests (`tests/test_usd_html_export.py`)

All heavy dependencies (`pxr`, `ansys.tools.usdviewer`) are mocked via `sys.modules`.

- `test_export_with_file_path` — file path input → HTML produced
- `test_export_with_stage` — Stage input → temp file written → HTML produced → temp cleaned up
- `test_show_mesh_lines_false` — no injection, no stage traversal
- `test_show_mesh_lines_true_injects_js` — mesh prims → JS marker present in HTML
- `test_import_error_no_usdviewer` — helpful ImportError when package missing
- `test_file_not_found` — FileNotFoundError for missing path
- `test_invalid_line_opacity` — ValueError for opacity out of range

### Integration tests (same file, marked `@pytest.mark.integration`)

Guarded with `pytest.importorskip("pxr")` and `pytest.importorskip("ansys.tools.usdviewer")`.

- `test_integration_real_usd_file` — write a minimal `.usda`, call function, assert HTML file
  exists and contains `THREE.LineSegments` marker
- `test_integration_stage_roundtrip` — build a stage in-memory with one mesh prim, export to HTML,
  verify output

---

## Alternatives Considered

- **Approach A** (thin wrapper, requires caller to pass topology): rejected — worse UX, forces
  PyAnsys-Geometry consumers to pass extra data.
- **Approach C** (full copy of PyPrimeMesh logic): rejected — duplication risk, tied to
  PyPrimeMesh geometry DTOs.
