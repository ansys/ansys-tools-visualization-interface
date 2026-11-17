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


def _build_transformed_stage(up_axis: str, scale=(100, 100, 100)) -> Usd.Stage:
    """Return a stage with a triangle under a translated and scaled parent Xform."""
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, up_axis)
    parent = UsdGeom.Xform.Define(stage, "/World")
    parent.AddTranslateOp().Set(Gf.Vec3d(10, 0, 0))
    parent.AddScaleOp().Set(Gf.Vec3f(*scale))
    mesh = UsdGeom.Mesh.Define(stage, "/World/Tri")
    mesh.GetPointsAttr().Set([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
    mesh.GetFaceVertexCountsAttr().Set([3])
    mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])
    return stage


def _glb_triangle(stage: Usd.Stage, tmp_path: Path) -> tuple[list, list]:
    """Convert *stage* to GLB and return the first primitive's positions and indices."""
    import numpy as np
    import pygltflib

    from ansys.tools.visualization_interface.backends.usd.web.glb import convert_usd_to_glb

    usd_path = tmp_path / "stage.usda"
    stage.Export(str(usd_path))
    gltf = pygltflib.GLTF2.load_from_bytes(convert_usd_to_glb(usd_path))
    blob = gltf.binary_blob()

    def _read(accessor_index, dtype):
        view = gltf.bufferViews[gltf.accessors[accessor_index].bufferView]
        return np.frombuffer(blob[view.byteOffset : view.byteOffset + view.byteLength], dtype)

    primitive = gltf.meshes[0].primitives[0]
    positions = _read(primitive.attributes.POSITION, np.float32).reshape(-1, 3).round(4).tolist()
    indices = _read(primitive.indices, np.uint32).tolist()
    return positions, indices


@pytest.mark.integration
def test_glb_applies_parent_transforms(tmp_path):
    """Parent translate and scale are baked into the GLB positions (#639)."""
    positions, indices = _glb_triangle(_build_transformed_stage(UsdGeom.Tokens.y), tmp_path)
    assert positions == [[10, 0, 0], [110, 0, 0], [10, 100, 0]]
    assert indices == [0, 1, 2]


@pytest.mark.integration
def test_glb_z_up_stage_is_rotated_to_y_up(tmp_path):
    """Z-up stages are rotated so USD +Z maps to Three.js +Y (#639)."""
    positions, _ = _glb_triangle(_build_transformed_stage(UsdGeom.Tokens.z), tmp_path)
    assert positions == [[10, 0, 0], [110, 0, 0], [10, 0, -100]]


@pytest.mark.integration
def test_glb_mirrored_transform_keeps_winding(tmp_path):
    """A negative scale reverses triangle winding so faces stay front-facing."""
    stage = _build_transformed_stage(UsdGeom.Tokens.y, scale=(-1, 1, 1))
    positions, indices = _glb_triangle(stage, tmp_path)
    assert positions == [[10, 0, 0], [9, 0, 0], [10, 1, 0]]
    assert indices == [0, 2, 1]


@pytest.mark.integration
def test_inject_mesh_lines_uses_world_space(tmp_path):
    """Edge overlay uses the same world-space points as the GLB."""
    import json
    import re

    html_path = _minimal_viewer_html(tmp_path)
    _inject_mesh_lines(html_path, _build_transformed_stage(UsdGeom.Tokens.z), "#ffffff", 0.9)
    match = re.search(r"new Float32Array\((\[.*?\])\)", html_path.read_text(encoding="utf-8"))
    points = {tuple(p) for p in zip(*[iter(json.loads(match.group(1)))] * 3)}
    assert points == {(10, 0, 0), (110, 0, 0), (10, 0, -100)}
