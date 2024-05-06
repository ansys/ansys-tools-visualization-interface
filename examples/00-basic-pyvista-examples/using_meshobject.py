# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
.. _ref_using_meshobject:

================================
Use the ``MeshObjectPlot`` class
================================

Visualization Interface tool provides the ``MeshObject`` helper class to relate a custom object
with its mesh. With a custom object, you can take advantage of the full potential of
Visualization Interface tool.

This example shows how to use the ``MeshObjectPlot`` class to plot your custom objects.
"""

###################################################
# Relate ``CustomObject`` class with a PyVista mesh
# =================================================

import pyvista as pv

# Note that the ``CustomObject`` class must have a way to get the mesh
# and a name or ID.

class CustomObject:
    def __init__(self):
        self.name = "CustomObject"
        self.mesh = pv.Cube()

    def get_mesh(self):
        return self.mesh

    def name(self):
        return self.name

# Create a custom object
custom_object = CustomObject()


######################################
# Create a ``MeshObjectPlot`` instance
# ====================================

from ansys.tools.visualization_interface import MeshObjectPlot

# Create an instance

mesh_object = MeshObjectPlot(custom_object, custom_object.get_mesh())

######################################
# Plot the ``MeshObjectPlot`` instance
# ====================================

from ansys.tools.visualization_interface import Plotter

pl = Plotter()
pl.plot(mesh_object)
pl.show()
pl = Plotter(use_trame=True)
pl.add(mesh_object)
pl.plot()
