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
"""Provides the parallel projection button widget."""
from pathlib import Path
from typing import TYPE_CHECKING

from vtk import vtkActor, vtkButtonWidget, vtkPNGReader

from ansys.tools.visualization_interface.backends.pyvista.widgets.widget import PlotterWidget

if TYPE_CHECKING:
    from ansys.tools.visualization_interface.backends.pyvista.pyvista import Plotter


class ParallelProjectionButton(PlotterWidget):
    """Toggle parallel projection for the camera.

    Parameters
    ----------
    plotter : Plotter
        Plotter to add the widget to.
    dark_mode : bool, optional
        Whether dark mode is active.

    """

    def __init__(self, plotter: "Plotter", dark_mode: bool = False) -> None:
        """Initialize the button."""
        super().__init__(plotter._pl.scene)
        self._dark_mode = dark_mode
        self._actor: vtkActor = None
        self._plotter = plotter
        self._button: vtkButtonWidget = self._plotter._pl.scene.add_checkbox_button_widget(
            self.callback, position=(5, 50), size=30, border_size=3
        )
        self.update()

    def callback(self, state: bool) -> None:
        """Toggle parallel projection.

        Parameters
        ----------
        state : bool
            Button state from PyVista.

        """
        if state:
            self._plotter.scene.camera.enable_parallel_projection()
        else:
            self._plotter.scene.camera.disable_parallel_projection()

    def update(self) -> None:
        """Update the button appearance."""
        if self._dark_mode:
            is_inv = "_inv"
        else:
            is_inv = ""

        show_vr = self._button.GetRepresentation()
        icon_file = Path(Path(__file__).parent / "_images" / f"parallel_projection{is_inv}.png")
        show_r_on = vtkPNGReader()
        show_r_on.SetFileName(icon_file)
        show_r_on.Update()
        image_on = show_r_on.GetOutput()

        show_r_off = vtkPNGReader()
        show_r_off.SetFileName(icon_file)
        show_r_off.Update()
        image_off = show_r_off.GetOutput()

        show_vr.SetButtonTexture(0, image_off)
        show_vr.SetButtonTexture(1, image_on)
