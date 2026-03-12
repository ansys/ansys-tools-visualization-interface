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
"""Test module for plotly backend."""
import numpy as np
from plotly.graph_objects import Mesh3d, Scatter3d
import pyvista as pv

from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.plotly.plotly_interface import PlotlyBackend
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot


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

def test_plot_structured_grid(tmp_path, image_compare):
    """Adds structured grid to the plotter."""
    pl = Plotter(backend=PlotlyBackend())
    xrng = np.arange(-10, 10, 2, dtype=np.float32)
    yrng = np.arange(-10, 10, 5, dtype=np.float32)
    zrng = np.arange(-10, 10, 1, dtype=np.float32)
    x, y, z = np.meshgrid(xrng, yrng, zrng, indexing='ij')
    grid = pv.StructuredGrid(x, y, z)
    pl.plot(grid)
    file = tmp_path / "test_plot_structured_grid.png"
    pl.show(screenshot=file)
    assert image_compare(file)

def test_plot_unstructured_grid(tmp_path, image_compare):
    """Adds unstructured grid to the plotter."""
    pl = Plotter(backend=PlotlyBackend())
    sphere = pv.Sphere()
    ug = pv.UnstructuredGrid(sphere)
    pl.plot(ug)
    file = tmp_path / "test_plot_unstructured_grid.png"
    pl.show(screenshot=file)
    assert image_compare(file)

def test_plot_pyvista_multiblock(tmp_path, image_compare):
    """Test plotting a PyVista MultiBlock mesh."""
    # Create a plotter with the Plotly backend
    pl = Plotter(backend=PlotlyBackend())

    # Create a PyVista MultiBlock
    multi_block = pv.MultiBlock()
    multi_block.append(pv.Sphere(center=(-1, -1, 0)))
    multi_block.append(pv.Cube(center=(-1, 1, 0)))

    # Plot the MultiBlock
    pl.plot(multi_block)

    # Show the plot (this will open a browser window)
    file = tmp_path / "test_plot_pyvista_multiblock.png"
    pl.show(screenshot=file)
    assert image_compare(file)


def test_plot_mesh_object_plot(tmp_path, image_compare):
    """Test plotting a MeshObjectPlot."""
    # Create a plotter with the Plotly backend
    pl = Plotter(backend=PlotlyBackend())

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


# --- Label and filtering tests ---

class _NamedObject:
    """Helper: simple object with a name attribute."""
    def __init__(self, name):
        self.name = name


def test_mesh_object_plot_label_on_trace():
    """Trace name and hovertemplate are set from MeshObjectPlot.name."""
    backend = PlotlyBackend()
    obj = _NamedObject("MySphere")
    mesh_obj = MeshObjectPlot(obj, pv.Sphere())
    backend.plot(mesh_obj)

    assert len(backend._fig.data) == 1
    trace = backend._fig.data[0]
    assert trace.name == "MySphere"
    assert trace.hovertemplate is not None
    assert "fullData.name" in trace.hovertemplate


def test_mesh_object_plot_visible_propagates_to_trace():
    """When MeshObjectPlot.visible is False, the trace is added with visible=False."""
    backend = PlotlyBackend()
    obj = _NamedObject("HiddenCube")
    mesh_obj = MeshObjectPlot(obj, pv.Cube())
    mesh_obj.visible = False
    backend.plot(mesh_obj)

    assert len(backend._fig.data) == 1
    assert backend._fig.data[0].visible is False


def test_set_trace_visibility():
    """set_trace_visibility toggles visibility for traces matching the given name."""
    backend = PlotlyBackend()

    obj_a = _NamedObject("Alpha")
    obj_b = _NamedObject("Beta")
    backend.plot(MeshObjectPlot(obj_a, pv.Sphere()))
    backend.plot(MeshObjectPlot(obj_b, pv.Cube()))

    # Hide "Alpha"
    backend.set_trace_visibility("Alpha", False)
    alpha_traces = [t for t in backend._fig.data if t.name == "Alpha"]
    beta_traces = [t for t in backend._fig.data if t.name == "Beta"]
    assert all(t.visible is False for t in alpha_traces)
    assert all(t.visible is True for t in beta_traces)

    # Show "Alpha" again
    backend.set_trace_visibility("Alpha", True)
    assert all(t.visible is True for t in backend._fig.data if t.name == "Alpha")


def test_filter_traces():
    """filter_traces shows only traces whose names are in the provided list."""
    backend = PlotlyBackend()

    for name, mesh in [("A", pv.Sphere()), ("B", pv.Cube()), ("C", pv.Cylinder())]:
        backend.plot(MeshObjectPlot(_NamedObject(name), mesh))

    backend.filter_traces(["A", "C"])

    for trace in backend._fig.data:
        if trace.name in ("A", "C"):
            assert trace.visible is True
        else:
            assert trace.visible is False


def test_multiblock_label_propagates():
    """All sub-traces of a MultiBlock MeshObjectPlot carry the parent name and hovertemplate."""
    backend = PlotlyBackend()
    mb = pv.MultiBlock([pv.Sphere(), pv.Cube()])
    obj = _NamedObject("MyBlock")
    backend.plot(MeshObjectPlot(obj, mb))

    assert len(backend._fig.data) == 2
    for trace in backend._fig.data:
        assert trace.name == "MyBlock"
        assert trace.hovertemplate is not None
        assert "fullData.name" in trace.hovertemplate


def test_name_filter_excludes_non_matching():
    """Objects whose name doesn't match name_filter are not added to the figure."""
    backend = PlotlyBackend()
    for name, mesh in [("Sphere", pv.Sphere()), ("Cube", pv.Cube()), ("Cylinder", pv.Cylinder())]:
        backend.plot(MeshObjectPlot(_NamedObject(name), mesh), name_filter="Cube")

    assert len(backend._fig.data) == 1
    assert backend._fig.data[0].name == "Cube"


def test_name_filter_regex():
    """name_filter supports regex patterns."""
    backend = PlotlyBackend()
    for name, mesh in [("Part_A", pv.Sphere()), ("Part_B", pv.Cube()), ("Other", pv.Cylinder())]:
        backend.plot(MeshObjectPlot(_NamedObject(name), mesh), name_filter="^Part")

    assert len(backend._fig.data) == 2
    names = {t.name for t in backend._fig.data}
    assert names == {"Part_A", "Part_B"}


def test_name_filter_in_plot_iter():
    """name_filter is respected when using plot_iter."""
    backend = PlotlyBackend()
    objects = [MeshObjectPlot(_NamedObject(n), m) for n, m in
               [("Alpha", pv.Sphere()), ("Beta", pv.Cube()), ("AlphaExtra", pv.Cylinder())]]
    backend.plot_iter(objects, name_filter="Alpha")

    names = {t.name for t in backend._fig.data}
    assert "Beta" not in names
    assert "Alpha" in names
    assert "AlphaExtra" in names


def test_name_filter_no_name_attr_passes_through():
    """Objects without a name attribute bypass the filter and are always plotted."""
    backend = PlotlyBackend()
    backend.plot(pv.Sphere(), name_filter="SomeName")

    assert len(backend._fig.data) == 1