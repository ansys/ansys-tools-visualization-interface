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
"""Provides the hide buttons widget for the PyAnsys plotter."""
from pathlib import Path
from typing import TYPE_CHECKING

from vtk import vtkActor, vtkButtonWidget, vtkPNGReader

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget

if TYPE_CHECKING:
    from ansys.tools.visualization_interface.backends.pyvista.pyvista import Plotter


class HideButton(PlotterWidget):
    """Provides the hide widget for the Visualization Interface Tool ``Plotter`` class.

    Parameters
    ----------
    plotter_helper : PlotterHelper
        Plotter to add the hide widget to.
    dark_mode : bool, optional
        Whether to activate the dark mode or not.

    """

    def __init__(self, plotter: "Plotter", dark_mode: bool = False) -> None:
        """Initialize the ``HideButton`` class."""
        # Call PlotterWidget ctor
        super().__init__(plotter._pl.scene)
        self._dark_mode = dark_mode
        # Initialize variables
        self._actor: vtkActor = None
        self._plotter = plotter
        self._button: vtkButtonWidget = self._plotter._pl.scene.add_checkbox_button_widget(
            self.callback, position=(10, 10), size=30, border_size=3
        )
        self.update()

    def callback(self, state: bool) -> None:
        """Remove or add the hide widget actor upon click.

        Parameters
        ----------
        state : bool
            Whether the state of the button, which is inherited from PyVista, is active.

        """
        if state:
            for widget in self.plotter._widgets:
                if widget is not self:
                    widget._button.Off()
                    widget._button.GetRepresentation().SetVisibility(0)
        else:
            for widget in self.plotter._widgets:
                widget._button.On()
                widget._button.GetRepresentation().SetVisibility(1)

    def update(self) -> None:
        """Define the hide widget button parameters."""
        if self._dark_mode:
            is_inv = "_inv"
        else:
            is_inv = ""

        show_vr = self._button.GetRepresentation()
        show_vison_icon_file = Path(
            Path(__file__).parent / "_images" / f"visibilityon{is_inv}.png"
        )
        show_visoff_icon_file = Path(
            Path(__file__).parent / "_images" / f"visibilityon{is_inv}.png"
        )
        show_r_on = vtkPNGReader()
        show_r_on.SetFileName(show_vison_icon_file)
        show_r_on.Update()
        image_on = show_r_on.GetOutput()

        show_r_off = vtkPNGReader()
        show_r_off.SetFileName(show_visoff_icon_file)
        show_r_off.Update()
        image_off = show_r_off.GetOutput()


        show_vr.SetButtonTexture(0, image_off)
        show_vr.SetButtonTexture(1, image_on)
