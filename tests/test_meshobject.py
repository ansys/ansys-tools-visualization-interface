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
"""Test module for the generic plotter."""
import os

import pyvista as pv

from ansys.tools.visualization_interface import MeshObjectPlot

IN_GITHUB_ACTIONS = os.getenv("IN_GITHUB_ACTIONS") == "true"


class CustomTestClass:
    """Mock custom class for testing MeshObjectPlot."""

    def __init__(self, name) -> None:
        """Mock init."""
        self.name = name



def test_mesh_object_plot_tree():
    """Test that basic parent-child relationships work."""
    parent_mesh = pv.Sphere()
    child_mesh = pv.Cube()

    parent_obj = MeshObjectPlot(CustomTestClass("parent"), parent_mesh)
    child_obj = MeshObjectPlot(CustomTestClass("child"), child_mesh)

    parent_obj.add_child(child_obj)


    # assert that the child's parent is set correctly
    assert child_obj.parent == parent_obj

    # assert that the parent's children contain the child
    assert child_obj in parent_obj._children

    # assert that the parent's parent is None
    assert parent_obj.parent is None

    # assert that the child has no children
    assert len(child_obj._children) == 0
