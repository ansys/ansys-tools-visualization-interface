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

from ansys.visualizer import DOCUMENTATION_BUILD
from ansys.visualizer.types.edgeplot import EdgePlot
from ansys.visualizer.types.meshobjectplot import MeshObjectPlot
from ansys.visualizer.utils.clip_plane import ClipPlane
from ansys.visualizer.utils.colors import Colors
from ansys.visualizer.utils.logger import logger


class PyVistaInterface:
    """Middle class between PyVista plotting operations and PyAnsys objects.

    This class is responsible for creating the PyVista scene and adding
    the PyAnsys objects to it.


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
    show_plane: bool, default: False
        Whether to show the XY plane in the plotter window. By default, false.
    """

    def __init__(
        self,
        scene: Optional[pv.Plotter] = None,
        color_opts: Optional[Dict] = None,
        num_points: int = 100,
        enable_widgets: bool = True,
        show_plane: bool = False,
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

        # Save the desired number of points
        self._num_points = num_points

        # Show the XY plane
        self._show_plane = show_plane

        self.scene.show_axes_all()
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
        """Clip the passed mesh with a plane.

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
        return mesh.clip(normal=plane.normal, origin=plane.origin)

    def add_meshobject(self, object: MeshObjectPlot, **plotting_options):
        """Add a generic MeshObjectPlot to the scene.

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
        if isinstance(object.mesh, pv.PolyData):
            actor = self.scene.add_mesh(object.mesh, **plotting_options)
        else:
            actor = self.scene.add_mesh(object.mesh, **plotting_options)
        object.actor = actor
        self._object_to_actors_map[actor] = object
        return actor.name

    def add_edges(self, custom_object: MeshObjectPlot, **plotting_options) -> None:
        """Add the outer edges of an object to the plot.

        This method has the side effect of adding the edges to the MeshObjectPlot that
        you pass through the parameters.

        Parameters
        ----------
        custom_object : MeshObjectPlot
            custom_object of which to add the edges.
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
                        line, line_width=10, color=Colors.EDGE_COLOR, **plotting_options
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

    def add(
        self,
        object: Union[pv.PolyData, pv.MultiBlock, MeshObjectPlot],
        filter: str = None,
        **plotting_options,
    ) -> None:
        """Add any type of object to the scene.

        These types of objects are supported: ``MeshObjectPlot``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``.

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
            self.add_meshobject(object, **plotting_options)
        else:
            logger.warning("The object type is not supported. ")

    def add_iter(
        self,
        plotting_list: List[Any],
        filter: str = None,
        **plotting_options,
    ) -> None:
        """Add a list of any type of object to the scene.

        These types of objects are supported: ``Body``, ``Component``, ``List[pv.PolyData]``,
        ``pv.MultiBlock``, and ``Sketch``.

        Parameters
        ----------
        plotting_list : List[Any]
            List of objects you want to plot.
        filter : str, default: None
            Regular expression with the desired name or names you want to include in the plotter.
        **plotting_options : dict, default: None
            Keyword arguments. For allowable keyword arguments, see the
            :meth:`Plotter.add_mesh <pyvista.Plotter.add_mesh>` method.
        """
        for object in plotting_list:
            _ = self.add(object, filter, **plotting_options)

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
        # compute the scaling
        bounds = self.scene.renderer.bounds
        x_length, y_length = bounds[1] - bounds[0], bounds[3] - bounds[2]
        sfac = max(x_length, y_length)

        # Create the fundamental XY plane
        if show_plane or self._show_plane:
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
        # This method should only be applied in 3D objects: bodies, components
        if "smooth_shading" not in plotting_options:
            plotting_options.setdefault("smooth_shading", True)
        if "color" not in plotting_options:
            plotting_options.setdefault("color", Colors.DEFAULT_COLOR.value)

    @property
    def object_to_actors_map(self) -> Dict[pv.Actor, MeshObjectPlot]:
        """Mapping between the ``pyvista.Actor`` and the PyAnsys objects."""
        return self._object_to_actors_map
