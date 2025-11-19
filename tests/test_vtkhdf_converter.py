#!/usr/bin/env python3

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

"""Test script to verify the VTKHDF converter functions work correctly."""

import pyvista as pv
from pyvista import examples

from ansys.tools.visualization_interface.utils.vtkhdf_converter import (
    pd_to_vtkhdf,
    ug_to_vtkhdf,
    vtkhdf_to_pd,
    vtkhdf_to_ug,
)


def test_pd_conversion(tmp_path):
    """Test PolyData to VTKHDF and back conversion."""
    print("Testing PolyData conversion...")

    # Create a sphere
    original_sphere = pv.Sphere()

    # Create temporary file path
    temp_file = tmp_path / "test_pd.vtkhdf"

    # Convert to VTKHDF
    pd_to_vtkhdf(original_sphere, str(temp_file))

    # Convert back
    loaded_sphere = vtkhdf_to_pd(str(temp_file))

    # Verify they have the same number of points and cells
    assert original_sphere.n_points == loaded_sphere.n_points, "Point count mismatch"
    assert original_sphere.n_cells == loaded_sphere.n_cells, "Cell count mismatch"

def test_ug_conversion(tmp_path):
    """Test UnstructuredGrid to VTKHDF and back conversion."""
    # Create an unstructured grid
    original_grid = pv.UnstructuredGrid(examples.hexbeamfile)

    # Create temporary file path
    temp_file = tmp_path / "test_ug.vtkhdf"

    # Convert to VTKHDF
    ug_to_vtkhdf(original_grid, str(temp_file))

    # Convert back
    loaded_grid = vtkhdf_to_ug(str(temp_file))

    # Verify they have the same number of points and cells
    assert original_grid.n_points == loaded_grid.n_points, "Point count mismatch"
    assert original_grid.n_cells == loaded_grid.n_cells, "Cell count mismatch"
