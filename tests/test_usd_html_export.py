# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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
from pathlib import Path
import sys
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
sys.modules.setdefault("ansys.tools.usdviewer.web.html_export", _mock_usdviewer_html_mod)

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
    """Tests for _is_usd_stage duck-typing function."""

    def test_stage_like_object_returns_true(self):
        """Test that an object with Stage methods returns True."""
        obj = MagicMock(spec=["Traverse", "GetPrimAtPath", "Export"])
        assert _is_usd_stage(obj) is True

    def test_string_returns_false(self):
        """Test that a string returns False."""
        assert _is_usd_stage("model.usd") is False

    def test_path_returns_false(self):
        """Test that a Path object returns False."""
        assert _is_usd_stage(Path("model.usd")) is False

    def test_none_returns_false(self):
        """Test that None returns False."""
        assert _is_usd_stage(None) is False

    def test_object_missing_one_attr_returns_false(self):
        """Test that an object missing one required attribute returns False."""
        obj = MagicMock(spec=["Traverse", "GetPrimAtPath"])  # no Export
        assert _is_usd_stage(obj) is False


class TestStageToTempUsd:
    """Tests for _stage_to_temp_usd temporary file creation."""

    def test_calls_stage_export_and_returns_usda_path(self):
        """Test that stage.Export is called and returns a .usda path."""
        stage = MagicMock()
        result = _stage_to_temp_usd(stage)
        assert result.suffix == ".usda"
        stage.Export.assert_called_once_with(str(result))
        result.unlink(missing_ok=True)


class TestExportUsdToHtml:
    """Tests for export_usd_to_html main function."""

    @pytest.fixture(autouse=True)
    def setup_mock_export(self, tmp_path):
        """Set up mock for export_viewer_html before each test."""
        self._html = _minimal_viewer_html(tmp_path)
        _mock_usdviewer_html_mod.export_viewer_html.return_value = self._html
        _mock_usdviewer_html_mod.export_viewer_html.reset_mock()

    def test_file_path_input_returns_html_path(self, tmp_path):
        """Test that a USD file path input returns the HTML path."""
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
        """Test that a USD file path as string input returns the HTML path."""
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
        """Test that a Stage input creates temp file and returns HTML."""
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
        """Test that temporary file is cleaned up after stage processing."""
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
        """Test that show_mesh_lines=False skips mesh line injection."""
        usd_file = tmp_path / "model.usda"
        usd_file.write_text("#usda 1.0\n", encoding="utf-8")

        with patch(
            "ansys.tools.visualization_interface.backends.usd.html_export._inject_mesh_lines"
        ) as mock_inject:
            export_usd_to_html(usd_file, show_mesh_lines=False)

        mock_inject.assert_not_called()

    def test_file_not_found_raises(self, tmp_path):
        """Test that FileNotFoundError is raised for non-existent file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            export_usd_to_html(tmp_path / "nonexistent.usd")

    def test_invalid_opacity_above_one_raises(self, tmp_path):
        """Test that ValueError is raised for opacity > 1.0."""
        usd_file = tmp_path / "model.usda"
        usd_file.write_text("#usda 1.0\n", encoding="utf-8")
        with pytest.raises(ValueError, match="line_opacity"):
            export_usd_to_html(usd_file, line_opacity=1.5)

    def test_invalid_opacity_below_zero_raises(self, tmp_path):
        """Test that ValueError is raised for opacity < 0.0."""
        usd_file = tmp_path / "model.usda"
        usd_file.write_text("#usda 1.0\n", encoding="utf-8")
        with pytest.raises(ValueError, match="line_opacity"):
            export_usd_to_html(usd_file, line_opacity=-0.1)

    def test_import_error_when_usdviewer_missing(self, tmp_path):
        """Test that ImportError is raised when usdviewer is missing."""
        usd_file = tmp_path / "model.usda"
        usd_file.write_text("#usda 1.0\n", encoding="utf-8")
        with patch.dict(sys.modules, {"ansys.tools.usdviewer.web.html_export": None}):
            with pytest.raises(ImportError, match="ansys-tools-usdviewer"):
                export_usd_to_html(usd_file)


class TestInjectMeshLines:
    """Tests for _inject_mesh_lines function."""

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


def test_export_usd_to_html_importable_from_top_level():
    """export_usd_to_html is accessible directly from the package root."""
    from ansys.tools.visualization_interface import export_usd_to_html as _fn

    assert callable(_fn)
