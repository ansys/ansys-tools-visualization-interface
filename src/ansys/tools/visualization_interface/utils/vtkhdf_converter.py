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

"""Utils module for VTKHDF management."""
from pathlib import Path
from typing import Union

import pyvista as pv
import vtk
from vtkmodules.vtkIOHDF import vtkHDFWriter


def pd_to_vtkhdf(pd: pv.PolyData, output_vtkhdf_file: Union[str, Path]) -> Path:
    """Write the PyVista PolyData directly to a VTKHDF file.

    Parameters
    ----------
    pd : pv.PolyData
        The PyVista PolyData to be written.
    output_vtkhdf_file : Union[str, Path]
        The output VTKHDF file path.

    Returns
    -------
    Path
        The path to the saved VTKHDF file.
    """
    writer = vtkHDFWriter()
    writer.SetFileName(str(output_vtkhdf_file))
    writer.SetInputDataObject(pd)
    writer.Write()
    return Path(output_vtkhdf_file)


def vtkhdf_to_pd(input_vtkhdf_file: Union[str, Path]) -> pv.PolyData:
    """Read a VTKHDF file and convert it to PyVista PolyData.

    Parameters
    ----------
    input_vtkhdf_file : Union[str, Path]
        The input VTKHDF file path.

    Returns
    -------
    pv.PolyData
        The converted PyVista PolyData.
    """
    reader = vtk.vtkHDFReader()
    reader.SetFileName(str(input_vtkhdf_file))
    reader.Update()
    # Convert VTK object directly to PyVista PolyData
    pd = pv.wrap(reader.GetOutput())

    return pd


def ug_to_vtkhdf(ug: pv.UnstructuredGrid, output_vtkhdf_file: Union[str, Path]) -> Path:
    """Write the PyVista UnstructuredGrid directly to a VTKHDF file.

    Parameters
    ----------
    ug : pv.UnstructuredGrid
        The PyVista UnstructuredGrid to be written.
    output_vtkhdf_file : Union[str, Path]
        The output VTKHDF file path.

    Returns
    -------
    Path
        The path to the saved VTKHDF file.
    """
    writer = vtkHDFWriter()
    writer.SetFileName(str(output_vtkhdf_file))
    writer.SetInputDataObject(ug)
    writer.Write()
    return Path(output_vtkhdf_file)


def vtkhdf_to_ug(input_vtkhdf_file: Union[str, Path]) -> pv.UnstructuredGrid:
    """Read a VTKHDF file and convert it to PyVista UnstructuredGrid.

    Parameters
    ----------
    input_vtkhdf_file : Union[str, Path]
        The input VTKHDF file path.

    Returns
    -------
    pv.UnstructuredGrid
        The converted PyVista UnstructuredGrid.
    """
    reader = vtk.vtkHDFReader()
    reader.SetFileName(str(input_vtkhdf_file))
    reader.Update()
    # Convert VTK object directly to PyVista UnstructuredGrid
    ug = pv.wrap(reader.GetOutput())

    return ug
