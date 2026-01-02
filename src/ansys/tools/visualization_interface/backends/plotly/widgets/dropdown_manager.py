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
"""Module for dropdown management in Plotly figures."""
from typing import Any, Dict, List

import plotly.graph_objects as go


class DashDropdownManager:
    """Class to manage dropdown menus in a Plotly figure.

    This class allows adding dropdown menus to a Plotly figure for controlling
    mesh visibility and other properties.

    Parameters
    ----------
    fig : go.Figure
        The Plotly figure to which dropdowns will be added.
    """

    def __init__(self, fig: go.Figure):
        """Initialize DropdownManager."""
        self._fig = fig
        self._mesh_names = []

    def add_mesh_name(self, name: str) -> None:
        """Add a mesh name to track for dropdown functionality.

        Parameters
        ----------
        name : str
            The name of the mesh to track.
        """
        if name and name not in self._mesh_names:
            self._mesh_names.append(name)

    def get_mesh_names(self) -> List[str]:
        """Get the list of tracked mesh names.

        Returns
        -------
        List[str]
            List of mesh names.
        """
        return self._mesh_names.copy()

    def get_visibility_args_for_meshes(self, visible_mesh_names: List[str]) -> Dict[str, Any]:
        """Get visibility arguments for showing only specified meshes.

        Parameters
        ----------
        visible_mesh_names : List[str]
            List of mesh names that should be visible.

        Returns
        -------
        Dict[str, Any]
            Arguments for restyle method to set mesh visibility.
        """
        visibility = []
        for trace in self._fig.data:
            trace_name = getattr(trace, 'name', None)
            is_visible = trace_name in visible_mesh_names
            visibility.append(is_visible)

        return {"visible": visibility}

    def clear(self) -> None:
        """Clear all tracked mesh names."""
        self._mesh_names.clear()
