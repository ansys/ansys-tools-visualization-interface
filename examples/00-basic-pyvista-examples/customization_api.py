# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
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
.. _api_ex:

Customization API example
=========================

This example demonstrates how to use the customization API of the visualization interface
to add various elements to a PyVista scene, such as points, lines, planes, and text annotations.
The example also shows how to plot a simple sphere mesh and customize its appearance.

"""


from ansys.tools.visualization_interface import Plotter
import pyvista as pv

sphere = pv.Sphere()
pl = Plotter()

# Add points at specific locations
points = [[0, 0, 0], [1, 1, 1], [2, 2, 2]]
pl.add_points(points, color="yellow", size=15)

# Add lines connecting the points
lines = [[0, 1], [1, 2]]
pl.add_lines(points, lines, color="red", width=5)

# Add a plane - note: add_planes takes a single center and normal, not lists
pl.add_planes(center=(0, 0, 0), normal=(0, 0, 1), i_size=2.0, j_size=2.0, color="blue", opacity=0.5)

# Add text annotation to the scene
pl.add_text("Customization API Example", position="upper_left", font_size=16, color="white")

# Plot the sphere mesh
pl.plot(sphere, color="lightblue", opacity=0.8)

# Show the complete visualization
pl.show()