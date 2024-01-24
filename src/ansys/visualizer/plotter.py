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
"""Provides plotting for various PyAnsys Geometry objects."""
import re

from beartype.typing import Any, Dict, List, Optional, Union
import numpy as np
import pyvista as pv 
from pyvista.plotting.plotter import Plotter as PyVistaPlotter
from pyvista.plotting.tools import create_axes_marker
from ansys.visualizer.colors import Colors 
from ansys.visualizer.plotter_types import EdgePlot, GeomObjectPlot, MeshObjectPlot
from abc import ABC, abstractmethod


class Plotter:
    """
    Provides for plotting sketches and bodies.

    Parameters 
    ----------
    scene : ~pyvista.Plotter, default: None
        ``Scene`` instance for rendering the objects.
    color_opts : dict, default: None
        Dictionary containing the background and top colors.
    num_points : int, default: 100
        Number of points to use to render the shapes.
    enable_widgets: bool, default: True
        Whether to enable widget buttons in the plotter window.
        Widget buttons must be disabled when using
        `trame <https://kitware.github.io/trame/index.html>`_
        for visualization.
    """

    def __init__(
        self,
        scene: Optional[pv.Plotter] = None,
        color_opts: Optional[Dict] = None,
        num_points: int = 100,
        enable_widgets: bool = True,
    ) -> None:
        """Initialize the plotter."""
        # Generate custom scene if ``None`` is provided
        if scene is None:
            scene = pv.Plotter()

        # If required, use a white background with no gradient
        if not color_opts:
            color_opts = dict(color="white")

        # Create the scene
        self._scene = scene
        # Scene: assign the background
        self._scene.set_background(**color_opts)
        view_box = self._scene.add_axes(line_width=5, color="black")

        # Save the desired number of points
        self._num_points = num_points

        # geometry objects to actors mapping
        self._object_to_actors_map = {}
        self._enable_widgets = enable_widgets

    @property
    def scene(self) -> PyVistaPlotter:
        """
        Rendered scene object.

        Returns
        -------
        ~pyvista.Plotter
            Rendered scene object.
        """
        return self._scene

    def view_xy(self) -> None:
        """View the scene from the XY plane."""
        self.scene.view_xy()

    def view_xz(self) -> None:
        """View the scene from the XZ plane."""
        self.scene.view_xz()

    def view_yx(self) -> None:
        """View the scene from the YX plane."""
        self.scene.view_yx()

    def view_yz(self) -> None:
        """View the scene from the YZ plane."""
        self.scene.view_yz()

    def view_zx(self) -> None:
        """View the scene from the ZX plane."""
        self.scene.view_zx()

    def view_zy(self) -> None:
        """View the scene from the ZY plane."""
        self.scene.view_zy()

    def clip(
        self, mesh: Union[pv.PolyData, pv.MultiBlock], normal: Union[tuple[float], str], origin: tuple[float] = None
    ) -> Union[pv.PolyData, pv.MultiBlock]:
        """
        Clip the passed mesh with a plane.

        Parameters
        ----------
        mesh : Union[pv.PolyData, pv.MultiBlock]
            Mesh you want to clip.
        normal : str, optional
            Plane you want to use for clipping, by default "x".
            Available options: ["x", "-x", "y", "-y", "z", "-z"]
        origin : tuple, optional
            Origin point of the plane, by default None

        Returns
        -------
        Union[pv.PolyData,pv.MultiBlock]
            The clipped mesh.
        """
        return mesh.clip(normal=normal, origin=origin)

    @abstractmethod
    def add_custom(self, object: MeshObjectPlot,  **plotting_options) -> pv.Polydata or pv.Multiblock:
        dataset = object.mesh
        if "clipping_plane" in plotting_options:
            dataset = self.clip(dataset, plotting_options["clipping_plane"])
            plotting_options.pop("clipping_plane", None)
        if isinstance(object.mesh, pv.PolyData):
            actor, _ = self.scene.add_mesh(object.mesh, **plotting_options)
        else:
            actor, _ = self.scene.add_mesh(object.mesh, **plotting_options)
        object.actor = actor
        self._object_to_actors_map[actor] = object
        return actor.name

    def add(
        self,
        object: Any,
        filter: str = None,
        **plotting_options,
    ) -> None:
        """
        Add any type of object to the scene.

        These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects that you want to plot.
        merge_bodies : bool, default: False
            Whether to merge each body into a single dataset. When ``True``,
            all the faces of each individual body are effectively combined
            into a single dataset without separating faces.
        merge_component : bool, default: False
            Whether to merge the component into a single dataset. When
            ``True``, all the individual bodies are effectively combined
            into a single dataset without any hierarchy.
        filter : str, default: None
            Regular expression with the desired name or names you want to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        if filter:
            if hasattr(object, "name") and not re.search(filter, object.name):
                return self._object_to_actors_map

        # Check what kind of object we are dealing with
        if isinstance(object, List) and isinstance(object[0], pv.PolyData):
            self.add_sketch_polydata(object, **plotting_options)
        elif isinstance(object, pv.PolyData):
            if "clipping_plane" in plotting_options:
                object = self.clip(object, plotting_options["clipping_plane"])
                plotting_options.pop("clipping_plane", None)
            self.scene.add_mesh(object, **plotting_options)
        elif isinstance(object, pv.MultiBlock):
            if "clipping_plane" in plotting_options:
                object = self.clip(object, plotting_options["clipping_plane"])
                plotting_options.pop("clipping_plane", None)
            self.scene.add_composite(object, **plotting_options)
        else:
            _ = self.add_custom(object, **plotting_options)

    def add_list(
        self,
        plotting_list: List[Any],
        merge_bodies: bool = False,
        merge_components: bool = False,
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
            _ = self.add(object, merge_bodies, merge_components, filter, **plotting_options)

    def show(
        self,
        show_axes_at_origin: bool = True,
        show_plane: bool = True,
        jupyter_backend: Optional[str] = None,
        **kwargs: Optional[Dict],
    ) -> None:
        """
        Show the rendered scene on the screen.

        Parameters
        ----------
        jupyter_backend : str, default: None
            PyVista Jupyter backend.
        **kwargs : dict, default: None
            Plotting keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.show <pyvista.Plotter.show>` method.

        Notes
        -----
        For more information on supported Jupyter backends, see
        `Jupyter Notebook Plotting <https://docs.pyvista.org/user-guide/jupyter/index.html>`_
        in the PyVista documentation.
        """
        # computue the scaling
        bounds = self.scene.renderer.bounds
        x_length, y_length = bounds[1] - bounds[0], bounds[3] - bounds[2]
        sfac = max(x_length, y_length)

        # # Show origin axes without labels
        # if show_axes_at_origin:
        #     axes = create_axes_marker(labels_off=True)
        #     self.scene.add_actor(axes)

        # Create the fundamental XY plane
        if show_plane:
            # self.scene.bounds
            plane = pv.Plane(i_size=sfac * 1.3, j_size=sfac * 1.3)
            self.scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)

        # Conditionally set the Jupyter backend as not all users will be within
        # a notebook environment to avoid a pyvista warning
        if self.scene.notebook and jupyter_backend is None:
            jupyter_backend = "trame"

        # Override jupyter backend in case we are building docs
        if DOCUMENTATION_BUILD:
            jupyter_backend = "static"

        # Enabling anti-aliasing by default on scene
        self.scene.enable_anti_aliasing("ssaa")

        self.scene.show(jupyter_backend=jupyter_backend, **kwargs)

    def __set_add_mesh_defaults(self, plotting_options: Optional[Dict]) -> None:
        # If the following keys do not exist, set the default values
        #
        # This method should only be applied in 3D objects: bodies, components
        plotting_options.setdefault("smooth_shading", True)
        plotting_options.setdefault("color", Colors.DEFAULT_COLOR)

    @property
    def object_to_actors_map(self) -> Dict[pv.Actor, GeomObjectPlot]:
        """Mapping between the ~pyvista.Actor and the PyAnsys Geometry objects."""
        return self._object_to_actors_map
