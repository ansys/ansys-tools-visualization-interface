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
from typing import Any, Iterable, List, Optional, Tuple, Union

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

    def _pv_to_mesh3d(self, pv_mesh: Union[PolyData, pv.UnstructuredGrid, pv.StructuredGrid, pv.ExplicitStructuredGrid, pv.MultiBlock]) -> Union[go.Mesh3d, list]:  # noqa: E501
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
                        # For volume meshes (e.g. pv.UnstructuredGrid), extract the surface
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
        elif isinstance(pv_mesh, (pv.StructuredGrid, pv.ExplicitStructuredGrid, pv.UnstructuredGrid)):
            # Handle single pv.UnstructuredGrid
            surface_mesh = pv_mesh.extract_surface()
            return self._convert_polydata_to_mesh3d(surface_mesh)
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

        # Check if there is an active point dataset
        array = None
        if triangulated_mesh.point_data.active_scalars_name:
            array_name = triangulated_mesh.point_data.active_scalars_name
            array = triangulated_mesh.point_data[array_name]

            # If each entry of the array is a vector, compute the norm
            if array.ndim > 1:
                array = ((array * array).sum(axis=1))**0.5

        return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, intensity=array)


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

        if isinstance(mesh, (PolyData, pv.StructuredGrid, pv.ExplicitStructuredGrid, pv.UnstructuredGrid, pv.MultiBlock)):  # noqa: E501
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

    def add_points(self, points, color="red", size=10.0, **kwargs):
        """Add point markers to the scene.

        Parameters
        ----------
        points : Union[List, Any]
            Points to add. Expected format: [[x1, y1, z1], [x2, y2, z2], ...] or Nx3 array.
        color : str, default: "red"
            Color of the points.
        size : float, default: 10.0
            Size of the point markers.
        **kwargs : dict
            Additional keyword arguments passed to Plotly's Scatter3d.

        Returns
        -------
        go.Scatter3d
            Plotly Scatter3d trace representing the added points.
        """
        import numpy as np

        # Convert points to numpy array
        points_array = np.asarray(points)
        if points_array.ndim == 1:
            points_array = points_array.reshape(-1, 3)

        # Create Plotly scatter trace for points
        scatter = go.Scatter3d(
            x=points_array[:, 0],
            y=points_array[:, 1],
            z=points_array[:, 2],
            mode='markers',
            marker=dict(
                size=size,
                color=color,
            ),
            **kwargs
        )

        self._fig.add_trace(scatter)
        return scatter

    def add_lines(self, points, connections=None, color="white", width=1.0, **kwargs):
        """Add line segments to the scene.

        Parameters
        ----------
        points : Union[List, Any]
            Points defining the lines. Expected format: [[x1, y1, z1], [x2, y2, z2], ...] or Nx3 array.
        connections : Optional[Union[List, Any]], default: None
            Line connectivity. If None, connects points sequentially.
            Expected format: [[start_idx1, end_idx1], [start_idx2, end_idx2], ...] or Mx2 array.
        color : str, default: "white"
            Color of the lines.
        width : float, default: 1.0
            Width of the lines.
        **kwargs : dict
            Additional keyword arguments passed to Plotly's Scatter3d.

        Returns
        -------
        Union[go.Scatter3d, List[go.Scatter3d]]
            Plotly Scatter3d trace(s) representing the added lines.
        """
        import numpy as np

        # Convert points to numpy array
        points_array = np.asarray(points)
        if points_array.ndim == 1:
            points_array = points_array.reshape(-1, 3)

        # Create connectivity if not provided (sequential connections)
        if connections is None:
            n_points = len(points_array)
            if n_points < 2:
                raise ValueError("At least 2 points are required to create lines")
            connections_array = np.array([[i, i + 1] for i in range(n_points - 1)])
        else:
            connections_array = np.asarray(connections)
            if connections_array.ndim == 1:
                connections_array = connections_array.reshape(-1, 2)

        # For Plotly, we need to create separate line traces or use None to break lines
        # We'll create line coordinates with None separators for disconnected segments
        x_coords = []
        y_coords = []
        z_coords = []

        for conn in connections_array:
            x_coords.extend([points_array[conn[0], 0], points_array[conn[1], 0], None])
            y_coords.extend([points_array[conn[0], 1], points_array[conn[1], 1], None])
            z_coords.extend([points_array[conn[0], 2], points_array[conn[1], 2], None])

        # Create Plotly scatter trace for lines
        line_trace = go.Scatter3d(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            mode='lines',
            line=dict(
                color=color,
                width=width,
            ),
            **kwargs
        )

        self._fig.add_trace(line_trace)
        return line_trace

    def add_planes(self, center=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), i_size=1.0, j_size=1.0, **kwargs):
        """Add a plane to the scene.

        Parameters
        ----------
        center : Tuple[float, float, float], default: (0.0, 0.0, 0.0)
            Center point of the plane (x, y, z).
        normal : Tuple[float, float, float], default: (0.0, 0.0, 1.0)
            Normal vector of the plane (x, y, z).
        i_size : float, default: 1.0
            Size of the plane in the i direction.
        j_size : float, default: 1.0
            Size of the plane in the j direction.
        **kwargs : dict
            Additional keyword arguments passed to Plotly's Mesh3d (e.g., color, opacity).

        Returns
        -------
        go.Mesh3d
            Plotly Mesh3d trace representing the added plane.
        """
        import numpy as np

        # Normalize the normal vector
        normal_array = np.array(normal)
        normal_array = normal_array / np.linalg.norm(normal_array)

        # Create two perpendicular vectors to the normal for the plane
        # Choose an arbitrary vector not parallel to normal
        if abs(normal_array[0]) < 0.9:
            v1 = np.cross(normal_array, [1, 0, 0])
        else:
            v1 = np.cross(normal_array, [0, 1, 0])
        v1 = v1 / np.linalg.norm(v1) * i_size / 2

        v2 = np.cross(normal_array, v1)
        v2 = v2 / np.linalg.norm(v2) * j_size / 2

        # Create plane corners
        center_array = np.array(center)
        corners = [
            center_array - v1 - v2,
            center_array + v1 - v2,
            center_array + v1 + v2,
            center_array - v1 + v2,
        ]

        # Extract coordinates
        x = [c[0] for c in corners]
        y = [c[1] for c in corners]
        z = [c[2] for c in corners]

        # Create two triangles to form the plane
        # Triangle indices: 0-1-2 and 0-2-3
        i_indices = [0, 0]
        j_indices = [1, 2]
        k_indices = [2, 3]

        # Set default styling if not provided
        if 'color' not in kwargs:
            kwargs['color'] = 'lightblue'
        if 'opacity' not in kwargs:
            kwargs['opacity'] = 0.5

        # Create Plotly mesh trace for plane
        plane_trace = go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=i_indices,
            j=j_indices,
            k=k_indices,
            **kwargs
        )

        self._fig.add_trace(plane_trace)
        return plane_trace

    def add_text(self, text, position, font_size=12, color="white", **kwargs):
        """Add text to the scene.

        Parameters
        ----------
        text : str
            Text string to display.
        position : Union[Tuple[float, float], Tuple[float, float, float]]
            Position for the text. For 3D, provide (x, y, z) coordinates.
            For 2D annotations, this will be interpreted as 3D coordinates.
        font_size : int, default: 12
            Font size for the text.
        color : str, default: "white"
            Color of the text.
        **kwargs : dict
            Additional keyword arguments passed to Plotly's Scatter3d or annotation.

        Returns
        -------
        Union[go.Scatter3d, dict]
            Plotly trace or annotation representing the added text.
        """
        # For Plotly, we'll use Scatter3d with text mode for 3D text
        if len(position) == 3:
            # 3D text using scatter points with text
            text_trace = go.Scatter3d(
                x=[position[0]],
                y=[position[1]],
                z=[position[2]],
                mode='text',
                text=[text],
                textfont=dict(
                    size=font_size,
                    color=color,
                ),
                **kwargs
            )
            self._fig.add_trace(text_trace)
            return text_trace
        else:
            # 2D annotation
            annotation = dict(
                x=position[0] if len(position) > 0 else 0,
                y=position[1] if len(position) > 1 else 0,
                text=text,
                font=dict(
                    size=font_size,
                    color=color,
                ),
                showarrow=False,
                xref="paper",
                yref="paper",
                **kwargs
            )
            self._fig.add_annotation(annotation)
            return annotation

    def add_mesh(
        self,
        mesh: Any,
        scalars: Optional[Union[str, Any]] = None,
        scalar_bar_args: Optional[dict] = None,
        show_edges: bool = False,
        nan_color: str = "grey",
        **kwargs
    ) -> Any:
        """Add a mesh to the scene.

        Note: This is a simplified implementation. For full mesh rendering
        in Plotly, see the plot() method which converts meshes to Mesh3d.

        Parameters
        ----------
        mesh : Any
            Mesh object to add.
        scalars : Optional[Union[str, Any]], default: None
            Scalars to use for coloring.
        scalar_bar_args : Optional[dict], default: None
            Arguments for the scalar bar.
        show_edges : bool, default: False
            Whether to show mesh edges.
        nan_color : str, default: "grey"
            Color to use for NaN values.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Any
            Plotly trace representing the mesh.
        """
        # Use the existing conversion method to convert the mesh
        mesh3d = self._pv_to_mesh3d(mesh)

        if isinstance(mesh3d, list):
            # MultiBlock case - add all traces
            for trace in mesh3d:
                self._fig.add_trace(trace)
            return mesh3d
        else:
            self._fig.add_trace(mesh3d)
            return mesh3d

    def add_point_labels(
        self,
        points: Union[List, Any],
        labels: List[str],
        font_size: int = 12,
        point_size: float = 5.0,
        **kwargs
    ) -> Any:
        """Add labels at 3D point locations.

        Parameters
        ----------
        points : Union[List, Any]
            Points where labels should be placed.
        labels : List[str]
            List of label strings to display at each point.
        font_size : int, default: 12
            Font size for the labels.
        point_size : float, default: 5.0
            Size of the point markers shown with labels.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        Any
            Plotly trace representing the labels.
        """
        import numpy as np

        points_array = np.asarray(points)
        if points_array.ndim == 1:
            points_array = points_array.reshape(-1, 3)

        # Create a scatter trace with both markers and text
        trace = go.Scatter3d(
            x=points_array[:, 0],
            y=points_array[:, 1],
            z=points_array[:, 2],
            mode='markers+text',
            text=labels,
            textfont=dict(size=font_size),
            marker=dict(size=point_size),
            **kwargs
        )
        self._fig.add_trace(trace)
        return trace

    def clear(self) -> None:
        """Clear all traces from the figure."""
        self._fig.data = []
