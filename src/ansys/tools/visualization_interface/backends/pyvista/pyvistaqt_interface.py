# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
"""Module for the PyVistaQt functionalities."""
import importlib
from typing import Any, Dict, List, Optional

import pyvista as pv
from vtkmodules.vtkInteractionWidgets import vtkHoverWidget
from vtkmodules.vtkRenderingCore import vtkPointPicker

import ansys.tools.visualization_interface as viz_interface
from ansys.tools.visualization_interface.backends.pyvista.pyvista import PyVistaBackendInterface
from ansys.tools.visualization_interface.backends.pyvista.pyvista_interface import PyVistaInterface
from ansys.tools.visualization_interface.backends.pyvista.widgets.displace_arrows import (
    CameraPanDirection,
    DisplacementArrow,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.hide_buttons import HideButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.measure import MeasureWidget
from ansys.tools.visualization_interface.backends.pyvista.widgets.ruler import Ruler
from ansys.tools.visualization_interface.backends.pyvista.widgets.screenshot import ScreenshotButton
from ansys.tools.visualization_interface.backends.pyvista.widgets.view_button import (
    ViewButton,
    ViewDirection,
)
from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget
from ansys.tools.visualization_interface.utils.logger import logger

_HAS_PYVISTAQT = importlib.util.find_spec("pyvistaqt")
if _HAS_PYVISTAQT:
    import pyvistaqt


class PyVistaQtInterface(PyVistaInterface):
    """Provides the middle class between PyVistaQt plotting operations and PyAnsys objects.

    The main purpose of this class is to simplify interaction between PyVista and the PyVistaQt
    backend provided. This class is responsible for creating the PyVista scene and adding
    the PyAnsys objects to it.


    Parameters
    ----------
    scene : ~pyvista.Plotter, default: None
        Scene for rendering the objects. If passed, ``off_screen`` needs to
        be set manually beforehand for documentation and testing.
    color_opts : dict, default: None
        Dictionary containing the background and top colors.
    num_points : int, default: 100
        Number of points to use to render the shapes.
    enable_widgets : bool, default: True
        Whether to enable widget buttons in the plotter window.
        Widget buttons must be disabled when using
        `trame <https://kitware.github.io/trame/index.html>`_
        for visualization.
    show_plane : bool, default: False
        Whether to show the XY plane in the plotter window.
    """
    def __init__(
        self,
        scene: Optional[pv.Plotter] = None,
        color_opts: Optional[Dict] = None,
        num_points: int = 100,
        enable_widgets: bool = True,
        show_plane: bool = False,
        **plotter_kwargs,
    ) -> None:
        """Initialize the plotter."""
        # Generate custom scene if ``None`` is provided

        if scene is None:
            if not _HAS_PYVISTAQT:
                message = "PyVistaQt dependency is not installed. Install it with " + \
                            "`pip install ansys-tools-visualization-interface[pyvistaqt]`."
                logger.warning(message)
            elif viz_interface.TESTING_MODE:
                scene = pyvistaqt.BackgroundPlotter(off_screen=True)
            else:
                scene = pyvistaqt.BackgroundPlotter()

        # If required, use a white background with no gradient
        if not color_opts:
            color_opts = dict(color="white")

        # Create the scene
        self._scene = scene
        # Scene: assign the background
        self._scene.set_background(**color_opts)

        # Save the desired number of points
        self._num_points = num_points

        # Show the XY plane
        self._show_plane = show_plane

        # objects to actors mapping
        self._object_to_actors_map = {}
        self._enable_widgets = enable_widgets
        self._show_edges = None

    def show(
            self,
            show_plane: bool = False,
            **kwargs: Optional[Dict],
            ) -> None:
        """Show the rendered scene on the screen.

        Parameters
        ----------
        show_plane : bool, default: True
            Whether to show the XY plane.

        Notes
        -----
        For more information on supported Jupyter backends, see
        `Jupyter Notebook Plotting <https://docs.pyvista.org/user-guide/jupyter/index.html>`_
        in the PyVista documentation.

        """
        # Compute the scaling
        bounds = self.scene.renderer.bounds
        x_length, y_length = bounds[1] - bounds[0], bounds[3] - bounds[2]
        sfac = max(x_length, y_length)

        # Create the fundamental XY plane
        if show_plane or self._show_plane:
            # self.scene.bounds
            plane = pv.Plane(i_size=sfac * 1.3, j_size=sfac * 1.3)
            self.scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)

        # Enabling anti-aliasing by default on scene
        self.scene.enable_anti_aliasing("ssaa")

        # If screenshot is requested, set off_screen to True for the plotter
        if kwargs.get("screenshot") is not None:
            self.scene.off_screen = True
        else:
            self.scene.show()


class PyVistaQtBackendInterface(PyVistaBackendInterface):
    """Provides the interface for the Visualization Interface Tool plotter for PyVistaQt.

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
    """
    def __init__(
        self,
        allow_picking: Optional[bool] = False,
        allow_hovering: Optional[bool] = False,
        plot_picked_names: Optional[bool] = False,
        show_plane: Optional[bool] = False,
        **plotter_kwargs,
    ) -> None:
        """Initialize the plotter."""
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

        # Dictionary of picked objects in MeshObject format.
        self._picked_dict = {}

        # Map that relates PyVista actors with the added actors by the picker
        self._picker_added_actors_map = {}

        # Map that relates PyVista actors with EdgePlot objects
        self._edge_actors_map = {}

        # List of widgets added to the plotter.
        self._widgets = []

        # Map that saves original colors of the plotted objects.
        self._origin_colors = {}

        self._pl = PyVistaQtInterface(show_plane=show_plane, **plotter_kwargs)

        self._enable_widgets = self._pl._enable_widgets

        self._hover_picker = vtkPointPicker() if self. _allow_hovering else None
        self._hover_widget = vtkHoverWidget() if self. _allow_hovering else None
        self._added_hover_labels = []

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
            self._widgets.append(HideButton(self))

    def close(self):
        """Close the plotter for PyVistaQT."""
        self.pv_interface.scene.close()

    def show_plotter(self, screenshot: Optional[str] = None) -> None:
        """Show the plotter or start the `trame <https://kitware.github.io/trame/index.html>`_ service.

        Parameters
        ----------
        plotter : Plotter
            Visualization Interface Tool plotter with the meshes added.
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.

        """
        self.pv_interface.show(screenshot=screenshot)
        pv.OFF_SCREEN = self._pv_off_screen_original

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
            for meshobject in self._picked_dict.values():
                for elem in plottable_object:
                    if hasattr(elem, "name") and elem.name == meshobject.name:
                        picked_objects_list.append(elem)
        elif hasattr(plottable_object, "name") and plottable_object.name in self._picked_dict:
            picked_objects_list = [plottable_object]
        else:
            # Return the picked objects in the order they were picked
            picked_objects_list = list(self._picked_dict.values())

        return picked_objects_list


class PyVistaQtBackend(PyVistaQtBackendInterface):
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
