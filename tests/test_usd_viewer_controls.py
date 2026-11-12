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

import pytest

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


def _viewer_data(**overrides) -> dict:
    """Return a valid viewer_data dict: 2 frames x 3 vertices plus a legend."""
    data = {
        "lut": [0, 0, 0] * 256,
        "legend": {"title": "T", "vmin": 0.0, "vmax": 1.0},
        "frames": {
            "data": base64.b64encode(bytes([0, 1, 2, 3, 4, 5])).decode("ascii"),
            "times": [0, 1],
        },
    }
    data.update(overrides)
    return data


def test_default_html_has_no_controls():
    """Without add_viewer_controls the page is the plain viewer."""
    html = build_viewer_html_glb("abc", "m.usd")
    assert "ansysViewerData" not in html
    assert "ansys-player" not in html
    assert "ansys-legend" not in html


def test_export_has_no_viewer_data_argument():
    """export_usd_to_html stays unchanged; controls are a separate add-on."""
    assert "viewer_data" not in inspect.signature(export_usd_to_html).parameters


def test_injects_data_and_controls(tmp_path):
    """Injection adds the data, the controls script and the marker."""
    html_path = _minimal_viewer_html(tmp_path)
    add_viewer_controls(html_path, _viewer_data())
    content = html_path.read_text(encoding="utf-8")
    assert "const ansysViewerData = " in content
    assert "ansysViewerControlsInjected" in content
    assert "ansys-player" in content
    assert "ansys-legend" in content
    # Data is defined before the GLB is decoded; controls run after scene.add.
    assert content.index("ansysViewerData") < content.index("const binary = atob(glbBase64);")
    assert content.index("scene.add(gltf.scene);") < content.index("ansys-player")


def test_injected_json_round_trips(tmp_path):
    """The embedded JSON parses back to the input dict."""
    html_path = _minimal_viewer_html(tmp_path)
    data = _viewer_data()
    add_viewer_controls(html_path, data)
    content = html_path.read_text(encoding="utf-8")
    m = re.search(r"const ansysViewerData = (.*);\n", content)
    assert json.loads(m.group(1)) == data


def test_script_close_tag_is_escaped(tmp_path):
    """A '</script>' in a title cannot end the surrounding script tag."""
    html_path = _minimal_viewer_html(tmp_path)
    data = _viewer_data(legend={"title": "</script><b>x", "vmin": 0, "vmax": 1})
    add_viewer_controls(html_path, data)
    content = html_path.read_text(encoding="utf-8")
    assert content.count("</script>") == 1


def test_idempotent(tmp_path):
    """Injecting twice gives the same output as injecting once."""
    html_path = _minimal_viewer_html(tmp_path)
    add_viewer_controls(html_path, _viewer_data())
    first = html_path.read_text(encoding="utf-8")
    add_viewer_controls(html_path, _viewer_data())
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
    add_viewer_controls(html_path, _viewer_data())
    content = html_path.read_text(encoding="utf-8")
    assert "ansysEdgesInjected" in content
    assert "ansysViewerControlsInjected" in content


def test_template_without_anchors_raises(tmp_path):
    """A page without the anchors cannot host the controls."""
    html_path = tmp_path / "viewer.html"
    html_path.write_text("<html>no anchors</html>", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required"):
        add_viewer_controls(html_path, _viewer_data())


def test_returns_resolved_path_and_accepts_str(tmp_path):
    """A str path is accepted and the resolved Path is returned."""
    html_path = _minimal_viewer_html(tmp_path)
    assert add_viewer_controls(str(html_path), _viewer_data()) == html_path.resolve()


def test_missing_html_raises(tmp_path):
    """FileNotFoundError when the HTML file does not exist."""
    with pytest.raises(FileNotFoundError, match="HTML file not found"):
        add_viewer_controls(tmp_path / "ghost.html", _viewer_data())


def test_legend_only_is_valid(tmp_path):
    """viewer_data with only a legend is accepted."""
    html_path = _minimal_viewer_html(tmp_path)
    data = _viewer_data()
    del data["frames"]
    add_viewer_controls(html_path, data)
    assert "ansysViewerData" in html_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "bad, match",
    [
        ("nope", "must be a dict"),
        ({"lut": [0] * 768}, "'legend', 'frames'"),
        (_viewer_data(lut=[0] * 10), "lut"),
        (_viewer_data(lut=[300] * 768), "lut"),
        (_viewer_data(legend={"title": "T"}), "vmin"),
        (_viewer_data(frames={"times": [0]}), "'data' and 'times'"),
        (_viewer_data(frames={"data": "AAAA", "times": []}), "non-empty"),
        (_viewer_data(frames={"data": "not base64!", "times": [0]}), "base64"),
        (_viewer_data(frames={"data": "AAAA", "times": [0, 1]}), "same number"),
        (_viewer_data(frames={"data": "AAAA", "times": [0], "fps": 0}), "fps"),
    ],
)
def test_invalid_viewer_data_raises(tmp_path, bad, match):
    """Malformed viewer_data is rejected and the HTML is left untouched."""
    html_path = _minimal_viewer_html(tmp_path)
    before = html_path.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        add_viewer_controls(html_path, bad)
    assert html_path.read_text(encoding="utf-8") == before


def test_add_viewer_controls_importable_from_top_level():
    """add_viewer_controls is accessible directly from the package root."""
    from ansys.tools.visualization_interface import add_viewer_controls as _fn

    assert _fn is add_viewer_controls
