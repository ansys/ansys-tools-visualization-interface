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

"""Plotly backend interface for visualization."""
from typing import Any, Iterable, Union

import plotly.graph_objects as go
import pyvista as pv
from pyvista import PolyData

from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.backends.plotly.widgets.button_manager import ButtonManager
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot


class PlotlyBackend(BaseBackend):
    """Plotly interface for visualization."""

    def __init__(self) -> None:
        """Initialize the Plotly backend."""
        self._fig = go.Figure()
        self._button_manager = ButtonManager(self._fig)

        # Stack buttons vertically on the left side
        self._button_manager.update_layout()

    def _pv_to_mesh3d(self, pv_mesh: Union[PolyData, pv.MultiBlock]) -> Union[go.Mesh3d, list]:
        """Convert a PyVista PolyData or MultiBlock mesh to Plotly Mesh3d format.

        Parameters
        ----------
        pv_mesh : Union[PolyData, pv.MultiBlock]
            The PyVista PolyData or MultiBlock mesh to convert.

        Returns
        -------
        Union[go.Mesh3d, list]
            The converted Plotly Mesh3d object(s). Returns a single Mesh3d for PolyData,
            or a list of Mesh3d objects for MultiBlock.
        """
        if isinstance(pv_mesh, pv.MultiBlock):
            # Handle MultiBlock by converting each block and returning a list
            mesh_list = []
            for i, block in enumerate(pv_mesh):
                if block is not None:
                    # Convert each block to PolyData if needed
                    if hasattr(block, 'extract_surface'):
                        # For volume meshes, extract the surface
                        block = block.extract_surface()
                    elif not isinstance(block, PolyData):
                        # Try to convert to PolyData
                        try:
                            block = block.cast_to_polydata()
                        except AttributeError:
                            continue  # Skip blocks that can't be converted

                    # Now convert the PolyData block
                    mesh_3d = self._convert_polydata_to_mesh3d(block)
                    mesh_list.append(mesh_3d)
            return mesh_list
        else:
            # Handle single PolyData
            return self._convert_polydata_to_mesh3d(pv_mesh)

    def _convert_polydata_to_mesh3d(self, pv_mesh: PolyData) -> go.Mesh3d:
        """Convert a single PolyData mesh to Plotly Mesh3d format.

        Parameters
        ----------
        pv_mesh : PolyData
            The PyVista PolyData mesh to convert.

        Returns
        -------
        go.Mesh3d
            The converted Plotly Mesh3d object.
        """
        points = pv_mesh.points
        x, y, z = points[:, 0], points[:, 1], points[:, 2]

        # Convert mesh to triangular mesh if needed, since Plotly only supports triangular faces
        triangulated_mesh = pv_mesh.triangulate()

        # Extract triangular faces
        faces = triangulated_mesh.faces.reshape((-1, 4))  # Now we know all faces are triangular (3 vertices + count)
        i, j, k = faces[:, 1], faces[:, 2], faces[:, 3]

        return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k)


    @property
    def layout(self) -> Any:
        """Get the current layout of the Plotly figure.

        Returns
        -------
        Any
            The current layout of the Plotly figure.
        """
        return self._fig.layout

    @layout.setter
    def layout(self, new_layout: Any) -> None:
        """Set a new layout for the Plotly figure.

        Parameters
        ----------
        new_layout : Any
            New layout to set for the Plotly figure.
        """
        self._fig.update_layout(new_layout)

    def plot_iter(self, plotting_list: Iterable[Any]) -> None:
        """Plot multiple objects using Plotly.

        Parameters
        ----------
        plotting_list : Iterable[Any]
            An iterable of objects to plot.
        """
        for item in plotting_list:
            self.plot(item)


    def plot(
            self,
            plottable_object: Union[PolyData, pv.MultiBlock, MeshObjectPlot, go.Mesh3d],
            name: str = None,
            **plotting_options
        ) -> None:
        """Plot a single object using Plotly.

        Parameters
        ----------
        plottable_object : Union[PolyData, pv.MultiBlock, MeshObjectPlot, go.Mesh3d]
            The object to plot. Can be a PyVista PolyData, MultiBlock, a MeshObjectPlot, or a Plotly Mesh3d.
        plotting_options : dict
            Additional plotting options.
        name : str, optional
            Name of the mesh for labeling in Plotly. Overrides the name from MeshObjectPlot if provided.
        """
        if isinstance(plottable_object, MeshObjectPlot):
            mesh = plottable_object.mesh
            name = name or plottable_object.name
        else:
            mesh = plottable_object

        if isinstance(mesh, (PolyData, pv.MultiBlock)):
            mesh_result = self._pv_to_mesh3d(mesh)
            # Handle both single mesh and list of meshes
            if isinstance(mesh_result, list):
                # MultiBlock case - add all meshes
                for mesh_3d in mesh_result:
                    mesh_3d.name = name or mesh_3d.name
                    self._fig.add_trace(mesh_3d)
            else:
                mesh_result.name = name if name is not None else mesh_result.name
                self._fig.add_trace(mesh_result)
        elif isinstance(plottable_object, go.Mesh3d):
            if name is not None:
                plottable_object.name = name
            self._fig.add_trace(plottable_object)
        else:
            # Try in case there is a compatible Plotly object
            try:
                plottable_object.name = name
                self._fig.add_trace(plottable_object)
            except Exception:
                raise TypeError("Unsupported plottable_object type for PlotlyInterface.")

    def show(self,
            plottable_object=None,
            screenshot: str = None,
            name_filter=None,
            **kwargs) -> Union[go.Figure, None]:
        """Render the Plotly scene.

        Parameters
        ----------
        plottable_object : Any, optional
            Object to show, by default None.
        screenshot : str, optional
            Path to save a screenshot, by default None.
        name_filter : bool, optional
            Flag to filter the object, by default None.
        kwargs : dict
            Additional options the selected backend accepts.

        Returns
        -------
        Union[go.Figure, None]
            The figure of the plot if in doc building environment. Else, None.
        """
        import os
        if os.environ.get("PYANSYS_VISUALIZER_DOC_MODE"):
            return self._fig

        if plottable_object is not None:
            self.plot(plottable_object)

        # Only show in browser if no screenshot is being taken
        if not screenshot:
            self._fig.show(**kwargs)
        else:
            screenshot_str = str(screenshot)
            if screenshot_str.endswith('.html'):
                self._fig.write_html(screenshot_str)
            else:
                self._fig.write_image(screenshot_str)
