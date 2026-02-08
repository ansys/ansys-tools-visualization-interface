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

"""Module for the backend base class."""
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional, Tuple, Union


class BaseBackend(ABC):
    """Base class for plotting backends."""

    @abstractmethod
    def plot(self, plottable_object: Any, **plotting_options):
        """Plot the specified object."""
        raise NotImplementedError("plot method must be implemented")

    @abstractmethod
    def plot_iter(self, plotting_list: Iterable):
        """Plot the elements of an iterable."""
        raise NotImplementedError("plot_iter method must be implemented")

    @abstractmethod
    def show(self):
        """Show the plotted objects."""
        raise NotImplementedError("show method must be implemented")

    @abstractmethod
    def add_points(
        self,
        points: Union[List, Any],
        color: str = "red",
        size: float = 10.0,
        **kwargs
    ) -> Any:
        """Add point markers to the scene.

        Parameters
        ----------
        points : Union[List, Any]
            Points to add. Can be a list of coordinates or array-like object.
            Expected format: [[x1, y1, z1], [x2, y2, z2], ...] or Nx3 array.
        color : str, default: "red"
            Color of the points.
        size : float, default: 10.0
            Size of the point markers.
        **kwargs : dict
            Additional backend-specific keyword arguments.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added points.
        """
        raise NotImplementedError("add_points method must be implemented")

    @abstractmethod
    def add_lines(
        self,
        points: Union[List, Any],
        connections: Optional[Union[List, Any]] = None,
        color: str = "white",
        width: float = 1.0,
        **kwargs
    ) -> Any:
        """Add line segments to the scene.

        Parameters
        ----------
        points : Union[List, Any]
            Points defining the lines. Can be a list of coordinates or array-like object.
            Expected format: [[x1, y1, z1], [x2, y2, z2], ...] or Nx3 array.
        connections : Optional[Union[List, Any]], default: None
            Line connectivity. If None, connects points sequentially.
            Expected format: [[start_idx1, end_idx1], [start_idx2, end_idx2], ...]
            or Mx2 array where M is the number of lines.
        color : str, default: "white"
            Color of the lines.
        width : float, default: 1.0
            Width of the lines.
        **kwargs : dict
            Additional backend-specific keyword arguments.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added lines.
        """
        raise NotImplementedError("add_lines method must be implemented")

    @abstractmethod
    def add_planes(
        self,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        normal: Tuple[float, float, float] = (0.0, 0.0, 1.0),
        i_size: float = 1.0,
        j_size: float = 1.0,
        **kwargs
    ) -> Any:
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
            Additional backend-specific keyword arguments.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added plane.
        """
        raise NotImplementedError("add_planes method must be implemented")

    @abstractmethod
    def add_text(
        self,
        text: str,
        position: Union[Tuple[float, float], Tuple[float, float, float], str],
        font_size: int = 12,
        color: str = "white",
        **kwargs
    ) -> Any:
        """Add text to the scene.

        Parameters
        ----------
        text : str
            Text string to display.
        position : Union[Tuple[float, float], Tuple[float, float, float], str]
            Position for the text. Can be 2D (x, y) for screen coordinates,
            3D (x, y, z) for world coordinates, or a string position like
            'upper_left', 'upper_right', 'lower_left', 'lower_right',
            'upper_edge', 'lower_edge' (backend-dependent support).
        font_size : int, default: 12
            Font size for the text.
        color : str, default: "white"
            Color of the text.
        **kwargs : dict
            Additional backend-specific keyword arguments.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added text.
        """
        raise NotImplementedError("add_text method must be implemented")

    @abstractmethod
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

        Parameters
        ----------
        mesh : Any
            Mesh object to add. Can be a PyVista mesh (UnstructuredGrid, PolyData,
            MultiBlock) or other backend-specific mesh type.
        scalars : Optional[Union[str, Any]], default: None
            Scalars to use for coloring. Can be a string name of an array in
            the mesh, or an array-like object with scalar values.
        scalar_bar_args : Optional[dict], default: None
            Arguments for the scalar bar (colorbar). Common keys include:
            - 'title': Title for the scalar bar
            - 'vertical': Whether to orient vertically (default False)
        show_edges : bool, default: False
            Whether to show mesh edges.
        nan_color : str, default: "grey"
            Color to use for NaN values in scalars.
        **kwargs : dict
            Additional backend-specific keyword arguments.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added mesh.
        """
        raise NotImplementedError("add_mesh method must be implemented")

    @abstractmethod
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
            Points where labels should be placed. Can be a list of coordinates
            or array-like object. Expected format: [[x1, y1, z1], ...] or Nx3 array.
        labels : List[str]
            List of label strings to display at each point.
        font_size : int, default: 12
            Font size for the labels.
        point_size : float, default: 5.0
            Size of the point markers shown with labels.
        **kwargs : dict
            Additional backend-specific keyword arguments.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added labels.
        """
        raise NotImplementedError("add_point_labels method must be implemented")

    @abstractmethod
    def clear(self) -> None:
        """Clear all actors from the scene.

        This method removes all previously added objects (meshes, points, lines,
        text, etc.) from the visualization scene.
        """
        raise NotImplementedError("clear method must be implemented")
