# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Provides for implementing buttons in PyAnsys."""

from abc import abstractmethod
from pathlib import Path

from pyvista import Plotter
from vtk import vtkButtonWidget, vtkPNGReader

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget


class Button(PlotterWidget):
    """Provides the abstract class for implementing buttons in PyAnsys.

    Notes
    -----
    This class wraps the PyVista ``add_checkbox_button_widget()`` method.

    Parameters
    ----------
    plotter : Plotter
        Plotter to draw the buttons on.
    button_config : tuple
        Tuple containing the position and the path to the icon of the button.

    """

    def __init__(self, plotter: Plotter, button_config: tuple):
        """Initialize the ``Button`` class."""
        super().__init__(plotter)
        self._button: vtkButtonWidget = self.plotter.add_checkbox_button_widget(
            self.callback, position=button_config.value[2], size=30, border_size=3
        )
        self.button_config = button_config

    @abstractmethod
    def callback(self, state: bool) -> None:
        """Get the functionality of the button, which is implemented by subclasses.

        Parameters
        ----------
        state : bool
            Whether the button is active.

        """
        pass

    def update(self) -> None:
        """Assign the image that represents the button."""
        button_repr = self._button.GetRepresentation()
        button_icon_path = Path(
            Path(__file__).parent / "_images", self.button_config.value[1]
        )
        button_icon = vtkPNGReader()
        button_icon.SetFileName(button_icon_path)
        button_icon.Update()
        image = button_icon.GetOutput()
        button_repr.SetButtonTexture(0, image)
        button_repr.SetButtonTexture(1, image)
