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
from abc import ABC, abstractmethod

import numpy as np
import pyvista as pv
from beartype.typing import Any, Dict, List, Optional, Union

from ansys.visualizer import USE_TRAME
from ansys.visualizer.colors import Colors
from ansys.visualizer.plotter import Plotter
from ansys.visualizer.plotter_types import EdgePlot, MeshObjectPlot
from ansys.visualizer.trame_gui import _HAS_TRAME, TrameVisualizer
from ansys.visualizer.utils.logger import logger
from ansys.visualizer.widgets import (CameraPanDirection, DisplacementArrow,
                                      MeasureWidget, PlotterWidget, Ruler,
                                      ViewButton, ViewDirection)


class PlotterInterface(ABC):
    def __init__(
        self, use_trame: Optional[bool] = None, allow_picking: Optional[bool] = False
    ) -> None:
        """Initialize ``use_trame`` and save current ``pv.OFF_SCREEN`` value."""
        # Check if the use of trame was requested
        if use_trame is None:
            use_trame = USE_TRAME

        self._use_trame = use_trame
        self._allow_picking = allow_picking
        self._pv_off_screen_original = bool(pv.OFF_SCREEN)
        self._object_to_actors_map = {}
        self._pl = None
        self._picked_list = set()
        self._picker_added_actors_map = {}
        self._edge_actors_map = {}
        self._widgets = []

        if self._use_trame and _HAS_TRAME:
            # avoids GUI window popping up
            pv.OFF_SCREEN = True
            self._pl = Plotter(enable_widgets=False)
        elif self._use_trame and not _HAS_TRAME:
            warn_msg = (
                "'use_trame' is active but trame dependencies are not installed."
                "Consider installing 'pyvista[trame]' to use this functionality."
            )
            logger.warning(warn_msg)
            self._pl = Plotter()
        else:
            self._pl = Plotter()

        self._enable_widgets = self._pl._enable_widgets

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

    def add_widget(self, widget: Union[PlotterWidget, List[PlotterWidget]]):
        """Add a widget to the plotter.
        
        Parameters
        ----------
        widget : Union[PlotterWidget, List[PlotterWidget]]
            Widget or list of widgets to add to the plotter.
        """
        if isinstance(widget, list):
            self._widgets.extend(widget)
        else:
            self._widgets.append(widget)

    def select_object(self, geom_object: Union[MeshObjectPlot, EdgePlot], pt: np.ndarray) -> None:
        """
        Select an object in the plotter.

        Highlights the object edges if any and adds a label with the object name and adds
        it to the PyAnsys object selection.

        Parameters
        ----------
        geom_object : Union[MeshObjectPlot, EdgePlot]
            Geometry object to select.
        pt : ~numpy.ndarray
            Set of points to determine the label position.
        """
        added_actors = []

        # Add edges if selecting an object
        if isinstance(geom_object, MeshObjectPlot):
            geom_object.actor.prop.color = Colors.PICKED_COLOR.value
            children_list = geom_object.edges
            for edge in children_list:
                edge.actor.SetVisibility(True)
                edge.actor.prop.color = Colors.EDGE_COLOR.value
        elif isinstance(geom_object, EdgePlot):
            geom_object.actor.prop.color = Colors.PICKED_EDGE_COLOR.value

        text = geom_object.name

        label_actor = self._pl.scene.add_point_labels(
            [pt],
            [text],
            always_visible=True,
            point_size=0,
            render_points_as_spheres=False,
            show_points=False,
        )
        if geom_object.name not in self._picked_list:
            self._picked_list.add(geom_object.name)
        added_actors.append(label_actor)
        self._picker_added_actors_map[geom_object.actor.name] = added_actors

    def unselect_object(self, geom_object: Union[MeshObjectPlot, EdgePlot]) -> None:
        """
        Unselect an object in the plotter.

        Removes edge highlighting and label from a plotter actor and removes it
        from the PyAnsys Geometry object selection.

        Parameters
        ----------
        geom_object : Union[MeshObjectPlot, EdgePlot]
            Object to unselect.
        """
        # remove actor from picked list and from scene
        object_name = geom_object.name
        if object_name in self._picked_list:
            self._picked_list.remove(object_name)

        if isinstance(geom_object, MeshObjectPlot):
            geom_object.actor.prop.color = Colors.DEFAULT_COLOR.value
        elif isinstance(geom_object, EdgePlot):
            geom_object.actor.prop.color = Colors.EDGE_COLOR.value

        if geom_object.actor.name in self._picker_added_actors_map:
            self._pl.scene.remove_actor(self._picker_added_actors_map[geom_object.actor.name])

            # remove actor and its children(edges) from the scene
            if isinstance(geom_object, MeshObjectPlot):
                for edge in geom_object.edges:
                    # hide edges in the scene
                    edge.actor.SetVisibility(False)
                    # recursion
                    self.unselect_object(edge)
            self._picker_added_actors_map.pop(geom_object.actor.name)

    def picker_callback(self, actor: "pv.Actor") -> None:
        """
        Define callback for the element picker.

        Parameters
        ----------
        actor : ~pyvista.Actor
            Actor that we are picking.
        """
        pt = self._pl.scene.picked_point

        # if object is a body/component
        if actor in self._object_to_actors_map:
            body_plot = self._object_to_actors_map[actor]
            if body_plot.custom_object.name not in self._picked_list:
                self.select_object(body_plot, pt)
            else:
                self.unselect_object(body_plot)

        # if object is an edge
        elif actor in self._edge_actors_map and actor.GetVisibility():
            edge = self._edge_actors_map[actor]
            if edge.name not in self._picked_list:
                self.select_object(edge, pt)
            else:
                self.unselect_object(edge)
                actor.prop.color = Colors.EDGE_COLOR.value

    def compute_edge_object_map(self) -> Dict[pv.Actor, EdgePlot]:
        """
        Compute the mapping between plotter actors and ``EdgePlot`` objects.

        Returns
        -------
        Dict[~pyvista.Actor, EdgePlot]
            Mapping between plotter actors and EdgePlot objects.
        """
        for mesh_object in self._object_to_actors_map.values():
            # get edges only from bodies
            if mesh_object.edges is not None:
                for edge in mesh_object.edges:
                    self._edge_actors_map[edge.actor] = edge

    def enable_picking(self):
        """Enable picking capabilities in the plotter."""
        self._pl.scene.enable_mesh_picking(
            callback=self.picker_callback, use_actor=True, show=False, show_message=False
        )

    def disable_picking(self):
        """Disable picking capabilities in the plotter."""
        self._pl.scene.disable_picking()

    def plot(
        self,
        object: Any = None,
        screenshot: Optional[str] = None,
        filter: str = None,
        **plotting_options,
    ) -> List[Any]:
        """
        Plot and show any PyAnsys Geometry object.

        These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

        Parameters
        ----------
        object : Any, default: None
            Any object or list of objects that you want to plot.
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combined
            into a single dataset without separating faces.
        merge_component : bool, default: False
            Whether to merge this component into a single dataset. When ``True``,
            all the individual bodies are effectively combined into a single
            dataset without any hierarchy.
        view_2d : Dict, default: None
            Dictionary with the plane and the viewup vectors of the 2D plane.
        filter : str, default: None
            Regular expression with the desired name or names you want to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        Returns
        -------
        List[Any]
            List with the picked bodies in the picked order.
        """
        self.add(object, filter, **plotting_options)
        if self._pl._object_to_actors_map:
            self._object_to_actors_map = self._pl._object_to_actors_map
        else:
            logger.warning("No actors added to the plotter.")
        
        # Compute mapping between the objects and its edges.
        _ = self.compute_edge_object_map()

        # Enable widgets and picking capabilities
        self.enable_widgets()
        if self._allow_picking:
            self.enable_picking()

        # Update all buttons/widgets
        [widget.update() for widget in self._widgets]

        self.show_plotter(screenshot)

        picked_objects_list = []
        if isinstance(object, list):
            # Keep them ordered based on picking
            for name in self._picked_list:
                for elem in object:
                    if hasattr(elem, "name") and elem.name == name:
                        picked_objects_list.append(elem)
        elif hasattr(object, "name") and object.name in self._picked_list:
            picked_objects_list = [object]

        return picked_objects_list

    def show_plotter(self, screenshot: Optional[str] = None) -> None:
        """
        Show the plotter or start the `trame <https://kitware.github.io/trame/index.html>`_ service.

        Parameters
        ----------
        plotter : Plotter
            PyAnsys Geometry plotter with the meshes added.
        screenshot : str, default: None
            Path for saving a screenshot of the image that is being represented.
        """
        if self._use_trame and _HAS_TRAME:
            visualizer = TrameVisualizer()
            visualizer.set_scene(self._pl)
            visualizer.show()
        else:
            self._pl.show(screenshot=screenshot)

        pv.OFF_SCREEN = self._pv_off_screen_original

    @abstractmethod
    def add_list(self, object: Any, filter, **plotting_options):
        pass

    @abstractmethod
    def add(self, object: Any, filter, **plotting_options):
        pass

class PlotterHelper(PlotterInterface):
    """
    Provides for simplifying the selection of trame in ``plot()`` functions.

    Parameters
    ----------
    use_trame : bool, default: None
        Whether to enable the use of `trame <https://kitware.github.io/trame/index.html>`_.
        The default is ``None``, in which case the ``USE_TRAME`` global setting
        is used.
    allow_picking: bool, default: False
        Enables/disables the picking capabilities in the PyVista plotter.
    """

    def __init__(
        self, use_trame: Optional[bool] = None, allow_picking: Optional[bool] = False
    ) -> None:
        """_summary_

        Parameters
        ----------
        use_trame : Optional[bool], optional
            _description_, by default None
        allow_picking : Optional[bool], optional
            _description_, by default False
        """
        super().__init__(use_trame, allow_picking)
        
    def add_list(
        self,
        plotting_list: List[Any],
        filter: str = None,
        **plotting_options,
    ) -> None:
        """
        Add a list of any type of object to the scene.

        These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects you want to plot.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combined
            into a single dataset without separating faces.
        filter : str, default: None
            Regular expression with the desired name or names you want to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        for object in plotting_list:
            _ = self.add(object, filter, **plotting_options)


    def add(self, object: Any, filter, **plotting_options):
        """
        Add a ``pyansys-geometry`` or ``PyVista`` object to the plotter.

        Parameters
        ----------
        object : Any
            Object you want to show.
        """
        if isinstance(object, List) and not isinstance(object[0], pv.PolyData):
            logger.debug("Plotting objects in list...")
            self._pl.add_list(object, filter, **plotting_options)
        else:
            self._pl.add(object, filter, **plotting_options)