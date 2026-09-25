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
.. _ref_plain_usage_dash:

======================================
Plain usage of the plotly dash backend
======================================

This example shows the plain usage of the Plotly Dash backend in the Visualization Interface Tool to plot different objects,
including PyVista meshes, custom objects, and Plotly-specific objects.
"""

from ansys.tools.visualization_interface.backends.plotly.plotly_dash import PlotlyDashBackend
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot
from ansys.tools.visualization_interface import Plotter
import pyvista as pv
from plotly.graph_objects import Mesh3d


# Create a plotter with the Plotly backend
pl = Plotter(backend=PlotlyDashBackend())

# Create a PyVista mesh
mesh = pv.Sphere()
mesh2 = pv.Cube(center=(2,0,0))
# Plot the mesh
pl.plot(mesh, name="Sphere")
pl.plot(mesh2, name="Cube")

# ----------------------------------
# Start the server and show the plot
# ----------------------------------
#
# .. code-block:: python
#
#     pl.show()

