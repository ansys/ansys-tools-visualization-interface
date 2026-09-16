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

"""
.. _ref_custom_picker:

====================
Create custom picker
====================

This example shows how to create a custom picker. In this case we will show how the default
picker is implemented through the ``AbstractPicker`` class.
"""

#####################################
# Import the ``AbstractPicker`` class
# ===================================

# Import the abstract picker class
from ansys.tools.visualization_interface.backends.pyvista.picker import AbstractPicker

# Import custom object meshes
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot

# Import plotter and color enum
from ansys.tools.visualization_interface import Plotter
from ansys.tools.visualization_interface.utils.color import Color


#####################################
# Create a custom picker class
# =================================

class CustomPicker(AbstractPicker):
    """Custom picker class that extends the AbstractPicker.
    This custom picker changes the color of picked objects to red and adds a label with the object's name.
    It also adds a label when hovering over an object.

    Parameters
    ----------
    plotter_backend : Plotter
        The plotter backend to use.
    plot_picked_names : bool, optional
        Whether to plot the names of picked objects, by default True.
    label : str, optional
        Extra parameter to exemplify the usage of custom parameters.
    """
    def __init__(self, plotter_backend: "Plotter", plot_picked_names: bool = True, label: str = "This label: ") -> None:
        """Initialize the ``Picker`` class."""
        # Picking variables
        self._plotter_backend = plotter_backend
        self._plot_picked_names = plot_picked_names
        self._label = label

        # Map that relates PyVista actors with the added actors by the picker
        self._picker_added_actors_map = {}

        # Dictionary of picked objects in MeshObject format.
        self._picked_dict = {}

        # Map that saves original colors of the plotted objects.
        self._origin_colors = {}

        # Hovering variables
        self._added_hover_labels = []

    def pick_select_object(self, custom_object: MeshObjectPlot, pt: "np.ndarray") -> None:
        """Add actor to picked list and add label if required.

        Parameters
        ----------
        custom_object : MeshObjectPlot
            The object to be selected.
        pt : np.ndarray
            The point where the object was picked.
        """
        added_actors = []

        # Pick only custom objects
        if isinstance(custom_object, MeshObjectPlot):
            self._origin_colors[custom_object] = custom_object.actor.prop.color
            custom_object.actor.prop.color = Color.PICKED.value

        # Get the name for the text label
        text = custom_object.name

        # If picking names is enabled, add a label to the picked object
        if self._plot_picked_names:
            label_actor = self._plotter_backend.pv_interface.scene.add_point_labels(
                [pt],
                [self._label + text],
                always_visible=True,
                point_size=0,
                render_points_as_spheres=False,
                show_points=False,
            )
            # Add the label actor to the list of added actors
            added_actors.append(label_actor)

        # Add the picked object to the picked dictionary if not already present, to keep track of it
        if custom_object.name not in self._picked_dict:
            self._picked_dict[custom_object.name] = custom_object
        # Add the picked object to the picked dictionary if not already present, to keep track of it
        self._picker_added_actors_map[custom_object.actor.name] = added_actors

    def pick_unselect_object(self, custom_object: MeshObjectPlot) -> None:
        """Remove actor from picked list and remove label if required.

        Parameters
        ----------
        custom_object : MeshObjectPlot
            The object to be unselected.
        """
        # remove actor from picked list and from scene
        if custom_object.name in self._picked_dict:
            self._picked_dict.pop(custom_object.name)

        # Restore original color if it was changed
        if isinstance(custom_object, MeshObjectPlot) and custom_object in self._origin_colors:
            custom_object.actor.prop.color = self._origin_colors[custom_object]

        # Remove any added actors (like labels) associated with this picked object
        if custom_object.actor.name in self._picker_added_actors_map:
            self._plotter_backend._pl.scene.remove_actor(self._picker_added_actors_map[custom_object.actor.name])
            self._picker_added_actors_map.pop(custom_object.actor.name)

    def hover_select_object(self, custom_object: MeshObjectPlot, actor: "Actor") -> None:
        """Add label to hovered object if required.

        Parameters
        ----------
        custom_object : MeshObjectPlot
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
        """Return the dictionary of picked objects.

        Returns
        -------
        dict
            Dictionary of picked objects.
        """
        return self._picked_dict

#######################################################
# Initialize the plotter backend with the custom picker
# =====================================================

from ansys.tools.visualization_interface.backends.pyvista import PyVistaBackend
pl_backend = PyVistaBackend(allow_picking=True, custom_picker=CustomPicker)


#################################################
# Create a custom object with a name to be picked
# ===============================================

import pyvista as pv

class CustomObject:
    def __init__(self):
        self.name = "CustomObject"
        self.mesh = pv.Cube(center=(1, 1, 0))

    def get_mesh(self):
        return self.mesh

    def name(self):
        return self.name

# Create a custom object
custom_cube = CustomObject()
custom_cube.name = "CustomCube"

#########################################
# Create a ``MeshObjectPlot`` instance
# =======================================

from ansys.tools.visualization_interface import MeshObjectPlot
# Create an instance
mesh_object_cube = MeshObjectPlot(custom_cube, custom_cube.get_mesh())

##################################################
# Display the plotter and interact with the object
# ================================================
# .. code-block:: python
#
#   pl = Plotter(backend=pl_backend)
#   pl.plot(mesh_object_cube)
#   pl.show()
