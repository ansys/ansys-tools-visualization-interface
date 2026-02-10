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
"""Test module for the customization API methods."""

from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.backends.plotly.plotly_interface import PlotlyBackend


def test_add_points_pyvista():
    """Test add_points API with PyVista backend."""
    pl = Plotter()
    points = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    actor = pl.add_points(points, color="red", size=10.0)
    assert actor is not None
    pl.show()


def test_add_points_plotly():
    """Test add_points API with Plotly backend."""
    pl = Plotter(backend=PlotlyBackend())
    points = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    trace = pl.add_points(points, color="red", size=10.0)
    assert trace is not None


def test_add_lines_pyvista():
    """Test add_lines API with PyVista backend."""
    pl = Plotter()
    points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    actor = pl.add_lines(points, color="blue", width=2.0)
    assert actor is not None
    pl.show()


def test_add_lines_plotly():
    """Test add_lines API with Plotly backend."""
    pl = Plotter(backend=PlotlyBackend())
    points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    trace = pl.add_lines(points, color="blue", width=2.0)
    assert trace is not None


def test_add_lines_with_connections_pyvista():
    """Test add_lines API with explicit connections using PyVista backend."""
    pl = Plotter()
    points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
    connections = [[0, 1], [2, 3]]
    actor = pl.add_lines(points, connections=connections, color="green", width=2.0)
    assert actor is not None
    pl.show()


def test_add_lines_with_connections_plotly():
    """Test add_lines API with explicit connections using Plotly backend."""
    pl = Plotter(backend=PlotlyBackend())
    points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
    connections = [[0, 1], [2, 3]]
    trace = pl.add_lines(points, connections=connections, color="green", width=2.0)
    assert trace is not None


def test_add_planes_pyvista():
    """Test add_planes API with PyVista backend."""
    pl = Plotter()
    actor = pl.add_planes(
        center=(0, 0, 0),
        normal=(0, 0, 1),
        i_size=2.0,
        j_size=2.0,
        color="lightblue",
        opacity=0.5
    )
    assert actor is not None
    pl.show()


def test_add_planes_plotly():
    """Test add_planes API with Plotly backend."""
    pl = Plotter(backend=PlotlyBackend())
    trace = pl.add_planes(
        center=(0, 0, 0),
        normal=(0, 0, 1),
        i_size=2.0,
        j_size=2.0,
        color="lightblue",
        opacity=0.5
    )
    assert trace is not None


def test_add_text_pyvista():
    """Test add_text API with PyVista backend."""
    pl = Plotter()
    actor = pl.add_text("Test Label", position=(10, 10), font_size=14, color="yellow")
    assert actor is not None
    pl.show()


def test_add_text_plotly():
    """Test add_text API with Plotly backend."""
    pl = Plotter(backend=PlotlyBackend())
    annotation = pl.add_text("Test Label", position=(0, 0, 1), font_size=14, color="yellow")
    assert annotation is not None
