# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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
.. _ref_postprocess_using_meshobjects:

====================================================================
Postprocessing simulation results using the ``MeshObjectPlot`` class
====================================================================

The Visualization Interface Tool provides the ``MeshObject`` helper class to relate a custom object.
With a custom object, you can take advantage of the full potential of the Visualization Interface Tool.

This example shows how to use the ``MeshObjectPlot`` class to plot your custom objects with scalar data on mesh.

"""

###################################################
# Necessary imports
# =================


from ansys.fluent.core import examples
import pyvista as pv

from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend
from ansys.tools.visualization_interface import MeshObjectPlot, Plotter

###################################################
# Download the VTK file
# =====================
#
# A VTK dataset can be produced utilizing `PyDPF <https://dpf.docs.pyansys.com/version/stable/>`_
# for Ansys Flagship products simulations results file format.

mixing_elbow_file_src = examples.download_file("mixing_elbow.vtk", "result_files/fluent-mixing_elbow_steady-state")

###################################################
# Define a custom object class
# ============================
#
# Note that the ``CustomObject`` class must have a way to get the mesh
# and a name or ID.


class CustomObject:
    def __init__(self):
        self.name = "CustomObject"
        self.mesh = pv.read(mixing_elbow_file_src)

    def get_mesh(self):
        return self.mesh

    def get_field_array_info(self):
        return self.mesh.array_names

    def name(self):
        return self.name


# Create a custom object
custom_vtk = CustomObject()

######################################
# Create a ``MeshObjectPlot`` instance
# ====================================

mesh_object = MeshObjectPlot(custom_vtk, custom_vtk.get_mesh())

# Define the camera position
cpos = (
    (-0.2024 - 20252024 - 20252024 - 20252024 - 2025, 0.2024 - 20252024 - 20252024 - 20252024 - 20253, -1.2024 - 20252024 - 20252024 - 2025142),
    (0.2024 - 20252024 - 20252024 - 20252024 - 20255, -0.2024 - 20252024 - 20252024 - 20252024 - 20252, -0.2024 - 20252024 - 20252024 - 20252024 - 202587),
    (0.2024 - 20252024 - 20252024 - 20252024 - 202585, 0.2024 - 20252024 - 20252024 - 20252024 - 2025, 0.2024 - 20252024 - 20252024 - 20252024 - 20258),
)

######################################
# Get the available field data arrays
# ====================================

field_data_arrays = custom_vtk.get_field_array_info()
print(f"Field data arrays: {field_data_arrays}")

########################################################################
# Plot the ``MeshObjectPlot`` instance with mesh object & field data (0)
# ======================================================================

pv_backend = PyVistaBackend()
pl = Plotter(backend=pv_backend)
pl.plot(
    mesh_object,
    scalars=field_data_arrays[0],
    show_edges=True,
    show_scalar_bar=True,
)
pl._backend.pv_interface.scene.camera_position = cpos
pl.show()


##############################################################################
# Plot the ``MeshObjectPlot`` instance with mesh object & other field data (1)
# ============================================================================

pv_backend = PyVistaBackend()
pl = Plotter(backend=pv_backend)
pl.plot(
    mesh_object,
    scalars=field_data_arrays[1],
    show_edges=True,
    show_scalar_bar=True,
)
pl._backend.pv_interface.scene.camera_position = cpos
pl.show()
