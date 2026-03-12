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
.. _ref_name_filter_plotly:

=======================================
Name filtering in the Plotly backend
=======================================

The ``name_filter`` parameter accepts a regular-expression string and is
available on :meth:`Plotter.plot`, :meth:`Plotter.plot_iter`, and
:meth:`Plotter.show`.  Only :class:`MeshObjectPlot` objects whose ``name``
matches the pattern are added to the figure; everything else is silently
skipped.
"""

import pyvista as pv

from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.plotly.plotly_interface import PlotlyBackend
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot


class Part:
    """Minimal domain object with a name."""

    def __init__(self, name: str):
        self.name = name


###############################################################################
# Build a set of named parts
# ==========================

parts = [
    MeshObjectPlot(Part("Wheel_FL"), pv.Sphere(center=(-1,  1, 0), radius=0.3)),
    MeshObjectPlot(Part("Wheel_FR"), pv.Sphere(center=( 1,  1, 0), radius=0.3)),
    MeshObjectPlot(Part("Wheel_RL"), pv.Sphere(center=(-1, -1, 0), radius=0.3)),
    MeshObjectPlot(Part("Wheel_RR"), pv.Sphere(center=( 1, -1, 0), radius=0.3)),
    MeshObjectPlot(Part("Chassis"),  pv.Box(bounds=(-0.8, 0.8, -1.2, 1.2, 0, 0.4))),
]

###############################################################################
# Show with ``name_filter`` via ``show()``
# ========================================
# Pass ``name_filter`` directly to :meth:`Plotter.show` together with the
# list of objects.  The filter is applied while plotting, so only matching
# parts are added to the figure.

pl = Plotter(backend=PlotlyBackend())
pl.show(plottable_object=parts, name_filter="Wheel")
