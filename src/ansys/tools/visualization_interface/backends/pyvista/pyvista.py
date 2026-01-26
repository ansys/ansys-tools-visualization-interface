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
"""Provides a wrapper to aid in plotting."""
from abc import abstractmethod
from collections.abc import Callable
import importlib.util
from typing import Any, Dict, List, Optional, Union

import pyvista as pv

import ansys.tools.visualization_interface
from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.backends.pyvista.picker import AbstractPicker, Picker
from ansys.tools.visualization_interface.backends.pyvista.pyvista_interface import PyVistaInterface
from ansys.tools.visualization_interface.backends.pyvista.widgets.dark_mode import DarkModeButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.displace_arrows import (
    CameraPanDirection,
    DisplacementArrow,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.hide_buttons import HideButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.measure import MeasureWidget
from ansys.tools.visualization_interface.backends.pyvista.widgets.mesh_slider import (
    MeshSliderWidget,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.pick_rotation_center import PickRotCenterButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.ruler import Ruler
from ansys.tools.visualization_interface.backends.pyvista.widgets.screenshot import ScreenshotButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.toggle_subtree import ToggleSubtreeButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.view_button import (
    ViewButton,
    ViewDirection,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget
from ansys.tools.visualization_interface.types.edge_plot import EdgePlot
from ansys.tools.visualization_interface.utils.color import Color
from ansys.tools.visualization_interface.utils.logger import logger

_HAS_TRAME = importlib.util.find_spec("pyvista.trame") and importlib.util.find_spec("trame.app")

DARK_MODE_THRESHOLD = 120


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
    plot_picked_names : Optional[bool], default: False
        Whether to plot the names of the picked objects.
    show_plane : Optional[bool], default: False
        Whether to show the plane in the plotter.
    use_qt : Optional[bool], default: False
        Whether to use the Qt backend for the plotter.
    show_qt : Optional[bool], default: True
        Whether to show the Qt window.
    custom_picker : AbstractPicker, default: None
        Custom picker class that extends the ``AbstractPicker`` class.
    custom_picker_kwargs : Optional[Dict[str, Any]], default: None
        Keyword arguments to pass to the custom picker class.
    """

    def __init__(
        self,
        use_trame: Optional[bool] = None,
        allow_picking: Optional[bool] = False,
        allow_hovering: Optional[bool] = False,
        plot_picked_names: Optional[bool] = False,
        show_plane: Optional[bool] = False,
        use_qt: Optional[bool] = False,
        show_qt: Optional[bool] = True,
        custom_picker: AbstractPicker = None,
        custom_picker_kwargs: Optional[Dict[str, Any]] = None,
        **plotter_kwargs,
    ) -> None:
        """Initialize the ``use_trame`` parameter and save the current ``pv.OFF_SCREEN`` value."""
        from vtkmodules.vtkInteractionWidgets import vtkHoverWidget
        from vtkmodules.vtkRenderingCore import vtkPointPicker

        # Check if the use of trame was requested
        if use_trame is None:
            use_trame = ansys.tools.visualization_interface.USE_TRAME
        self._use_qt = use_qt
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

        self._edge_actors_map: Dict[pv.Actor, EdgePlot] = {}

        # PyVista plotter
        self._pl = None

        # List of widgets added to the plotter.
        self._widgets = []

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
            self._pl = PyVistaInterface(
                show_plane=show_plane,
                use_qt=use_qt,
                show_qt=show_qt,
                **plotter_kwargs
            )

        self._enable_widgets = self._pl._enable_widgets

        self._hover_picker = vtkPointPicker() if self._allow_hovering else None
        self._hover_widget = vtkHoverWidget() if self._allow_hovering else None

        if custom_picker is None:
            self._custom_picker = Picker(self, self._plot_picked_names)
        elif issubclass(custom_picker, AbstractPicker):
            if custom_picker_kwargs:
                self._custom_picker = custom_picker(self, **custom_picker_kwargs)
            else:
                self._custom_picker = custom_picker(self)
        else:
            raise TypeError("custom_picker must be an instance of AbstractPicker.")

    @property
    def pv_interface(self) -> PyVistaInterface:
        """PyVista interface."""
        return self._pl

    @property
    def scene(self) -> pv.Plotter:
        """PyVista scene."""
        return self._pl.scene

    def enable_widgets(self, dark_mode: bool = False) -> None:
        """Enable the widgets for the plotter.

        Parameters
        ----------
        dark_mode : bool, default: False
            Whether to use dark mode for the widgets.
        """
        # Create Plotter widgets
        if self._enable_widgets:
            self._widgets: List[PlotterWidget] = []
            self._widgets.append(Ruler(self._pl._scene, dark_mode))
            [
                self._widgets.append(DisplacementArrow(self._pl._scene, dir, dark_mode))
                for dir in CameraPanDirection
            ]
            [
                self._widgets.append(ViewButton(self._pl._scene, dir, dark_mode))
                for dir in ViewDirection
            ]
            self._widgets.append(MeasureWidget(self, dark_mode))
            self._widgets.append(ScreenshotButton(self, dark_mode))
            if not self._use_qt:
                self._widgets.append(MeshSliderWidget(self, dark_mode))
            self._widgets.append(HideButton(self, dark_mode))
            self._widgets.append(PickRotCenterButton(self, dark_mode))
            self._widgets.append(DarkModeButton(self, dark_mode))
            self._widgets.append(ToggleSubtreeButton(self, dark_mode, include_root=True))

    def add_widget(self, widget: Union[PlotterWidget, List[PlotterWidget]]):
        """Add one or more custom widgets to the plotter.

        Parameters
        ----------
        widget : Union[PlotterWidget, List[PlotterWidget]]
            One or more custom widgets.

        """
        if isinstance(widget, list):
            self._widgets.extend(widget)
            for w in widget:
                w.update()
        else:
            self._widgets.append(widget)
            widget.update()

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
            if body_plot.actor.name not in self._custom_picker.picked_dict:
                self._custom_picker.pick_select_object(body_plot, pt)
            else:
                # Toggle-clicking the same object - restore visibility
                self._custom_picker.pick_unselect_object(body_plot, restore_visibility=True)

        # if object is an edge
        elif actor in self._edge_actors_map and actor.GetVisibility():
            edge = self._edge_actors_map[actor]
            if edge.actor.name not in self._custom_picker.picked_dict:
                self._custom_picker.pick_select_object(edge, pt)
            else:
                # Toggle-clicking the same edge - restore visibility
                self._custom_picker.pick_unselect_object(edge, restore_visibility=True)
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
        if actor in self._object_to_actors_map:
            custom_object = self._object_to_actors_map[actor]
            self._custom_picker.hover_select_object(custom_object, actor)

        else:
            self._custom_picker.hover_unselect_object()

    def focus_point_selection(self, actor: "pv.Actor") -> None:
        """Focus the camera on a selected actor.

        Parameters
        ----------
        actor : ~pyvista.Actor
            Actor to focus the camera on.

        """
        pt = self._pl.scene.picked_point
        sphere = pv.Sphere(center=pt, radius=0.1)
        self._picked_ball = self._pl.scene.add_mesh(sphere, color="red", name="focus_sphere_temp", reset_camera=False)
        self._pl.scene.set_focus(pt)
        self._pl.scene.render()

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

    def enable_set_focus_center(self):
        """Enable setting the focus of the camera to the picked point."""
        self._pl.scene.enable_mesh_picking(
            callback=self.focus_point_selection,
            use_actor=True,
            show=False,
            show_message=False,
            picker="cell",
        )

    def enable_hover(self):
        """Enable hover capabilities in the plotter."""
        from vtkmodules.vtkCommonCore import vtkCommand
        from vtkmodules.vtkInteractionWidgets import vtkHoverWidget

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

    def disable_center_focus(self):
        """Disable setting the focus of the camera to the picked point."""
        self._pl.scene.disable_picking()
        if hasattr(self, '_picked_ball'):
            self._picked_ball.SetVisibility(False)

    def __extract_kwargs(self, func_name: Callable, input_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts the keyword arguments from a function signature and returns it as dict.

        Parameters
        ----------
        func_name : Callable
            Function to extract the keyword arguments from. It should be a callable function
        input_kwargs : Dict[str, Any]
            Dictionary with the keyword arguments to update the extracted ones.

        Returns
        -------
        Dict[str, Any]
            Dictionary with the keyword arguments extracted from the function signature and
            updated with the input kwargs.
        """
        import inspect
        signature = inspect.signature(func_name)
        kwargs = {}
        for k, v in signature.parameters.items():
            # We are ignoring positional arguments, and passing everything as kwarg
            if v.default is not inspect.Parameter.empty:
                kwargs[k] = input_kwargs[k] if k in input_kwargs else v.default
        return kwargs

    def show(
        self,
        plottable_object: Any = None,
        screenshot: Optional[str] = None,
        view_2d: Dict = None,
        name_filter: str = None,
        dark_mode: bool = False,
        **kwargs: Dict[str, Any],
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
        dark_mode : bool, default: False
            Whether to use dark mode for the widgets.
        **kwargs : Any
            Additional keyword arguments for the show or plot method.

        Returns
        -------
        List[Any]
            List with the picked bodies in the picked order.

        """
        plotting_options = self.__extract_kwargs(
            self._pl._scene.add_mesh,
            kwargs,
        )
        show_options = self.__extract_kwargs(
            self._pl.scene.show,
            kwargs,
        )
        self.plot(plottable_object, name_filter, **plotting_options)
        if self._pl.object_to_actors_map:
            self._object_to_actors_map = self._pl.object_to_actors_map
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
            if dark_mode:
                self.enable_widgets(dark_mode=dark_mode)
            elif all([
                    color < DARK_MODE_THRESHOLD
                    for color in self._pl.scene.background_color.int_rgb
                    ]):
                print([color for color in self._pl.scene.background_color.int_rgb])
                self.enable_widgets(dark_mode=True)
            else:
                self.enable_widgets()

        if self._allow_picking:
            self.enable_picking()
        elif self._allow_hovering:
            self.enable_hover()

        # Update all buttons/widgets
        [widget.update() for widget in self._widgets]

        # Remove screenshot from show options since we pass it manually
        show_options.pop("screenshot", None)
        self.show_plotter(screenshot, **show_options)

        picked_objects_list = []
        if isinstance(plottable_object, list):
            # Keep them ordered based on picking
            for meshobject in self._custom_picker.picked_dict.values():
                for elem in plottable_object:
                    if hasattr(elem, "name") and elem.name == meshobject.name:
                        picked_objects_list.append(elem)
        elif hasattr(plottable_object, "name") and plottable_object.name in self._custom_picker.picked_dict:
            picked_objects_list = [plottable_object]
        else:
            # Return the picked objects in the order they were picked
            picked_objects_list = list(self._custom_picker.picked_dict.values())

        return picked_objects_list

    def show_plotter(self, screenshot: Optional[str] = None, **kwargs) -> None:
        """Show the plotter or start the `trame <https://kitware.github.io/trame/index.html>`_ service.

        Parameters
        ----------
        plotter : Plotter
            Visualization Interface Tool plotter with the meshes added.
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.

        """
        if self._use_trame and _HAS_TRAME:
            from ansys.tools.visualization_interface.backends.pyvista.trame_local import (
                TrameVisualizer,
            )
            visualizer = TrameVisualizer()
            visualizer.set_scene(self._pl)
            visualizer.show()
        else:
            self.pv_interface.show(screenshot=screenshot, **kwargs)

        pv.OFF_SCREEN = self._pv_off_screen_original

    @abstractmethod
    def plot_iter(self, plottable_object: Any, name_filter: str = None, **plotting_options):
        """Plot one or more compatible objects to the plotter.

        Parameters
        ----------
        plottable_object : Any
            One or more objects to add.
        name_filter : str, default: None.
            Regular expression with the desired name or names to include in the plotter.
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
            Object to plot.
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
        plot_picked_names: Optional[bool] = True,
        use_qt: Optional[bool] = False,
        show_qt: Optional[bool] = False,
        custom_picker: AbstractPicker = None,
    ) -> None:
        """Initialize the generic plotter."""
        super().__init__(
            use_trame,
            allow_picking,
            allow_hovering,
            plot_picked_names,
            use_qt=use_qt,
            show_qt=show_qt,
            custom_picker=custom_picker
        )

    @property
    def base_plotter(self):
        """Return the base plotter object."""
        return self._pl.scene

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
            Object to plot.
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

    def close(self):
        """Close the plotter for PyVistaQT."""
        if self._use_qt:
            self.pv_interface.scene.close()
