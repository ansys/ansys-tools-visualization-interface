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

# Create a plotter using the Plotly backend and add basic geometry.

plotter = Plotter()

# Add a sphere - this works fine
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))
plotter.plot(sphere)


# Add point markers to highlight specific locations.

key_points = [
    [1, 0, 0],   # Point on X axis
    [0, 1, 0],   # Point on Y axis
    [0, 0, 1],   # Point on Z axis
]

plotter.add_points(key_points, color='red', size=10)

# Add line segments to show coordinate axes.

# X axis
x_axis = [[0, 0, 0], [1.5, 0, 0]]
plotter.add_lines(x_axis, color='red', width=4.0)

# Y axis
y_axis = [[0, 0, 0], [0, 1.5, 0]]
plotter.add_lines(y_axis, color='green', width=4.0)

# Z axis
z_axis = [[0, 0, 0], [0, 0, 1.5]]
plotter.add_lines(z_axis, color='blue', width=4.0)


# Add a plane to show a reference surface.

plotter.add_planes(
    center=(0, 0, 0),
    normal=(0, 0, 1),
    i_size=2.5,
    j_size=2.5,
    color='lightblue',
    opacity=0.2
)


# Scene title at the top center
plotter.add_text("Customization API Example", position="upper_edge", font_size=18, color='white')

# Additional labels at the top corners
plotter.add_text("PyVista Backend", position="upper_left", font_size=12, color='lightblue')
plotter.add_text("3D Visualization", position="upper_right", font_size=12, color='lightgreen')


# Add labels at specific 3D points to annotate key locations in space.

label_points = [
    [1, 0, 0],   # X axis endpoint
    [0, 1, 0],   # Y axis endpoint
    [0, 0, 1],   # Z axis endpoint
]

labels = ['X-axis', 'Y-axis', 'Z-axis']

plotter.add_point_labels(label_points, labels, font_size=16, point_size=8.0)


# Note: In PyVista, clear() must be called BEFORE show(). Once show() is called,
# the plotter cannot be reused. Typical workflow: build scene -> clear -> rebuild -> show().
# Therefore, clear() method is mainly useful for resetting the scene during interactive work.

# Uncomment to clear everything added above and start fresh:
# plotter.clear()
# plotter.plot(pv.Cube())  # Would show only a cube instead


# Display the visualization with all customizations.

plotter.show()
