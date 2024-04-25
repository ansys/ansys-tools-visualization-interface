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
"""Test module for the generic plotter."""
import pyvista as pv

from ansys.visualizer import ClipPlane, MeshObjectPlot, Plotter


class CustomTestClass:
    """Mock custom class for testing MeshObjectPlot."""

    def __init__(self, name) -> None:
        """Mock init."""
        self.name = name


def test_plotter_add_pd():
    """Adds polydata to the plotter."""
    pl = Plotter()
    sphere = pv.Sphere()
    pl.plot(sphere)
    pl.show()


def test_plotter_add_mb():
    """Adds multiblock to the plotter."""
    pl = Plotter()
    sphere = pv.Sphere()
    mb = pv.MultiBlock()
    mb.append(sphere)
    pl.plot(mb)
    pl.show()


def test_plotter_add_custom():
    """Adds a MeshObjectPlot object to the plotter."""
    sphere = pv.Sphere()
    custom = MeshObjectPlot(CustomTestClass("myname"), sphere)
    pl = Plotter()
    pl.plot(custom)
    pl.show()


def test_plotter_filter():
    """Test regex filter usage."""
    sphere = pv.Sphere(center=(1, 4, 0))
    cube = pv.Cube(center=(-1, 0, 3))
    custom_sphere = MeshObjectPlot(CustomTestClass("sphere"), sphere)
    custom_cube = MeshObjectPlot(CustomTestClass("cube"), cube)

    pl = Plotter()
    pl.plot([custom_sphere, custom_cube], filter="cube")
    pl.show()


def test_clipping_plane():
    """Test clipping plane usage."""
    sphere = pv.Sphere()
    pl = Plotter()
    clipping_plane = ClipPlane()
    pl.plot(sphere, clipping_plane=clipping_plane)
    pl.show()


def test_plotter_add_list():
    """Adds a list to the plotter."""
    pl = Plotter()
    sphere = pv.Sphere(center=(1, 4, 0))
    cube = pv.Cube(center=(-1, 0, 3))
    polydata_list = [sphere, cube]
    pl.plot(polydata_list)
    pl.show()
