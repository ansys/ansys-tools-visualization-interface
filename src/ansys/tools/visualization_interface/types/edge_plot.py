# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Provides the edge type for plotting."""


from typing import TYPE_CHECKING, Any

import pyvista as pv

if TYPE_CHECKING:
    from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot

class EdgePlot:
    """Provides the mapper class for relating PyAnsys object edges with its PyVista actor.

    Parameters
    ----------
    actor : ~pyvista.Actor
        PyVista actor that represents the edge.
    edge_object : Edge
        PyAnsys object edge that is represented by the PyVista actor.
    parent : MeshObjectPlot, default: None
        Parent PyAnsys object of the edge.

    """

    def __init__(self, actor: pv.Actor, edge_object: Any, parent: Any = None) -> None:
        """Initialize ``EdgePlot`` variables."""
        self._actor = actor
        self._object = edge_object
        self._parent = parent

    @property
    def actor(self) -> pv.Actor:
        """PyVista actor of the object.

        Returns
        -------
        ~pyvista.Actor
            PyVista actor.

        """
        return self._actor

    @property
    def edge_object(self) -> Any:
        """PyAnsys edge.

        Returns
        -------
        Any
            PyAnsys edge.

        """
        return self._object

    @property
    def parent(self) -> Any:
        """Parent PyAnsys object of the edge.

        Returns
        -------
        Any
            Parent PyAnsys object.

        """
        return self._parent

    @property
    def name(self) -> str:
        """Name of the edge.

        Returns
        -------
        str
            Name of the edge.

        """
        if self.parent:
            return f"{self.parent.name}-{self.edge_object.id}"
        else:
            return self.edge_object.id

    @parent.setter
    def parent(self, parent: "MeshObjectPlot"):
        """Set the parent object of the edge.

        Parameters
        ----------
        parent : MeshObjectPlot
            Parent of the edge.

        """
        self._parent = parent
