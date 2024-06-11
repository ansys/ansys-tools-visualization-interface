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
"""Provides plotting for various PyAnsys objects."""
import re
from typing import Union

from beartype.typing import Any, Dict, List, Optional
import pyvista as pv
from pyvista.plotting.plotter import Plotter as PyVistaPlotter

import ansys.tools.visualization_interface as viz_interface
from ansys.tools.visualization_interface.types.edge_plot import EdgePlot
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot
from ansys.tools.visualization_interface.utils.clip_plane import ClipPlane
from ansys.tools.visualization_interface.utils.color import Color
from ansys.tools.visualization_interface.utils.logger import logger


class PyVistaInterface:
    """Provides the middle class between PyVista plotting operations and PyAnsys objects.

    The main purpose of this class is to simplify interaction between PyVista and the PyVista backend
    provided. This class is responsible for creating the PyVista scene and adding
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
            if viz_interface.TESTING_MODE or viz_interface.DOCUMENTATION_BUILD:
                scene = pv.Plotter(off_screen=True, **plotter_kwargs)
            else:
                scene = pv.Plotter(**plotter_kwargs)
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

        self.scene.add_axes(interactive=False)
        # objects to actors mapping
        self._object_to_actors_map = {}
        self._enable_widgets = enable_widgets

    @property
    def scene(self) -> PyVistaPlotter:
        """Rendered scene object.

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
        self, mesh: Union[pv.PolyData, pv.MultiBlock], plane: ClipPlane
    ) -> Union[pv.PolyData, pv.MultiBlock]:
        """Clip a given mesh with a plane.

        Parameters
        ----------
        mesh : Union[pv.PolyData, pv.MultiBlock]
            Mesh.
        normal : str, default: "x"
            Plane to use for clipping. Options are ``"x"``, ``"-x"``,
            ``"y"``, ``"-y"``, ``"z"``, and ``"-z"``.
        origin : tuple, default: None
            Origin point of the plane.
        plane : ClipPlane, default: None
            Clipping plane to cut the mesh with.

        Returns
        -------
        Union[pv.PolyData,pv.MultiBlock]
            Clipped mesh.

        """
        return mesh.clip(normal=plane.normal, origin=plane.origin)

    def plot_meshobject(self, object: MeshObjectPlot, **plotting_options):
        """Plot a generic ``MeshObjectPlot`` object to the scene.

        Parameters
        ----------
        object : MeshObjectPlot
            Object to add to the scene.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        dataset = object.mesh
        if "clipping_plane" in plotting_options:
            dataset = self.clip(dataset, plotting_options["clipping_plane"])
            plotting_options.pop("clipping_plane", None)
        actor = self.scene.add_mesh(dataset, **plotting_options)
        object.actor = actor
        self._object_to_actors_map[actor] = object
        return actor.name

    def plot_edges(self, custom_object: MeshObjectPlot, **plotting_options) -> None:
        """Plot the outer edges of an object to the plot.

        This method has the side effect of adding the edges to the ``MeshObjectPlot``
        object that you pass through the parameters.

        Parameters
        ----------
        custom_object : MeshObjectPlot
            Custom object with the edges to add.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        edge_plot_list = []

        # Check if object has edges attb and if these edges have start and end points.
        if hasattr(custom_object, "edges"):
            for edge in custom_object.object.edges:
                if hasattr(edge, "start_point") and hasattr(edge, "end_point"):
                    line = pv.Line(edge.start_point, edge.end_point)
                    edge_actor = self.scene.add_mesh(
                        line, line_width=10, color=Color.EDGE, **plotting_options
                    )
                    edge_actor.SetVisibility(False)
                    edge_plot = EdgePlot(edge_actor, edge, custom_object)
                    edge_plot_list.append(edge_plot)
                else:
                    logger.warning("The edge does not have start and end points.")
                    break
            custom_object.edges = edge_plot_list
        else:
            logger.warning("The object does not have edges.")

    def plot(
        self,
        object: Union[pv.PolyData, pv.MultiBlock, MeshObjectPlot],
        filter: str = None,
        **plotting_options,
    ) -> None:
        """Plot any type of object to the scene.

        Supported object types are ``List[pv.PolyData]``, ``MeshObjectPlot``,
        and ``pv.MultiBlock``.

        Parameters
        ----------
        object : Union[pv.PolyData, pv.MultiBlock, MeshObjectPlot]
            Object to plot.
        filter : str, default: None
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        if filter:
            if hasattr(object, "name") and not re.search(filter, object.name):
                return self._object_to_actors_map

        # Check what kind of object we are dealing with
        if isinstance(object, pv.PolyData):
            if "clipping_plane" in plotting_options:
                mesh = self.clip(object, plotting_options["clipping_plane"])
                plotting_options.pop("clipping_plane", None)
                self.scene.add_mesh(mesh, **plotting_options)
            else:
                self.scene.add_mesh(object, **plotting_options)
        elif isinstance(object, pv.MultiBlock):
            if "clipping_plane" in plotting_options:
                mesh = self.clip(object, plotting_options["clipping_plane"])
                plotting_options.pop("clipping_plane", None)
                self.scene.add_composite(mesh, **plotting_options)
            else:
                self.scene.add_composite(object, **plotting_options)
        elif isinstance(object, MeshObjectPlot):
            self.plot_meshobject(object, **plotting_options)
        else:
            logger.warning("The object type is not supported. ")

    def plot_iter(
        self,
        plotting_list: List[Any],
        filter: str = None,
        **plotting_options,
    ) -> None:
        """Plot elements of an iterable of any type of objects to the scene.

        Supported object types are ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects to plot.
        filter : str, default: None
            Regular expression with the desired name or names to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        for object in plotting_list:
            _ = self.plot(object, filter, **plotting_options)

    def show(
        self,
        show_plane: bool = False,
        jupyter_backend: Optional[str] = None,
        **kwargs: Optional[Dict],
    ) -> None:
        """Show the rendered scene on the screen.

        Parameters
        ----------
        show_plane : bool, default: True
            Whether to show the XY plane.
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
        # Compute the scaling
        bounds = self.scene.renderer.bounds
        x_length, y_length = bounds[1] - bounds[0], bounds[3] - bounds[2]
        sfac = max(x_length, y_length)

        # Create the fundamental XY plane
        if show_plane or self._show_plane:
            # self.scene.bounds
            plane = pv.Plane(i_size=sfac * 1.3, j_size=sfac * 1.3)
            self.scene.add_mesh(plane, color="white", show_edges=True, opacity=0.1)

        # To avoid a PyVista warning, conditionally set the Jupyter backend as not
        # all users will be within a notebnook environment
        if self.scene.notebook and jupyter_backend is None:
            jupyter_backend = "trame"

        # Override Jupyter backend if building docs
        if viz_interface.DOCUMENTATION_BUILD:
            jupyter_backend = "html"

        # Enabling anti-aliasing by default on scene
        self.scene.enable_anti_aliasing("ssaa")

        # If screenshot is requested, set off_screen to True for the plotter
        if kwargs.get("screenshot") is not None:
            self.scene.off_screen = True

        self.scene.show(jupyter_backend=jupyter_backend, **kwargs)

    def set_add_mesh_defaults(self, plotting_options: Optional[Dict]) -> None:
        """Set the default values for the plotting options.

        Parameters
        ----------
        plotting_options : Optional[Dict]
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.

        """
        # If the following keys do not exist, set the default values
        #
        # This method should only be applied in 3D objects (bodies and components)
        if "smooth_shading" not in plotting_options:
            plotting_options.setdefault("smooth_shading", True)
        if "color" not in plotting_options:
            plotting_options.setdefault("color", Color.DEFAULT.value)

    @property
    def object_to_actors_map(self) -> Dict[pv.Actor, MeshObjectPlot]:
        """Mapping between the PyVista actor and the PyAnsys objects."""
        return self._object_to_actors_map
