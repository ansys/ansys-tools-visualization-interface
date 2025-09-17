# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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
from typing import Any

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
        ) -> None:
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
        """
        self._backend.show(
            plottable_object=plottable_object,
            screenshot=screenshot,
            name_filter=name_filter,
            **kwargs
        )
