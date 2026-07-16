# USD-to-HTML Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `export_usd_to_html()` to `ansys-tools-visualization-interface` so any PyAnsys library that exports USD can convert it to a self-contained Three.js HTML page, with optional wireframe mesh-line overlay.

**Architecture:** A new module `backends/usd/html_export.py` delegates HTML generation to `ansys.tools.usdviewer.web.html_export.export_viewer_html` (lazy import), then optionally traverses the USD stage via `pxr` to extract polygon edges and injects them as Three.js `LineSegments` into the HTML. All `pxr` and `usdviewer` imports are lazy (inside function bodies) so the module loads without those packages installed.

**Tech Stack:** Python ≥ 3.10, `usd-core` (PyPI pure-Python wheel, provides `pxr`), `ansys-tools-usdviewer` (lazy, provides `export_viewer_html`), Three.js (CDN, embedded in generated HTML), pytest.

## Global Constraints

- Python ≥ 3.10, < 4.
- All new `.py` files under `src/` and `tests/` need the ANSYS MIT license header (pre-commit `add-license-headers` hook adds it automatically on first commit attempt; run `git add` and `git commit` a second time after the hook auto-fixes).
- `pxr` and `ansys.tools.usdviewer` imports must be **lazy** (inside function bodies only). Module-level imports of these packages are forbidden.
- `usd-core >= 24.0` added to the `[usd]` optional extra in `pyproject.toml`.
- Ruff is the linter/formatter. Run `ruff check --fix` and `ruff format` before committing if pre-commit fails.
- HTML injection anchors from `python-usd-viewer`'s `glb_template.html`:
  - config anchor: `const binary = atob(glbBase64);`
  - scene anchor: `scene.add(gltf.scene);`
  - idempotency marker: `// ansysEdgesInjected`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `pyproject.toml` | Modify | Add `usd-core >= 24.0` to `[usd]` extra |
| `src/ansys/tools/visualization_interface/backends/usd/html_export.py` | Create | Public `export_usd_to_html()` + private helpers |
| `src/ansys/tools/visualization_interface/backends/usd/__init__.py` | Modify | Re-export `export_usd_to_html` |
| `src/ansys/tools/visualization_interface/__init__.py` | Modify | Top-level `export_usd_to_html` import |
| `tests/test_usd_html_export.py` | Create | Unit tests (all deps mocked) |
| `tests/test_usd_html_export_integration.py` | Create | Integration tests (require real `pxr`) |
| `doc/source/user_guide/usdviewer.rst` | Modify | Add HTML export section |

---

### Task 1: Update `pyproject.toml` — add `usd-core` dependency

**Files:**
- Modify: `pyproject.toml`

**Interfaces:**
- Produces: `usd-core >= 24.0` available when `pip install ansys-tools-visualization-interface[usd]`

- [ ] **Step 1: Edit `pyproject.toml`**

  Change the `[usd]` entry from:
  ```toml
  usd = [
      "ansys-tools-usdviewer >= 0.1.0,< 1"
  ]
  ```
  to:
  ```toml
  usd = [
      "ansys-tools-usdviewer >= 0.1.0,< 1",
      "usd-core >= 24.0",
  ]
  ```

- [ ] **Step 2: Verify TOML syntax**

  ```powershell
  python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb')); print('OK')"
  ```
  Expected: `OK`

- [ ] **Step 3: Commit**

  ```bash
  git add pyproject.toml
  git commit -m "build: add usd-core to [usd] optional dependency"
  ```

---

### Task 2: Create `html_export.py` with core `export_usd_to_html` + unit tests (no mesh-lines yet)

**Files:**
- Create: `src/ansys/tools/visualization_interface/backends/usd/html_export.py`
- Create: `tests/test_usd_html_export.py`

**Interfaces:**
- Produces:
  - `export_usd_to_html(source, output_path=None, *, show_mesh_lines=True, line_color="#ffffff", line_opacity=0.9) -> Path`
  - `_is_usd_stage(obj) -> bool`
  - `_stage_to_temp_usd(stage) -> Path`
  - `_open_stage(usd_path: Path) -> pxr.Usd.Stage`
  - `_inject_mesh_lines(html_path: Path, stage, line_color: str, line_opacity: float) -> None` (stub — raises `NotImplementedError` in this task, replaced in Task 3)

- [ ] **Step 1: Write failing tests**

  Create `tests/test_usd_html_export.py`:

  ```python
  # Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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
  """Unit tests for backends/usd/html_export.py — all heavy deps mocked."""
  import sys
  from pathlib import Path
  from unittest.mock import MagicMock, patch

  import pytest

  # ── Mock pxr and ansys-tools-usdviewer before importing the module under test ──
  # setdefault: only overrides if NOT already in sys.modules (safe for CI without
  # these packages installed).
  _mock_usd_stage_class = type("Stage", (), {})
  _mock_usd_module = MagicMock()
  _mock_usd_module.Stage = _mock_usd_stage_class

  _mock_pxr = MagicMock()
  _mock_pxr.Usd = _mock_usd_module
  _mock_usd_geom = MagicMock()
  _mock_pxr.UsdGeom = _mock_usd_geom

  sys.modules.setdefault("pxr", _mock_pxr)
  sys.modules.setdefault("pxr.Usd", _mock_usd_module)
  sys.modules.setdefault("pxr.UsdGeom", _mock_usd_geom)

  _mock_usdviewer_html_mod = MagicMock()
  sys.modules.setdefault("ansys.tools.usdviewer", MagicMock())
  sys.modules.setdefault("ansys.tools.usdviewer.web", MagicMock())
  sys.modules.setdefault(
      "ansys.tools.usdviewer.web.html_export", _mock_usdviewer_html_mod
  )

  from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: E402
      _inject_mesh_lines,
      _is_usd_stage,
      _stage_to_temp_usd,
      export_usd_to_html,
  )

  # ── Helpers ───────────────────────────────────────────────────────────────────


  def _minimal_viewer_html(tmp_path: Path) -> Path:
      """Write a minimal viewer HTML with both injection anchors."""
      content = (
          "<!doctype html><html><body><script type='module'>\n"
          "const binary = atob(glbBase64);\n"
          "scene.add(gltf.scene);\n"
          "</script></body></html>"
      )
      path = tmp_path / "model_viewer.html"
      path.write_text(content, encoding="utf-8")
      return path


  # ── _is_usd_stage ─────────────────────────────────────────────────────────────


  class TestIsUsdStage:
      def test_stage_like_object_returns_true(self):
          obj = MagicMock(spec=["Traverse", "GetPrimAtPath", "Export"])
          assert _is_usd_stage(obj) is True

      def test_string_returns_false(self):
          assert _is_usd_stage("model.usd") is False

      def test_path_returns_false(self):
          assert _is_usd_stage(Path("model.usd")) is False

      def test_none_returns_false(self):
          assert _is_usd_stage(None) is False

      def test_object_missing_one_attr_returns_false(self):
          obj = MagicMock(spec=["Traverse", "GetPrimAtPath"])  # no Export
          assert _is_usd_stage(obj) is False


  # ── _stage_to_temp_usd ────────────────────────────────────────────────────────


  class TestStageToTempUsd:
      def test_calls_stage_export_and_returns_usda_path(self):
          stage = MagicMock()
          result = _stage_to_temp_usd(stage)
          assert result.suffix == ".usda"
          stage.Export.assert_called_once_with(str(result))
          result.unlink(missing_ok=True)


  # ── export_usd_to_html ────────────────────────────────────────────────────────


  class TestExportUsdToHtml:
      @pytest.fixture(autouse=True)
      def setup_mock_export(self, tmp_path):
          """Configure the usdviewer mock to return a viewer HTML per test."""
          self._html = _minimal_viewer_html(tmp_path)
          _mock_usdviewer_html_mod.export_viewer_html.return_value = self._html
          _mock_usdviewer_html_mod.export_viewer_html.reset_mock()

      def test_file_path_input_returns_html_path(self, tmp_path):
          usd_file = tmp_path / "model.usda"
          usd_file.write_text("#usda 1.0\n", encoding="utf-8")
          mock_stage = MagicMock()
          mock_stage.Traverse.return_value = []

          with patch(
              "ansys.tools.visualization_interface.backends.usd.html_export._open_stage",
              return_value=mock_stage,
          ):
              result = export_usd_to_html(usd_file)

          assert result == self._html

      def test_file_path_as_string(self, tmp_path):
          usd_file = tmp_path / "model.usda"
          usd_file.write_text("#usda 1.0\n", encoding="utf-8")
          mock_stage = MagicMock()
          mock_stage.Traverse.return_value = []

          with patch(
              "ansys.tools.visualization_interface.backends.usd.html_export._open_stage",
              return_value=mock_stage,
          ):
              result = export_usd_to_html(str(usd_file))

          assert result == self._html

      def test_stage_input_calls_stage_to_temp_and_returns_html(self, tmp_path):
          stage = MagicMock()
          stage.Traverse.return_value = []
          stage.GetPrimAtPath = MagicMock()
          stage.Export = MagicMock()
          fake_tmp = tmp_path / "tmp_stage.usda"
          fake_tmp.write_text("#usda 1.0\n", encoding="utf-8")

          with patch(
              "ansys.tools.visualization_interface.backends.usd.html_export._stage_to_temp_usd",
              return_value=fake_tmp,
          ) as mock_to_tmp:
              result = export_usd_to_html(stage)

          mock_to_tmp.assert_called_once_with(stage)
          assert result == self._html

      def test_stage_input_temp_file_cleaned_up(self, tmp_path):
          stage = MagicMock()
          stage.Traverse.return_value = []
          stage.GetPrimAtPath = MagicMock()
          stage.Export = MagicMock()
          fake_tmp = tmp_path / "tmp_stage.usda"
          fake_tmp.write_text("#usda 1.0\n", encoding="utf-8")
          assert fake_tmp.exists()

          with patch(
              "ansys.tools.visualization_interface.backends.usd.html_export._stage_to_temp_usd",
              return_value=fake_tmp,
          ):
              export_usd_to_html(stage)

          assert not fake_tmp.exists()

      def test_show_mesh_lines_false_skips_injection(self, tmp_path):
          usd_file = tmp_path / "model.usda"
          usd_file.write_text("#usda 1.0\n", encoding="utf-8")

          with patch(
              "ansys.tools.visualization_interface.backends.usd.html_export._inject_mesh_lines"
          ) as mock_inject:
              export_usd_to_html(usd_file, show_mesh_lines=False)

          mock_inject.assert_not_called()

      def test_file_not_found_raises(self, tmp_path):
          with pytest.raises(FileNotFoundError, match="not found"):
              export_usd_to_html(tmp_path / "nonexistent.usd")

      def test_invalid_opacity_above_one_raises(self, tmp_path):
          usd_file = tmp_path / "model.usda"
          usd_file.write_text("#usda 1.0\n", encoding="utf-8")
          with pytest.raises(ValueError, match="line_opacity"):
              export_usd_to_html(usd_file, line_opacity=1.5)

      def test_invalid_opacity_below_zero_raises(self, tmp_path):
          usd_file = tmp_path / "model.usda"
          usd_file.write_text("#usda 1.0\n", encoding="utf-8")
          with pytest.raises(ValueError, match="line_opacity"):
              export_usd_to_html(usd_file, line_opacity=-0.1)

      def test_import_error_when_usdviewer_missing(self, tmp_path):
          usd_file = tmp_path / "model.usda"
          usd_file.write_text("#usda 1.0\n", encoding="utf-8")
          with patch.dict(sys.modules, {"ansys.tools.usdviewer.web.html_export": None}):
              with pytest.raises(ImportError, match="ansys-tools-usdviewer"):
                  export_usd_to_html(usd_file)
  ```

- [ ] **Step 2: Run tests to verify they fail**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  .venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py -v 2>&1 | Select-Object -First 40
  ```
  Expected: `ImportError` or `ModuleNotFoundError` — the module doesn't exist yet.

- [ ] **Step 3: Create `src/ansys/tools/visualization_interface/backends/usd/html_export.py`**

  ```python
  # Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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

  """USD-to-HTML export utility for ansys-tools-visualization-interface."""

  from __future__ import annotations

  import tempfile
  from pathlib import Path

  _USDVIEWER_IMPORT_ERROR = (
      "The 'ansys-tools-usdviewer' package is required for HTML export. "
      "Install it with: pip install 'ansys-tools-visualization-interface[usd]'"
  )

  _USD_CORE_IMPORT_ERROR = (
      "The 'usd-core' package is required for mesh-line injection. "
      "Install it with: pip install 'ansys-tools-visualization-interface[usd]'"
  )

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
      return Usd.Stage.Open(str(usd_path))


  def _inject_mesh_lines(
      html_path: Path,
      stage: object,
      line_color: str,
      line_opacity: float,
  ) -> None:
      """Inject Three.js LineSegments derived from UsdGeomMesh prims into *html_path*.

      Parameters
      ----------
      html_path : Path
          Path to the viewer HTML file to patch in place.
      stage : pxr.Usd.Stage
          USD stage whose UsdGeomMesh prims are traversed for edge extraction.
      line_color : str
          CSS hex colour string (e.g. ``"#ffffff"``).
      line_opacity : float
          Opacity in ``[0.0, 1.0]``.
      """
      import json

      try:
          from pxr import UsdGeom
      except ImportError as exc:
          raise ImportError(_USD_CORE_IMPORT_ERROR) from exc

      html_text = html_path.read_text(encoding="utf-8")

      if _INJECTION_MARKER in html_text:
          return  # idempotent

      if _CONFIG_ANCHOR not in html_text or _SCENE_ANCHOR not in html_text:
          # Template incompatible — skip gracefully rather than corrupt the file.
          return

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
      source: "str | Path",
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
          If ``ansys-tools-usdviewer`` or ``usd-core`` is not installed.
      FileNotFoundError
          If a file path is given but does not exist on disk.
      ValueError
          If ``line_opacity`` is outside [0.0, 1.0].
      """
      try:
          from ansys.tools.usdviewer.web.html_export import (
              export_viewer_html as _export_viewer_html,
          )
      except ImportError as exc:
          raise ImportError(_USDVIEWER_IMPORT_ERROR) from exc

      if not (0.0 <= line_opacity <= 1.0):
          raise ValueError(
              f"line_opacity must be between 0.0 and 1.0, got {line_opacity!r}."
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

- [ ] **Step 4: Run tests — expect them to pass**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  .venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py -v
  ```
  Expected: all tests PASS.

- [ ] **Step 5: Commit**

  ```bash
  git add src/ansys/tools/visualization_interface/backends/usd/html_export.py tests/test_usd_html_export.py
  git commit -m "feat(usd): add export_usd_to_html utility"
  ```
  If pre-commit adds license headers, `git add` and `git commit` again with the same message.

---

### Task 3: Add `_inject_mesh_lines` unit tests + integration test file

`_inject_mesh_lines` is already implemented in Task 2. This task adds the remaining unit tests
for it and the separate integration test file.

**Files:**
- Modify: `tests/test_usd_html_export.py` — add `TestInjectMeshLines` class
- Create: `tests/test_usd_html_export_integration.py` — integration tests guarded by `pytest.importorskip`

**Interfaces:**
- Consumes: `_inject_mesh_lines(html_path, stage, line_color, line_opacity)` from Task 2

- [ ] **Step 1: Add `TestInjectMeshLines` class to `tests/test_usd_html_export.py`**

  Append this class after `TestExportUsdToHtml`:

  ```python
  # ── _inject_mesh_lines ────────────────────────────────────────────────────────


  class TestInjectMeshLines:
      def _html_with_anchors(self, tmp_path: Path) -> Path:
          content = (
              "<!doctype html><html><body><script type='module'>\n"
              "const binary = atob(glbBase64);\n"
              "scene.add(gltf.scene);\n"
              "</script></body></html>"
          )
          path = tmp_path / "viewer.html"
          path.write_text(content, encoding="utf-8")
          return path

      def test_injects_marker(self, tmp_path):
          html_path = self._html_with_anchors(tmp_path)
          stage = MagicMock()
          stage.Traverse.return_value = []
          _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
          assert "ansysEdgesInjected" in html_path.read_text(encoding="utf-8")

      def test_injects_line_color(self, tmp_path):
          html_path = self._html_with_anchors(tmp_path)
          stage = MagicMock()
          stage.Traverse.return_value = []
          _inject_mesh_lines(html_path, stage, "#ff0000", 0.5)
          content = html_path.read_text(encoding="utf-8")
          assert "#ff0000" in content
          assert "0.5" in content

      def test_idempotent(self, tmp_path):
          html_path = self._html_with_anchors(tmp_path)
          stage = MagicMock()
          stage.Traverse.return_value = []
          _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
          first = html_path.read_text(encoding="utf-8")
          _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
          second = html_path.read_text(encoding="utf-8")
          assert first == second

      def test_skips_incompatible_template(self, tmp_path):
          html_path = tmp_path / "viewer.html"
          original = "<html>no anchors here</html>"
          html_path.write_text(original, encoding="utf-8")
          stage = MagicMock()
          stage.Traverse.return_value = []
          _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
          assert html_path.read_text(encoding="utf-8") == original

      def test_no_mesh_prims_produces_empty_segments(self, tmp_path):
          html_path = self._html_with_anchors(tmp_path)
          stage = MagicMock()
          # Return one prim where UsdGeom.Mesh() evaluates to False (not a mesh)
          mock_prim = MagicMock()
          non_mesh = MagicMock()
          non_mesh.__bool__ = lambda self: False
          _mock_usd_geom.Mesh.return_value = non_mesh
          stage.Traverse.return_value = [mock_prim]
          _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
          content = html_path.read_text(encoding="utf-8")
          # Empty segment array — still injected but with empty Float32Array
          assert "ansysEdgesInjected" in content
          assert "Float32Array([])" in content

      def test_with_triangle_prim_injects_three_edges(self, tmp_path):
          html_path = self._html_with_anchors(tmp_path)

          mock_mesh = MagicMock()
          mock_mesh.__bool__ = lambda self: True
          mock_mesh.GetPointsAttr.return_value.Get.return_value = [
              (0.0, 0.0, 0.0),
              (1.0, 0.0, 0.0),
              (0.0, 1.0, 0.0),
          ]
          mock_mesh.GetFaceVertexCountsAttr.return_value.Get.return_value = [3]
          mock_mesh.GetFaceVertexIndicesAttr.return_value.Get.return_value = [0, 1, 2]
          _mock_usd_geom.Mesh.return_value = mock_mesh

          mock_prim = MagicMock()
          stage = MagicMock()
          stage.Traverse.return_value = [mock_prim]

          _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
          content = html_path.read_text(encoding="utf-8")

          # A triangle has 3 edges → 3 pairs of points → 18 floats
          assert "ansysEdgeSegs" in content
          assert "THREE.LineSegments" in content
          # 18 float values separated by commas (3 edges × 2 verts × 3 coords)
          import json, re

          m = re.search(r"new Float32Array\((\[.*?\])\)", content)
          assert m is not None
          floats = json.loads(m.group(1))
          assert len(floats) == 18
  ```

- [ ] **Step 2: Run unit tests to confirm all pass**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  .venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py -v
  ```
  Expected: all tests PASS.

- [ ] **Step 3: Create integration test file**

  Create `tests/test_usd_html_export_integration.py`:

  ```python
  # Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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
  """Integration tests for html_export — require real pxr (usd-core).

  These tests are skipped automatically when ``usd-core`` is not installed.
  Run them with: pytest tests/test_usd_html_export_integration.py -v
  """
  import sys
  from pathlib import Path
  from unittest.mock import MagicMock, patch

  import pytest

  pxr = pytest.importorskip(
      "pxr", reason="usd-core not installed; skipping integration tests"
  )

  from pxr import Gf, Usd, UsdGeom  # noqa: E402

  # The module under test may have already been imported (unit test run before this).
  # Import it fresh — since pxr is real here, _open_stage will use the real Usd.
  from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: E402
      _inject_mesh_lines,
      export_usd_to_html,
  )

  # ── Helpers ───────────────────────────────────────────────────────────────────


  def _build_triangle_stage() -> Usd.Stage:
      """Return an in-memory USD stage with one UsdGeomMesh triangle prim."""
      stage = Usd.Stage.CreateInMemory()
      mesh = UsdGeom.Mesh.Define(stage, "/TriMesh")
      stage.SetDefaultPrim(mesh.GetPrim())
      mesh.GetPointsAttr().Set([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)])
      mesh.GetFaceVertexCountsAttr().Set([3])
      mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])
      return stage


  def _minimal_viewer_html(tmp_path: Path) -> Path:
      content = (
          "<!doctype html><html><body><script type='module'>\n"
          "const binary = atob(glbBase64);\n"
          "scene.add(gltf.scene);\n"
          "</script></body></html>"
      )
      path = tmp_path / "model_viewer.html"
      path.write_text(content, encoding="utf-8")
      return path


  # ── Tests ─────────────────────────────────────────────────────────────────────


  @pytest.mark.integration
  def test_inject_mesh_lines_real_stage_triangle(tmp_path):
      """Real pxr stage with one triangle → 18 float edge segments injected."""
      import json
      import re

      stage = _build_triangle_stage()
      html_path = _minimal_viewer_html(tmp_path)

      _inject_mesh_lines(html_path, stage, "#aabbcc", 0.8)

      content = html_path.read_text(encoding="utf-8")
      assert "ansysEdgesInjected" in content
      assert "#aabbcc" in content
      assert "0.8" in content

      m = re.search(r"new Float32Array\((\[.*?\])\)", content)
      assert m is not None, "Float32Array not found in injected HTML"
      floats = json.loads(m.group(1))
      # Triangle has 3 unique edges → 3 pairs of Vec3 → 18 floats
      assert len(floats) == 18


  @pytest.mark.integration
  def test_inject_mesh_lines_real_stage_no_mesh_prims(tmp_path):
      """Stage with no mesh prims → empty segment array, marker still injected."""
      import json
      import re

      stage = Usd.Stage.CreateInMemory()
      UsdGeom.Xform.Define(stage, "/Root")  # Xform, not Mesh

      html_path = _minimal_viewer_html(tmp_path)
      _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)

      content = html_path.read_text(encoding="utf-8")
      assert "ansysEdgesInjected" in content

      m = re.search(r"new Float32Array\((\[.*?\])\)", content)
      assert m is not None
      floats = json.loads(m.group(1))
      assert floats == []


  @pytest.mark.integration
  def test_export_usd_to_html_stage_roundtrip(tmp_path):
      """Stage input → temp file written → HTML with mesh-line injection."""
      stage = _build_triangle_stage()
      html_output = tmp_path / "out_viewer.html"

      # Mock export_viewer_html so we don't need the full usdviewer C++ stack
      fake_html = _minimal_viewer_html(tmp_path)

      with patch.dict(
          sys.modules,
          {
              "ansys.tools.usdviewer.web.html_export": MagicMock(
                  export_viewer_html=MagicMock(return_value=fake_html)
              )
          },
      ):
          result = export_usd_to_html(stage, output_path=html_output)

      assert result == fake_html
      content = fake_html.read_text(encoding="utf-8")
      assert "ansysEdgesInjected" in content
      # Triangle edges injected — 18 floats
      import json
      import re

      m = re.search(r"new Float32Array\((\[.*?\])\)", content)
      assert m is not None
      floats = json.loads(m.group(1))
      assert len(floats) == 18


  @pytest.mark.integration
  def test_export_usd_to_html_file_path_input(tmp_path):
      """Real .usda file input → HTML with mesh-line injection from real stage."""
      stage = _build_triangle_stage()
      usd_path = tmp_path / "triangle.usda"
      stage.Export(str(usd_path))

      fake_html = _minimal_viewer_html(tmp_path)

      with patch.dict(
          sys.modules,
          {
              "ansys.tools.usdviewer.web.html_export": MagicMock(
                  export_viewer_html=MagicMock(return_value=fake_html)
              )
          },
      ):
          result = export_usd_to_html(usd_path)

      content = fake_html.read_text(encoding="utf-8")
      assert "ansysEdgesInjected" in content
      import json
      import re

      m = re.search(r"new Float32Array\((\[.*?\])\)", content)
      assert m is not None
      floats = json.loads(m.group(1))
      assert len(floats) == 18
  ```

- [ ] **Step 4: Run integration tests (skip if pxr not available)**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  .venv\Scripts\python.exe -m pytest tests/test_usd_html_export_integration.py -v -m integration
  ```
  Expected: either all PASS (if `usd-core` installed) or all SKIP (if not).

- [ ] **Step 5: Commit**

  ```bash
  git add tests/test_usd_html_export.py tests/test_usd_html_export_integration.py
  git commit -m "test(usd): add unit and integration tests for export_usd_to_html"
  ```

---

### Task 4: Expose `export_usd_to_html` at top level + update docs

**Files:**
- Modify: `src/ansys/tools/visualization_interface/backends/usd/__init__.py`
- Modify: `src/ansys/tools/visualization_interface/__init__.py`
- Modify: `doc/source/user_guide/usdviewer.rst`
- Modify: `tests/test_usd_html_export.py` — add top-level import test

**Interfaces:**
- Consumes: `export_usd_to_html` from `backends/usd/html_export.py` (Task 2)
- Produces: `from ansys.tools.visualization_interface import export_usd_to_html`

- [ ] **Step 1: Write a failing test for the top-level import**

  Append to the bottom of `tests/test_usd_html_export.py`:

  ```python
  # ── Top-level import ──────────────────────────────────────────────────────────


  def test_export_usd_to_html_importable_from_top_level():
      from ansys.tools.visualization_interface import export_usd_to_html as _fn

      assert callable(_fn)
  ```

- [ ] **Step 2: Run the new test to verify it fails**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  .venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py::test_export_usd_to_html_importable_from_top_level -v
  ```
  Expected: `ImportError` — `export_usd_to_html` is not yet in `__init__.py`.

- [ ] **Step 3: Update `src/ansys/tools/visualization_interface/backends/usd/__init__.py`**

  Replace the file content with:

  ```python
  # Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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

  """USD backend initialization."""

  from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: F401
      export_usd_to_html,
  )
  ```

- [ ] **Step 4: Update `src/ansys/tools/visualization_interface/__init__.py`**

  Add the import after the existing `MeshObjectPlot` import:

  ```python
  from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: F401, E402
      export_usd_to_html,
  )
  ```

  The full `__init__.py` imports block should read:

  ```python
  from ansys.tools.visualization_interface.plotter import Plotter  # noqa: F401, E402
  from ansys.tools.visualization_interface.types.edge_plot import (
      EdgePlot,
  )  # noqa: F401, E402
  from ansys.tools.visualization_interface.types.mesh_object_plot import (  # noqa: F401, E402
      MeshObjectPlot,
  )
  from ansys.tools.visualization_interface.utils.clip_plane import (
      ClipPlane,
  )  # noqa: F401, E402
  from ansys.tools.visualization_interface.utils.color import Color  # noqa: F401, E402
  from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: F401, E402
      export_usd_to_html,
  )
  ```

- [ ] **Step 5: Run all tests — expect PASS**

  ```powershell
  cd D:\repositories\ansys-tools-visualization-interface
  .venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py -v
  ```
  Expected: all tests PASS including `test_export_usd_to_html_importable_from_top_level`.

- [ ] **Step 6: Update `doc/source/user_guide/usdviewer.rst`**

  Append the following section to the existing file:

  ```rst
  USD to HTML export
  ------------------

  To convert a USD file to a self-contained HTML viewer page (backed by Three.js),
  use :func:`~ansys.tools.visualization_interface.export_usd_to_html`.  The
  generated file embeds all geometry as a base64-encoded GLB and requires only a
  CDN connection to render.

  .. code-block:: python

      from ansys.tools.visualization_interface import export_usd_to_html

      # From a file path
      html_path = export_usd_to_html("my_model.usd", "my_model_viewer.html")

      # From an in-memory pxr.Usd.Stage (no .usd file needed)
      from pxr import Usd, UsdGeom, Gf

      stage = Usd.Stage.CreateInMemory()
      mesh = UsdGeom.Mesh.Define(stage, "/Box")
      stage.SetDefaultPrim(mesh.GetPrim())
      mesh.GetPointsAttr().Set([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)])
      mesh.GetFaceVertexCountsAttr().Set([3])
      mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])

      html_path = export_usd_to_html(stage, "triangle_viewer.html")

  The optional ``show_mesh_lines``, ``line_color``, and ``line_opacity`` parameters
  control a wireframe edge overlay injected directly into the HTML:

  .. code-block:: python

      html_path = export_usd_to_html(
          "my_model.usd",
          show_mesh_lines=True,
          line_color="#00ffcc",
          line_opacity=0.7,
      )

  .. note::

      This feature requires the ``[usd]`` optional dependencies:
      ``pip install ansys-tools-visualization-interface[usd]``
  ```

- [ ] **Step 7: Commit**

  ```bash
  git add src/ansys/tools/visualization_interface/backends/usd/__init__.py \
          src/ansys/tools/visualization_interface/__init__.py \
          doc/source/user_guide/usdviewer.rst \
          tests/test_usd_html_export.py
  git commit -m "feat(usd): expose export_usd_to_html at top level and update docs"
  ```

---

## Self-Review Checklist

- [x] `export_usd_to_html(file_path)` → Task 2
- [x] `export_usd_to_html(stage)` → Task 2
- [x] `show_mesh_lines=False` skips injection → Task 2 test
- [x] `line_color` / `line_opacity` parameters → Task 2 + Task 3
- [x] `FileNotFoundError` → Task 2 test
- [x] `ValueError` for bad opacity → Task 2 test
- [x] `ImportError` for missing usdviewer → Task 2 test
- [x] All `pxr` / `usdviewer` imports lazy → enforced in implementation
- [x] `usd-core >= 24.0` in `pyproject.toml` → Task 1
- [x] Top-level `export_usd_to_html` → Task 4
- [x] Docs updated → Task 4
- [x] Integration tests (real `pxr`) → Task 3
- [x] Idempotent injection → Task 3 test
- [x] Incompatible template handled gracefully → Task 3 test
- [x] Temp file cleaned up after Stage input → Task 2 test
