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
.. _plotly_customization_api_example:

Backend-Agnostic Customization APIs (Plotly)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example demonstrates the backend-agnostic customization APIs with
the Plotly backend.

The same API calls work with both PyVista and Plotly backends, demonstrating
the true backend-agnostic nature of these methods.
"""

import pyvista as pv
from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.plotly.plotly_interface import PlotlyBackend

###############################################################################
# Create a plotter with Plotly backend
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a plotter using the Plotly backend and add basic geometry.

plotter = Plotter(backend=PlotlyBackend())

# Add a sphere - this works fine
sphere = pv.Sphere(radius=1.0, center=(0, 0, 0))
plotter.plot(sphere)

print("✓ Basic geometry added successfully with Plotly backend")

###############################################################################
# Add points
# ~~~~~~~~~~
# Add point markers to highlight specific locations.

key_points = [
    [1, 0, 0],   # Point on X axis
    [0, 1, 0],   # Point on Y axis
    [0, 0, 1],   # Point on Z axis
]

plotter.add_points(key_points, color='red', size=10)
print("✓ Points added successfully")

###############################################################################
# Add lines
# ~~~~~~~~~
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

print("✓ Lines added successfully")

###############################################################################
# Add a reference plane
# ~~~~~~~~~~~~~~~~~~~~~
# Add a plane to show a reference surface.

plotter.add_planes(
    center=(0, 0, 0),
    normal=(0, 0, 1),
    i_size=2.5,
    j_size=2.5,
    color='lightblue',
    opacity=0.2
)
print("✓ Plane added successfully")

###############################################################################
# Add text labels
# ~~~~~~~~~~~~~~~
# Add text annotations to label features.

# Axis labels (3D world coordinates)
plotter.add_text("X", position=(1.6, 0, 0), font_size=14, color='red')
plotter.add_text("Y", position=(0, 1.6, 0), font_size=14, color='green')
plotter.add_text("Z", position=(0, 0, 1.6), font_size=14, color='blue')
print("✓ Text labels added successfully")

###############################################################################
# Show the result
# ~~~~~~~~~~~~~~~
# Display the visualization with all customizations.

print("\n" + "="*70)
print("Summary:")
print("  ✓ All customization APIs work with Plotly backend!")
print("  ✓ Same API calls as PyVista - truly backend-agnostic")
print("="*70)

# Uncomment to show in browser:
plotter.show()
