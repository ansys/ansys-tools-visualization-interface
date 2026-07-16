# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Asset resolver for handling various file types and USD asset paths."""

from pathlib import Path
from typing import Optional, Union
import warnings

try:
    from pxr import Gf, Usd, UsdGeom
except ImportError:  # pragma: no cover
    warnings.warn(
        "The 'pxr' module is required to use the USDViewer. "
        "Install the 'usd-core' package. "
        "For installation instructions, see the documentation."
    )

import vtk


class VTKConverter:
    """Convert VTK files to USD format for visualization."""

    @staticmethod
    def _normalize_rgb_color(color: tuple[float, float, float]) -> "Gf.Vec3f":
        """Normalize an RGB tuple to USD's 0-1 range."""
        if any(c > 1.0 for c in color):
            return Gf.Vec3f(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
        return Gf.Vec3f(color[0], color[1], color[2])

    @staticmethod
    def _extract_display_colors_from_scalars(
        scalars: "vtk.vtkDataArray",
    ) -> list["Gf.Vec3f"]:
        """Extract RGB display colors from VTK scalar data.

        For RGB/RGBA arrays, values are used directly (alpha ignored).
        For single-component scalar arrays, a lookup table is used to map
        scalar values to colors.
        """
        num_components = scalars.GetNumberOfComponents()
        num_tuples = scalars.GetNumberOfTuples()

        if num_tuples == 0:
            return []

        if num_components >= 3:
            colors = []
            for i in range(num_tuples):
                color = scalars.GetTuple(i)
                colors.append(VTKConverter._normalize_rgb_color((color[0], color[1], color[2])))
            return colors

        if num_components == 1:
            lut = scalars.GetLookupTable()
            if lut is None:
                lut = vtk.vtkLookupTable()
                scalar_min, scalar_max = scalars.GetRange()
                if scalar_min == scalar_max:
                    scalar_max = scalar_min + 1.0
                lut.SetRange(scalar_min, scalar_max)
                lut.Build()

            colors = []
            for i in range(num_tuples):
                scalar_value = scalars.GetTuple1(i)
                rgb = [0.0, 0.0, 0.0]
                lut.GetColor(scalar_value, rgb)
                colors.append(Gf.Vec3f(rgb[0], rgb[1], rgb[2]))
            return colors

        return []

    @staticmethod
    def convert_vtk_file_to_usd(vtk_file_path: Union[str, Path], stage: "Usd.Stage" = None) -> None:
        """Convert a VTK file to a USD file.

        Parameters
        ----------
        vtk_file_path : Union[str, Path]
            Path to the VTK file to convert.
        stage : Usd.Stage
            Stage to add the converted USD data to.
        """
        vtk_file_path = Path(vtk_file_path)
        mesh_name = vtk_file_path.stem  # Use filename without extension

        if not vtk_file_path.exists():
            raise FileNotFoundError(f"VTK file not found: {vtk_file_path}")

        # Read VTK file
        reader = VTKConverter.get_vtk_reader(vtk_file_path)
        reader.SetFileName(str(vtk_file_path))
        reader.Update()

        return VTKConverter.convert_vtk_to_usd(reader.GetOutput(), stage, mesh_name)

    @staticmethod
    def convert_vtk_to_usd(
        data: "vtk.vtkDataSet", stage: "Usd.Stage" = None, mesh_name: str = "VTKMesh"
    ) -> "Usd.Stage":
        """Convert a VTK file to a USD stage.

        Parameters
        ----------
        vtk_file_path : Union[str, Path]
            Path to the VTK file to convert.
        stage : Usd.Stage
            Stage to add the VTK data to.

        Returns
        -------
        Usd.Stage
            Stage containing the VTK data.
        """
        if stage is None:
            stage = Usd.Stage.CreateNew("temp.usda")

        # Convert to polydata if necessary
        if isinstance(data, vtk.vtkPolyData):
            polydata = data
        elif isinstance(data, vtk.vtkUnstructuredGrid):
            # Convert unstructured grid to polydata
            geometry_filter = vtk.vtkGeometryFilter()
            geometry_filter.SetInputData(data)
            geometry_filter.Update()
            polydata = geometry_filter.GetOutput()
        else:
            # Try to extract surface from other data types
            try:
                geometry_filter = vtk.vtkGeometryFilter()
                geometry_filter.SetInputData(data)
                geometry_filter.Update()
                polydata = geometry_filter.GetOutput()
            except Exception as e:
                raise ValueError(f"Unable to convert VTK data type {type(data).__name__} to polydata: {e}")

        # Convert VTK polydata to USD mesh with unique name based on file
        VTKConverter.convert_polydata_to_usd_mesh(polydata, stage, mesh_name)

        return stage

    @staticmethod
    def get_vtk_reader(file_path: Path) -> vtk.vtkAlgorithm:
        """Get the appropriate VTK reader based on the file extension.

        Parameters
        ----------
        file_path : Path
            Path to the VTK file.
        """
        extension = file_path.suffix.lower()

        match extension:
            case ".vtk":
                return vtk.vtkPolyDataReader()
            case ".vtp":
                return vtk.vtkXMLPolyDataReader()
            case ".vtu":
                return vtk.vtkXMLUnstructuredGridReader()
            case ".vts":
                return vtk.vtkXMLStructuredGridReader()
            case ".obj":
                return vtk.vtkOBJReader()
            case ".ply":
                return vtk.vtkPLYReader()
            case ".stl":
                return vtk.vtkSTLReader()
            case _:
                raise ValueError(f"Unsupported VTK file format: {extension}")

    @staticmethod
    def convert_polydata_to_usd_mesh(
        polydata: vtk.vtkPolyData, stage: "Usd.Stage" = None, mesh_name: str = "VTKMesh"
    ) -> None:
        """Convert VTK polydata to USD mesh geometry.

        Parameters
        ----------
        polydata : vtk.vtkPolyData
            VTK polydata to convert.
        stage : Usd.Stage
            USD stage to add the mesh to.
        mesh_name : str, default: ``"VTKMesh"``
            Name of the mesh in USD.
        """
        if stage is None:
            stage = Usd.Stage.CreateNew("temp.usda")

        # Create a mesh primitive in USD with unique name
        mesh_path = f"/{mesh_name}"
        mesh_prim = UsdGeom.Mesh.Define(stage, mesh_path)

        # Get points from VTK
        points = polydata.GetPoints()
        if points:
            num_points = points.GetNumberOfPoints()
            point_array = []
            for i in range(num_points):
                point = points.GetPoint(i)
                point_array.append(Gf.Vec3f(point[0], point[1], point[2]))

            mesh_prim.CreatePointsAttr().Set(point_array)

        # Get faces from VTK
        polys = polydata.GetPolys()
        if polys:
            face_vertex_indices = []
            face_vertex_counts = []

            polys.InitTraversal()
            id_list = vtk.vtkIdList()

            while polys.GetNextCell(id_list):
                num_vertices = id_list.GetNumberOfIds()
                face_vertex_counts.append(num_vertices)

                for i in range(num_vertices):
                    face_vertex_indices.append(id_list.GetId(i))

            mesh_prim.CreateFaceVertexIndicesAttr().Set(face_vertex_indices)
            mesh_prim.CreateFaceVertexCountsAttr().Set(face_vertex_counts)

        # Handle colors if available
        point_data = polydata.GetPointData()
        cell_data = polydata.GetCellData()

        scalars = None
        interpolation = None

        if point_data and point_data.GetScalars() and point_data.GetScalars().GetNumberOfTuples() > 0:
            scalars = point_data.GetScalars()
            interpolation = UsdGeom.Tokens.vertex
        elif cell_data and cell_data.GetScalars() and cell_data.GetScalars().GetNumberOfTuples() > 0:
            scalars = cell_data.GetScalars()
            interpolation = UsdGeom.Tokens.uniform

        if scalars is not None:
            colors = VTKConverter._extract_display_colors_from_scalars(scalars)
            if colors:
                display_color_primvar = mesh_prim.CreateDisplayColorPrimvar(interpolation)
                display_color_primvar.Set(colors)

    @staticmethod
    def convert_usd_to_vtk(stage: "Usd.Stage", mesh_path: Optional[str] = None) -> Optional[vtk.vtkPolyData]:
        """Convert a USD mesh to VTK polydata.

        Parameters
        ----------
        stage : Usd.Stage
            USD stage containing the mesh.
        mesh_path : str, default: None
            Path to the mesh in USD. If ``None``, the first mesh in the stage is used.

        Returns
        -------
        Optional[vtk.vtkPolyData]
            Converted VTK polydata or ``None`` if conversion failed.
        """
        # If no mesh path is provided, find the first mesh in the stage
        if mesh_path is None:
            for prim in stage.Traverse():
                if prim.IsA(UsdGeom.Mesh):
                    mesh_path = str(prim.GetPath())
                    break

            if mesh_path is None:
                warnings.warn("No mesh found in the USD stage.")
                return None

        mesh_prim = stage.GetPrimAtPath(mesh_path)
        if not mesh_prim or not mesh_prim.IsA(UsdGeom.Mesh):
            warnings.warn(f"Mesh not found or invalid: {mesh_path}")
            return None

        mesh = UsdGeom.Mesh(mesh_prim)

        # Create a new VTK polydata object
        polydata = vtk.vtkPolyData()

        # Convert points
        points_attr = mesh.GetPointsAttr()
        if points_attr:
            points = points_attr.Get()
            if points:
                vtk_points = vtk.vtkPoints()
                for point in points:
                    vtk_points.InsertNextPoint(point[0], point[1], point[2])
                polydata.SetPoints(vtk_points)

        # Convert faces
        face_vertex_indices_attr = mesh.GetFaceVertexIndicesAttr()
        face_vertex_counts_attr = mesh.GetFaceVertexCountsAttr()

        if face_vertex_indices_attr and face_vertex_counts_attr:
            face_vertex_indices = face_vertex_indices_attr.Get()
            face_vertex_counts = face_vertex_counts_attr.Get()

            if face_vertex_indices and face_vertex_counts:
                vtk_faces = vtk.vtkCellArray()
                start = 0
                for count in face_vertex_counts:
                    vtk_faces.InsertNextCell(count, face_vertex_indices[start : start + count])
                    start += count
                polydata.SetPolys(vtk_faces)

        # Convert colors
        display_color_attr = mesh.GetDisplayColorAttr()
        if display_color_attr:
            colors = display_color_attr.Get()
            if colors:
                vtk_colors = vtk.vtkUnsignedCharArray()
                vtk_colors.SetNumberOfComponents(3)
                vtk_colors.SetName("Colors")

                for color in colors:
                    # USD colors are typically in 0-1 range, convert to 0-255 for VTK
                    r = int(color[0] * 255) if color[0] <= 1.0 else int(color[0])
                    g = int(color[1] * 255) if color[1] <= 1.0 else int(color[1])
                    b = int(color[2] * 255) if color[2] <= 1.0 else int(color[2])
                    vtk_colors.InsertNextTuple3(r, g, b)

                polydata.GetPointData().SetScalars(vtk_colors)

        return polydata

    def load_asset(self, asset_path: str, stage: "Usd.Stage") -> Optional["Usd.Stage"]:
        """Load a VTK asset into a given stage.

        Parameters
        ----------
        asset_path : str
            Path to the asset file.
        stage : Usd.Stage
            Stage to add the asset to.

        Returns
        -------
        Optional[Usd.Stage]
            Stage with the loaded asset or ``None`` if loading failed.
        """
        # Resolve and validate the asset path
        asset_file = Path(asset_path)
        if not asset_file.exists():
            warnings.warn(f"Asset not found: {asset_path}")
            return None

        resolved_path = asset_file.resolve()
        file_extension = resolved_path.suffix.lower()

        # Check if file format is supported
        supported_formats = [".vtk", ".vtp", ".vtu", ".vts", ".obj", ".ply", ".stl"]
        if file_extension not in supported_formats:
            warnings.warn(f"Unsupported file format: {file_extension}")
            return None

        # Convert VTK data directly into the provided stage
        try:
            self.convert_vtk_file_to_usd(str(resolved_path), stage)
            return stage
        except (FileNotFoundError, ValueError) as e:
            warnings.warn(f"Failed to convert VTK file {resolved_path}: {e}")
            return None
        except Exception as e:
            warnings.warn(f"Unexpected error converting {resolved_path}: {e}")
            return None
