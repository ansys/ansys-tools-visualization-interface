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

"""
.. _ref_usd_to_html_time_slider:

==================================================
Export a time-sampled USD field with a time slider
==================================================

This example shows how to export a USD mesh whose scalar field changes over
time, such as a simulation result, to a self-contained HTML page with a
play button, a time slider, and a color legend.

:func:`~ansys.tools.visualization_interface.export_usd_to_html` writes a
plain viewer of the stage at a single time.
:func:`~ansys.tools.visualization_interface.add_viewer_controls` then adds the
player and the legend to that page as an optional add-on.

.. note::

    This feature requires the ``[usd]`` optional dependencies::

        pip install ansys-tools-visualization-interface[usd]

    To run this example from a clone of the repository::

        uv run --extra usd examples/02-basic-usd-examples/usd_to_html_time_slider.py
"""

###################################
# Create a time-sampled USD stage
# ===============================
# Build a triangulated sphere and store a scalar field with one USD time
# sample per frame. Here the field is a wave travelling from the bottom to
# the top of the sphere.

import numpy as np
import pyvista as pv
from pxr import Sdf, Usd, UsdGeom, Vt

sphere = pv.Sphere(theta_resolution=60, phi_resolution=60).triangulate()
points = np.asarray(sphere.points, dtype=np.float32)
face_indices = sphere.faces.reshape(-1, 4)[:, 1:].ravel()

n_frames = 60
times = np.arange(n_frames)
frames = np.stack(
    [np.sin(6.0 * points[:, 1] - 2.0 * np.pi * t / n_frames) for t in times]
).astype(np.float32)

stage = Usd.Stage.CreateInMemory()
stage.SetStartTimeCode(float(times[0]))
stage.SetEndTimeCode(float(times[-1]))
mesh = UsdGeom.Mesh.Define(stage, "/Sphere")
mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points))
mesh.GetFaceVertexCountsAttr().Set([3] * (len(face_indices) // 3))
mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray.FromNumpy(face_indices))
field = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
    "wave", Sdf.ValueTypeNames.FloatArray, UsdGeom.Tokens.vertex
)
for t, values in zip(times, frames):
    field.Set(Vt.FloatArray.FromNumpy(values), Usd.TimeCode(float(t)))

###################################
# Map the field to colors
# =======================
# Use one fixed color range for all frames so that colors are comparable
# over time. A 256-entry blue-white-red lookup table turns each value into a
# single byte, which keeps the HTML page small.

vmin, vmax = float(frames.min()), float(frames.max())
levels = np.rint((frames - vmin) / (vmax - vmin) * 255).astype(np.uint8)

stops = np.array([[0.23, 0.30, 0.75], [0.87, 0.87, 0.87], [0.71, 0.02, 0.15]])
ramp = np.linspace(0.0, 2.0, 256)
lut = np.empty((256, 3))
for channel in range(3):
    lut[:, channel] = np.interp(ramp, [0.0, 1.0, 2.0], stops[:, channel])

# The exporter reads ``displayColor``, which USD stores in linear color space.
# Author it with the first frame so the stage is also correct on its own.
mesh.CreateDisplayColorPrimvar(UsdGeom.Tokens.vertex).Set(
    Vt.Vec3fArray.FromNumpy((lut[levels[0]] ** 2.2).astype(np.float32))
)

###################################
# Pack the frames for the viewer
# ==============================
# The exporter writes one GLB vertex per triangle corner, so for a triangle
# mesh the GLB vertex ``k`` takes the value of USD point
# ``faceVertexIndices[k]``. Reorder the frames to match and encode them as
# base64 bytes, one byte per vertex per frame.

import base64

viewer_data = {
    "lut": np.rint(lut * 255).astype(int).ravel().tolist(),
    "legend": {"title": "wave", "vmin": vmin, "vmax": vmax},
    "frames": {
        "data": base64.b64encode(levels[:, face_indices].tobytes()).decode("ascii"),
        "times": times.tolist(),
        "label": "Time",
        "fps": 20,
    },
}

###################################
# Export the stage to HTML
# ========================
# Export the first frame with the built-in viewer. This page has no player yet.

from ansys.tools.visualization_interface import add_viewer_controls, export_usd_to_html

html_path = export_usd_to_html(stage, "time_slider_viewer.html", show_mesh_lines=False)

###################################
# Add the time slider and legend
# ==============================
# Pass the frames and the colormap to
# :func:`~ansys.tools.visualization_interface.add_viewer_controls` to add a
# Play/Pause button, a time slider, and a color legend to the page.

add_viewer_controls(html_path, viewer_data)
print(f"Viewer with time slider written to: {html_path}")
