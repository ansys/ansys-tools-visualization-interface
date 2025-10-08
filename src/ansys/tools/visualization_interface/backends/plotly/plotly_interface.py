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

"""Plotly backend interface for visualization."""
from typing import Any, Iterable, Union

import plotly.graph_objects as go
from pyvista import PolyData

from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot


class PlotlyBackend(BaseBackend):
    """Plotly interface for visualization."""

    def __init__(self) -> None:
        """Initialize the Plotly backend."""
        self._fig = go.Figure()

    def _pv_to_mesh3d(self, pv_mesh: PolyData) -> go.Mesh3d:
        """Convert a PyVista PolyData mesh to Plotly Mesh3d format.

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


    def plot(self, plottable_object: Union[PolyData, MeshObjectPlot, go.Mesh3d], **plotting_options) -> None:
        """Plot a single object using Plotly.

        Parameters
        ----------
        plottable_object : Union[PolyData, MeshObjectPlot, go.Mesh3d]
            The object to plot. Can be a PyVista PolyData, a MeshObjectPlot, or a Plotly Mesh3d.
        plotting_options : dict
            Additional plotting options.
        """
        if isinstance(plottable_object, PolyData):
            mesh = self._pv_to_mesh3d(plottable_object)
            self._fig.add_trace(mesh)
        elif isinstance(plottable_object, MeshObjectPlot):
            pv_mesh = plottable_object.mesh
            mesh = self._pv_to_mesh3d(pv_mesh)
            self._fig.add_trace(mesh)
        elif isinstance(plottable_object, go.Mesh3d):
            self._fig.add_trace(plottable_object)
        else:
            try:
                self._fig.add_trace(plottable_object)
            except Exception:
                raise TypeError("Unsupported plottable_object type for PlotlyInterface.")

    def show(self,
            plottable_object=None,
            screenshot: str = None,
            name_filter=None,
            **kwargs) -> None:
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
        """
        if plottable_object is not None:
            self.plot(plottable_object)

        # Only show in browser if no screenshot is being taken
        if not screenshot:
            self._fig.show(**kwargs)

        if screenshot:
            screenshot_str = str(screenshot)
            if screenshot_str.endswith('.html'):
                self._fig.write_html(screenshot_str)
            else:
                self._fig.write_image(screenshot_str)
