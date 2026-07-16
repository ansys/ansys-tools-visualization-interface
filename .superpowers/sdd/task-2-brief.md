# Task 2 Brief: Create `html_export.py` with core `export_usd_to_html` + unit tests

## Task from Plan

**Files:**
- Create: `src/ansys/tools/visualization_interface/backends/usd/html_export.py`
- Create: `tests/test_usd_html_export.py`

**Interfaces produced** (later tasks depend on these exact names/signatures):
- `export_usd_to_html(source, output_path=None, *, show_mesh_lines=True, line_color="#ffffff", line_opacity=0.9) -> Path`
- `_is_usd_stage(obj) -> bool`
- `_stage_to_temp_usd(stage) -> Path`
- `_open_stage(usd_path: Path) -> object`
- `_inject_mesh_lines(html_path: Path, stage, line_color: str, line_opacity: float) -> None`

---

## TDD Workflow (REQUIRED)

You MUST follow this cycle for each test:

1. **RED** — Write the test. Run it. Confirm it FAILS with a clear reason (ImportError or AttributeError because the module/function doesn't exist yet). Record the command and the relevant failure output.
2. **GREEN** — Write the minimal implementation to make it pass. Run the test again. Confirm PASS.
3. **Commit** only after all tests pass.

Your report MUST include TDD evidence: the RED command + failing output snippet, and the GREEN command + passing output.

---

## Implementation

### `src/ansys/tools/visualization_interface/backends/usd/html_export.py`

Create with this exact content (license header will be added by pre-commit):

```python
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

### `tests/test_usd_html_export.py`

Create with this exact content:

```python
"""Unit tests for backends/usd/html_export.py — all heavy deps mocked."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Mock pxr and ansys-tools-usdviewer before importing the module under test ──
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


class TestStageToTempUsd:
    def test_calls_stage_export_and_returns_usda_path(self):
        stage = MagicMock()
        result = _stage_to_temp_usd(stage)
        assert result.suffix == ".usda"
        stage.Export.assert_called_once_with(str(result))
        result.unlink(missing_ok=True)


class TestExportUsdToHtml:
    @pytest.fixture(autouse=True)
    def setup_mock_export(self, tmp_path):
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

---

## TDD Steps

**RED phase:** Create `tests/test_usd_html_export.py` with the test code above. Then run:

```powershell
cd D:\repositories\ansys-tools-visualization-interface
.venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py -v 2>&1 | Select-Object -First 30
```

Expected failure: `ImportError` — module `ansys.tools.visualization_interface.backends.usd.html_export` doesn't exist yet. Record this output.

**GREEN phase:** Create `src/ansys/tools/visualization_interface/backends/usd/html_export.py` with the implementation above. Then run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_usd_html_export.py -v
```

Expected: all tests PASS.

## Commit

```bash
git add src/ansys/tools/visualization_interface/backends/usd/html_export.py tests/test_usd_html_export.py
git commit -m "feat(usd): add export_usd_to_html utility"
```

If pre-commit auto-fixes files (license headers), run `git add` and `git commit` a second time with the same message.

## Global Constraints

- Python >= 3.10, < 4
- License header on all new `.py` files (pre-commit adds it automatically)
- `pxr` and `ansys.tools.usdviewer` imports MUST be lazy (inside function bodies only — never at module level)
- HTML injection anchors: config anchor = `const binary = atob(glbBase64);`, scene anchor = `scene.add(gltf.scene);`, marker = `// ansysEdgesInjected`
- Ruff is the linter/formatter — run `ruff check --fix` and `ruff format` if pre-commit fails on ruff
