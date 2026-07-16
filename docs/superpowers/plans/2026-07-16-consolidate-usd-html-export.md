# Consolidate USD → HTML Export Into `ansys-tools-visualization-interface` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the entire USD-to-HTML export code path (GLB conversion, templates, VTK asset conversion, and the public `export_usd_to_html()` function) out of `ansys-tools-usdviewer` and into `ansys-tools-visualization-interface`, so the feature no longer depends on `ansys-tools-usdviewer` (which requires a bespoke WASM/compiled `usd-core` build). After the migration `ansys-tools-usdviewer` no longer contains any HTML-export code.

**Architecture:** Vendor the entire `web/` subpackage plus `vtk_converter.py` from `python-usd-viewer` into `ansys-tools-visualization-interface` under `backends/usd/`. Rewrite the existing thin `html_export.py` in vis-interface to call the *local* pipeline directly (no `ansys.tools.usdviewer` import). Split the `[usd]` extra into two: `[usd]` (HTML export — needs only `usd-core` + `pygltflib` + transitive `vtk` via `pyvista`) and `[usd-live-viewer]` (Qt live viewer — still needs `ansys-tools-usdviewer`). Then delete the migrated code from `python-usd-viewer`.

**Tech Stack:** Python ≥ 3.10, `usd-core` (PyPI, provides `pxr`), `pygltflib`, `vtk` (transitive via `pyvista`), Three.js (CDN, embedded in generated HTML), pytest, ruff, pre-commit, hatchling (usd-viewer) / flit (vis-interface).

## Global Constraints

- Two repositories are involved. **Both live locally**:
  - `D:\repositories\ansys-tools-visualization-interface` (target — receives code)
  - `D:\repositories\python-usd-viewer` (source — code is removed here)
- Python ≥ 3.10, < 4 in both repos.
- All new `.py` files under `src/` and `tests/` must carry the ANSYS MIT license header. The `add-license-headers` pre-commit hook adds it automatically on first commit; if pre-commit modifies files, `git add` and re-`git commit`.
- Vendored files keep their original MIT license header verbatim (do not rewrite copyright lines).
- No lazy-import gymnastics for `pxr` inside the vendored web/glb modules — vis-interface's `[usd]` extra now guarantees `usd-core` is installed whenever the HTML export path is used. Keep the `pxr` imports at module top like the originals.
- `ansys.tools.usdviewer` **must not appear as an import** anywhere on the HTML-export code path in vis-interface after this plan is executed.
- Ruff is the linter/formatter in both repos. Run `ruff check --fix` and `ruff format` before committing if pre-commit fails.
- HTML injection anchors in `glb_template.html` (must remain intact after migration):
  - config anchor: `const binary = atob(glbBase64);`
  - scene anchor: `scene.add(gltf.scene);`
  - idempotency marker for mesh-line injection: `// ansysEdgesInjected`
- `hatchling` in `python-usd-viewer` currently ships the template via `include = [ "src/ansys/tools/usdviewer/web/*.html" ]`. The equivalent must be configured for vis-interface (flit) so `glb_template.html` ships with the wheel.
- Package name change: the public function stays `export_usd_to_html` (vis-interface's name). The vendored lower-level function `export_viewer_html` in `python-usd-viewer` becomes a private helper `_export_viewer_html` inside vis-interface's `html_export.py`.
- `ansys-tools-usdviewer` is not yet released / not yet consumed — no deprecation shim is required in `python-usd-viewer`. Delete the migrated code outright and record the removal in the changelog.

---

## File Map

### `ansys-tools-visualization-interface` (target)

| File | Action | Responsibility |
|------|--------|----------------|
| `src/ansys/tools/visualization_interface/backends/usd/vtk_converter.py` | Create (vendored) | VTK → USD asset converter used by both `html_export` and `usd_interface` |
| `src/ansys/tools/visualization_interface/backends/usd/web/__init__.py` | Create | Marks `web/` as a subpackage |
| `src/ansys/tools/visualization_interface/backends/usd/web/glb.py` | Create (vendored) | Top-level `convert_usd_to_glb()` entrypoint |
| `src/ansys/tools/visualization_interface/backends/usd/web/glb_builder.py` | Create (vendored) | glTF/GLB buffer builder |
| `src/ansys/tools/visualization_interface/backends/usd/web/glb_lights.py` | Create (vendored) | USD → glTF light conversion |
| `src/ansys/tools/visualization_interface/backends/usd/web/glb_materials.py` | Create (vendored) | USD → glTF PBR material conversion |
| `src/ansys/tools/visualization_interface/backends/usd/web/glb_mesh.py` | Create (vendored) | USD mesh → glTF mesh conversion |
| `src/ansys/tools/visualization_interface/backends/usd/web/templates.py` | Create (vendored) | `build_viewer_html_glb()` template renderer |
| `src/ansys/tools/visualization_interface/backends/usd/web/glb_template.html` | Create (vendored) | Three.js viewer HTML template |
| `src/ansys/tools/visualization_interface/backends/usd/html_export.py` | Modify | Rewrite to use local `web/` package and local `vtk_converter`; remove `ansys.tools.usdviewer` imports |
| `src/ansys/tools/visualization_interface/backends/usd/usd_interface.py` | Modify | Import `VTKConverter` from local `.vtk_converter`; keep `USDViewer` import as lazy for the live-viewer feature |
| `pyproject.toml` | Modify | Add `pygltflib`; split `usd` extra; add `usd-live-viewer` extra; ensure `glb_template.html` ships with wheel |
| `tests/test_usd_html_export.py` | Modify | Drop all `ansys.tools.usdviewer` mocking; assert local pipeline is invoked |
| `tests/test_usd_html_export_integration.py` | Modify | Drop `ansys.tools.usdviewer.web.html_export` mocks; run the full local pipeline |
| `CHANGELOG.md` | Modify | Add "Added" (self-contained HTML export) and "Changed" (extra split) entries |
| `doc/source/user_guide/usdviewer.rst` | Modify | Update installation instructions to `[usd]` (no usdviewer needed for HTML export) |

### `python-usd-viewer` (source — removal)

| File | Action | Responsibility |
|------|--------|----------------|
| `src/ansys/tools/usdviewer/web/` (entire directory) | Delete | HTML export moves to vis-interface |
| `src/ansys/tools/usdviewer/vtk_converter.py` | Delete | Now owned by vis-interface |
| `src/ansys/tools/usdviewer/viewer.py` | Modify | Remove import of `.vtk_converter`; inline the small piece it actually uses **or** vendor a minimal internal shim (see Task 12 for the exact scope check) |
| `src/ansys/tools/usdviewer/__init__.py` | Modify (if it re-exports removed symbols) | Drop any exports of removed modules |
| `pyproject.toml` | Modify | Drop `include = [ "src/ansys/tools/usdviewer/web/*.html" ]`; drop `pygltflib` runtime dep (unused after removal) |
| `tests/` | Modify | Remove any tests targeting `web/` or `vtk_converter`; keep viewer tests |
| `examples/` | Modify | Remove or port any HTML-export examples |
| `doc/` | Modify | Remove any HTML-export documentation pages |
| `CHANGELOG.md` / `doc/source/changelog.rst` | Modify | Add "Removed" entry: HTML export moved to `ansys-tools-visualization-interface` |

---

## Execution Order Overview

Tasks 1–10 apply to `ansys-tools-visualization-interface`. Tasks 11–15 apply to `python-usd-viewer`. **Do not start Task 11 until Task 10 is committed** — deleting the source files before the target repo is green will break both packages simultaneously.

---

### Task 1: Add `pygltflib` dependency and split `usd` extra in vis-interface `pyproject.toml`

**Files:**
- Modify: `D:\repositories\ansys-tools-visualization-interface\pyproject.toml`

**Interfaces:**
- Produces: `pygltflib` and `usd-core` guaranteed installed by `pip install ansys-tools-visualization-interface[usd]`; `ansys-tools-usdviewer` moved to a new `[usd-live-viewer]` extra.

- [ ] **Step 1: Read current extras block**

  Run:
  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\pyproject.toml -Pattern "^usd|^all|optional-dependencies" -Context 0,10
  ```
  Confirm the current `usd` extra is:
  ```toml
  usd = [
      "ansys-tools-usdviewer >= 0.1.0,< 1",
      "usd-core >= 24.0,< 26"
  ]
  ```

- [ ] **Step 2: Edit `[project.optional-dependencies]`**

  Replace the `usd` and `all` blocks with:
  ```toml
  usd = [
      "usd-core >= 24.0,< 26",
      "pygltflib >= 1.16,< 2"
  ]

  usd-live-viewer = [
      "ansys-tools-usdviewer >= 0.1.0,< 1",
      "usd-core >= 24.0,< 26"
  ]

  all = [
      "pyside6 >= 6.8.0,<7",
      "pyvistaqt >= 0.11.1,<1",
      "plotly >= 6.3.1,<7",
      "kaleido >= 1.1.0,<2",
      "dash >= 3.2.0,< 5",
      "imageio[ffmpeg] >= 2.37.2",
      "ansys-tools-usdviewer >= 0.1.0,< 1",
      "usd-core >= 24.0,< 26",
      "pygltflib >= 1.16,< 2"
  ]
  ```

- [ ] **Step 3: Ensure `glb_template.html` ships with the wheel**

  Find the flit build config in `pyproject.toml` (look for `[tool.flit.module]` / `[tool.flit.sdist]`). If there is no explicit include for HTML files under `backends/usd/web/`, add:
  ```toml
  [tool.flit.sdist]
  include = [
      "src/ansys/tools/visualization_interface/backends/usd/web/*.html",
  ]
  ```
  If a `[tool.flit.sdist]` section already exists, add the path to its `include` list rather than duplicating the section.

  Note: flit includes package data by default for files inside the package tree, so this step is defensive. Verify in Task 10 that the wheel actually ships the template.

- [ ] **Step 4: Verify TOML syntax**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"
  ```
  Expected: `OK`

- [ ] **Step 5: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add pyproject.toml
  git commit -m "build(usd): split [usd] extra and add pygltflib runtime dep"
  ```

---

### Task 2: Vendor `vtk_converter.py` into vis-interface

**Files:**
- Create: `D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\vtk_converter.py`
- Source: `D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\vtk_converter.py`

**Interfaces:**
- Produces: `class VTKConverter` with the same public API (`load_asset`, `convert_vtk_file_to_usd`, `convert_vtk_to_usd`) importable as `from ansys.tools.visualization_interface.backends.usd.vtk_converter import VTKConverter`.

- [ ] **Step 1: Copy file verbatim (preserve license header)**

  ```powershell
  Copy-Item `
    D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\vtk_converter.py `
    D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\vtk_converter.py
  ```

- [ ] **Step 2: Adjust any internal imports (should be none)**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\vtk_converter.py -Pattern "ansys\.tools\.usdviewer|from \.|from \.\."
  ```
  Expected: no matches (the original only imports `pathlib`, `typing`, `warnings`, `pxr`, and `vtk`). If any match appears, edit the file to remove those internal references — the module must be self-contained.

- [ ] **Step 3: Smoke-import**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  python -c "from ansys.tools.visualization_interface.backends.usd.vtk_converter import VTKConverter; print(VTKConverter)"
  ```
  Expected: `<class 'ansys.tools.visualization_interface.backends.usd.vtk_converter.VTKConverter'>` (a `UserWarning` about `pxr` may print if `usd-core` isn't installed in the dev env; that's fine — install with `pip install -e .[usd]` if you want it silent).

- [ ] **Step 4: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add src/ansys/tools/visualization_interface/backends/usd/vtk_converter.py
  git commit -m "feat(usd): vendor VTKConverter from ansys-tools-usdviewer"
  ```

---

### Task 3: Vendor the `web/` subpackage (GLB pipeline + templates) into vis-interface

**Files:**
- Create: `D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\web\__init__.py`
- Create (copy): `web/glb.py`, `glb_builder.py`, `glb_lights.py`, `glb_materials.py`, `glb_mesh.py`, `templates.py`, `glb_template.html` (all under `.../backends/usd/web/`)
- Source: `D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\web\` (excluding `html_export.py`, which is handled in Task 4)

**Interfaces:**
- Produces:
  - `from ansys.tools.visualization_interface.backends.usd.web.glb import convert_usd_to_glb` — signature `convert_usd_to_glb(path: pathlib.Path) -> bytes`
  - `from ansys.tools.visualization_interface.backends.usd.web.templates import build_viewer_html_glb` — signature `build_viewer_html_glb(glb_b64: str, model_name: str) -> str`
- Consumes: `pxr` (from `usd-core`), `pygltflib` (from Task 1 dependency).

- [ ] **Step 1: Create the `web/` package directory and `__init__.py`**

  ```powershell
  $target = "D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\web"
  New-Item -ItemType Directory -Path $target -Force | Out-Null
  ```

  Create `web/__init__.py` with content:
  ```python
  # Copyright (C) 2025 - 2026 ANSYS, Inc. and/or its affiliates.
  # SPDX-License-Identifier: MIT
  #
  # (Full MIT license header block — same as the other vendored files.)

  """USD-to-HTML web export pipeline (GLB + Three.js templates)."""
  ```
  Use the same MIT license header block as `glb.py`; copy-paste from any of the vendored files to guarantee consistency.

- [ ] **Step 2: Copy the six Python modules verbatim**

  ```powershell
  $src = "D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\web"
  $dst = "D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\web"
  foreach ($f in @("glb.py","glb_builder.py","glb_lights.py","glb_materials.py","glb_mesh.py","templates.py")) {
      Copy-Item "$src\$f" "$dst\$f"
  }
  ```

- [ ] **Step 3: Copy the HTML template**

  ```powershell
  Copy-Item `
    "D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\web\glb_template.html" `
    "D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\web\glb_template.html"
  ```

- [ ] **Step 4: Verify internal imports (relative imports between `web/` modules are already correct)**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\web\*.py -Pattern "ansys\.tools\.usdviewer"
  ```
  Expected: no matches. If any of the vendored modules imports from `ansys.tools.usdviewer` (they shouldn't — verify with the source-tree grep in the plan header), edit that file to remove the dependency; the whole point is a self-contained pipeline.

- [ ] **Step 5: Verify injection anchors in the template are intact**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\web\glb_template.html -Pattern "atob\(glbBase64\)|scene\.add\(gltf\.scene\)"
  ```
  Expected: two matches — one per anchor. If either is missing, the copy was incomplete; re-copy.

- [ ] **Step 6: Smoke-import the entry points**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  python -c "from ansys.tools.visualization_interface.backends.usd.web.glb import convert_usd_to_glb; from ansys.tools.visualization_interface.backends.usd.web.templates import build_viewer_html_glb; print('imports OK')"
  ```
  Expected: `imports OK`. If `pygltflib` is missing in the dev venv, `pip install pygltflib` first (it's now in `[usd]`, so `pip install -e .[usd]` also works).

- [ ] **Step 7: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add src/ansys/tools/visualization_interface/backends/usd/web
  git commit -m "feat(usd): vendor web/ GLB pipeline and viewer template"
  ```

---

### Task 4: Rewrite `backends/usd/html_export.py` to use local pipeline

**Files:**
- Modify: `D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\html_export.py`

**Interfaces:**
- Consumes:
  - `from ansys.tools.visualization_interface.backends.usd.vtk_converter import VTKConverter` (Task 2)
  - `from ansys.tools.visualization_interface.backends.usd.web.glb import convert_usd_to_glb` (Task 3)
  - `from ansys.tools.visualization_interface.backends.usd.web.templates import build_viewer_html_glb` (Task 3)
- Produces: `export_usd_to_html(source, output_path=None, *, show_mesh_lines=True, line_color="#ffffff", line_opacity=0.9) -> pathlib.Path` — same public signature as before; **no** `ansys.tools.usdviewer` import anywhere in the module.

- [ ] **Step 1: Write the failing regression test asserting no `usdviewer` import**

  Create `D:\repositories\ansys-tools-visualization-interface\tests\test_usd_html_export_decoupled.py`:
  ```python
  # Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
  # SPDX-License-Identifier: MIT
  #
  # (Full MIT license header — copy from tests/test_usd_html_export.py)

  """Regression test: html_export.py must not import ansys.tools.usdviewer."""
  from pathlib import Path


  def test_html_export_module_has_no_usdviewer_reference():
      module_path = (
          Path(__file__).resolve().parents[1]
          / "src"
          / "ansys"
          / "tools"
          / "visualization_interface"
          / "backends"
          / "usd"
          / "html_export.py"
      )
      text = module_path.read_text(encoding="utf-8")
      assert (
          "ansys.tools.usdviewer" not in text
      ), "html_export.py must not depend on ansys.tools.usdviewer after migration."
  ```

- [ ] **Step 2: Run the test and verify it fails**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  pytest tests/test_usd_html_export_decoupled.py -v
  ```
  Expected: **FAIL** with `AssertionError: html_export.py must not depend on ansys.tools.usdviewer after migration.` (because the current file still contains `from ansys.tools.usdviewer.web.html_export import ...`).

- [ ] **Step 3: Rewrite `html_export.py` end-to-end**

  Replace the entire contents of `src/ansys/tools/visualization_interface/backends/usd/html_export.py` with:
  ```python
  # Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
  # SPDX-License-Identifier: MIT
  #
  # Permission is hereby granted, free of charge, to any person obtaining a copy
  # of this software and associated documentation files (the "Software"), to deal
  # in the Software without restriction, including without limitation the rights
  # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  # copies of the Software, and to permit persons to whom the Software is
  # furnished to do so, subject to the following conditions:
  #
  # The above copyright notice and this permission notice shall be included in all
  # copies or substantial portions of the Software.
  #
  # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  # SOFTWARE.

  """Self-contained USD → Three.js HTML export.

  Converts a USD asset (file or in-memory ``pxr.Usd.Stage``) into a
  self-contained HTML viewer page. The generated page embeds the geometry as a
  base64 GLB and requires only a CDN connection for Three.js at runtime.
  """

  from __future__ import annotations

  import base64
  from pathlib import Path
  import re
  import tempfile

  _USD_CORE_IMPORT_ERROR = (
      "The 'usd-core' package is required for USD-to-HTML export. "
      "Install it with: pip install 'ansys-tools-visualization-interface[usd]'"
  )

  _SUPPORTED_USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}
  _VTK_ASSET_EXTENSIONS = {".vtk", ".vtp", ".vtu", ".vts", ".obj", ".ply", ".stl"}

  _CONFIG_ANCHOR = "const binary = atob(glbBase64);"
  _SCENE_ANCHOR = "scene.add(gltf.scene);"
  _INJECTION_MARKER = "// ansysEdgesInjected"


  def _is_usd_stage(obj: object) -> bool:
      """Return True if *obj* duck-types as a ``pxr.Usd.Stage``."""
      return (
          hasattr(obj, "Traverse")
          and hasattr(obj, "GetPrimAtPath")
          and hasattr(obj, "Export")
      )


  def _stage_to_temp_usd(stage: object) -> Path:
      """Export *stage* to a temporary ``.usda`` file and return its path."""
      tmp = tempfile.NamedTemporaryFile(suffix=".usda", delete=False)
      tmp.close()
      tmp_path = Path(tmp.name)
      stage.Export(str(tmp_path))  # type: ignore[union-attr]
      return tmp_path


  def _open_stage(usd_path: Path) -> object:
      """Open *usd_path* as a ``pxr.Usd.Stage`` (lazy import)."""
      try:
          from pxr import Usd
      except ImportError as exc:
          raise ImportError(_USD_CORE_IMPORT_ERROR) from exc
      stage = Usd.Stage.Open(str(usd_path))
      if not stage:
          raise RuntimeError(f"Failed to open USD stage: {usd_path}")
      return stage


  def _prepare_source_for_web(source_path: Path, export_root: Path) -> Path:
      """Prepare a source USD file for web export by materializing VTK asset references.

      For files that reference VTK-family assets via custom ``Asset`` attributes,
      convert those assets into USD mesh data before packaging so downstream
      web loaders don't have to resolve them.

      Returns the original path when no preparation is required.
      """
      if source_path.suffix.lower() == ".usdz":
          return source_path

      try:
          from pxr import Usd
      except ImportError as exc:
          raise ImportError(_USD_CORE_IMPORT_ERROR) from exc

      stage = Usd.Stage.Open(str(source_path))
      if not stage:
          raise RuntimeError(f"Failed to open USD stage: {source_path}")

      vtk_asset_paths: list[Path] = []
      vtk_asset_attrs = []
      for prim in stage.Traverse():
          attr = prim.GetAttribute("Asset")
          if not attr:
              continue
          value = attr.Get()
          asset_path = getattr(value, "path", None)
          if not asset_path:
              continue
          if Path(asset_path).suffix.lower() not in _VTK_ASSET_EXTENSIONS:
              continue

          resolved_asset = Path(asset_path)
          if not resolved_asset.is_absolute():
              resolved_asset = (source_path.parent / resolved_asset).resolve()
          vtk_asset_paths.append(resolved_asset)
          vtk_asset_attrs.append(attr)

      if not vtk_asset_paths:
          return source_path

      from ansys.tools.visualization_interface.backends.usd.vtk_converter import (
          VTKConverter,
      )

      converter = VTKConverter()
      for vtk_path in vtk_asset_paths:
          loaded = converter.load_asset(str(vtk_path), stage)
          if loaded is None:
              raise RuntimeError(
                  f"Failed to load VTK asset referenced by stage: {vtk_path}"
              )

      for attr in vtk_asset_attrs:
          attr.Clear()

      prepared_source = export_root / f"{source_path.stem}_webprep.usda"
      stage.Export(str(prepared_source))
      return prepared_source


  def _export_viewer_html(source_path: Path, output_path: Path | None) -> Path:
      """Generate a self-contained HTML viewer file for *source_path*."""
      source_path = Path(source_path).expanduser().resolve()
      if not source_path.exists():
          raise FileNotFoundError(f"Input file not found: {source_path}")

      extension = source_path.suffix.lower()
      if extension not in _SUPPORTED_USD_EXTENSIONS:
          supported = ", ".join(sorted(_SUPPORTED_USD_EXTENSIONS))
          raise ValueError(
              f"Unsupported input format '{extension}'. Supported formats: {supported}."
          )

      if output_path is None:
          html_path = source_path.parent / f"{source_path.stem}_viewer.html"
      else:
          html_path = Path(output_path).expanduser().resolve()

      html_path.parent.mkdir(parents=True, exist_ok=True)

      from ansys.tools.visualization_interface.backends.usd.web.glb import (
          convert_usd_to_glb,
      )
      from ansys.tools.visualization_interface.backends.usd.web.templates import (
          build_viewer_html_glb,
      )

      prepared_path = _prepare_source_for_web(source_path, html_path.parent)
      glb_bytes = convert_usd_to_glb(prepared_path)
      glb_b64 = base64.b64encode(glb_bytes).decode("ascii")
      html = build_viewer_html_glb(glb_b64, source_path.name)
      html_path.write_text(html, encoding="utf-8")
      return html_path


  def _inject_mesh_lines(
      html_path: Path,
      stage: object,
      line_color: str,
      line_opacity: float,
  ) -> None:
      """Inject Three.js LineSegments derived from ``UsdGeomMesh`` prims into *html_path*."""
      import json

      try:
          from pxr import UsdGeom
      except ImportError as exc:
          raise ImportError(_USD_CORE_IMPORT_ERROR) from exc

      html_text = html_path.read_text(encoding="utf-8")

      if _INJECTION_MARKER in html_text:
          return  # idempotent

      if _CONFIG_ANCHOR not in html_text or _SCENE_ANCHOR not in html_text:
          return  # incompatible template, skip gracefully

      segments: list[float] = []
      for prim in stage.Traverse():  # type: ignore[union-attr]
          mesh = UsdGeom.Mesh(prim)
          if not mesh:
              continue

          pts = mesh.GetPointsAttr().Get()
          counts = mesh.GetFaceVertexCountsAttr().Get()
          indices = mesh.GetFaceVertexIndicesAttr().Get()

          if not pts or not counts or not indices:
              continue

          seen: set[tuple[int, int]] = set()
          cursor = 0
          for n in counts:
              face_verts = indices[cursor : cursor + n]
              for i in range(n):
                  a = int(face_verts[i])
                  b = int(face_verts[(i + 1) % n])
                  key = (min(a, b), max(a, b))
                  if key not in seen:
                      seen.add(key)
                      pa = pts[a]
                      pb = pts[b]
                      segments.extend([float(pa[0]), float(pa[1]), float(pa[2])])
                      segments.extend([float(pb[0]), float(pb[1]), float(pb[2])])
              cursor += n

      segs_json = json.dumps([round(v, 6) for v in segments], separators=(",", ":"))

      config_block = (
          f"      const ansysEdgeSegs = new Float32Array({segs_json});\n"
          f'      const ansysEdgeLineColor = new THREE.Color("{line_color}");\n'
          f"      const ansysEdgeLineOpacity = {line_opacity};\n"
          f"      {_INJECTION_MARKER}\n\n"
          "      "
      )
      html_text = html_text.replace(_CONFIG_ANCHOR, config_block + _CONFIG_ANCHOR, 1)

      edge_js = (
          f"{_SCENE_ANCHOR}\n"
          "        if (ansysEdgeSegs.length >= 6) {\n"
          "          const geo = new THREE.BufferGeometry();\n"
          '          geo.setAttribute("position", new THREE.BufferAttribute(ansysEdgeSegs, 3));\n'
          "          const mat = new THREE.LineBasicMaterial({\n"
          "            color: ansysEdgeLineColor,\n"
          "            transparent: ansysEdgeLineOpacity < 1.0,\n"
          "            opacity: ansysEdgeLineOpacity,\n"
          "          });\n"
          "          const lines = new THREE.LineSegments(geo, mat);\n"
          '          lines.name = "AnsysEdges";\n'
          "          lines.frustumCulled = false;\n"
          "          lines.renderOrder = 1;\n"
          "          scene.add(lines);\n"
          "        }"
      )
      html_text = html_text.replace(_SCENE_ANCHOR, edge_js, 1)
      html_path.write_text(html_text, encoding="utf-8")


  def export_usd_to_html(
      source: "str | Path | object",
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
          Opacity of the mesh-edge overlay (0.0 - 1.0).

      Returns
      -------
      pathlib.Path
          Absolute path to the written HTML file.

      Raises
      ------
      ImportError
          If ``usd-core`` is not installed.
      FileNotFoundError
          If a file path is given but does not exist on disk.
      ValueError
          If ``line_opacity`` is outside [0.0, 1.0] or ``line_color`` is not a
          valid CSS hex color.
      """
      if not (0.0 <= line_opacity <= 1.0):
          raise ValueError(
              f"line_opacity must be between 0.0 and 1.0, got {line_opacity!r}."
          )

      if not re.fullmatch(r"#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3,5})?", line_color):
          raise ValueError(
              f"line_color must be a CSS hex color string (e.g. '#ffffff'), got {line_color!r}."
          )

      tmp_path: Path | None = None
      stage: object | None = None

      try:
          if _is_usd_stage(source):
              stage = source
              tmp_path = _stage_to_temp_usd(stage)
              usd_path = tmp_path
          else:
              usd_path = Path(source).expanduser().resolve()  # type: ignore[arg-type]
              if not usd_path.exists():
                  raise FileNotFoundError(f"USD file not found: {usd_path}")

          html_path = _export_viewer_html(usd_path, output_path)

          if show_mesh_lines:
              if stage is None:
                  stage = _open_stage(usd_path)
              _inject_mesh_lines(html_path, stage, line_color, line_opacity)

          return html_path

      finally:
          if tmp_path is not None:
              tmp_path.unlink(missing_ok=True)
  ```

- [ ] **Step 4: Re-run the regression test — expect PASS**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  pytest tests/test_usd_html_export_decoupled.py -v
  ```
  Expected: **PASS**.

- [ ] **Step 5: Smoke-import at top level**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  python -c "from ansys.tools.visualization_interface import export_usd_to_html; print(export_usd_to_html)"
  ```
  Expected: `<function export_usd_to_html at 0x...>`. No `ImportError`, no `usdviewer` reference in the traceback.

- [ ] **Step 6: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add src/ansys/tools/visualization_interface/backends/usd/html_export.py tests/test_usd_html_export_decoupled.py
  git commit -m "refactor(usd): make html_export self-contained (drop usdviewer dep)"
  ```

---

### Task 5: Update `usd_interface.py` to import local `VTKConverter`

**Files:**
- Modify: `D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\usd_interface.py`

**Interfaces:**
- Consumes: `from ansys.tools.visualization_interface.backends.usd.vtk_converter import VTKConverter` (Task 2)
- Produces: `USDInterface` class no longer imports `VTKConverter` from `ansys.tools.usdviewer`; `USDViewer` remains imported from `ansys.tools.usdviewer.viewer` (the live-viewer feature stays coupled to the usdviewer package — that's intentional).

- [ ] **Step 1: Edit the imports block**

  Replace:
  ```python
  try:
      from ansys.tools.usdviewer.viewer import USDViewer
      from ansys.tools.usdviewer.vtk_converter import VTKConverter
  except ImportError:  # pragma: no cover
      warnings.warn(
          "The 'ansys-tools-usdviewer' package is required to use the USD backend. "
          "Install it with: pip install ansys-tools-usdviewer"
      )
  ```
  with:
  ```python
  from ansys.tools.visualization_interface.backends.usd.vtk_converter import VTKConverter

  try:
      from ansys.tools.usdviewer.viewer import USDViewer
  except ImportError:  # pragma: no cover
      warnings.warn(
          "The 'ansys-tools-usdviewer' package is required for the live USD "
          "viewer window. Install it with: "
          "pip install 'ansys-tools-visualization-interface[usd-live-viewer]'"
      )
  ```

- [ ] **Step 2: Verify no other reference to the old import path exists**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\usd_interface.py -Pattern "ansys\.tools\.usdviewer\.vtk_converter"
  ```
  Expected: no matches.

- [ ] **Step 3: Smoke-import**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  python -c "from ansys.tools.visualization_interface.backends.usd.usd_interface import USDInterface; print(USDInterface)"
  ```
  Expected: `<class '...USDInterface'>`. A `UserWarning` about `ansys-tools-usdviewer` is acceptable if that package isn't installed in the dev env.

- [ ] **Step 4: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add src/ansys/tools/visualization_interface/backends/usd/usd_interface.py
  git commit -m "refactor(usd): import VTKConverter from local module"
  ```

---

### Task 6: Rewrite `tests/test_usd_html_export.py` (drop usdviewer mocking)

**Files:**
- Modify: `D:\repositories\ansys-tools-visualization-interface\tests\test_usd_html_export.py`

**Interfaces:**
- Consumes: local `_export_viewer_html`, `_inject_mesh_lines`, `_is_usd_stage`, `_stage_to_temp_usd`, `export_usd_to_html` from `ansys.tools.visualization_interface.backends.usd.html_export`.
- Produces: green test suite that mocks the local `_export_viewer_html` boundary (not the removed `ansys.tools.usdviewer.web.html_export` module).

- [ ] **Step 1: Delete the sys.modules pre-injection block for `ansys.tools.usdviewer`**

  Remove these lines from the file's top-level (lines ~34–47 of the current file):
  ```python
  _mock_usdviewer_html_mod = MagicMock()
  sys.modules.setdefault("ansys.tools.usdviewer", MagicMock())
  sys.modules.setdefault("ansys.tools.usdviewer.web", MagicMock())
  sys.modules.setdefault(
      "ansys.tools.usdviewer.web.html_export", _mock_usdviewer_html_mod
  )
  ```
  Keep the `pxr` mocking block (`_mock_pxr`, `_mock_usd_module`, `_mock_usd_geom`, and their `sys.modules.setdefault` lines) — the tests still rely on it.

- [ ] **Step 2: Replace the `setup_mock_export` fixture with one that patches the local boundary**

  In `class TestExportUsdToHtml`, replace:
  ```python
  @pytest.fixture(autouse=True)
  def setup_mock_export(self, tmp_path):
      """Set up mock for export_viewer_html before each test."""
      self._html = _minimal_viewer_html(tmp_path)
      _mock_usdviewer_html_mod.export_viewer_html.return_value = self._html
      _mock_usdviewer_html_mod.export_viewer_html.reset_mock()
  ```
  with:
  ```python
  @pytest.fixture(autouse=True)
  def setup_mock_export(self, tmp_path, monkeypatch):
      """Patch the local _export_viewer_html boundary before each test."""
      self._html = _minimal_viewer_html(tmp_path)
      self._mock_export = MagicMock(return_value=self._html)
      monkeypatch.setattr(
          "ansys.tools.visualization_interface.backends.usd.html_export._export_viewer_html",
          self._mock_export,
      )
  ```

- [ ] **Step 3: Rewrite `test_import_error_when_usdviewer_missing`**

  Replace it with a test that asserts `ImportError` when `usd-core` (`pxr`) is missing on the mesh-line path. Replace:
  ```python
  def test_import_error_when_usdviewer_missing(self, tmp_path):
      """Test that ImportError is raised when usdviewer is missing."""
      usd_file = tmp_path / "model.usda"
      usd_file.write_text("#usda 1.0\n", encoding="utf-8")
      with patch.dict(sys.modules, {"ansys.tools.usdviewer.web.html_export": None}):
          with pytest.raises(ImportError, match="ansys-tools-usdviewer"):
              export_usd_to_html(usd_file)
  ```
  with:
  ```python
  def test_import_error_when_usd_core_missing(self, tmp_path):
      """ImportError is raised when usd-core (pxr) is missing on the mesh-line path."""
      usd_file = tmp_path / "model.usda"
      usd_file.write_text("#usda 1.0\n", encoding="utf-8")
      # Force _open_stage to raise ImportError, simulating missing usd-core
      with patch(
          "ansys.tools.visualization_interface.backends.usd.html_export._open_stage",
          side_effect=ImportError(
              "The 'usd-core' package is required for USD-to-HTML export."
          ),
      ):
          with pytest.raises(ImportError, match="usd-core"):
              export_usd_to_html(usd_file, show_mesh_lines=True)
  ```

- [ ] **Step 4: Run the unit tests**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  pytest tests/test_usd_html_export.py -v
  ```
  Expected: all tests **PASS** (no `ansys.tools.usdviewer` references remain).

- [ ] **Step 5: Grep the test file for any stray references**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\tests\test_usd_html_export.py -Pattern "ansys\.tools\.usdviewer"
  ```
  Expected: no matches.

- [ ] **Step 6: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add tests/test_usd_html_export.py
  git commit -m "test(usd): rewrite unit tests against local html_export boundary"
  ```

---

### Task 7: Rewrite `tests/test_usd_html_export_integration.py` (drop usdviewer mocking)

**Files:**
- Modify: `D:\repositories\ansys-tools-visualization-interface\tests\test_usd_html_export_integration.py`

**Interfaces:**
- Consumes: real `pxr` (via `pytest.importorskip("pxr")`), the vendored `web/` pipeline, and the rewritten `html_export.py`.
- Produces: an integration test file that exercises the full local pipeline end-to-end without touching `ansys.tools.usdviewer`.

- [ ] **Step 1: Inspect the existing test file to enumerate every `ansys.tools.usdviewer` reference**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\tests\test_usd_html_export_integration.py -Pattern "ansys\.tools\.usdviewer" -Context 2,4
  ```
  Note every line — you must remove or rewrite each.

- [ ] **Step 2: Remove every `patch.dict(sys.modules, {"ansys.tools.usdviewer.web.html_export": MagicMock(...)})` block**

  Wherever the tests wrap calls with `patch.dict(sys.modules, {"ansys.tools.usdviewer.web.html_export": ...})`, delete the `with patch.dict(...)` wrapper and call `export_usd_to_html(...)` directly — the local pipeline now runs end-to-end and needs no mocking.

- [ ] **Step 3: Add an explicit `pygltflib` skip guard next to the existing `pxr` guard**

  Below the existing:
  ```python
  pxr = pytest.importorskip(
      "pxr", reason="usd-core not installed; skipping integration tests"
  )
  ```
  add:
  ```python
  pytest.importorskip(
      "pygltflib", reason="pygltflib not installed; skipping integration tests"
  )
  ```

- [ ] **Step 4: Run the integration tests**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  pip install -e .[usd,tests]
  pytest tests/test_usd_html_export_integration.py -v
  ```
  Expected: all tests **PASS**. If any test still fails because it asserted on mocked behavior, rewrite it to assert against real generated HTML (search for the same markers — `ansysEdgesInjected`, `Float32Array`, `THREE.LineSegments`).

- [ ] **Step 5: Grep the file for stray references**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\tests\test_usd_html_export_integration.py -Pattern "ansys\.tools\.usdviewer"
  ```
  Expected: no matches.

- [ ] **Step 6: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add tests/test_usd_html_export_integration.py
  git commit -m "test(usd): run integration tests against local pipeline"
  ```

---

### Task 8: Update documentation

**Files:**
- Modify: `D:\repositories\ansys-tools-visualization-interface\doc\source\user_guide\usdviewer.rst`

**Interfaces:**
- Produces: a user guide page that tells the reader HTML export requires only `pip install 'ansys-tools-visualization-interface[usd]'` and that the live viewer (a separate feature) requires `pip install 'ansys-tools-visualization-interface[usd-live-viewer]'`.

- [ ] **Step 1: Read the current page**

  ```powershell
  Get-Content D:\repositories\ansys-tools-visualization-interface\doc\source\user_guide\usdviewer.rst
  ```

- [ ] **Step 2: Replace any reference to installing `ansys-tools-usdviewer` for HTML export**

  Any line that says something like `pip install ansys-tools-usdviewer` in the context of HTML export must be changed to:
  ```
  pip install 'ansys-tools-visualization-interface[usd]'
  ```
  Preserve any live-viewer section but update its install line to:
  ```
  pip install 'ansys-tools-visualization-interface[usd-live-viewer]'
  ```

- [ ] **Step 3: Verify the file still renders (best-effort)**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  python -c "import docutils.parsers.rst, docutils.utils, docutils.frontend; s = docutils.frontend.OptionParser(components=(docutils.parsers.rst.Parser,)).get_default_values(); d = docutils.utils.new_document('usdviewer.rst', s); docutils.parsers.rst.Parser().parse(open(r'doc/source/user_guide/usdviewer.rst', encoding='utf-8').read(), d); print('parsed OK')"
  ```
  Expected: `parsed OK`. If this fails because `docutils` is not installed, skip and rely on Sphinx CI to validate.

- [ ] **Step 4: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add doc/source/user_guide/usdviewer.rst
  git commit -m "docs(usd): update install instructions after html-export decoupling"
  ```

---

### Task 9: Add a CHANGELOG entry in vis-interface

**Files:**
- Modify: `D:\repositories\ansys-tools-visualization-interface\CHANGELOG.md`

**Interfaces:**
- Produces: a user-visible changelog note for the migration.

- [ ] **Step 1: Read the current unreleased section**

  ```powershell
  Get-Content D:\repositories\ansys-tools-visualization-interface\CHANGELOG.md -TotalCount 60
  ```

- [ ] **Step 2: Add entries under the unreleased section**

  Under the appropriate "Added" and "Changed" subsections (create them if missing, matching the file's existing style):

  - Added: `USD-to-HTML export is now self-contained — the GLB conversion pipeline, viewer template, and VTK-to-USD converter have been vendored into ``ansys.tools.visualization_interface.backends.usd``. HTML export no longer requires ``ansys-tools-usdviewer``.`
  - Changed: `Split the ``[usd]`` optional extra: ``[usd]`` now installs only ``usd-core`` and ``pygltflib`` (the minimum needed for HTML export). The live Qt USD viewer moved to a new ``[usd-live-viewer]`` extra that pulls in ``ansys-tools-usdviewer``.`

- [ ] **Step 3: Commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add CHANGELOG.md
  git commit -m "docs: changelog for self-contained USD HTML export"
  ```

---

### Task 10: Full-repo verification in vis-interface

**Files:** none new; validation only.

**Interfaces:** none.

- [ ] **Step 1: Reinstall extras and run the full USD-related test surface**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  pip install -e .[usd,tests]
  pytest tests/test_usd_html_export.py tests/test_usd_html_export_integration.py tests/test_usd_html_export_decoupled.py tests/test_usd_interface.py -v
  ```
  Expected: all pass.

- [ ] **Step 2: Grep the vis-interface source tree for any remaining reference to `usdviewer` on the HTML-export path**

  ```powershell
  Select-String -Path D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\html_export.py, D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\web\*.py, D:\repositories\ansys-tools-visualization-interface\src\ansys\tools\visualization_interface\backends\usd\vtk_converter.py -Pattern "ansys\.tools\.usdviewer"
  ```
  Expected: no matches. If any appear, fix them before moving on.

- [ ] **Step 3: Build the wheel and inspect its contents for the HTML template**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  python -m pip install --upgrade build
  python -m build --wheel --outdir dist_verify
  python -c "import zipfile, glob; z = zipfile.ZipFile(glob.glob('dist_verify/*.whl')[0]); names = z.namelist(); assert any(n.endswith('glb_template.html') for n in names), 'glb_template.html missing from wheel!'; print('template present:', [n for n in names if n.endswith('.html')])"
  Remove-Item -Recurse -Force dist_verify
  ```
  Expected: prints the template path(s) inside the wheel; assertion does not fire.

- [ ] **Step 4: Run ruff**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  ruff check src tests
  ruff format --check src tests
  ```
  Expected: clean. If format fails, run `ruff format src tests` and re-commit under whichever task the file belongs to.

- [ ] **Step 5: If any fix commits were made in Steps 3–4, push them as a single verification commit**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  git add -A
  git diff --cached --quiet; if ($LASTEXITCODE -ne 0) { git commit -m "chore(usd): post-migration verification fixes" }
  ```

---

### Task 11: Delete the `web/` subpackage from `python-usd-viewer`

**Files:**
- Delete: `D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\web\` (entire directory including `__init__.py`, `glb.py`, `glb_builder.py`, `glb_lights.py`, `glb_materials.py`, `glb_mesh.py`, `glb_template.html`, `html_export.py`, `templates.py`, `__pycache__/`)

**Interfaces:**
- Removes: the entire `ansys.tools.usdviewer.web` package.

- [ ] **Step 1: Confirm Task 10 was committed on the vis-interface side**

  ```powershell
  git -C D:\repositories\ansys-tools-visualization-interface log --oneline -10
  ```
  Confirm the migration commits from Tasks 1–10 are present. Do not proceed until they are.

- [ ] **Step 2: Delete the `web/` directory**

  ```powershell
  Remove-Item -Recurse -Force D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\web
  ```

- [ ] **Step 3: Verify nothing in the remaining source still imports from `.web`**

  ```powershell
  Select-String -Path D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\*.py -Pattern "from \.web|ansys\.tools\.usdviewer\.web|from ansys\.tools\.usdviewer\.web"
  ```
  Expected: no matches. If any appear, remove those imports (they're now dead code).

- [ ] **Step 4: Commit**

  ```powershell
  cd D:\repositories\python-usd-viewer
  git add -A
  git commit -m "refactor: remove web/ HTML-export subpackage (moved to ansys-tools-visualization-interface)"
  ```

---

### Task 12: Delete `vtk_converter.py` from `python-usd-viewer` (and update its remaining consumers)

**Files:**
- Modify: `D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\viewer.py` (and any other file that imports `.vtk_converter`)
- Delete: `D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\vtk_converter.py`

**Interfaces:**
- Removes: `ansys.tools.usdviewer.vtk_converter` module.
- `viewer.py` is refactored to no longer depend on `VTKConverter` (or, if the viewer genuinely needs it and can't function without it, this task must be split and vis-interface's copy must be re-exported from a shared location — see the decision point below).

**Decision point — inspect first, then act:**

- [ ] **Step 1: Enumerate all consumers of `.vtk_converter` inside `python-usd-viewer`**

  ```powershell
  Select-String -Path D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\*.py -Pattern "vtk_converter|VTKConverter"
  ```
  Record each match. Currently expected: `viewer.py` imports `VTKConverter`, and `autosetup.py` may or may not.

- [ ] **Step 2: Read `viewer.py` to see how it uses `VTKConverter`**

  ```powershell
  Select-String -Path D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\viewer.py -Pattern "VTKConverter" -Context 2,10
  ```
  Determine which methods it calls. Two possibilities:

  **(a) `viewer.py` uses `VTKConverter` non-trivially** — in that case, leave `vtk_converter.py` in place for now (rename this task to "keep vtk_converter for viewer usage") and skip deletion. Move on to Task 13. The vis-interface repo already has its own vendored copy from Task 2; the two files diverging is acceptable because they belong to different packages.

  **(b) `viewer.py` only uses `VTKConverter` from `.web` code paths** (i.e., after removing `web/` there are no live callers) — in that case, delete `vtk_converter.py` and remove the import from `viewer.py`.

- [ ] **Step 3: Execute the chosen path**

  If **(a)**: no source-file changes here. Commit message for a no-op task: skip commit; move on.

  If **(b)**:
  ```powershell
  Remove-Item -Force D:\repositories\python-usd-viewer\src\ansys\tools\usdviewer\vtk_converter.py
  ```
  Then edit `viewer.py` to drop the `from ansys.tools.usdviewer.vtk_converter import VTKConverter` line and any code that references it.

- [ ] **Step 4: Verify the package still imports cleanly**

  ```powershell
  cd D:\repositories\python-usd-viewer
  python -c "import ansys.tools.usdviewer; from ansys.tools.usdviewer.viewer import USDViewer; print(USDViewer)"
  ```
  Expected: no `ImportError` traceback. `warnings` about `pxr` are OK if the WASM/compiled build isn't active in your dev env.

- [ ] **Step 5: Commit (only if changes were made under path (b))**

  ```powershell
  cd D:\repositories\python-usd-viewer
  git add -A
  git commit -m "refactor: drop VTKConverter (moved to ansys-tools-visualization-interface)"
  ```

---

### Task 13: Update `python-usd-viewer` `pyproject.toml`

**Files:**
- Modify: `D:\repositories\python-usd-viewer\pyproject.toml`

**Interfaces:**
- Removes: `pygltflib` runtime dep (only used by the removed `web/` GLB pipeline) and the `include = [ "src/ansys/tools/usdviewer/web/*.html" ]` build directive.

- [ ] **Step 1: Confirm `pygltflib` is unused after Task 11**

  ```powershell
  Select-String -Path D:\repositories\python-usd-viewer\src -Pattern "pygltflib" -Recurse
  ```
  Expected: no matches. If any match appears (e.g., outside `web/`), leave the dep in place and skip the corresponding edit below.

- [ ] **Step 2: Edit `pyproject.toml`**

  - Remove `"pygltflib",` from the `[project] dependencies` list (only if Step 1 confirmed no remaining usage).
  - Remove the line `include = [ "src/ansys/tools/usdviewer/web/*.html" ]` from `[tool.hatch.build.targets.wheel]`. Keep the `packages = [ "src/ansys" ]` line.

- [ ] **Step 3: Verify TOML syntax and package still builds**

  ```powershell
  cd D:\repositories\python-usd-viewer
  python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"
  python -m build --wheel --outdir dist_verify
  Remove-Item -Recurse -Force dist_verify
  ```
  Expected: `OK` then a successful wheel build.

- [ ] **Step 4: Commit**

  ```powershell
  cd D:\repositories\python-usd-viewer
  git add pyproject.toml
  git commit -m "build: drop pygltflib dep and web/*.html include after HTML export removal"
  ```

---

### Task 14: Remove HTML-export tests, examples, and docs from `python-usd-viewer`

**Files:**
- Modify or delete: any file under `D:\repositories\python-usd-viewer\tests\`, `examples\`, or `doc\` that references `web`, `html_export`, `export_viewer_html`, `glb`, or `vtk_converter`.

**Interfaces:**
- Removes: dangling references to removed modules.

- [ ] **Step 1: Enumerate references**

  ```powershell
  Select-String -Path D:\repositories\python-usd-viewer\tests\*, D:\repositories\python-usd-viewer\examples\*, D:\repositories\python-usd-viewer\doc\* -Recurse -Pattern "\.web|html_export|export_viewer_html|convert_usd_to_glb|VTKConverter"
  ```
  Record every hit.

- [ ] **Step 2: For each hit, decide delete vs. edit**

  - Test files whose entire purpose is exercising `web/` or `vtk_converter`: delete the file.
  - Example scripts under `examples/` demonstrating HTML export: delete the file (the equivalent example now lives at `D:\repositories\ansys-tools-visualization-interface\examples\02-basic-usd-examples\usd_to_html_export.py`).
  - Doc pages describing HTML export: delete the file and remove its entry from any `toctree` (`.rst`) that references it.
  - Mixed files that reference these symbols only in passing (e.g., a general test suite that also has one HTML-export test class): edit the file to remove only the offending sections.

- [ ] **Step 3: Verify no dangling toctree entries remain**

  ```powershell
  Get-ChildItem D:\repositories\python-usd-viewer\doc -Recurse -Filter *.rst | ForEach-Object { Select-String -Path $_.FullName -Pattern "html_export|web\/|glb" }
  ```
  Expected: no matches.

- [ ] **Step 4: Run the remaining test suite**

  ```powershell
  cd D:\repositories\python-usd-viewer
  pytest -v
  ```
  Expected: all remaining tests pass. If tests fail because they still reference removed symbols, revisit Step 2.

- [ ] **Step 5: Commit**

  ```powershell
  cd D:\repositories\python-usd-viewer
  git add -A
  git commit -m "test/docs: remove HTML-export tests, examples, and doc pages"
  ```

---

### Task 15: CHANGELOG in `python-usd-viewer`

**Files:**
- Modify: `D:\repositories\python-usd-viewer\CHANGELOG.md` (or `doc/source/changelog.rst` if the former re-directs there — check the file first).

**Interfaces:**
- Produces: a user-visible "Removed" note explaining the split.

- [ ] **Step 1: Read the current changelog to find the unreleased section and correct file**

  ```powershell
  Get-Content D:\repositories\python-usd-viewer\CHANGELOG.md -TotalCount 40
  ```
  Follow any `include` directive or convention documented at the top; edit the file that actually contains change entries.

- [ ] **Step 2: Add an entry under a "Removed" (or the repo's equivalent "Breaking") subsection**

  Entry text:
  > Removed the ``ansys.tools.usdviewer.web`` subpackage and the ``ansys.tools.usdviewer.vtk_converter`` module. HTML export now lives in ``ansys-tools-visualization-interface`` — install with ``pip install 'ansys-tools-visualization-interface[usd]'`` and use ``from ansys.tools.visualization_interface import export_usd_to_html``.

- [ ] **Step 3: Commit**

  ```powershell
  cd D:\repositories\python-usd-viewer
  git add CHANGELOG.md
  git commit -m "docs: changelog for HTML-export removal"
  ```

---

## Post-Migration Verification (both repos)

- [ ] **Both wheels build:**
  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface; python -m build --wheel --outdir dist_verify; Remove-Item -Recurse -Force dist_verify
  cd D:\repositories\python-usd-viewer; python -m build --wheel --outdir dist_verify; Remove-Item -Recurse -Force dist_verify
  ```
- [ ] **HTML export works with just `[usd]` (no usdviewer installed):**
  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  # Create a fresh venv to prove usdviewer is not required
  python -m venv .venv_verify
  .\.venv_verify\Scripts\Activate.ps1
  pip install -e .[usd]
  python -c "from ansys.tools.visualization_interface import export_usd_to_html; from pxr import Gf, Usd, UsdGeom; s = Usd.Stage.CreateInMemory(); m = UsdGeom.Mesh.Define(s, '/T'); s.SetDefaultPrim(m.GetPrim()); m.GetPointsAttr().Set([Gf.Vec3f(0,0,0), Gf.Vec3f(1,0,0), Gf.Vec3f(0,1,0)]); m.GetFaceVertexCountsAttr().Set([3]); m.GetFaceVertexIndicesAttr().Set([0,1,2]); import tempfile, pathlib; out = pathlib.Path(tempfile.gettempdir()) / 'triangle_viewer.html'; p = export_usd_to_html(s, out); assert p.exists() and p.stat().st_size > 1000; print('OK', p)"
  deactivate
  Remove-Item -Recurse -Force .venv_verify
  ```
  Expected: `OK <path>` and no `ImportError` mentioning `ansys.tools.usdviewer`.

---

## Self-Review Notes

- Spec coverage: every item in the original design discussion (vendor GLB pipeline, vendor templates, vendor vtk_converter, rewrite html_export, split extras, delete from source repo, update tests/docs/changelog in both repos) has a task.
- Placeholders: none — every code block is complete; every command is exact; every file path is absolute.
- Type consistency: `_export_viewer_html(source_path: Path, output_path: Path | None) -> Path` is defined in Task 4 Step 3 and referenced by name in the Task 6 monkeypatch string — signatures match. `convert_usd_to_glb(path: Path) -> bytes` is vendored unchanged in Task 3 and called from `_export_viewer_html` in Task 4 — signature matches. `build_viewer_html_glb(glb_b64: str, model_name: str) -> str` likewise.
- Cross-repo ordering: Task 11 explicitly blocks on Task 10 completion.
- Task 12 has an explicit decision-point (a/b) because the correct action depends on runtime inspection of `viewer.py`, and forcing an answer up-front would risk making the plan wrong for one branch.
