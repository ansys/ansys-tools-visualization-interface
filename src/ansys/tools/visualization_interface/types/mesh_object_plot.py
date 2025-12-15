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
"""Provides the ``MeshObjectPlot`` class."""


from typing import TYPE_CHECKING, Any, List, Type, Union

import pyvista as pv

from ansys.tools.visualization_interface.types.edge_plot import EdgePlot

if TYPE_CHECKING:
    from plotly.graph_objects import Mesh3d

class MeshObjectPlot:
    """Relates a custom object with a mesh, provided by the consumer library."""

    def __init__(
        self,
        custom_object: Any,
        mesh: Union[pv.PolyData, pv.MultiBlock, "Mesh3d"],
        actor: pv.Actor = None,
        edges: List[EdgePlot] = None,
        children: List["MeshObjectPlot"] = None,
        parent: "MeshObjectPlot" = None,
    ) -> None:
        """Relates a custom object with a mesh provided by the consumer library.

        This class is meant to be used as a mapper between a custom object and its mesh
        representation. It is used to store the custom object and its mesh, and to relate
        the custom object with its PyVista actor and its edges.

        Parameters
        ----------
        custom_object : Any
            Any object that the consumer library wants to relate with a mesh.
        mesh : Union[pv.PolyData, pv.MultiBlock, Mesh3d]
            PyVista mesh that represents the custom object.
        actor : pv.Actor, default: None
            Actor of the mesh in the plotter.
        edges : List[EdgePlot], default: None
            Edges of the object if it has any.

        """
        self._custom_object = custom_object
        self._mesh = mesh
        self._actor = actor
        self._edges = edges
        self._children: List["MeshObjectPlot"] = children if children is not None else []
        self._parent: "MeshObjectPlot" = parent

    def add_child(self, child: "MeshObjectPlot"):
        """Set a child MeshObjectPlot to the current object.

        This method is used to set a child MeshObjectPlot to the current object.
        It is useful when the custom object has a hierarchical structure, and
        the consumer library wants to relate the child objects with their meshes.

        Parameters
        ----------
        child : MeshObjectPlot
            Child MeshObjectPlot to be set.

        """
        child.parent = self
        self._children.append(child)

    @property
    def parent(self) -> "MeshObjectPlot":
        """Get the parent MeshObjectPlot of the current object.

        This method is used to set a parent MeshObjectPlot to the current object.
        It is useful when the custom object has a hierarchical structure, and
        the consumer library wants to relate the parent objects with their meshes.

        Parameters
        ----------
        parent : MeshObjectPlot
            Parent MeshObjectPlot to be set.

        """
        return self._parent

    @parent.setter
    def parent(self, parent: "MeshObjectPlot"):
        """Set the parent MeshObjectPlot of the current object.

        Parameters
        ----------
        parent : MeshObjectPlot
            Parent MeshObjectPlot to be set.
        """
        self._parent = parent

    @property
    def mesh(self) -> Union[pv.PolyData, pv.MultiBlock, "Mesh3d"]:
        """Mesh of the object in PyVista format.

        Returns
        -------
        Union[pv.PolyData, pv.MultiBlock]
            Mesh of the object.

        """
        return self._mesh

    @mesh.setter
    def mesh(self, mesh: Union[pv.PolyData, pv.MultiBlock, "Mesh3d"]):
        """Set the mesh of the object in PyVista format.

        Parameters
        ----------
        mesh : Union[pv.PolyData, pv.MultiBlock, Mesh3d]
            Mesh of the object.

        """
        self._mesh = mesh

    @property
    def custom_object(self) -> Any:
        """Custom object.

        Returns
        -------
        Any
            Custom object.

        """
        return self._custom_object

    @custom_object.setter
    def custom_object(self, custom_object: Any):
        """Set the custom object.

        Parameters
        ----------
        custom_object : Any
            Custom object.

        """
        self._custom_object = custom_object

    @property
    def actor(self) -> pv.Actor:
        """PyVista actor of the object in the plotter.

        Returns
        -------
        pv.Actor
            PyVista actor of the object.

        """
        return self._actor

    @actor.setter
    def actor(self, actor: pv.Actor):
        """Set the PyVista actor of the object in the plotter.

        Parameters
        ----------
        actor : pv.Actor
            PyVista actor of the object.

        """
        self._actor = actor

    @property
    def edges(self) -> List[EdgePlot]:
        """Edges of the object.

        Returns
        -------
        List[EdgePlot]
            Edges of the object.

        """
        return self._edges

    @edges.setter
    def edges(self, edges: List[EdgePlot]):
        """Set the edges of the object.

        Parameters
        ----------
        edges : List[EdgePlot]
            Edges of the object.

        """
        self._edges = edges

    @property
    def name(self) -> str:
        """Name of the object.

        Returns
        -------
        str
            Name of the object.

        """
        if hasattr(self._custom_object, "name"):
            return self._custom_object.name
        elif hasattr(self._custom_object, "id"):
            return self._custom_object.id
        else:
            return "Unknown"

    @property
    def mesh_type(self) -> Type:
        """Type of the mesh.

        Returns
        -------
        type
            Type of the mesh.

        """
        return type(self._mesh)