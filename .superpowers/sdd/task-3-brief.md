# Task 3 Brief: Add `_inject_mesh_lines` unit tests + integration test file

## Task from Plan

**Files:**
- Modify: `tests/test_usd_html_export.py` — append `TestInjectMeshLines` class
- Create: `tests/test_usd_html_export_integration.py` — integration tests guarded by `pytest.importorskip`

**Interfaces consumed** (already implemented in Task 2):
- `_inject_mesh_lines(html_path: Path, stage, line_color: str, line_opacity: float) -> None`
- Module-level mocks in `tests/test_usd_html_export.py`: `_mock_usd_geom` (mock for `pxr.UsdGeom`)

---

## TDD Workflow (REQUIRED)

For `TestInjectMeshLines`:
1. **RED** — Append the test class to `tests/test_usd_html_export.py`. Run just those new tests:
   ```
   pytest tests/test_usd_html_export.py::TestInjectMeshLines -v
   ```
   They must FAIL (the class doesn't exist yet in the test file, or some tests fail if implementation has gaps). Record failing output.
2. **GREEN** — The `_inject_mesh_lines` implementation already exists in `html_export.py` from Task 2. After adding the tests, all should pass. Run again and confirm GREEN.
3. For the integration test file: write it, run with `pytest.importorskip` guards (they will SKIP if `pxr` not installed, which is the expected RED for CI).

Your report MUST include TDD evidence.

---

## Tests to Add

### Append to `tests/test_usd_html_export.py` (after `TestExportUsdToHtml`)

```python
class TestInjectMeshLines:
    def _html_with_anchors(self, tmp_path: Path) -> Path:
        """Write a minimal viewer HTML with both injection anchors."""
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
        """Injection adds the idempotency marker to the HTML."""
        html_path = self._html_with_anchors(tmp_path)
        stage = MagicMock()
        stage.Traverse.return_value = []
        _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
        assert "ansysEdgesInjected" in html_path.read_text(encoding="utf-8")

    def test_injects_line_color(self, tmp_path):
        """Injection embeds the requested line color."""
        html_path = self._html_with_anchors(tmp_path)
        stage = MagicMock()
        stage.Traverse.return_value = []
        _inject_mesh_lines(html_path, stage, "#ff0000", 0.5)
        content = html_path.read_text(encoding="utf-8")
        assert "#ff0000" in content
        assert "0.5" in content

    def test_idempotent(self, tmp_path):
        """Calling inject twice produces the same output as calling it once."""
        html_path = self._html_with_anchors(tmp_path)
        stage = MagicMock()
        stage.Traverse.return_value = []
        _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
        first = html_path.read_text(encoding="utf-8")
        _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
        second = html_path.read_text(encoding="utf-8")
        assert first == second

    def test_skips_incompatible_template(self, tmp_path):
        """HTML without injection anchors is left untouched."""
        html_path = tmp_path / "viewer.html"
        original = "<html>no anchors here</html>"
        html_path.write_text(original, encoding="utf-8")
        stage = MagicMock()
        stage.Traverse.return_value = []
        _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
        assert html_path.read_text(encoding="utf-8") == original

    def test_no_mesh_prims_produces_empty_segments(self, tmp_path):
        """Stage with no mesh prims injects an empty Float32Array."""
        html_path = self._html_with_anchors(tmp_path)
        # One prim that is NOT a mesh (UsdGeom.Mesh returns falsy)
        mock_prim = MagicMock()
        non_mesh = MagicMock()
        non_mesh.__bool__ = lambda self: False
        _mock_usd_geom.Mesh.return_value = non_mesh
        stage = MagicMock()
        stage.Traverse.return_value = [mock_prim]
        _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
        content = html_path.read_text(encoding="utf-8")
        assert "ansysEdgesInjected" in content
        assert "Float32Array([])" in content

    def test_with_triangle_prim_injects_eighteen_floats(self, tmp_path):
        """One triangle prim produces exactly 18 floats (3 edges x 2 verts x 3 coords)."""
        import json
        import re

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

        stage = MagicMock()
        stage.Traverse.return_value = [MagicMock()]

        _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
        content = html_path.read_text(encoding="utf-8")

        assert "ansysEdgeSegs" in content
        assert "THREE.LineSegments" in content

        m = re.search(r"new Float32Array\((\[.*?\])\)", content)
        assert m is not None, "Float32Array not found in injected HTML"
        floats = json.loads(m.group(1))
        assert len(floats) == 18
```

### Create `tests/test_usd_html_export_integration.py`

```python
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

from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: E402
    _inject_mesh_lines,
    export_usd_to_html,
)


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


@pytest.mark.integration
def test_inject_mesh_lines_real_stage_triangle(tmp_path):
    """Real pxr stage with one triangle -> 18 float edge segments injected."""
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
    assert len(floats) == 18


@pytest.mark.integration
def test_inject_mesh_lines_real_stage_no_mesh_prims(tmp_path):
    """Stage with no mesh prims -> empty segment array, marker still injected."""
    import json
    import re

    stage = Usd.Stage.CreateInMemory()
    UsdGeom.Xform.Define(stage, "/Root")

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
    """Stage input -> temp file written -> HTML with mesh-line injection."""
    stage = _build_triangle_stage()
    fake_html = _minimal_viewer_html(tmp_path)

    with patch.dict(
        sys.modules,
        {
            "ansys.tools.usdviewer.web.html_export": MagicMock(
                export_viewer_html=MagicMock(return_value=fake_html)
            )
        },
    ):
        result = export_usd_to_html(stage)

    assert result == fake_html
    content = fake_html.read_text(encoding="utf-8")
    assert "ansysEdgesInjected" in content

    import json
    import re

    m = re.search(r"new Float32Array\((\[.*?\])\)", content)
    assert m is not None
    floats = json.loads(m.group(1))
    assert len(floats) == 18


@pytest.mark.integration
def test_export_usd_to_html_file_path_input(tmp_path):
    """Real .usda file input -> HTML with mesh-line injection from real stage."""
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

---

## Commit

```bash
git add tests/test_usd_html_export.py tests/test_usd_html_export_integration.py
git commit -m "test(usd): add inject_mesh_lines unit tests and integration test file"
```

## Global Constraints

- Python >= 3.10, < 4
- License header on all new `.py` files (pre-commit adds automatically)
- `pxr` and `ansys.tools.usdviewer` imports MUST be lazy in the implementation (already done in Task 2)
- Integration tests use `pytest.importorskip("pxr")` at module level — they skip automatically when `usd-core` is not installed
- Integration tests are marked `@pytest.mark.integration`
- Ruff is the linter/formatter
