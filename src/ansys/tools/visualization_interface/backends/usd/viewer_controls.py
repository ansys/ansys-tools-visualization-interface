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

"""Optional viewer controls for exported HTML pages.

Adds a color legend and a frame player (Play/Pause button and time slider)
to a page written by :func:`~ansys.tools.visualization_interface.export_usd_to_html`.
The browser code lives in ``web/viewer_controls.js``.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

from ansys.tools.visualization_interface.backends.usd.html_export import (
    _CONFIG_ANCHOR,
    _SCENE_ANCHOR,
)
from ansys.tools.visualization_interface.backends.usd.web.templates import validate_template

_CONTROLS_MARKER = "// ansysViewerControlsInjected"
_CONTROLS_JS_FILE = Path(__file__).parent / "web" / "viewer_controls.js"


def _validate_viewer_data(viewer_data: object) -> None:
    """Raise ``ValueError`` if *viewer_data* does not follow the documented schema."""
    if not isinstance(viewer_data, dict):
        raise ValueError("viewer_data must be a dict.")
    legend = viewer_data.get("legend")
    frames = viewer_data.get("frames")
    if legend is None and frames is None:
        raise ValueError("viewer_data must contain 'legend', 'frames', or both.")

    lut = viewer_data.get("lut")
    if (
        not isinstance(lut, (list, tuple))
        or len(lut) != 768
        or not all(isinstance(v, int) and 0 <= v <= 255 for v in lut)
    ):
        raise ValueError(
            "viewer_data['lut'] must be a flat list of 768 ints in [0, 255] "
            "(256 RGB colors)."
        )

    if legend is not None:
        if not isinstance(legend, dict) or not {"vmin", "vmax"} <= legend.keys():
            raise ValueError(
                "viewer_data['legend'] must be a dict with 'vmin' and 'vmax'."
            )

    if frames is not None:
        if not isinstance(frames, dict) or not {"data", "times"} <= frames.keys():
            raise ValueError(
                "viewer_data['frames'] must be a dict with 'data' and 'times'."
            )
        times = frames["times"]
        if not isinstance(times, (list, tuple)) or not times:
            raise ValueError("viewer_data['frames']['times'] must be a non-empty list.")
        try:
            n_bytes = len(base64.b64decode(frames["data"], validate=True))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "viewer_data['frames']['data'] must be a base64 string."
            ) from exc
        if n_bytes == 0 or n_bytes % len(times):
            raise ValueError(
                "viewer_data['frames']['data'] must hold the same number of "
                "bytes for every frame in 'times'."
            )
        fps = frames.get("fps", 20)
        if not isinstance(fps, (int, float)) or fps <= 0:
            raise ValueError("viewer_data['frames']['fps'] must be a positive number.")


def add_viewer_controls(html_path: "str | Path", viewer_data: dict) -> Path:
    """Add a color legend and a frame player to an exported HTML viewer.

    This is an optional add-on for pages written by
    :func:`~ansys.tools.visualization_interface.export_usd_to_html`. The page stays a plain viewer unless this
    function is called. It adds a Play/Pause button and a time slider that
    change the mesh vertex colors frame by frame, and a color legend.

    .. warning::

        Experimental. The ``viewer_data`` schema may change in a future release.

    Parameters
    ----------
    html_path : str | Path
        HTML file written by
        :func:`~ansys.tools.visualization_interface.export_usd_to_html`. It must contain the
        anchors ``const binary = atob(glbBase64);`` and
        ``scene.add(gltf.scene);``, as the built-in template does.
    viewer_data : dict
        Data for the controls:

        - ``"lut"`` (required): flat list of 768 ints in [0, 255], a 256-entry
          sRGB color lookup table.
        - ``"legend"`` (optional): ``{"title": str, "vmin": float, "vmax": float}``.
        - ``"frames"`` (optional): ``{"data": str, "times": list, "label": str,
          "fps": float}``. ``data`` is base64 of ``uint8`` LUT indices, one per
          GLB vertex per frame, frame after frame. ``label`` defaults to
          ``"Time"`` and ``fps`` to 20.

        At least one of ``"legend"`` or ``"frames"`` must be given.

    Returns
    -------
    pathlib.Path
        Absolute path to the updated HTML file.

    Raises
    ------
    FileNotFoundError
        If ``html_path`` does not exist.
    ValueError
        If ``viewer_data`` does not follow the schema or the page is missing
        the anchors.
    """
    _validate_viewer_data(viewer_data)
    html_path = Path(html_path).expanduser().resolve()
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    html_text = html_path.read_text(encoding="utf-8")
    if _CONTROLS_MARKER in html_text:
        return html_path  # idempotent

    validate_template(html_text, [_CONFIG_ANCHOR, _SCENE_ANCHOR])

    # Escape "</" so the data cannot close the surrounding <script> tag.
    data_json = json.dumps(viewer_data, separators=(",", ":")).replace("</", r"<\/")
    config_block = (
        f"      const ansysViewerData = {data_json};\n"
        f"      {_CONTROLS_MARKER}\n\n"
        "      "
    )
    html_text = html_text.replace(_CONFIG_ANCHOR, config_block + _CONFIG_ANCHOR, 1)

    controls_js = _CONTROLS_JS_FILE.read_text(encoding="utf-8").rstrip()
    html_text = html_text.replace(_SCENE_ANCHOR, f"{_SCENE_ANCHOR}\n{controls_js}", 1)
    html_path.write_text(html_text, encoding="utf-8")
    return html_path
