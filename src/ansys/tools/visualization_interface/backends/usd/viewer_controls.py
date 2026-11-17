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

"""Optional viewer controls for exported HTML pages.

Adds a color legend and a frame player (Play/Pause button and time slider)
to a page written by :func:`~ansys.tools.visualization_interface.export_usd_to_html`.
The browser code lives in ``web/viewer_controls.js``.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

import numpy as np

from ansys.tools.visualization_interface.backends.usd.html_export import (
    _CONFIG_ANCHOR,
    _SCENE_ANCHOR,
)
from ansys.tools.visualization_interface.backends.usd.web.templates import validate_template

_CONTROLS_MARKER = "// ansysViewerControlsInjected"
_CONTROLS_JS_FILE = Path(__file__).parent / "web" / "viewer_controls.js"
_COLORMAP_SIZE = 256


@dataclass
class Legend:
    """Color legend shown in the top-right corner of the viewer.

    .. warning::

        Experimental. This class may change in a future release.

    Parameters
    ----------
    vmin : float
        Value at the start of the colormap.
    vmax : float
        Value at the end of the colormap. Must be greater than ``vmin``.
    title : str, default: ""
        Title shown above the color bar, for example ``"Temperature [K]"``.
    """

    vmin: float
    vmax: float
    title: str = ""

    def __post_init__(self):
        """Validate the value range."""
        self.vmin = float(self.vmin)
        self.vmax = float(self.vmax)
        if not np.isfinite([self.vmin, self.vmax]).all() or not self.vmin < self.vmax:
            raise ValueError(f"Legend.vmin must be smaller than Legend.vmax, got {self.vmin} and {self.vmax}.")


@dataclass
class Frames:
    """Per-frame vertex colors for the Play/Pause button and time slider.

    .. warning::

        Experimental. This class may change in a future release.

    Parameters
    ----------
    indices : numpy.ndarray
        Integer array of shape ``(n_frames, n_vertices)`` with values in
        [0, 255]. Each value selects a row of the colormap. ``n_vertices`` is
        the number of vertices in the exported GLB, which has one vertex per
        triangle corner. For a triangle mesh, reorder per-point values with
        ``values[:, face_vertex_indices]``.
    times : Sequence[float]
        One value per frame, shown next to ``label`` on the slider.
    label : str, default: "Time"
        Text shown before the frame value, for example ``"Iteration"``.
    fps : float, default: 20
        Playback speed in frames per second.
    """

    indices: np.ndarray
    times: Sequence[float]
    label: str = "Time"
    fps: float = 20

    def __post_init__(self):
        """Validate shapes and values."""
        indices = np.asarray(self.indices)
        if indices.ndim != 2 or indices.size == 0:
            raise ValueError(
                f"Frames.indices must be a non-empty 2D array (n_frames, n_vertices), got shape {indices.shape}."
            )
        if not np.issubdtype(indices.dtype, np.integer):
            raise ValueError(f"Frames.indices must contain integers, got dtype {indices.dtype}.")
        if indices.min() < 0 or indices.max() >= _COLORMAP_SIZE:
            raise ValueError(f"Frames.indices values must be in [0, {_COLORMAP_SIZE - 1}].")
        self.indices = indices.astype(np.uint8)

        self.times = [t.item() if isinstance(t, np.generic) else t for t in self.times]
        if len(self.times) != indices.shape[0]:
            raise ValueError(
                f"Frames.times must have one value per frame: got {len(self.times)} "
                f"times for {indices.shape[0]} frames."
            )
        self.fps = float(self.fps)
        if not self.fps > 0:
            raise ValueError(f"Frames.fps must be positive, got {self.fps}.")


def _colormap_to_lut(colormap: np.ndarray) -> list[int]:
    """Convert a ``(256, 3)`` or ``(256, 4)`` float colormap to 768 sRGB bytes."""
    cmap = np.asarray(colormap, dtype=float)
    if cmap.ndim != 2 or cmap.shape[0] != _COLORMAP_SIZE or cmap.shape[1] not in (3, 4):
        raise ValueError(f"colormap must have shape ({_COLORMAP_SIZE}, 3) or ({_COLORMAP_SIZE}, 4), got {cmap.shape}.")
    rgb = cmap[:, :3]
    if not np.isfinite(rgb).all() or rgb.min() < 0.0 or rgb.max() > 1.0:
        raise ValueError("colormap values must be in [0, 1].")
    return np.rint(rgb * 255).astype(int).ravel().tolist()


def add_viewer_controls(
    html_path: "str | Path",
    colormap: np.ndarray,
    *,
    legend: Legend | None = None,
    frames: Frames | None = None,
) -> Path:
    """Add a color legend and a frame player to an exported HTML viewer.

    Call this on a page written by
    :func:`~ansys.tools.visualization_interface.export_usd_to_html`. Without
    this call the page shows the model without a slider or a legend. The
    time slider changes the mesh colors from one frame to the next. The mesh
    shape is the same in every frame.

    .. warning::

        Experimental. This function may change in a future release.

    Parameters
    ----------
    html_path : str | Path
        HTML file written by
        :func:`~ansys.tools.visualization_interface.export_usd_to_html`. It
        must contain the anchors ``const binary = atob(glbBase64);`` and
        ``scene.add(gltf.scene);``, as the built-in template does.
    colormap : numpy.ndarray
        Array of shape ``(256, 3)`` with sRGB colors in [0, 1]. A
        ``(256, 4)`` RGBA array is also accepted and alpha is ignored, so
        ``matplotlib.colormaps["coolwarm"](numpy.linspace(0, 1, 256))`` works.
    legend : Legend | None, default: None
        Color legend to show.
    frames : Frames | None, default: None
        Per-frame colors for the Play/Pause button and time slider.

    Returns
    -------
    pathlib.Path
        Absolute path to the updated HTML file.

    Raises
    ------
    FileNotFoundError
        If ``html_path`` does not exist.
    TypeError
        If ``legend`` or ``frames`` has the wrong type.
    ValueError
        If neither ``legend`` nor ``frames`` is given, ``colormap`` has the
        wrong shape or values, or the page is missing the anchors.
    """
    if legend is None and frames is None:
        raise ValueError("Give a legend, frames, or both.")
    if legend is not None and not isinstance(legend, Legend):
        raise TypeError(f"legend must be a Legend, got {type(legend).__name__}.")
    if frames is not None and not isinstance(frames, Frames):
        raise TypeError(f"frames must be a Frames, got {type(frames).__name__}.")

    # Internal format read by web/viewer_controls.js.
    data: dict = {"lut": _colormap_to_lut(colormap)}
    if legend is not None:
        data["legend"] = {"title": legend.title, "vmin": legend.vmin, "vmax": legend.vmax}
    if frames is not None:
        data["frames"] = {
            "data": base64.b64encode(frames.indices.tobytes()).decode("ascii"),
            "times": list(frames.times),
            "label": frames.label,
            "fps": frames.fps,
        }

    html_path = Path(html_path).expanduser().resolve()
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    html_text = html_path.read_text(encoding="utf-8")
    if _CONTROLS_MARKER in html_text:
        return html_path  # idempotent

    validate_template(html_text, [_CONFIG_ANCHOR, _SCENE_ANCHOR])

    # Escape "</" so the data cannot close the surrounding <script> tag.
    data_json = json.dumps(data, separators=(",", ":")).replace("</", r"<\/")
    config_block = f"      const ansysViewerData = {data_json};\n      {_CONTROLS_MARKER}\n\n      "
    html_text = html_text.replace(_CONFIG_ANCHOR, config_block + _CONFIG_ANCHOR, 1)

    controls_js = _CONTROLS_JS_FILE.read_text(encoding="utf-8").rstrip()
    html_text = html_text.replace(_SCENE_ANCHOR, f"{_SCENE_ANCHOR}\n{controls_js}", 1)
    html_path.write_text(html_text, encoding="utf-8")
    return html_path
