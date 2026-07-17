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
.. _ref_usd_to_html_export:

==========================
Export a USD file to HTML
==========================

This example shows how to convert a USD file (or an in-memory
:class:`pxr.Usd.Stage`) into a self-contained HTML viewer page.  The page
embeds all geometry as a base64-encoded GLB file and renders it with
`Three.js <https://threejs.org>`_ — only a CDN connection is required to open
it in any modern browser.

.. note::

    This feature requires the ``[usd]`` optional dependencies::

        pip install ansys-tools-visualization-interface[usd]
"""


###################################
# Create a sample USD file
# ========================
# Build a minimal USD stage with one triangular mesh and save it to disk so
# the file-path examples below have something to read.

from pxr import Gf, Usd, UsdGeom

stage = Usd.Stage.CreateNew("my_model.usd")
mesh = UsdGeom.Mesh.Define(stage, "/Triangle")
stage.SetDefaultPrim(mesh.GetPrim())
mesh.GetPointsAttr().Set(
    [Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)]
)
mesh.GetFaceVertexCountsAttr().Set([3])
mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])
stage.Save()

###################################
# Export from a USD file on disk
# ===============================
# Pass a file path string or :class:`pathlib.Path` to
# :func:`~ansys.tools.visualization_interface.export_usd_to_html`.
# The function returns the :class:`pathlib.Path` to the generated HTML file.

from ansys.tools.visualization_interface import export_usd_to_html

html_path = export_usd_to_html("my_model.usd", "my_model_viewer.html")
print(f"Viewer written to: {html_path}")


###################################
# Export from an in-memory stage
# ================================
# You can pass a :class:`pxr.Usd.Stage` directly — no ``.usd`` file on disk
# is required.  A temporary file is created automatically, used to generate
# the GLB, and removed when the function returns.

html_path = export_usd_to_html(stage, "triangle_viewer.html")
print(f"Viewer written to: {html_path}")


###################################
# Add a wireframe overlay
# ========================
# Set ``show_mesh_lines=True`` to inject a Three.js ``LineSegments`` overlay
# that traces every polygon edge.  Use ``line_color`` (CSS hex) and
# ``line_opacity`` (0–1) to style it.

html_path = export_usd_to_html(
    "my_model.usd",
    "my_model_viewer.html",
    show_mesh_lines=True,
    line_color="#00ffcc",
    line_opacity=0.7,
)
print(f"Viewer with wireframe written to: {html_path}")
