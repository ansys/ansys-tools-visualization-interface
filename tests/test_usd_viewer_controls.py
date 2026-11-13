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

"""Tests for the optional viewer controls add-on (legend and frame player)."""

import base64
import inspect
import json
from pathlib import Path
import re
import sys
from unittest.mock import MagicMock

import numpy as np
import pytest

from ansys.tools.visualization_interface.backends.usd import Frames, Legend
from ansys.tools.visualization_interface.backends.usd.html_export import (
    _inject_mesh_lines,
    export_usd_to_html,
)
from ansys.tools.visualization_interface.backends.usd.viewer_controls import (
    add_viewer_controls,
)
from ansys.tools.visualization_interface.backends.usd.web.templates import (
    build_viewer_html_glb,
)

_COLORMAP = np.linspace(0.0, 1.0, 256)[:, None].repeat(3, axis=1)  # gray ramp


def _minimal_viewer_html(tmp_path: Path, name: str = "model_viewer.html") -> Path:
    """Write a minimal viewer HTML with both injection anchors."""
    content = (
        "<!doctype html><html><body><script type='module'>\n"
        "const binary = atob(glbBase64);\n"
        "scene.add(gltf.scene);\n"
        "</script></body></html>"
    )
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def _frames() -> Frames:
    """Return 2 frames x 3 vertices."""
    return Frames(np.array([[0, 1, 2], [3, 4, 5]]), times=[0, 1])


def _embedded_data(html_path: Path) -> dict:
    """Return the JSON object embedded in the page."""
    content = html_path.read_text(encoding="utf-8")
    m = re.search(r"const ansysViewerData = (.*);\n", content)
    return json.loads(m.group(1))


# Legend


def test_legend_casts_to_float():
    """Vmin and vmax are stored as floats."""
    legend = Legend(np.float32(1), 2)
    assert legend.vmin == 1.0
    assert type(legend.vmin) is float
    assert type(legend.vmax) is float


@pytest.mark.parametrize("vmin, vmax", [(1, 1), (2, 1), (0, float("nan")), (0, float("inf"))])
def test_legend_invalid_range_raises(vmin, vmax):
    """Vmin must be finite and smaller than vmax."""
    with pytest.raises(ValueError, match="vmin must be smaller"):
        Legend(vmin, vmax)


# Frames


def test_frames_stores_uint8_and_plain_times():
    """Indices become uint8; numpy times become plain Python numbers."""
    frames = Frames(np.array([[0, 255]], dtype=np.int64), times=np.array([0.5]))
    assert frames.indices.dtype == np.uint8
    assert frames.times == [0.5]
    assert type(frames.times[0]) is float
    assert frames.fps == 20.0
    assert frames.label == "Time"


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"indices": np.array([0, 1]), "times": [0]}, "2D"),
        ({"indices": np.zeros((0, 3), int), "times": []}, "non-empty"),
        ({"indices": np.array([[0.5, 1.0]]), "times": [0]}, "integers"),
        ({"indices": np.array([[0, 256]]), "times": [0]}, r"\[0, 255\]"),
        ({"indices": np.array([[-1, 0]]), "times": [0]}, r"\[0, 255\]"),
        ({"indices": np.array([[0, 1]]), "times": [0, 1]}, "one value per frame"),
        ({"indices": np.array([[0, 1]]), "times": [0], "fps": 0}, "fps"),
    ],
)
def test_frames_invalid_raises(kwargs, match):
    """Frames validates shape, dtype, range, times and fps."""
    with pytest.raises(ValueError, match=match):
        Frames(**kwargs)


# add_viewer_controls


def test_default_html_has_no_controls():
    """Without add_viewer_controls the page is the plain viewer."""
    html = build_viewer_html_glb("abc", "m.usd")
    assert "ansysViewerData" not in html
    assert "ansys-player" not in html
    assert "ansys-legend" not in html


def test_export_has_no_viewer_controls_arguments():
    """export_usd_to_html stays unchanged; controls are a separate add-on."""
    params = inspect.signature(export_usd_to_html).parameters
    assert not {"viewer_data", "legend", "frames", "colormap"} & params.keys()


def test_injects_data_and_controls(tmp_path):
    """Injection adds the data, the controls script and the marker."""
    html_path = _minimal_viewer_html(tmp_path)
    add_viewer_controls(html_path, _COLORMAP, legend=Legend(0, 1), frames=_frames())
    content = html_path.read_text(encoding="utf-8")
    assert "ansysViewerControlsInjected" in content
    assert "ansys-player" in content
    assert "ansys-legend" in content
    # Data is defined before the GLB is decoded; controls run after scene.add.
    assert content.index("ansysViewerData") < content.index("const binary = atob(glbBase64);")
    assert content.index("scene.add(gltf.scene);") < content.index("ansys-player")


def test_embedded_data_format(tmp_path):
    """The page gets the format that viewer_controls.js reads."""
    html_path = _minimal_viewer_html(tmp_path)
    frames = Frames(np.array([[0, 1, 2], [3, 4, 5]]), times=[10, 20], label="Iteration", fps=5)
    add_viewer_controls(html_path, _COLORMAP, legend=Legend(300, 400, "Temperature"), frames=frames)
    data = _embedded_data(html_path)

    assert len(data["lut"]) == 768
    assert data["lut"][:3] == [0, 0, 0]
    assert data["lut"][-3:] == [255, 255, 255]
    assert data["legend"] == {"title": "Temperature", "vmin": 300.0, "vmax": 400.0}
    assert data["frames"]["times"] == [10, 20]
    assert data["frames"]["label"] == "Iteration"
    assert data["frames"]["fps"] == 5.0
    assert base64.b64decode(data["frames"]["data"]) == bytes([0, 1, 2, 3, 4, 5])


def test_rgba_colormap_ignores_alpha(tmp_path):
    """A (256, 4) colormap, as returned by matplotlib, is accepted."""
    html_path = _minimal_viewer_html(tmp_path)
    rgba = np.hstack([_COLORMAP, np.full((256, 1), 0.5)])
    add_viewer_controls(html_path, rgba, legend=Legend(0, 1))
    assert len(_embedded_data(html_path)["lut"]) == 768


def test_legend_only_and_frames_only(tmp_path):
    """Either part can be given on its own."""
    legend_page = _minimal_viewer_html(tmp_path, "legend.html")
    add_viewer_controls(legend_page, _COLORMAP, legend=Legend(0, 1))
    assert "frames" not in _embedded_data(legend_page)

    frames_page = _minimal_viewer_html(tmp_path, "frames.html")
    add_viewer_controls(frames_page, _COLORMAP, frames=_frames())
    assert "legend" not in _embedded_data(frames_page)


def test_script_close_tag_is_escaped(tmp_path):
    """A '</script>' in a title cannot end the surrounding script tag."""
    html_path = _minimal_viewer_html(tmp_path)
    add_viewer_controls(html_path, _COLORMAP, legend=Legend(0, 1, "</script><b>x"))
    content = html_path.read_text(encoding="utf-8")
    assert content.count("</script>") == 1
    assert _embedded_data(html_path)["legend"]["title"] == "</script><b>x"


def test_idempotent(tmp_path):
    """Injecting twice gives the same output as injecting once."""
    html_path = _minimal_viewer_html(tmp_path)
    add_viewer_controls(html_path, _COLORMAP, legend=Legend(0, 1))
    first = html_path.read_text(encoding="utf-8")
    add_viewer_controls(html_path, _COLORMAP, legend=Legend(0, 1))
    assert html_path.read_text(encoding="utf-8") == first


def test_works_with_mesh_lines(tmp_path, monkeypatch):
    """Controls and the wireframe overlay can both be injected."""
    mock_pxr = MagicMock()
    monkeypatch.setitem(sys.modules, "pxr", mock_pxr)
    monkeypatch.setitem(sys.modules, "pxr.UsdGeom", mock_pxr.UsdGeom)
    html_path = _minimal_viewer_html(tmp_path)
    stage = MagicMock()
    stage.Traverse.return_value = []
    _inject_mesh_lines(html_path, stage, "#ffffff", 0.9)
    add_viewer_controls(html_path, _COLORMAP, frames=_frames())
    content = html_path.read_text(encoding="utf-8")
    assert "ansysEdgesInjected" in content
    assert "ansysViewerControlsInjected" in content


def test_template_without_anchors_raises(tmp_path):
    """A page without the anchors cannot host the controls."""
    html_path = tmp_path / "viewer.html"
    html_path.write_text("<html>no anchors</html>", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required"):
        add_viewer_controls(html_path, _COLORMAP, legend=Legend(0, 1))


def test_returns_resolved_path_and_accepts_str(tmp_path):
    """A str path is accepted and the resolved Path is returned."""
    html_path = _minimal_viewer_html(tmp_path)
    result = add_viewer_controls(str(html_path), _COLORMAP, legend=Legend(0, 1))
    assert result == html_path.resolve()


def test_missing_html_raises(tmp_path):
    """FileNotFoundError when the HTML file does not exist."""
    with pytest.raises(FileNotFoundError, match="HTML file not found"):
        add_viewer_controls(tmp_path / "ghost.html", _COLORMAP, legend=Legend(0, 1))


@pytest.mark.parametrize(
    "colormap, kwargs, error, match",
    [
        (_COLORMAP, {}, ValueError, "legend, frames, or both"),
        (_COLORMAP, {"legend": {"vmin": 0, "vmax": 1}}, TypeError, "Legend"),
        (_COLORMAP, {"frames": "x"}, TypeError, "Frames"),
        (np.zeros((10, 3)), {"legend": Legend(0, 1)}, ValueError, "shape"),
        (np.zeros((256, 2)), {"legend": Legend(0, 1)}, ValueError, "shape"),
        (np.full((256, 3), 2.0), {"legend": Legend(0, 1)}, ValueError, r"\[0, 1\]"),
        (np.full((256, 3), np.nan), {"legend": Legend(0, 1)}, ValueError, r"\[0, 1\]"),
    ],
)
def test_invalid_arguments_raise(tmp_path, colormap, kwargs, error, match):
    """Bad arguments are rejected and the HTML is left untouched."""
    html_path = _minimal_viewer_html(tmp_path)
    before = html_path.read_text(encoding="utf-8")
    with pytest.raises(error, match=match):
        add_viewer_controls(html_path, colormap, **kwargs)
    assert html_path.read_text(encoding="utf-8") == before


def test_add_viewer_controls_importable_from_top_level():
    """add_viewer_controls is accessible directly from the package root."""
    from ansys.tools.visualization_interface import add_viewer_controls as _fn

    assert _fn is add_viewer_controls
