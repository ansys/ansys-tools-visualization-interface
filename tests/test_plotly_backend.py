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

from plotly.graph_objects import Mesh3d, Scatter3d
import pyvista as pv

from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.plotly.plotly_interface import PlotlyBackend
from ansys.tools.visualization_interface.types import MeshObjectPlot


def test_plot_3dmesh(tmp_path, image_compare):
    """Test plotting a Plotly Mesh3d object."""
    # Create a plotter with the Plotly backend
    pl = Plotter(backend=PlotlyBackend())

    # Create a Plotly Mesh3d object
    mesh3d = Mesh3d(
        x=[0, 1, 2],
        y=[0, 1, 0],
        z=[0, 0, 1],
        i=[0],
        j=[1],
        k=[2],
        color='lightblue',
        opacity=0.50
    )

    # Plot the Mesh3d object
    pl.plot(mesh3d)

    # Show the plot (this will open a browser window)
    file = tmp_path / "test_plot_3dmesh.png"
    pl.show(screenshot=file)
    assert image_compare(file)


def test_plot_pyvista_mesh(tmp_path, image_compare):
    """Test plotting a PyVista mesh."""
    # Create a plotter with the Plotly backend
    pl = Plotter(backend=PlotlyBackend())

    # Create a PyVista mesh (e.g., a sphere)
    mesh = pv.Sphere()

    # Plot the PyVista mesh
    pl.plot(mesh)

    # Show the plot (this will open a browser window)
    file = tmp_path / "test_plot_pyvista_mesh.png"
    pl.show(screenshot=file)
    assert image_compare(file)


def test_plot_mesh_object_plot(tmp_path, image_compare):
    """Test plotting a MeshObjectPlot."""
    # Create a plotter with the Plotly backend
    pl = Plotter(backend=PlotlyBackend())

    # Create a PyVista mesh (e.g., a cube)
    mesh = pv.Cube()

    # Create a custom object with a get_mesh method
    class CustomObject:
        def __init__(self):
            self.name = "CustomObject"
            self.mesh = pv.Cube(center=(1, 1, 0))

        def get_mesh(self):
            return self.mesh

        def name(self):
            return self.name

    custom_obj = CustomObject()

    # Create a MeshObjectPlot instance

    mesh_object = MeshObjectPlot(custom_obj, custom_obj.get_mesh())

    # Plot the MeshObjectPlot
    pl.plot(mesh_object)

    # Show the plot (this will open a browser window)
    file = tmp_path / "test_plot_mesh_object_plot.png"
    pl.show(screenshot=file)
    assert image_compare(file)


def test_plot_scatter_points(tmp_path, image_compare):
    """Test plotting scatter points using Plotly."""
    # Create a plotter with the Plotly backend
    pl = Plotter(backend=PlotlyBackend())

    # Create some scatter points
    scatter_points = Scatter3d(
        x=[0, 1, 2, 3],
        y=[0, 1, 0, 1],
        z=[0, 0, 1, 1],
        mode='markers',
        marker=dict(size=5, color='red')
    )

    # Plot the scatter points
    pl.plot(scatter_points)

    # Show the plot (this will open a browser window)
    file = tmp_path / "test_plot_scatter_points.png"
    pl.show(screenshot=file)
    assert image_compare(file)

def test_plot_iter(tmp_path, image_compare):
    """Test plotting multiple objects using Plotly."""
    # Create a plotter with the Plotly backend
    pl = Plotter(backend=PlotlyBackend())

    # Create a list of PyVista meshes
    meshes = [pv.Sphere(), pv.Cube(), pv.Cylinder()]

    # Plot the meshes
    pl.plot_iter(meshes)

    # Show the plot (this will open a browser window)
    file = tmp_path / "test_plot_iter.png"
    pl.show(screenshot=file)
    assert image_compare(file)