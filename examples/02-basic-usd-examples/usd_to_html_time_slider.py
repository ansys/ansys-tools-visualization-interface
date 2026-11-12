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

:func:`~ansys.tools.visualization_interface.export_usd_to_html` reads the stage
at a single time, so this example embeds the extra frames itself. It inserts
them at the two anchor strings that the built-in template documents for the
wireframe overlay (see :ref:`Custom HTML templates <ref_usd_viewer>`).

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
# Export the stage to HTML
# ========================
# Export the first frame with the built-in viewer.

from ansys.tools.visualization_interface import export_usd_to_html

html_path = export_usd_to_html(stage, "time_slider_viewer.html", show_mesh_lines=False)

###################################
# Add the frames, slider, and legend
# ==================================
# The exporter writes one GLB vertex per triangle corner, so for a triangle
# mesh the GLB vertex ``k`` takes the value of USD point
# ``faceVertexIndices[k]``. Reorder the frames to match, then insert them
# and a small player before and after the two template anchors.

import base64
import json

data = {
    "frames": base64.b64encode(levels[:, face_indices].tobytes()).decode("ascii"),
    "lut": np.rint(lut * 255).astype(int).ravel().tolist(),
    "times": times.tolist(),
    "title": "wave",
    "vmin": vmin,
    "vmax": vmax,
    "fps": 20,
}

config_js = f"const timeData = {json.dumps(data)};\n      "

player_js = """
        {
          const d = timeData;
          const frames = Uint8Array.from(atob(d.frames), (c) => c.charCodeAt(0));
          const nFrames = d.times.length;
          const nVerts = frames.length / nFrames;
          let colors = null;
          gltf.scene.traverse((obj) => {
            const attr = obj.isMesh && obj.geometry.getAttribute("color");
            if (attr && attr.count === nVerts) {
              colors = attr;
              // Matte surface so the field colors read clearly.
              obj.material.metalness = 0;
            }
          });
          // The lookup table is sRGB; vertex colors are linear.
          const lut = [];
          for (let i = 0; i < 256; i++) {
            const c = new THREE.Color().setRGB(
              d.lut[3 * i] / 255, d.lut[3 * i + 1] / 255, d.lut[3 * i + 2] / 255,
              THREE.SRGBColorSpace);
            lut.push(c.r, c.g, c.b);
          }

          const style = "position:fixed;padding:8px 12px;border-radius:8px;"
            + "background:rgba(20,22,26,0.78);font-size:13px;";
          const player = document.createElement("div");
          player.style.cssText = style + "bottom:16px;left:50%;transform:translateX(-50%);"
            + "display:flex;gap:10px;align-items:center;";
          const play = document.createElement("button");
          const slider = Object.assign(document.createElement("input"),
            { type: "range", min: 0, max: nFrames - 1, value: 0 });
          slider.style.width = "40vw";
          const label = document.createElement("span");
          player.append(play, slider, label);

          const legend = document.createElement("div");
          legend.style.cssText = style + "top:12px;right:12px;";
          const gradient = [];
          for (let i = 0; i < 256; i += 15) {
            gradient.push("rgb(" + d.lut.slice(3 * i, 3 * i + 3).join(",") + ")");
          }
          legend.innerHTML = "<div>" + d.title + "</div>"
            + "<div style='width:200px;height:12px;background:linear-gradient(to right,"
            + gradient.join(",") + ")'></div>"
            + "<div style='display:flex;justify-content:space-between'><span>"
            + d.vmin.toPrecision(3) + "</span><span>" + d.vmax.toPrecision(3)
            + "</span></div>";
          document.body.append(player, legend);

          const show = (f) => {
            if (colors) {
              for (let i = 0; i < nVerts; i++) {
                const k = 3 * frames[f * nVerts + i];
                colors.setXYZ(i, lut[k], lut[k + 1], lut[k + 2]);
              }
              colors.needsUpdate = true;
            }
            slider.value = f;
            label.textContent = "Time " + d.times[f];
          };
          let timer = null;
          const stop = () => { clearInterval(timer); timer = null; play.textContent = "Play"; };
          play.onclick = () => {
            if (timer) return stop();
            play.textContent = "Pause";
            timer = setInterval(() => show((+slider.value + 1) % nFrames), 1000 / d.fps);
          };
          slider.oninput = () => { stop(); show(+slider.value); };
          stop();
          show(0);
        }"""

config_anchor = "const binary = atob(glbBase64);"
scene_anchor = "scene.add(gltf.scene);"
html = html_path.read_text(encoding="utf-8")
html = html.replace(config_anchor, config_js + config_anchor, 1)
html = html.replace(scene_anchor, scene_anchor + player_js, 1)
html_path.write_text(html, encoding="utf-8")
print(f"Viewer with time slider written to: {html_path}")
