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

"""USD backend interface for visualization using python-usd-viewer."""

from pathlib import Path
from typing import Any, Iterable, Tuple
import warnings

try:
    from pxr import Usd
except ImportError:  # pragma: no cover
    warnings.warn(
        "The 'pxr' module is required to use the USD backend. "
        "Install OpenUSD or run 'usd-setup' from the python-usd-viewer package."
    )

try:
    from ansys.tools.usdviewer.viewer import USDViewer
    from ansys.tools.usdviewer.vtk_converter import VTKConverter
except ImportError:  # pragma: no cover
    warnings.warn(
        "The 'ansys-tools-usdviewer' package is required to use the USD backend. "
        "Install it with: pip install ansys-tools-usdviewer"
    )

from ansys.tools.visualization_interface.backends._base import BaseBackend
from ansys.tools.visualization_interface.types.mesh_object_plot import MeshObjectPlot
from ansys.tools.visualization_interface.utils.logger import logger

_USD_EXTENSIONS = {".usd", ".usda", ".usdc", ".usdz"}


class USDInterface(BaseBackend):
    """USD backend interface using python-usd-viewer.

    Parameters
    ----------
    title : str, default: ``"USD Viewer"``
        Title of the viewer window.
    size : tuple[int, int], default: ``(750, 750)``
        Width and height of the viewer window in pixels.
    """

    def __init__(self, title: str = "USD Viewer", size: Tuple[int, int] = (750, 750)) -> None:
        """Initialize the USD interface."""
        self._viewer = USDViewer(title=title, size=size)
        self._converter = VTKConverter()
        self._stage = Usd.Stage.CreateInMemory()
        self._prim_counter: dict = {}

    def _unique_prim_path(self, prefix: str) -> str:
        """Return a unique USD prim path for the given prefix."""
        idx = self._prim_counter.get(prefix, 0)
        self._prim_counter[prefix] = idx + 1
        return f"/{prefix}_{idx}"

    def plot(self, plottable_object: Any, **plotting_options) -> None:
        """Add a plottable object to the USD stage.

        Parameters
        ----------
        plottable_object : Any
            Supported types:

            * :class:`pxr.Usd.Stage` — replaces the current stage.
            * ``str`` / :class:`pathlib.Path` — USD files replace the current
              stage; VTK-compatible files are converted and merged into it.
            * :class:`~ansys.tools.visualization_interface.types.mesh_object_plot.MeshObjectPlot`
              — the underlying PyVista mesh is converted and added.
            * Any PyVista or VTK dataset — converted via
              :class:`~ansys.tools.usdviewer.vtk_converter.VTKConverter`.
        **plotting_options : dict
            Reserved for future backend-specific options.
        """
        if isinstance(plottable_object, Usd.Stage):
            self._stage = plottable_object

        elif isinstance(plottable_object, (str, Path)):
            path = Path(plottable_object)
            if path.suffix.lower() in _USD_EXTENSIONS:
                self._stage = Usd.Stage.Open(str(path))
            else:
                self._converter.convert_vtk_file_to_usd(str(path), self._stage)

        elif isinstance(plottable_object, MeshObjectPlot):
            prim_path = self._unique_prim_path("Mesh")
            self._converter.convert_vtk_to_usd(plottable_object.mesh, self._stage, prim_path.lstrip("/"))

        elif hasattr(plottable_object, "GetPoints") or hasattr(plottable_object, "GetPolys"):
            prim_path = self._unique_prim_path("Mesh")
            self._converter.convert_vtk_to_usd(plottable_object, self._stage, prim_path.lstrip("/"))

        else:
            logger.warning(
                f"USDInterface: unsupported object type '{type(plottable_object).__name__}'. "
                "Supported types: Usd.Stage, str/Path, MeshObjectPlot, PyVista/VTK datasets."
            )

    def plot_iter(self, plotting_list: Iterable) -> None:
        """Add all objects in an iterable to the USD stage."""
        for obj in plotting_list:
            self.plot(obj)

    def show(self, plottable_object=None, screenshot=None, name_filter=None, **kwargs) -> None:
        """Display the current USD stage in the viewer window.

        Opens the Qt-based USD viewer and starts the event loop.
        This call blocks until the window is closed.

        Parameters
        ----------
        plottable_object : Any, optional
            Optional object to plot before showing.
        screenshot : str, optional
            Unused — screenshots are not supported by the USD backend.
        name_filter : str, optional
            Unused — name filtering is not supported by the USD backend.
        **kwargs : dict
            Additional keyword arguments (unused).
        """
        if plottable_object is not None:
            self.plot(plottable_object)

        self._viewer.plot(self._stage)
        self._viewer.show()

    def add_points(self, points, color="red", size=10.0, **kwargs):
        """Not implemented for the USD backend."""
        raise NotImplementedError("add_points is not implemented for USDInterface.")

    def add_lines(self, points, connections=None, color="white", width=1.0, **kwargs):
        """Not implemented for the USD backend."""
        raise NotImplementedError("add_lines is not implemented for USDInterface.")

    def add_planes(self, center=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0), i_size=1.0, j_size=1.0, **kwargs):
        """Not implemented for the USD backend."""
        raise NotImplementedError("add_planes is not implemented for USDInterface.")

    def add_text(self, text, position, font_size=12, color="white", **kwargs):
        """Not implemented for the USD backend."""
        raise NotImplementedError("add_text is not implemented for USDInterface.")

    def add_labels(self, points, labels, font_size=12, point_size=5.0, **kwargs):
        """Not implemented for the USD backend."""
        raise NotImplementedError("add_labels is not implemented for USDInterface.")

    def clear(self) -> None:
        """Not implemented for the USD backend."""
        raise NotImplementedError("clear is not implemented for USDInterface.")
