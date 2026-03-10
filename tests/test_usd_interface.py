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
"""Tests for the USD backend interface."""

from unittest.mock import MagicMock, patch

from pxr import Usd, UsdGeom
import pytest
import pyvista as pv

from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.usd.usd_interface import USDInterface
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot


@pytest.fixture
def mock_usd_viewer():
    """Patch USDViewer so no Qt window is created."""
    with patch("ansys.tools.visualization_interface.backends.usd.usd_interface.USDViewer") as mock:
        mock.return_value = MagicMock()
        yield mock.return_value


@pytest.fixture
def iface(mock_usd_viewer):
    """Return a USDInterface with a mocked viewer."""
    return USDInterface()


@pytest.fixture
def usd_file(tmp_path):
    """Write a minimal USD file to disk and return its path."""
    path = tmp_path / "test.usda"
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.Sphere.Define(stage, "/Sphere")
    stage.Save()
    return path


def test_init_creates_empty_stage(iface):
    """USDInterface starts with an empty in-memory stage."""
    assert isinstance(iface._stage, Usd.Stage)
    prims = list(iface._stage.Traverse())
    assert prims == []


def test_multiple_instances_do_not_raise(mock_usd_viewer):
    """Creating two USDInterface instances must not raise RuntimeError."""
    i1 = USDInterface(title="First")
    i2 = USDInterface(title="Second")
    assert i1 is not i2


def test_plot_usd_stage(iface):
    """Passing a Usd.Stage replaces the internal stage."""
    new_stage = Usd.Stage.CreateInMemory()
    UsdGeom.Sphere.Define(new_stage, "/Ball")
    iface.plot(new_stage)
    assert iface._stage is new_stage


def test_plot_usd_file_path(iface, usd_file):
    """Passing a USD file path opens and sets the stage."""
    iface.plot(str(usd_file))
    assert iface._stage is not None
    paths = [str(p.GetPath()) for p in iface._stage.Traverse()]
    assert "/Sphere" in paths


def test_plot_usd_file_pathlib(iface, usd_file):
    """Passing a pathlib.Path to a USD file works the same as a str path."""
    iface.plot(usd_file)
    paths = [str(p.GetPath()) for p in iface._stage.Traverse()]
    assert "/Sphere" in paths


def test_plot_pyvista_mesh(iface):
    """Passing a PyVista PolyData mesh adds a prim to the stage."""
    mesh = pv.Sphere()
    iface.plot(mesh)
    prims = list(iface._stage.Traverse())
    assert len(prims) > 0


def test_plot_mesh_object_plot(iface):
    """Passing a MeshObjectPlot adds its mesh to the stage."""
    obj = MagicMock()
    mesh = pv.Cube()
    mop = MeshObjectPlot(obj, mesh)
    iface.plot(mop)
    prims = list(iface._stage.Traverse())
    assert len(prims) > 0


def test_plot_unsupported_type_logs_warning(iface):
    """Passing an unsupported type logs a warning and leaves the stage untouched."""
    prims_before = list(iface._stage.Traverse())
    iface.plot(object())  # unsupported
    assert list(iface._stage.Traverse()) == prims_before



def test_plot_iter_adds_multiple_meshes(iface):
    """plot_iter adds all meshes in the iterable to the stage."""
    meshes = [pv.Sphere(), pv.Cube(), pv.Cylinder()]
    iface.plot_iter(meshes)
    prims = list(iface._stage.Traverse())
    assert len(prims) >= 3


def test_show_calls_viewer(iface, mock_usd_viewer):
    """show() calls plot() and show() on the underlying USDViewer."""
    iface.show()
    mock_usd_viewer.plot.assert_called_once_with(iface._stage)
    mock_usd_viewer.show.assert_called_once()


def test_show_with_plottable_object(iface, mock_usd_viewer):
    """show(plottable_object=...) plots the object before showing."""
    mesh = pv.Sphere()
    iface.show(plottable_object=mesh)
    prims = list(iface._stage.Traverse())
    assert len(prims) > 0
    mock_usd_viewer.show.assert_called_once()


def test_plotter_integration(mock_usd_viewer):
    """USDInterface works correctly when used through the Plotter facade."""
    pl = Plotter(backend=USDInterface())
    pl.plot(pv.Sphere())
    pl.show()
    mock_usd_viewer.show.assert_called_once()

