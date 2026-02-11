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
.. _customization_api_example:

Backend-Agnostic Customization APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates the new backend-agnostic customization APIs
that allow you to add points, lines, planes, and text to visualizations
without directly coupling to the PyVista backend.

These APIs work consistently across different backends, making your code
more portable and maintainable.
"""

import pyvista as pv
from ansys.tools.visualization_interface import Plotter

###############################################################################
# Create a plotter and add basic geometry
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# First, create a plotter and add some geometry to visualize.

plotter = Plotter()

# Add a sphere as our main geometry
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))
plotter.plot(sphere, color='lightblue', opacity=0.6)

###############################################################################
# Add points
# ~~~~~~~~~~
# Add point markers to highlight specific locations.

key_points = [
    [1, 0, 0],   # Point on X axis
    [0, 1, 0],   # Point on Y axis
    [0, 0, 1],   # Point on Z axis
]

plotter.add_points(key_points, color='red', size=20)

###############################################################################
# Add lines
# ~~~~~~~~~
# Add line segments to show coordinate axes or connections.

# X axis
x_axis = [[0, 0, 0], [1.5, 0, 0]]
plotter.add_lines(x_axis, color='red', width=4.0)

# Y axis
y_axis = [[0, 0, 0], [0, 1.5, 0]]
plotter.add_lines(y_axis, color='green', width=4.0)

# Z axis
z_axis = [[0, 0, 0], [0, 0, 1.5]]
plotter.add_lines(z_axis, color='blue', width=4.0)

###############################################################################
# Add a reference plane
# ~~~~~~~~~~~~~~~~~~~~~
# Add a plane to show a reference surface.

plotter.add_planes(
    center=(0, 0, 0),
    normal=(0, 0, 1),
    i_size=2.5,
    j_size=2.5,
    color='white',
    opacity=0.2
)

###############################################################################
# Add text labels
# ~~~~~~~~~~~~~~~
# Add text annotations to label features using 2D screen coordinates.

# Scene title at the top (pixel coordinates)
plotter.add_text("Customization API Example", position=(400, 550), font_size=18, color='white')

# Additional labels at corners (pixel coordinates)
plotter.add_text("PyVista Backend", position=(1, 1), font_size=12, color='lightblue')
plotter.add_text("3D Visualization", position=(1, 10), font_size=12, color='lightgreen')

###############################################################################
# Show the result
# ~~~~~~~~~~~~~~~
# Display the visualization with all customizations.

plotter.show()
