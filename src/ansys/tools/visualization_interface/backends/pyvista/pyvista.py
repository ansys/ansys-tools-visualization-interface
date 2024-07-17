# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Provides a wrapper to aid in plotting."""
from abc import abstractmethod

from beartype.typing import Any, Dict, List, Optional, Union
import numpy as np
import pyvista as pv
from vtkmodules.vtkCommonCore import vtkCommand
from vtkmodules.vtkInteractionWidgets import vtkHoverWidget
from vtkmodules.vtkRenderingCore import vtkPointPicker

import ansys.tools.visualization_interface
from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.backends.pyvista.pyvista_interface import PyVistaInterface
from ansys.tools.visualization_interface.backends.pyvista.trame_local import (
    _HAS_TRAME,
    TrameVisualizer,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.displace_arrows import (
    CameraPanDirection,
    DisplacementArrow,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.hide_buttons import HideButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.measure import MeasureWidget
from ansys.tools.visualization_interface.backends.pyvista.widgets.mesh_slider import (
    MeshSliderWidget,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.ruler import Ruler
from ansys.tools.visualization_interface.backends.pyvista.widgets.screenshot import ScreenshotButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.view_button import (
    ViewButton,
    ViewDirection,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget
from ansys.tools.visualization_interface.types.edge_plot import EdgePlot
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot
from ansys.tools.visualization_interface.utils.color import Color
from ansys.tools.visualization_interface.utils.logger import logger


class PyVistaBackendInterface(BaseBackend):
    """Provides the interface for the Visualization Interface Tool plotter.

    This class is intended to be used as a base class for the custom plotters
    in the different PyAnsys libraries. It provides the basic plotter functionalities,
    such as adding objects and enabling widgets and picking capabilities. It also
    provides the ability to show the plotter using the `trame <https://kitware.github.io/trame/index.html>`_
    service.

    You can override the ``plot_iter()``, ``plot()``, and ``picked_operation()`` methods.
    The ``plot_iter()`` method is intended to plot a list of objects to the plotter, while the
    ``plot()`` method is intended to plot a single object to the plotter. The ``show()`` method is
    intended to show the plotter. The ``picked_operation()`` method is
    intended to perform an operation on the picked objects.

    Parameters
    ----------
    use_trame : Optional[bool], default: None
        Whether to activate the usage of the trame UI instead of the Python window.
    allow_picking : Optional[bool], default: False
        Whether to allow picking capabilities in the window. Incompatible with hovering.
        Picking will take precedence over hovering.
    allow_hovering : Optional[bool], default: False
        Whether to allow hovering capabilities in the window. Incompatible with picking.
        Picking will take precedence over hovering.
    """

    def __init__(
        self,
        use_trame: Optional[bool] = None,
        allow_picking: Optional[bool] = False,
        allow_hovering: Optional[bool] = False,
        plot_picked_names: Optional[bool] = False,
        show_plane: Optional[bool] = False,
        **plotter_kwargs,
    ) -> None:
        """Initialize the ``use_trame`` parameter and save the current ``pv.OFF_SCREEN`` value."""
        # Check if the use of trame was requested
        if use_trame is None:
            use_trame = ansys.tools.visualization_interface.USE_TRAME

        self._use_trame = use_trame
        self._allow_picking = allow_picking
        self._allow_hovering = allow_hovering
        if self._allow_picking and self._allow_hovering:
            logger.warning(
                "Picking and hovering are incompatible. Picking will take precedence."
            )
            self._allow_hovering = False
        self._pv_off_screen_original = bool(pv.OFF_SCREEN)
        self._plot_picked_names = plot_picked_names
        # Map that relates PyVista actors with PyAnsys objects
        self._object_to_actors_map = {}

        # PyVista plotter
        self._pl = None

        # List of picked objects in MeshObject format.
        self._picked_list = set()

        # Map that relates PyVista actors with the added actors by the picker
        self._picker_added_actors_map = {}

        # Map that relates PyVista actors with EdgePlot objects
        self._edge_actors_map = {}

        # List of widgets added to the plotter.
        self._widgets = []

        # Map that saves original colors of the plotted objects.
        self._origin_colors = {}

        # Enable the use of trame if requested and available
        if self._use_trame and _HAS_TRAME:
            # avoids GUI window popping up
            pv.OFF_SCREEN = True
            self._pl = PyVistaInterface(
                enable_widgets=False, show_plane=show_plane, **plotter_kwargs
            )
        elif self._use_trame and not _HAS_TRAME:
            warn_msg = (
                "'use_trame' is active but trame dependencies are not installed."
                "Consider installing 'pyvista[trame]' to use this functionality."
            )
            logger.warning(warn_msg)
            self._pl = PyVistaInterface(show_plane=show_plane)
        else:
            self._pl = PyVistaInterface(show_plane=show_plane)

        self._enable_widgets = self._pl._enable_widgets

        self._hover_picker = vtkPointPicker() if self. _allow_hovering else None
        self._hover_widget = vtkHoverWidget() if self. _allow_hovering else None
        self._added_hover_labels = []

    @property
    def pv_interface(self) -> PyVistaInterface:
        """PyVista interface."""
        return self._pl

    def enable_widgets(self):
        """Enable the widgets for the plotter."""
        # Create Plotter widgets
        if self._enable_widgets:
            self._widgets: List[PlotterWidget] = []
            self._widgets.append(Ruler(self._pl._scene))
            [
                self._widgets.append(DisplacementArrow(self._pl._scene, direction=dir))
                for dir in CameraPanDirection
            ]
            [
                self._widgets.append(ViewButton(self._pl._scene, direction=dir))
                for dir in ViewDirection
            ]
            self._widgets.append(MeasureWidget(self))
            self._widgets.append(ScreenshotButton(self))
            self._widgets.append(MeshSliderWidget(self))
            self._widgets.append(HideButton(self))

    def add_widget(self, widget: Union[PlotterWidget, List[PlotterWidget]]):
        """Add one or more custom widgets to the plotter.

        Parameters
        ----------
        widget : Union[PlotterWidget, List[PlotterWidget]]
            One or more custom widgets.

        """
        if isinstance(widget, list):
            self._widgets.extend(widget)
            widget.update()
        else:
            self._widgets.append(widget)
            widget.update()

    def select_object(self, custom_object: Union[MeshObjectPlot, EdgePlot], pt: np.ndarray) -> None:
        """Select a custom object in the plotter.

        This method highlights the edges of a body and adds a label. It also adds
        the object to the ``_picked_list`` and the actor to the ``_picker_added_actors_map``.

        Parameters
        ----------
        custom_object : Union[MeshObjectPlot, EdgePlot]
            Custom object to select.
        pt : ~numpy.ndarray
            Set of points to determine the label position.

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
            label_actor = self._pl.scene.add_point_labels(
                [pt],
                [text],
                always_visible=True,
                point_size=0,
                render_points_as_spheres=False,
                show_points=False,
            )
            added_actors.append(label_actor)

        if custom_object not in self._picked_list:
            self._picked_list.add(custom_object)

        self._picker_added_actors_map[custom_object.actor.name] = added_actors

    def unselect_object(self, custom_object: Union[MeshObjectPlot, EdgePlot]) -> None:
        """Unselect a custom object in the plotter.

        This method removes edge highlighting and the label from a plotter actor and removes
        the object from the Visualization Interface Tool object selection.

        Parameters
        ----------
        custom_object : Union[MeshObjectPlot, EdgePlot]
            Custom object to unselect.

        """
        # remove actor from picked list and from scene
        if custom_object in self._picked_list:
            self._picked_list.remove(custom_object)

        if isinstance(custom_object, MeshObjectPlot) and custom_object in self._origin_colors:
            custom_object.actor.prop.color = self._origin_colors[custom_object]
        elif isinstance(custom_object, EdgePlot):
            custom_object.actor.prop.color = Color.EDGE.value

        if custom_object.actor.name in self._picker_added_actors_map:
            self._pl.scene.remove_actor(self._picker_added_actors_map[custom_object.actor.name])

            # remove actor and its children(edges) from the scene
            if isinstance(custom_object, MeshObjectPlot):
                if custom_object.edges is not None:
                    for edge in custom_object.edges:
                        # hide edges in the scene
                        edge.actor.SetVisibility(False)
                        # recursion
                        self.unselect_object(edge)
            self._picker_added_actors_map.pop(custom_object.actor.name)

    def picker_callback(self, actor: "pv.Actor") -> None:
        """Define the callback for the element picker.

        Parameters
        ----------
        actor : ~pyvista.Actor
            Actor to select for the picker.

        """
        pt = self._pl.scene.picked_point

        # if object is a body/component
        if actor in self._object_to_actors_map:
            body_plot = self._object_to_actors_map[actor]
            if body_plot not in self._picked_list:
                self.select_object(body_plot, pt)
            else:
                self.unselect_object(body_plot)

        # if object is an edge
        elif actor in self._edge_actors_map and actor.GetVisibility():
            edge = self._edge_actors_map[actor]
            if edge not in self._picked_list:
                self.select_object(edge, pt)
            else:
                self.unselect_object(edge)
                actor.prop.color = Color.EDGE.value

    def hover_callback(self, _widget, event_name) -> None:
        """Define the callback for the element hover.

        Parameters
        ----------
        actor : ~pyvista.Actor
            Actor to hover for the picker.

        """
        plotter = self._pl.scene
        x, y = plotter.iren.interactor.GetEventPosition()
        renderer = plotter.iren.get_poked_renderer(x, y)
        self._hover_picker.Pick(x, y, 0, renderer)
        actor = self._hover_picker.GetActor()
        if actor is not None and actor in self._object_to_actors_map:
            custom_object = self._object_to_actors_map[actor]
            for label in self._added_hover_labels:
                self._pl.scene.remove_actor(label)
            label_actor = self._pl.scene.add_point_labels(
                [actor.GetCenter()],
                [custom_object.name],
                always_visible=True,
                point_size=0,
                render_points_as_spheres=False,
                show_points=False,
            )
            self._added_hover_labels.append(label_actor)
        else:
            for label in self._added_hover_labels:
                self._pl.scene.remove_actor(label)

    def compute_edge_object_map(self) -> Dict[pv.Actor, EdgePlot]:
        """Compute the mapping between plotter actors and ``EdgePlot`` objects.

        Returns
        -------
        Dict[~pyvista.Actor, EdgePlot]
            Dictionary defining the mapping between plotter actors and ``EdgePlot`` objects.

        """
        for mesh_object in self._object_to_actors_map.values():
            # get edges only from bodies
            if mesh_object.edges is not None:
                for edge in mesh_object.edges:
                    self._edge_actors_map[edge.actor] = edge

    def enable_picking(self):
        """Enable picking capabilities in the plotter."""
        self._pl.scene.enable_mesh_picking(
            callback=self.picker_callback,
            use_actor=True,
            show=False,
            show_message=False,
            picker="cell",
        )

    def enable_hover(self):
        """Enable hover capabilities in the plotter."""
        self._hover_widget = vtkHoverWidget()
        self._hover_widget.SetInteractor(self._pl.scene.iren.interactor)
        self._hover_widget.SetTimerDuration(100)  # Time (ms) required to trigger a hover event
        self._hover_widget.AddObserver(vtkCommand.TimerEvent, self.hover_callback)  # Start of hover
        self._hover_widget.AddObserver(vtkCommand.EndInteractionEvent, self.hover_callback)  # Hover ended (mouse moved)
        self._hover_widget.EnabledOn()


    def disable_picking(self):
        """Disable picking capabilities in the plotter."""
        self._pl.scene.disable_picking()

    def disable_hover(self):
        """Disable hover capabilities in the plotter."""
        self._hover_widget.EnabledOff()

    def show(
        self,
        plottable_object: Any = None,
        screenshot: Optional[str] = None,
        view_2d: Dict = None,
        name_filter: str = None,
        **plotting_options,
    ) -> List[Any]:
        """Plot and show any PyAnsys object.

        The types of objects supported are ``MeshObjectPlot``,
        ``pv.MultiBlock``, and ``pv.PolyData``.

        Parameters
        ----------
        plottable_object : Any, default: None
           Object or list of objects to plot.
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.
        view_2d : Dict, default: None
            Dictionary with the plane and the viewup vectors of the 2D plane.
        name_filter : str, default: None
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        Returns
        -------
        List[Any]
            List with the picked bodies in the picked order.

        """
        self.plot(plottable_object, name_filter, **plotting_options)
        if self._pl._object_to_actors_map:
            self._object_to_actors_map = self._pl._object_to_actors_map
        else:
            logger.warning("No actors were added to the plotter.")

        # Compute mapping between the objects and its edges.
        _ = self.compute_edge_object_map()

        if view_2d is not None:
            self._pl.scene.view_vector(
                vector=view_2d["vector"],
                viewup=view_2d["viewup"],
            )
        # Enable widgets and picking capabilities
        if screenshot is None and not ansys.tools.visualization_interface.DOCUMENTATION_BUILD:
            self.enable_widgets()

        if self._allow_picking:
            self.enable_picking()
        elif self._allow_hovering:
            self.enable_hover()

        # Update all buttons/widgets
        [widget.update() for widget in self._widgets]

        self.show_plotter(screenshot)

        picked_objects_list = []
        if isinstance(plottable_object, list):
            # Keep them ordered based on picking
            for meshobject in self._picked_list:
                for elem in plottable_object:
                    if hasattr(elem, "name") and elem.name == meshobject.name:
                        picked_objects_list.append(elem)
        elif hasattr(plottable_object, "name") and plottable_object in self._picked_list:
            picked_objects_list = [plottable_object]

        return picked_objects_list

    def show_plotter(self, screenshot: Optional[str] = None) -> None:
        """Show the plotter or start the `trame <https://kitware.github.io/trame/index.html>`_ service.

        Parameters
        ----------
        plotter : Plotter
            Visualization Interface Tool plotter with the meshes added.
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.

        """
        if self._use_trame and _HAS_TRAME:
            visualizer = TrameVisualizer()
            visualizer.set_scene(self._pl)
            visualizer.show()
        else:
            self.pv_interface.show(screenshot=screenshot)

        pv.OFF_SCREEN = self._pv_off_screen_original

    @abstractmethod
    def plot_iter(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        """Plot one or more compatible objects to the plotter.

        Parameters
        ----------
        plottable_object : Any
            One or more objects to add.
        name_filter : str, default: None.
            Regular expression with the desired name or names  to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        pass

    @abstractmethod
    def plot(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        """Plot a single object to the plotter.

        Parameters
        ----------
        plottable_object : Any
            Object to add.
        name_filter : str
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        pass

    def picked_operation(self) -> None:
        """Perform an operation on the picked objects."""
        pass


class PyVistaBackend(PyVistaBackendInterface):
    """Provides the generic plotter implementation for PyAnsys libraries.

    This class accepts ``MeshObjectPlot``, ``pv.MultiBlock`` and ``pv.PolyData`` objects.

    Parameters
    ----------
    use_trame : bool, default: None
        Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
        The default is ``None``, in which case the ``USE_TRAME`` global setting
        is used.
    allow_picking : Optional[bool], default: False
        Whether to allow picking capabilities in the window. Incompatible with hovering.
        Picking will take precedence over hovering.
    allow_hovering : Optional[bool], default: False
        Whether to allow hovering capabilities in the window. Incompatible with picking.
        Picking will take precedence over hovering.
    plot_picked_names : bool, default: True
        Whether to plot the names of the picked objects.

    """

    def __init__(
        self,
        use_trame: Optional[bool] = None,
        allow_picking: Optional[bool] = False,
        allow_hovering: Optional[bool] = False,
        plot_picked_names: Optional[bool] = True
    ) -> None:
        """Initialize the generic plotter."""
        super().__init__(use_trame, allow_picking, allow_hovering, plot_picked_names)

    def plot_iter(
        self,
        plotting_list: List[Any],
        name_filter: str = None,
        **plotting_options,
    ) -> None:
        """Plot the elements of an iterable of any type of object to the scene.

        The types of objects supported are ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects to plot.
        name_filter : str, default: None
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        for plottable_object in plotting_list:
            self.plot(plottable_object, name_filter, **plotting_options)

    def plot(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        """Plot a ``pyansys`` or ``PyVista`` object to the plotter.

        Parameters
        ----------
        plottable_object : Any
            Object to add.
        name_filter : str
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        if hasattr(plottable_object, "__iter__"):
            logger.debug("Plotting objects in list...")
            self.pv_interface.plot_iter(plottable_object, name_filter, **plotting_options)
        else:
            self.pv_interface.plot(plottable_object, name_filter, **plotting_options)

