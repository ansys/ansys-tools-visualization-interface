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

"""Integration tests for html_export — require real pxr (usd-core).

These tests are skipped automatically when ``usd-core`` is not installed.
Run them with: pytest tests/test_usd_html_export_integration.py -v
"""
from pathlib import Path

import pytest

pxr = pytest.importorskip("pxr", reason="usd-core not installed; skipping integration tests")

pytest.importorskip(
    "pygltflib", reason="pygltflib not installed; skipping integration tests"
)

from pxr import Gf, Usd, UsdGeom  # noqa: E402

# Guard against the mock-pxr injected by unit tests leaking into this module.
if not hasattr(Usd.Stage, "CreateInMemory"):
    pytest.skip("Real usd-core not available (mock detected)", allow_module_level=True)

from ansys.tools.visualization_interface.backends.usd.html_export import (  # noqa: E402
    _inject_mesh_lines,
    export_usd_to_html,
)


def _build_triangle_stage() -> Usd.Stage:
    """Return an in-memory USD stage with one UsdGeomMesh triangle prim."""
    stage = Usd.Stage.CreateInMemory()
    mesh = UsdGeom.Mesh.Define(stage, "/TriMesh")
    stage.SetDefaultPrim(mesh.GetPrim())
    mesh.GetPointsAttr().Set(
        [Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)]
    )
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

    result = export_usd_to_html(stage)

    assert result.exists()
    content = result.read_text(encoding="utf-8")
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

    result = export_usd_to_html(usd_path)

    assert result.exists()
    content = result.read_text(encoding="utf-8")
    assert "ansysEdgesInjected" in content

    import json
    import re

    m = re.search(r"new Float32Array\((\[.*?\])\)", content)
    assert m is not None
    floats = json.loads(m.group(1))
    assert len(floats) == 18
