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

"""Module for the Plotter class."""
from typing import Any, List, Optional, Tuple, Union

from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.backends.pyvista.pyvista import PyVistaBackend


class Plotter():
    """Base plotting class containing common methods and attributes.

    This class is responsible for plotting objects using the specified backend.

    Parameters
    ----------
    backend : BaseBackend, optional
        Plotting backend to use, by default PyVistaBackend.
    """
    def __init__(self, backend: BaseBackend = None) -> None:
        """Initialize plotter class."""
        if backend is None:
            self._backend = PyVistaBackend()
        else:
            self._backend = backend

    @property
    def backend(self):
        """Return the base plotter object."""
        return self._backend

    def plot_iter(self, plotting_list: List, **plotting_options):
        """Plots multiple objects using the specified backend.

        Parameters
        ----------
        plotting_list : List
            List of objects to plot.
        plotting_options : dict
            Additional plotting options.
        """
        self._backend.plot_iter(plotting_list=plotting_list, **plotting_options)

    def plot(self, plottable_object: Any, **plotting_options):
        """Plots an object using the specified backend.

        Parameters
        ----------
        plottable_object : Any
            Object to plot.
        plotting_options : dict
            Additional plotting options.
        """
        self._backend.plot(plottable_object=plottable_object, **plotting_options)

    def show(
        self,
        plottable_object: Any = None,
        screenshot: str = None,
        name_filter: bool = None,
        **kwargs
        ) -> List:
        """Show the plotted objects.

        Parameters
        ----------
        plottable_object : Any, optional
            Object to show, by default None.
        screenshot : str, optional
            Path to save a screenshot, by default None.
        name_filter : bool, optional
            Flag to filter the object, by default None.
        kwargs : dict
            Additional options the selected backend accepts.

        Returns
        -------
        List
            List of picked objects.
        """
        return self._backend.show(
            plottable_object=plottable_object,
            screenshot=screenshot,
            name_filter=name_filter,
            **kwargs
        )

    def animate(
        self,
        frames: List[Any],
        fps: int = 30,
        loop: bool = False,
        scalar_bar_args: Optional[dict] = None,
        **plot_kwargs,
    ):
        """Create an animation from a sequence of frames.

        This method provides a convenient way to create animations from time-series
        simulation results, transient analyses, and dynamic phenomena. It wraps the
        backend's animation functionality in a simple, consistent API.

        Parameters
        ----------
        frames : List[Any]
            Sequence of frame objects to animate. Can be PyVista meshes,
            ``MeshObjectPlot`` objects, or any plottable objects.
        fps : int, optional
            Frames per second for playback. Default is 30.
        loop : bool, optional
            Whether to loop animation continuously. Default is False.
        scalar_bar_args : dict, optional
            Scalar bar arguments to apply to all frames (e.g., ``clim`` for fixed
            color scale). If not provided, a global color scale is calculated
            automatically to ensure visual integrity across frames.
        **plot_kwargs
            Additional keyword arguments passed to add_mesh for all frames
            (e.g., ``cmap='viridis'``, ``opacity=0.8``).

        Returns
        -------
        Animation
            Animation controller object with playback controls:
            - ``play()``: Start animation
            - ``pause()``: Pause animation
            - ``stop()``: Stop and reset to first frame
            - ``step_forward()``: Advance one frame
            - ``step_backward()``: Rewind one frame
            - ``seek(frame_index)``: Jump to specific frame
            - ``save(filename)``: Export to video (MP4, GIF, AVI)
            - ``show()``: Display with plotter

        Raises
        ------
        ValueError
            If frames list is empty or fps is not positive.
        NotImplementedError
            If the backend does not support animations.

        See Also
        --------
        Animation : Animation controller class with detailed playback controls

        Notes
        -----
        - Fixed color scales are recommended (and calculated by default) to ensure
          visual integrity and prevent misleading animations where color meanings
          change between frames.
        - For large datasets (1000+ frames or >5M cells), consider implementing
          a custom ``FrameSequence`` with lazy loading capabilities.
        - The animation uses the backend's native capabilities. Currently, only
          PyVista backend supports animations.

        Examples
        --------
        Create and play a simple animation from transient simulation results:

        >>> from ansys.tools.visualization_interface import Plotter
        >>> import pyvista as pv
        >>> # Create example meshes representing time steps
        >>> sphere = pv.Sphere()
        >>> frames = []
        >>> for i in range(20):
        ...     mesh = sphere.copy()
        ...     mesh["displacement"] = np.random.rand(mesh.n_points) * i * 0.1
        ...     frames.append(mesh)
        >>> plotter = Plotter()
        >>> animation = plotter.animate(frames, fps=10, loop=True)
        >>> animation.show()

        Export animation to video:

        >>> animation = plotter.animate(frames, fps=30)
        >>> animation.save("simulation.mp4", quality=8)

        Use fixed color scale for accurate comparison:

        >>> animation = plotter.animate(
        ...     frames,
        ...     fps=30,
        ...     scalar_bar_args={"clim": (0.0, 1.0), "title": "Displacement [m]"}
        ... )
        >>> animation.play()
        >>> animation.show()

        Control playback programmatically:

        >>> animation = plotter.animate(frames)
        >>> animation.play()  # Start animation
        >>> # ... after some time ...
        >>> animation.pause()  # Pause
        >>> animation.step_forward()  # Advance one frame
        >>> animation.seek(10)  # Jump to frame 10
        >>> animation.stop()  # Reset to beginning
        """
        # Check if backend supports animations
        if not hasattr(self._backend, "create_animation"):
            raise NotImplementedError(
                f"Backend {type(self._backend).__name__} does not support animations. "
                "Only PyVistaBackend currently supports animation creation."
            )

        # Delegate to backend's animation creation
        return self._backend.create_animation(
            frames=frames,
            fps=fps,
            loop=loop,
            scalar_bar_args=scalar_bar_args,
            **plot_kwargs,
        )

    def add_points(
        self,
        points: Union[List, Any],
        color: str = "red",
        size: float = 10.0,
        **kwargs
    ) -> Any:
        """Add point markers to the scene.

        This method provides a backend-agnostic way to add point markers to the
        visualization scene. The points will be rendered using the active backend's
        native point rendering capabilities.

        Parameters
        ----------
        points : Union[List, Any]
            Points to add. Can be a list of coordinates or array-like object.
            Expected format: [[x1, y1, z1], [x2, y2, z2], ...] or Nx3 array.
        color : str, default: "red"
            Color of the points. Can be a color name (e.g., 'red', 'blue')
            or hex color code (e.g., '#FF0000').
        size : float, default: 10.0
            Size of the point markers in pixels or display units
            (interpretation depends on backend).
        **kwargs : dict
            Additional backend-specific keyword arguments for advanced customization.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added points.
            Can be used for further manipulation or removal.

        Examples
        --------
        Add simple point markers at three locations:

        >>> from ansys.tools.visualization_interface import Plotter
        >>> plotter = Plotter()
        >>> points = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
        >>> plotter.add_points(points, color='blue', size=15)
        >>> plotter.show()

        Add points with custom styling:

        >>> import numpy as np
        >>> points = np.random.rand(100, 3)
        >>> plotter.add_points(points, color='yellow', size=8)
        >>> plotter.show()
        """
        return self._backend.add_points(points=points, color=color, size=size, **kwargs)

    def add_lines(
        self,
        points: Union[List, Any],
        connections: Optional[Union[List, Any]] = None,
        color: str = "white",
        width: float = 1.0,
        **kwargs
    ) -> Any:
        """Add line segments to the scene.

        This method provides a backend-agnostic way to add lines to the
        visualization scene. Lines can connect points sequentially or based
        on explicit connectivity information.

        Parameters
        ----------
        points : Union[List, Any]
            Points defining the lines. Can be a list of coordinates or array-like object.
            Expected format: [[x1, y1, z1], [x2, y2, z2], ...] or Nx3 array.
        connections : Optional[Union[List, Any]], default: None
            Line connectivity. If None, connects points sequentially (0->1, 1->2, 2->3, ...).
            If provided, should define line segments as pairs of point indices:
            [[start_idx1, end_idx1], [start_idx2, end_idx2], ...] or Mx2 array
            where M is the number of line segments.
        color : str, default: "white"
            Color of the lines. Can be a color name or hex color code.
        width : float, default: 1.0
            Width of the lines in pixels or display units (interpretation depends on backend).
        **kwargs : dict
            Additional backend-specific keyword arguments for advanced customization.

        Returns
        -------
        Any
            Backend-specific actor or object representing the added lines.
            Can be used for further manipulation or removal.

        Examples
        --------
        Add a line connecting points sequentially:

        >>> from ansys.tools.visualization_interface import Plotter
        >>> plotter = Plotter()
        >>> points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        >>> plotter.add_lines(points, color='green', width=2.0)
        >>> plotter.show()

        Add specific line segments with explicit connectivity:

        >>> points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
        >>> connections = [[0, 1], [2, 3], [0, 2]]  # Connect specific pairs
        >>> plotter.add_lines(points, connections=connections, color='red', width=3.0)
        >>> plotter.show()
        """
        return self._backend.add_lines(
            points=points, connections=connections, color=color, width=width, **kwargs
        )

    def add_planes(
        self,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        normal: Tuple[float, float, float] = (0.0, 0.0, 1.0),
        i_size: float = 1.0,
        j_size: float = 1.0,
        **kwargs
    ) -> Any:
        """Add a plane to the scene.

        This method provides a backend-agnostic way to add plane objects to the
        visualization scene. Planes are useful for showing reference planes,
        symmetry planes, or cutting planes.

        Parameters
        ----------
        center : Tuple[float, float, float], default: (0.0, 0.0, 0.0)
            Center point of the plane in 3D space (x, y, z).
        normal : Tuple[float, float, float], default: (0.0, 0.0, 1.0)
            Normal vector of the plane (x, y, z). The vector will be normalized
            by the backend if needed.
        i_size : float, default: 1.0
            Size of the plane in the i direction (local coordinate system).
        j_size : float, default: 1.0
            Size of the plane in the j direction (local coordinate system).
        **kwargs : dict
            Additional backend-specific keyword arguments for advanced customization
            (e.g., color, opacity, resolution).

        Returns
        -------
        Any
            Backend-specific actor or object representing the added plane.
            Can be used for further manipulation or removal.

        Examples
        --------
        Add a horizontal plane at z=0:

        >>> from ansys.tools.visualization_interface import Plotter
        >>> plotter = Plotter()
        >>> plotter.add_planes(center=(0, 0, 0), normal=(0, 0, 1), i_size=2.0, j_size=2.0)
        >>> plotter.show()

        Add a vertical plane with custom styling:

        >>> plotter.add_planes(
        ...     center=(1, 0, 0),
        ...     normal=(1, 0, 0),
        ...     i_size=3.0,
        ...     j_size=3.0,
        ...     color='lightblue',
        ...     opacity=0.5
        ... )
        >>> plotter.show()
        """
        return self._backend.add_planes(
            center=center, normal=normal, i_size=i_size, j_size=j_size, **kwargs
        )

    def add_text(
        self,
        text: str,
        position: Union[Tuple[float, float], Tuple[float, float, float], str],
        font_size: int = 12,
        color: str = "white",
        **kwargs
    ) -> Any:
        """Add text to the scene.

        This method provides a backend-agnostic way to add text labels to the
        visualization scene. Text can be positioned in 2D screen coordinates or
        3D world coordinates depending on the backend capabilities.

        Parameters
        ----------
        text : str
            Text string to display.
        position : Union[Tuple[float, float], Tuple[float, float, float], str]
            Position for the text. Can be:
            - 2D tuple (x, y) for screen/viewport coordinates (pixels from bottom-left)
            - 3D tuple (x, y, z) for world coordinates (backend-dependent support)
            - String position like 'upper_left', 'upper_right', 'lower_left',
              'lower_right', 'upper_edge', 'lower_edge' (backend-dependent support)
        font_size : int, default: 12
            Font size for the text in points.
        color : str, default: "white"
            Color of the text. Can be a color name or hex color code.
        **kwargs : dict
            Additional backend-specific keyword arguments for advanced customization
            (e.g., font_family, bold, italic, shadow).

        Returns
        -------
        Any
            Backend-specific actor or object representing the added text.
            Can be used for further manipulation or removal.

        Examples
        --------
        Add text at a screen position:

        >>> from ansys.tools.visualization_interface import Plotter
        >>> plotter = Plotter()
        >>> plotter.add_text("Title", position=(10, 10), font_size=18, color='yellow')
        >>> plotter.show()

        Add text at a 3D world coordinate:

        >>> plotter.add_text(
        ...     "Point A",
        ...     position=(1.0, 2.0, 3.0),
        ...     font_size=14,
        ...     color='red'
        ... )
        >>> plotter.show()
        """
        return self._backend.add_text(
            text=text, position=position, font_size=font_size, color=color, **kwargs
        )
