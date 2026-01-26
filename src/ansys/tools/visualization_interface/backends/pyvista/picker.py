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

"""Module for managing picking and hovering of objects in a PyVista plotter."""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

from ansys.tools.visualization_interface.types.edge_plot import EdgePlot
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot
from ansys.tools.visualization_interface.utils.color import Color

if TYPE_CHECKING:
    import numpy as np
    from pyvista import Actor

    from ansys.tools.visualization_interface.backends.pyvista.pyvista import Plotter

class AbstractPicker(ABC):
    """Abstract base class for pickers."""
    @abstractmethod
    def __init__(self, plotter_backend: "Plotter", **kwargs) -> None:
        """Initialize the ``AbstractPicker`` class."""
        pass

    @abstractmethod
    def pick_select_object(self, custom_object: Union[MeshObjectPlot, EdgePlot], pt: "np.ndarray") -> None:
        """Determine actions to take when an object is selected."""
        pass

    @abstractmethod
    def pick_unselect_object(self, custom_object: Union[MeshObjectPlot, EdgePlot]) -> None:
        """Determine actions to take when an object is unselected."""
        pass
    @abstractmethod
    def hover_select_object(self, custom_object: Union[MeshObjectPlot, EdgePlot], pt: "np.ndarray") -> None:
        """Determine actions to take when an object is hovered over."""
        pass

    @abstractmethod
    def hover_unselect_object(self, custom_object: Union[MeshObjectPlot, EdgePlot]) -> None:
        """Determine actions to take when an object is unhovered."""
        pass

    @property
    @abstractmethod
    def picked_dict(self) -> dict:
        """Return the dictionary of picked objects."""
        pass


class Picker(AbstractPicker):
    """Class to manage picking and hovering of objects in the plotter.

    This class is responsible for managing the selection and deselection of objects
    in the plotter, both through direct picking and hovering. It keeps track of the
    currently selected and hovered objects, and provides methods to select and unselect
    them.


    Parameters
    ----------
    plotter_backend : Plotter
        The plotter instance to which this picker is attached.
    plot_picked_names : bool, optional
        Whether to display the names of picked objects in the plotter. Defaults to True.
    """

    def __init__(self, plotter_backend: "Plotter", plot_picked_names: bool = True) -> None:
        """Initialize the ``Picker`` class."""
        # Picking variables
        self._plotter_backend = plotter_backend
        self._plot_picked_names = plot_picked_names

        # Map that relates PyVista actors with the added actors by the picker
        self._picker_added_actors_map = {}

        # Dictionary of picked objects in MeshObject format.
        self._picked_dict = {}

        # Map that saves original colors of the plotted objects.
        self._origin_colors = {}

        # Hovering variables
        self._added_hover_labels = []

    def pick_select_object(self, custom_object: Union[MeshObjectPlot, EdgePlot], pt: "np.ndarray") -> None:
        """Add actor to picked list and add label if required.

        Parameters
        ----------
        custom_object : Union[MeshObjectPlot, EdgePlot]
            The object to be selected.
        pt : np.ndarray
            The point where the object was picked.
        """
        added_actors = []

        # Add edges if selecting an object
        if isinstance(custom_object, MeshObjectPlot):
            self._origin_colors[custom_object] = custom_object.actor.prop.color
            custom_object.actor.prop.color = Color.PICKED.value
            children_list = custom_object.edges
            if children_list is not None:
                for edge in children_list:
                    edge.actor.SetVisibility(True)
                    edge.actor.prop.color = Color.EDGE.value
        elif isinstance(custom_object, EdgePlot):
            custom_object.actor.prop.color = Color.PICKED_EDGE.value

        text = custom_object.name

        if self._plot_picked_names:
            label_actor = self._plotter_backend.pv_interface.scene.add_point_labels(
                [pt],
                [text],
                always_visible=True,
                point_size=0,
                render_points_as_spheres=False,
                show_points=False,
            )
            added_actors.append(label_actor)

        # Use actor name as key to ensure uniqueness (custom_object.name might not be unique)
        if custom_object.actor.name not in self._picked_dict:
            self._picked_dict[custom_object.actor.name] = custom_object

        self._picker_added_actors_map[custom_object.actor.name] = added_actors

    def pick_unselect_object(
        self, custom_object: Union[MeshObjectPlot, EdgePlot], restore_visibility: bool = True
    ) -> None:
        """Remove actor from picked list and remove label if required.

        Parameters
        ----------
        custom_object : Union[MeshObjectPlot, EdgePlot]
            The object to be unselected.
        restore_visibility : bool, default: True
            Whether to restore visibility when unpicking. Default is True which
            restores visibility in all unpick scenarios (toggle-click, empty space, etc.).
        """
        # Restore visibility of object and its subtree when unpicking (if requested)
        if restore_visibility and isinstance(custom_object, MeshObjectPlot):
            self._restore_subtree_visibility(custom_object)

        # remove actor from picked list and from scene (use actor name as key)
        if custom_object.actor.name in self._picked_dict:
            self._picked_dict.pop(custom_object.actor.name)

        if isinstance(custom_object, MeshObjectPlot) and custom_object in self._origin_colors:
            custom_object.actor.prop.color = self._origin_colors[custom_object]
        elif isinstance(custom_object, EdgePlot):
            custom_object.actor.prop.color = Color.EDGE.value

        if custom_object.actor.name in self._picker_added_actors_map:
            self._plotter_backend._pl.scene.remove_actor(self._picker_added_actors_map[custom_object.actor.name])

            # remove actor and its children(edges) from the scene
            if isinstance(custom_object, MeshObjectPlot):
                if custom_object.edges is not None:
                    for edge in custom_object.edges:
                        # hide edges in the scene
                        edge.actor.SetVisibility(False)
                        # recursion
                        self.pick_unselect_object(edge, restore_visibility=restore_visibility)
            self._picker_added_actors_map.pop(custom_object.actor.name)

    def _restore_subtree_visibility(self, custom_object: MeshObjectPlot) -> None:
        """Restore visibility of an object and all its children.

        Parameters
        ----------
        custom_object : MeshObjectPlot
            The object whose subtree visibility should be restored.
        """
        # Restore this object's visibility
        custom_object.visible = True

        # Recursively restore all children
        for child in custom_object._children:
            self._restore_subtree_visibility(child)

    def hover_select_object(self, custom_object: Union[MeshObjectPlot, EdgePlot], actor: "Actor") -> None:
        """Add label to hovered object if required.

        Parameters
        ----------
        custom_object : Union[MeshObjectPlot, EdgePlot]
            The object to be hovered over.
        actor : vtkActor
            The actor corresponding to the hovered object.
        """
        for label in self._added_hover_labels:
            self._plotter_backend._pl.scene.remove_actor(label)
        label_actor = self._plotter_backend._pl.scene.add_point_labels(
            [actor.GetCenter()],
            [custom_object.name],
            always_visible=True,
            point_size=0,
            render_points_as_spheres=False,
            show_points=False,
        )
        self._added_hover_labels.append(label_actor)

    def hover_unselect_object(self):
        """Remove all hover labels from the scene."""
        for label in self._added_hover_labels:
            self._plotter_backend._pl.scene.remove_actor(label)

    @property
    def picked_dict(self) -> dict:
        """Return the dictionary of picked objects."""
        return self._picked_dict