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
.. _ref_plain_usage_usd:

==============================
Plain usage of the USD backend
==============================

This example shows how to use the Python USD viewer backend in the Visualization Interface Tool
to display meshes using the OpenUSD-based viewer from the ``python-usd-viewer`` package.
"""

####################
# Plot a single mesh
# ==================
# This code shows how to plot a single PyVista mesh with the USD backend.
#
# .. code-block:: python
#
#   import pyvista as pv
#
#   from ansys.tools.visualization_interface import Plotter
#   from ansys.tools.visualization_interface.backends.usd.usd_interface import USDInterface
#
#   mesh = pv.Sphere()
#
#   # Create a plotter with the USD backend
#   pl = Plotter(backend=USDInterface())
#
#   # Add the mesh to the plotter
#   pl.plot(mesh)
#
#   # Show the plotter — opens a Qt window and blocks until it is closed
#   pl.show()


######################
# Plot multiple meshes
# ====================
# Use :meth:`plot_iter` to add several meshes at once before showing the viewer.
#
# .. code-block:: python
#
#   import pyvista as pv
#
#   from ansys.tools.visualization_interface import Plotter
#   from ansys.tools.visualization_interface.backends.usd.usd_interface import USDInterface
#
#   meshes = [
#       pv.Sphere(center=(0, 0, 0)),
#       pv.Cube(center=(2, 0, 0)),
#       pv.Cylinder(center=(-2, 0, 0)),
#   ]
#
#   pl = Plotter(backend=USDInterface())
#   pl.plot_iter(meshes)
#   pl.show()


#############################
# Load and display a USD file
# ===========================
# If you already have a ``.usd`` / ``.usda`` / ``.usdc`` file on disk, pass
# its path directly to :meth:`plot`.  The file is opened as a
# :class:`pxr.Usd.Stage` and displayed in the viewer.
#
# .. code-block:: python
#
#   import pyvista as pv
#   import tempfile, os
#
#   from ansys.tools.visualization_interface import Plotter
#   from ansys.tools.visualization_interface.backends.usd.usd_interface import USDInterface
#
#   # Write a simple USD file to a temporary location for demonstration purposes
#   usd_content = """\
#   #usda 1.0
#
#   def Sphere "Ball"
#   {
#       double radius = 1
#   }
#   """
#   tmp = tempfile.NamedTemporaryFile(suffix=".usda", mode="w", delete=False)
#   tmp.write(usd_content)
#   tmp.close()
#
#   pl = Plotter(backend=USDInterface())
#   pl.plot(tmp.name)
#   pl.show()
#
#   os.unlink(tmp.name)
